"""Small auditable REST client. Credentials never enter saved request traces."""
from __future__ import annotations
import hashlib,json,os,pathlib,threading,time,urllib.error,urllib.request,uuid

class APIError(RuntimeError):
    pass

class OpenAIClient:
    def __init__(self, trace_directory, key=None, timeout=90):
        self.key=key or os.environ.get("OPENAI_API_KEY")
        if not self.key: raise APIError("Set OPENAI_API_KEY before running live experiments.")
        self.trace_directory=pathlib.Path(trace_directory)
        self.trace_directory.mkdir(parents=True,exist_ok=True)
        self.timeout=timeout
        self.records=[]
        self.lock=threading.Lock()

    def post(self, endpoint, payload, tag):
        request_id=uuid.uuid4().hex
        start=time.perf_counter()
        record={"request_id":request_id,"tag":tag,"endpoint":endpoint,"payload":payload,
                "payload_sha256":hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest(),
                "started_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"attempts":[]}
        response=None
        for attempt in range(3):
            attempt_start=time.perf_counter()
            req=urllib.request.Request("https://api.openai.com/v1/"+endpoint.lstrip("/"),
                data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+self.key,
                "Content-Type":"application/json"},method="POST")
            try:
                with urllib.request.urlopen(req,timeout=self.timeout) as result:
                    response=json.loads(result.read())
                    record["attempts"].append({"http_status":result.status,"elapsed_ms":(time.perf_counter()-attempt_start)*1000})
                break
            except urllib.error.HTTPError as exc:
                error=exc.read().decode(errors="replace").replace(self.key,"[REDACTED]")[:2000]
                record["attempts"].append({"http_status":exc.code,"error":error,"elapsed_ms":(time.perf_counter()-attempt_start)*1000})
                if exc.code not in [429,500,502,503,504] or attempt==2: break
                time.sleep(min(2**attempt,4))
            except Exception as exc:
                record["attempts"].append({"error_type":type(exc).__name__,"error":str(exc).replace(self.key,"[REDACTED]")[:500],"elapsed_ms":(time.perf_counter()-attempt_start)*1000})
                if attempt==2:break
                time.sleep(min(2**attempt,4))
        record["elapsed_ms"]=(time.perf_counter()-start)*1000
        record["response"]=response
        with self.lock:self.records.append(record)
        (self.trace_directory/(request_id+".json")).write_text(json.dumps(record,ensure_ascii=False,indent=2))
        if response is None:raise APIError("API call failed; see ignored trace "+request_id)
        return response,record

    def chat(self,model,messages,tag,**kwargs):
        payload={"model":model,"messages":messages,**kwargs}
        response,record=self.post("chat/completions",payload,tag)
        choices=response.get("choices",[])
        if not choices:raise APIError("No choices in response; see trace "+record["request_id"])
        message=choices[0]["message"]
        text=message.get("content")
        if not isinstance(text,str) or not text.strip():raise APIError("No completed text; see trace "+record["request_id"])
        return text,record

    def decide(self,messages,tag,model="gpt-6-luna"):
        # No publisher dimension, rubric, future turns or human continuation is an input.
        history="\n\n".join(str(x.get("role",""))+": "+str(x.get("content","")) for x in messages)
        question={"type":"choice","name":"next_teaching_mode",
          "instructions":"Select the mode for the tutor's next reply from the dialogue evidence. Scaffold when the learner needs targeted help to understand or take the next mathematical step. Rigor when the learner is ready to explain, justify, connect ideas or work more independently and extra assistance would take over that work. Do not assume speed or a bare agreement establishes understanding. Select the best-supported mode for this particular moment, not a general preference for always helping or always questioning.",
          "choices":[{"value":"scaffolding","description":"Target support to the learner's current mathematical difficulty while preserving their participation."},{"value":"rigor","description":"Invite the learner's reasoning or appropriate independent work; avoid unnecessary takeover."}]}
        response,record=self.post("decisions",{"model":model,"input":history,"questions":[question]},tag)
        answer=next((a for a in response.get("answers",[]) if a.get("name")=="next_teaching_mode"),{})
        if answer.get("type")!="choice" or answer.get("choice") not in ["scaffolding","rigor"]:
            return None,record
        return answer,record
