#!/usr/bin/env python3
"""Run the predeclared small pilot. Source corpus and full traces stay outside Git."""
from __future__ import annotations
import argparse,concurrent.futures,csv,hashlib,json,pathlib,statistics,sys,time,traceback
ROOT=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from tm_router.api import OpenAIClient,QuotaExhausted
from tm_router import publisher_protocol as protocol
from tm_router.scoring_contract import FACETS_RESPONSE_FORMAT,parse_strict_facets
from tm_router.reliability import (recover_terminal_checkpoint, publisher_no_generated_annotation,
    has_tutor_text, metric_coverage, paired_scored_comparison, first_decision_agreement)

def save(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    if isinstance(obj,dict) and 'calls' in obj:obj['calls']=list({x['request_id']:x for x in obj['calls']}.values())
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2));tmp.replace(path)

def call_summary(record,kind,step):
    response=record.get('response') or {}
    return {'request_id':record['request_id'],'kind':kind,'step':step,'elapsed_ms':record['elapsed_ms'],'model':response.get('model'),'usage':response.get('usage',{}),'attempts':len(record['attempts']),'payload_sha256':record['payload_sha256']}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=pathlib.Path,required=True);ap.add_argument('--config',type=pathlib.Path,default=ROOT/'configs/pilot8.json');ap.add_argument('--workers',type=int,default=2);ap.add_argument('--retry-failed',action='store_true');ap.add_argument('--stage',choices=['rollouts','score','all'],default='all');args=ap.parse_args()
    config=json.loads(args.config.read_text());source=args.source.read_bytes()
    if hashlib.sha256(source).hexdigest()!=config['source_moments_sha256']:raise RuntimeError('Source hash differs from fixed plan.')
    moments=[json.loads(l) for l in source.decode().splitlines() if l.strip()]
    run_tag=args.config.stem
    run_dir=ROOT/'data'/run_tag;run_dir.mkdir(parents=True,exist_ok=True)
    client=OpenAIClient(ROOT/'raw_responses'/run_tag)
    # Only the tutor and structured router are original requested models. Auxiliaries
    # use the same GPT-5.5 proxy because an Anthropic key is unavailable.
    proxy=config['tutor_model']
    proxy_student_kwargs={'reasoning_effort':'low','max_completion_tokens':128000}
    proxy_judge_kwargs={'reasoning_effort':'high','max_completion_tokens':128000,'response_format':{'type':'json_object'}}
    def rollout(moment,condition):
        idx=moments.index(moment) if False else index_by_id[moment['id']]
        path=run_dir/f'{idx}-{condition}.json'
        state=json.loads(path.read_text()) if path.exists() else {'moment_index':idx,'moment_id':moment['id'],'condition':condition,'generated_turns':[],'calls':[],'next_speaking_step':0,'routes':[],'status':'pending','auxiliary_models_are_proxies':True}
        if recover_terminal_checkpoint(state):save(path,state)
        if state.get('status') in ['rollout_complete','scored']:return state
        if state.get('status')=='failed':
            if not args.retry_failed:return state
            state['previous_failure']={k:state.get(k) for k in ['error','error_type']}
            state.pop('error',None);state.pop('error_type',None);state['status']='pending'
        state['status']='running';save(path,state)
        try:
            generated=state['generated_turns']
            for step in range(state['next_speaking_step'],protocol.MAX_SPEAKING_TURNS):
                tag=f'{idx}:{condition}:{step}'
                if step%2==0:
                    route=None;router_ms=0
                    if condition.endswith('_plus_decisions'):
                        route,rr=client.decide(protocol.router_messages(moment,generated),tag+':router',model=config['decision_model']);state['calls'].append(call_summary(rr,'router',step));router_ms=rr['elapsed_ms'];state['routes'].append({'step':step,'answer':route,'fallback_to_original_prompt':route is None})
                    directive=protocol.route_instruction(route['choice']) if route else None
                    mode='scaffolding_rigor' if condition.startswith('aware_low_reasoning') else condition
                    msgs=protocol.tutor_messages(moment,mode=mode,generated_turns=generated,route_instruction=directive)
                    tutor_kwargs=dict(protocol.TUTOR_KWARGS)
                    if condition.startswith('aware_low_reasoning'):tutor_kwargs['reasoning_effort']='low'
                    text,record=client.chat(config['tutor_model'],msgs,tag+':tutor',**tutor_kwargs)
                    c=call_summary(record,'tutor',step);c['reply_end_to_end_ms']=router_ms+record['elapsed_ms'];state['calls'].append(c)
                    cleaned,ended,changed=protocol.parse_tutor_output(text)
                    pieces=protocol.split_messages(cleaned)
                    if not pieces and not ended and not changed:pieces=['...']
                    generated=protocol.append_generated_turns(moment,generated,'TUTOR',pieces)
                    state['generated_turns']=generated;state['next_speaking_step']=step+1;state['last_tutor_control']={'ended':ended,'problem_change':changed}
                    if ended or changed:
                        state['stop_reason']='end' if ended else 'problem_change'
                        state['status']='rollout_complete'
                    save(path,state)
                    if ended or changed:break
                else:
                    msgs=protocol.student_messages(moment,generated)
                    text,record=client.chat(proxy,msgs,tag+':student_proxy',**proxy_student_kwargs);state['calls'].append(call_summary(record,'student_proxy',step))
                    pieces=protocol.split_messages(text) or ['...'];generated=protocol.append_generated_turns(moment,generated,'STUDENT',pieces);state['generated_turns']=generated;state['next_speaking_step']=step+1;save(path,state)
            state['status']='rollout_complete';state.setdefault('stop_reason','max_five_speaking_calls');save(path,state)
        except Exception as exc:
            state.update({'status':'failed','error_type':type(exc).__name__,'error':str(exc)[:1000]});save(path,state)
            if isinstance(exc,QuotaExhausted):raise
        print(json.dumps({'event':'rollout','moment':idx,'condition':condition,'status':state['status'],'speaking_calls':state['next_speaking_step']}),flush=True)
        return state
    def score(moment,condition):
        idx=index_by_id[moment['id']];path=run_dir/f'{idx}-{condition}.json'
        if not path.exists():return None
        state=json.loads(path.read_text())
        if state.get('status')=='scored' or state.get('status')=='failed':return state
        if state.get('status')!='rollout_complete':return state
        try:
            if not state['generated_turns']:
                # Publisher score_batch: minimal Annotation, no judge calls.
                state['annotation']=publisher_no_generated_annotation(moment['id'])
                state['annotation_source']='publisher_minimal_no_generated_turns'
                state['status']='scored';state.pop('scoring_error',None);save(path,state)
                return state
            prompt=protocol.scorer_annotate_prompt(moment,state['generated_turns'])
            if prompt is None:raise RuntimeError('No generated excerpt to score')
            text,record=client.chat(proxy,[{'role':'user','content':prompt}],f'{idx}:{condition}:judge_annotate',**proxy_judge_kwargs);state['calls'].append(call_summary(record,'judge_proxy_annotate',0));annotation=protocol.parse_annotation(text)
            decomposed={}
            for kind in ['action','overscaffold']:
                prompt=protocol.scorer_decompose_prompt(annotation,kind)
                if prompt:
                    facet_kwargs={**proxy_judge_kwargs,'response_format':FACETS_RESPONSE_FORMAT}
                    text,record=client.chat(proxy,[{'role':'user','content':prompt}],f'{idx}:{condition}:judge_decompose_{kind}',**facet_kwargs);state['calls'].append(call_summary(record,'judge_proxy_decompose_'+kind,0));decomposed[kind]=parse_strict_facets(text)
                else:decomposed[kind]=[]
            prompt=protocol.scorer_structure_prompt(decomposed['action'])
            if prompt:
                text,record=client.chat(proxy,[{'role':'user','content':prompt}],f'{idx}:{condition}:judge_structure',**proxy_judge_kwargs);state['calls'].append(call_summary(record,'judge_proxy_structure',0));label=protocol.parse_action_label(text)
            else:label='neither'
            state['annotation']={**annotation,'action_label':label,'action_decomposed':decomposed['action'],'overscaffold_decomposed':decomposed['overscaffold']};state['annotation_source']='proxy_judge';state['status']='scored';state.pop('scoring_error',None);save(path,state)
        except Exception as exc:
            state['scoring_error']={'type':type(exc).__name__,'message':str(exc)[:1000]};save(path,state)
            if isinstance(exc,QuotaExhausted):raise
        print(json.dumps({'event':'score','moment':idx,'condition':condition,'status':state['status'],'label':state.get('annotation',{}).get('action_label')}),flush=True)
        return state
    index_by_id={m['id']:j for j,m in enumerate(moments)}
    selected=[moments[x['moment_index']] for x in config['cases']]
    for c,m in zip(config['cases'],selected):
        if c['moment_id']!=m['id']:raise RuntimeError('Fixed moment ID changed')
    jobs=[]
    for i,m in enumerate(selected):
        order=config['conditions'][i%len(config['conditions']):]+config['conditions'][:i%len(config['conditions'])]
        jobs.extend((m,c) for c in order)
    def run_job(job):
        if args.stage=='all':
            rollout(*job)
            return score(*job)
        return rollout(*job) if args.stage=='rollouts' else score(*job)
    credit_stop=False
    pool=concurrent.futures.ThreadPoolExecutor(max_workers=args.workers)
    todo=iter(jobs);active=set()
    for _ in range(args.workers):
        job=next(todo,None)
        if job is not None:active.add(pool.submit(run_job,job))
    try:
        while active:
            done,active=concurrent.futures.wait(active,return_when=concurrent.futures.FIRST_COMPLETED)
            for future in done:
                try:future.result()
                except QuotaExhausted:credit_stop=True
            if credit_stop:
                for future in active:future.cancel()
                break
            for _ in done:
                job=next(todo,None)
                if job is not None:active.add(pool.submit(run_job,job))
    finally:pool.shutdown(wait=True,cancel_futures=True)
    summary={'status':'Exploratory pipeline experiment; final paper focus not selected','source_config':str(args.config.relative_to(ROOT)),'tutor_model':config['tutor_model'],'decision_model':config['decision_model'],'source_auxiliary_models':{'student':protocol.STUDENT_MODEL,'scorer':protocol.SCORER_MODEL},'actual_auxiliary_models':{'student':proxy,'scorer':proxy},'facet_output_contract':'Strict facets-array wrapper; prevents loss of actions encoded as JSON dictionary keys. Publisher prompt text unchanged.', 'protocol_deviation':'Original tutor, oracle-student and scorer prompt text and five-call dialogue protocol retained. GPT-5.5 replaces Claude Opus4.6 for simulated student and scorer. These are proxy scores, not an official leaderboard replication. Student lowreasoning; judge highreasoning. All same across conditions.','timing_scope':'Full nonstreaming request wall time, router+generator per tutor reply; not TTFT. Cache and concurrency can affect timing.','conditions':{},'failures':[],'stopped_for_api_credits':credit_stop}
    case_rows=[]
    states_by_condition={}
    for condition in config['conditions']:
        states=[json.loads((run_dir/f'{index_by_id[m["id"]]}-{condition}.json').read_text()) for m in selected if (run_dir/f'{index_by_id[m["id"]]}-{condition}.json').exists()]
        states_by_condition[condition]=states
        scored=[s for s in states if s['status']=='scored'];pairs=[(moments[s['moment_index']],s['annotation']) for s in scored]
        calls=[c for s in states for c in s.get('calls',[])];tutor=[c for c in calls if c['kind']=='tutor'];router=[c for c in calls if c['kind']=='router'];metrics=protocol.publisher_metrics(pairs) if pairs else None
        def distribution(values):return {'n':len(values),'median':statistics.median(values) if values else None,'mean':statistics.mean(values) if values else None,'min':min(values) if values else None,'max':max(values) if values else None}
        summary['conditions'][condition]={'planned_cases':len(config['cases']),'rollouts_completed':sum(s['status'] in ['rollout_complete','scored'] for s in states),'scored_cases':len(scored),'proxy_publisher_metrics':metrics,'tutor_reply_end_to_end_ms':distribution([c['reply_end_to_end_ms'] for c in tutor]),'tutor_generator_ms':distribution([c['elapsed_ms'] for c in tutor]),'router_ms':distribution([c['elapsed_ms'] for c in router]),'api_calls':len(calls),'token_usage':{k:sum(c['usage'].get(k,0) for c in calls) for k in ['input_tokens','output_tokens','prompt_tokens','completion_tokens','total_tokens']}}
        summary['conditions'][condition]['metric_scope']='Available scored cases; use paired_scored_comparison for matched condition comparison.'
        summary['conditions'][condition]['metric_coverage']=metric_coverage(states,len(config['cases']))
        summary['conditions'][condition]['initial_route_agreement_proxy']=first_decision_agreement(states,moments) if condition.endswith('_plus_decisions') else None
        for s in states:
            if s.get('status')=='failed' or s.get('scoring_error'):summary['failures'].append({'moment_index':s['moment_index'],'condition':condition,'error':s.get('error') or s.get('scoring_error')})
            if s.get('annotation'):case_rows.append({'moment_index':s['moment_index'],'condition':condition,'publisher_category':moments[s['moment_index']]['dimension'],'proxy_action_label':s['annotation']['action_label'],'proxy_overscaffold_facets':len(s['annotation']['overscaffold_decomposed']),'generated_messages':len(s['generated_turns']),'stop_reason':s['stop_reason'],'has_tutor_text':has_tutor_text(s),'annotation_source':s.get('annotation_source','proxy_judge_or_legacy')})
    summary['paired_scored_comparison']=paired_scored_comparison(states_by_condition,moments,[index_by_id[m['id']] for m in selected],protocol.publisher_metrics)
    save(ROOT/'results'/f'{run_tag}_summary.json',summary)
    if case_rows:
        with (ROOT/'results'/f'{run_tag}_case_results.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(case_rows[0]));w.writeheader();w.writerows(case_rows)
    print(json.dumps({'event':'summary_saved','path':str(ROOT/'results'/f'{run_tag}_summary.json'),'conditions':{k:{'rollouts':v['rollouts_completed'],'scored':v['scored_cases']} for k,v in summary['conditions'].items()}}),flush=True)

if __name__=='__main__':main()
