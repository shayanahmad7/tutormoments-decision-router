"""Auditable REST client with resumable trace reuse and a credit circuit breaker."""
from __future__ import annotations
import hashlib,json,os,pathlib,threading,time,urllib.error,urllib.request,uuid
class APIError(RuntimeError):pass
class QuotaExhausted(APIError):pass

class OpenAIClient:
    def __init__(self,trace_directory,key=None,timeout=90):
        self.key=key or os.environ.get('OPENAI_API_KEY')
        if not self.key:raise APIError('Set OPENAI_API_KEY before live experiments.')
        self.trace_directory=pathlib.Path(trace_directory);self.trace_directory.mkdir(parents=True,exist_ok=True)
        self.timeout=timeout;self.records=[];self.lock=threading.Lock();self.credit_exhausted=threading.Event();self.cache={}
        for f in self.trace_directory.glob('*.json'):
            try:
                r=json.loads(f.read_text())
                if r.get('response') is not None:self.cache[(r['tag'],r['payload_sha256'])]=r
            except (ValueError,KeyError,OSError):pass

    def post(self,endpoint,payload,tag):
        sha=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
        cached=self.cache.get((tag,sha))
        if cached is not None:
            reused={**cached,'local_resume_reuse':True}
            with self.lock:self.records.append(reused)
            return reused['response'],reused
        if self.credit_exhausted.is_set():raise QuotaExhausted('API credit balance exhausted; restore funding before resuming.')
        rid=uuid.uuid4().hex;start=time.perf_counter();record={'request_id':rid,'tag':tag,'endpoint':endpoint,'payload':payload,'payload_sha256':sha,'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'attempts':[]};response=None
        for attempt in range(4):
            if self.credit_exhausted.is_set():break
            st=time.perf_counter();req=urllib.request.Request('https://api.openai.com/v1/'+endpoint.lstrip('/'),data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+self.key,'Content-Type':'application/json'},method='POST')
            try:
                with urllib.request.urlopen(req,timeout=self.timeout) as result:
                    response=json.loads(result.read());record['rate_limits']={k:result.headers.get(k) for k in ['x-ratelimit-limit-requests','x-ratelimit-remaining-requests','x-ratelimit-limit-tokens','x-ratelimit-remaining-tokens','x-ratelimit-reset-tokens'] if result.headers.get(k) is not None};record['attempts'].append({'http_status':result.status,'elapsed_ms':(time.perf_counter()-st)*1000})
                break
            except urllib.error.HTTPError as exc:
                error=exc.read().decode(errors='replace').replace(self.key,'[REDACTED]')[:2000]
                record['attempts'].append({'http_status':exc.code,'error':error,'elapsed_ms':(time.perf_counter()-st)*1000})
                try:
                    detail=json.loads(error).get('error',{});code=detail.get('code') if isinstance(detail,dict) else None;kind=detail.get('type') if isinstance(detail,dict) else None
                except (ValueError,AttributeError):code=kind=None
                if code=='credit_balance_exhausted' or kind=='insufficient_quota':
                    self.credit_exhausted.set();break
                if exc.code not in [429,500,502,503,504] or attempt==3:break
                try:delay=float(exc.headers.get('retry-after',''))
                except (ValueError,TypeError):delay=5*(attempt+1) if exc.code==429 else min(2**attempt,8)
                time.sleep(min(max(delay,0.1),60))
            except Exception as exc:
                record['attempts'].append({'error_type':type(exc).__name__,'error':str(exc).replace(self.key,'[REDACTED]')[:500],'elapsed_ms':(time.perf_counter()-st)*1000})
                if attempt==3:break
                time.sleep(min(2**attempt,8))
        record['elapsed_ms']=(time.perf_counter()-start)*1000;record['response']=response
        with self.lock:
            self.records.append(record)
            if response is not None:self.cache[(tag,sha)]=record
        (self.trace_directory/(rid+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2))
        if response is None:
            if self.credit_exhausted.is_set():raise QuotaExhausted('API credit balance exhausted; saved trace '+rid)
            raise APIError('API call failed; see ignored trace '+rid)
        return response,record

    def chat(self,model,messages,tag,**kwargs):
        response,record=self.post('chat/completions',{'model':model,'messages':messages,**kwargs},tag);choices=response.get('choices',[])
        if not choices:raise APIError('No choices in response; trace '+record['request_id'])
        text=choices[0]['message'].get('content')
        if not isinstance(text,str) or not text.strip():raise APIError('No completed text; trace '+record['request_id'])
        return text,record

    def decide(self,messages,tag,model='gpt-6-luna'):
        history='\n\n'.join(str(x.get('role',''))+': '+str(x.get('content','')) for x in messages)
        question={'type':'choice','name':'next_teaching_mode','instructions':"Select the mode for the tutor's next reply from the dialogue evidence. Scaffold when the learner needs targeted help to understand or take the next mathematical step. Rigor when the learner is ready to explain, justify, connect ideas or work more independently and extra assistance would take over that work. Do not assume speed or a bare agreement establishes understanding. Select the best-supported mode for this particular moment, not a general preference for always helping or always questioning.",'choices':[{'value':'scaffolding','description':"Target support to the learner's current mathematical difficulty while preserving their participation."},{'value':'rigor','description':"Invite the learner's reasoning or appropriate independent work; avoid unnecessary takeover."}]}
        response,record=self.post('decisions',{'model':model,'input':history,'questions':[question]},tag);answer=next((a for a in response.get('answers',[]) if a.get('name')=='next_teaching_mode'),{})
        if answer.get('type')!='choice' or answer.get('choice') not in ['scaffolding','rigor']:return None,record
        return answer,record
