import csv,json,pathlib,hashlib,collections,html
P=pathlib.Path.cwd(); out=P/'experiments/decision-error-review';out.mkdir(exist_ok=True)
M=[json.loads(x) for x in (P/'data/jev/moments.jsonl').read_text().splitlines()]; assert len(M)==520
G=[x['dimension'] for x in M];runs={};sources=[];derived={}
def add(file,columns,index,base,gold):
 rows=list(csv.DictReader(open(P/file)));assert len(rows)==520
 rows=sorted(rows,key=lambda x:int(x[index])-base)
 assert [int(x[index])-base for x in rows]==list(range(520))
 assert [x[gold] for x in rows]==G
 sources.append({'path':file,'sha256':hashlib.sha256((P/file).read_bytes()).hexdigest()})
 for name,col in columns.items():
  v=[x[col] for x in rows];assert set(v)<=set(['scaffolding','rigor']);runs[name]=v
 return rows
old=add('experiments/openai-decision-comparison/All 520 decisions.csv',{'Jev earlier':'jev_decision','OpenAI Decisions earlier':'openai_decisions_decision','Luna one-word earlier':'llm_one_word_decision'},'moment_number',1,'reference')
latest=add('experiments/final-prompt-revision/All 520 decisions.csv',{'Jev revised':'jev_revised','OpenAI Decisions revised':'decisions_revised','Luna one-word revised':'llm_revised'},'moment_number',1,'reference')
six=add('experiments/jev-all-520-search/All 520 - Six prompt decisions.csv',{f'Jev prompt {x}':f'{x}_decision' for x in 'ABCDEF'},'moment_index',0,'reference_label')
study=add('experiments/jev-decision-study/All 520 decisions.csv',{'Jev original archived':'original_archived','Jev previous archived':'previous_selected_archived','Jev previous fresh':'previous_selected_fresh','Jev selected C':'new_decision','Jev repeat 2':'repeat_2','Jev repeat 3':'repeat_3'},'moment_index',0,'reference_label')
# Verify the older result tables against their downstream archived copies.
old_file='experiments/jev/Context-focused prompt test/All 520 - Original versus optimized.csv'
old_rows=sorted(csv.DictReader(open(P/old_file)),key=lambda x:int(x['moment_index']))
assert len(old_rows)==520 and [x['reference_label'] for x in old_rows]==G
assert [x['original_decision'] for x in old_rows]==runs['Jev original archived']
assert [x['optimized_decision'] for x in old_rows]==runs['Jev previous archived']
sources.append({'path':old_file,'sha256':hashlib.sha256((P/old_file).read_bytes()).hexdigest(),'verified_aliases':['Jev original archived','Jev previous archived']})
for name,col in [('Jev threshold adjustment','thresholded_decision'),('Jev majority of repeats','majority_decision'),('Jev mean probability','mean_probability_decision')]:derived[name]=[x[col] for x in study]
# Duplicate vectors are aliases, not evidence of independent experiments.
canonical={};aliases={}
for name,v in runs.items():
 key=tuple(v)
 if key in canonical:aliases[name]=canonical[key]
 else:canonical[key]=name
unique={name:list(v) for v,name in canonical.items()}
api={int(x['source_index']):x for x in csv.DictReader(open(P/'experiments/astra-publisher-prompt-decisions/All 20 decisions.csv'))}
blinddir=P/'experiments/astra-blind-subagents';frozen=json.loads((blinddir/'frozen-inputs.json').read_text());answers=json.loads((blinddir/'responses.json').read_text());blind={frozen['records'][r['sequence']-1]['source_index']:r['answer'] for r in answers}
fullerrors=[i for i in range(520) if any(v[i]!=G[i] for v in runs.values())]
latestnames=['Jev revised','OpenAI Decisions revised','Luna one-word revised']
latesterrors=[i for i in range(520) if any(runs[n][i]!=G[i] for n in latestnames)]
allthree=[i for i in range(520) if all(runs[n][i]!=G[i] for n in latestnames)]
partialextra=[i for i in api if (api[i]['publisher_prompt_decision']!=G[i] or api[i]['previous_prompt_decision']!=G[i] or blind.get(i,G[i])!=G[i]) and i not in fullerrors]
errors=sorted(set(fullerrors+partialextra))
groups=collections.defaultdict(list)
for i,m in enumerate(M):groups[json.dumps(m['context'],sort_keys=True,ensure_ascii=False)].append(i)
conflicts=[v for v in groups.values() if len({G[i] for i in v})>1];conflictmap={i:[j+1 for j in v if j!=i] for v in conflicts for i in v}
GT={r['conversation_id']:r for r in map(json.loads,(P/'../02 - Original Data/002 - TutorMoments-Preview/Publisher Files/ground_truth.jsonl').read_text().splitlines())}
def annotation(m):
 p=m['provenance'];t=p['conv_id'].split('_')[-1];matches=[x for x in GT.get(t,{}).get('key_moments',[]) if x['turn_start']==p['turn_start'] and x['turn_end']==p['turn_end'] and x['annotator_id']==p['annotator_id']]
 return matches
summary={'n':520,'gold_counts':dict(collections.Counter(G)),'run_columns':len(runs),'distinct_prediction_vectors':len(unique),'aliases':aliases,'full_run_error_union':len(fullerrors),'latest_three_error_union':len(latesterrors),'latest_three_all_wrong':len(allthree),'partial_only_extra':len(partialextra),'document_cases':len(errors),'identical_context_conflict_groups':[[i+1 for i in x] for x in conflicts],'unique_contexts':len(groups),'completed_blind_cases':len(blind),'runs':{n:{'correct':sum(a==b for a,b in zip(v,G)),'scaffolding_correct':sum(v[i]==G[i] for i in range(520) if G[i]=='scaffolding'),'rigor_correct':sum(v[i]==G[i] for i in range(520) if G[i]=='rigor')} for n,v in runs.items()},'source_files':sources}
if len(blind)==20:
 summary['blind_results']={'correct':sum(blind[i]==G[i] for i in blind),'scaffolding_correct':sum(blind[i]==G[i] for i in blind if G[i]=='scaffolding'),'rigor_correct':sum(blind[i]==G[i] for i in blind if G[i]=='rigor'),'agrees_with_api':sum(blind[i]==api[i]['publisher_prompt_decision'] for i in blind),'corrected_api_errors':[i+1 for i in blind if blind[i]==G[i] and api[i]['publisher_prompt_decision']!=G[i]],'new_api_errors':[i+1 for i in blind if blind[i]!=G[i] and api[i]['publisher_prompt_decision']==G[i]]}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
with (out/'All 520 decisions for review.csv').open('w') as f:
 fields=['moment','source_id','reference','domain','identical_context_opposite_label']+list(runs)+list(derived)+['Astra API publisher prompt (20 only)','Astra API earlier prompt (20 only)','Astra fresh subagent (20 only)']
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for i,m in enumerate(M):
  w.writerow({'moment':i+1,'source_id':m['id'],'reference':G[i],'domain':latest[i]['review_domain'],'identical_context_opposite_label':','.join(map(str,conflictmap.get(i,[]))),**{n:v[i] for n,v in runs.items()},**{n:v[i] for n,v in derived.items()},'Astra API publisher prompt (20 only)':api.get(i,{}).get('publisher_prompt_decision',''),'Astra API earlier prompt (20 only)':api.get(i,{}).get('previous_prompt_decision',''),'Astra fresh subagent (20 only)':blind.get(i,'')})
base='https://github.com/shayanahmad7/tutormoments-decision-router/blob/main/experiments/decision-error-review/cases/'
casefolder=out/'cases';casefolder.mkdir(exist_ok=True)
sections=[];pages=[]
intro='''TutorMoments Decision Errors for Review
11 November 2026

What this document is for
This is a casebook of disagreements with the released scaffolding/rigor labels. Read the conversation first, decide what the tutor should do next, then compare the reference and model decisions. A disagreement is a benchmark error, not proof that either the teacher or the model is pedagogically wrong.

Why the website says about 93%
The website scores a short tutoring exchange, not a one-word decision. Its evaluator can label the tutor's behavior scaffolding, rigor, both or neither. A scaffolding case passes when the behavior is scaffolding or both, with no over-scaffolding; a rigor case passes when it is rigor or both, with no over-scaffolding. The leaderboard averages these two rates. Astra's displayed evaluation-aware rates are 93.8% and 91.5%, averaging 92.65% (about 92.7%). Our binary test allows only one category before the next student reply. These are different outcomes.
The released replay uses up to five speaking calls: three tutor replies alternating with two simulated student replies. The tutor receives prior conversation and student metadata, but no reference category. The oracle student receives the released persona and reference continuation. The judge receives the teacher-category hint and the generated exchange. Default student and judge are Claude Opus 4.6; Astra uses high reasoning. We checked the publisher's implementation and configuration, not just the chart.
A tutor can begin with a request for justification, then offer a hint if the simulated student struggles, and be scored as both. That can pass the website metric even when its initial exclusive category choice would disagree with the reference. This explains why the scores cannot be equated; it does not establish exactly how much of Astra's numerical gap is caused by each protocol difference.
Sources: https://tutormoments.allen.ai/
Scoring: https://github.com/allenai/tutormoments/blob/main/src/tutormoments/report.py
Configuration: https://github.com/allenai/tutormoments/blob/main/src/tutormoments/default_config.yaml

The new Astra check
Twenty cases were fixed in the earlier API pilot, with ten of each reference category and twenty distinct students. For this check, each fresh GPT-6 Astra agent received one neutral file containing exactly the earlier API request's input text. Agents were launched sequentially with no parent conversation, no labels, no teacher hints, no future continuation and no earlier answers. Each was asked to read that file only and return one word. The input hashes were recorded before scoring. The Codex system/tool environment differs from the API environment, so this is a diagnostic replication, not an identical inference setup or a new independent test set.
'''
if len(blind)==20:
 b=summary['blind_results'];intro+=f"Fresh Astra subagents: {b['correct']}/20 ({b['correct']/20:.0%}); scaffolding {b['scaffolding_correct']}/10; rigor {b['rigor_correct']}/10. Same-input official API test: 14/20, scaffolding 6/10, rigor 8/10. Earlier revised-prompt API test: 13/20. Subagents agreed with the same-input API on {b['agrees_with_api']}/20 cases. This small, reused sample does not establish a ranking over all 520. No paid API calls were made for this check.\n"
else:intro+='Results pending completion of all twenty.\n'
intro+=f'''\nWhich failures are included
The main casebook includes {len(fullerrors)} distinct moments where at least one archived full-520 raw decision column disagreed with the reference. Across the latest revised Jev, OpenAI Decisions and Luna runs, {len(latesterrors)} moments had at least one error and {len(allthree)} had errors from all three. There are {len(runs)} archived raw-result columns, representing {len(unique)} distinct prediction vectors. Identical copies are documented as aliases, not counted as additional experiments. Derived threshold and ensemble decisions are in the companion CSV and full case files, separate from raw calls. The Astra tests cover only twenty cases; blank Astra cells mean not tested.
This document has {len(errors)} case entries, including {len(partialextra)} extra cases found only by the twenty-case Astra checks. The full source prefix is available in each linked private-repository case file and the local HTML viewer. The Google Doc shows the last eight source records as an explicitly shortened preview; it is not the full model input. Source record counts include speech and screen events, sometimes sharing a turn number. Context is never silently truncated in the linked full case files.

Full-520 results
'''
for n in latestnames+['Jev earlier','OpenAI Decisions earlier','Luna one-word earlier']:
 s=summary['runs'][n];intro+=f"{n}: {s['correct']}/520 ({s['correct']/520:.1%}); scaffolding {s['scaffolding_correct']}/260; rigor {s['rigor_correct']}/260.\n"
intro+='\nHow to judge a disagreement\nLook for evidence available before the cut: what the student attempted, whether the answer was correct, whether they explained it, and whether they were stuck. Asking for an explanation can diagnose understanding as well as push rigor. A brief helpful prompt can support productive struggle without taking over. Check whether the released category refers to the immediate next move or to a larger teacher-annotated episode. Teacher comments can describe later events that the decision model was not shown.\n'
intro+=f"We found {len(conflicts)} groups with exactly identical released context but opposite reference categories: "+'; '.join('/'.join(map(str,[i+1 for i in c])) for c in conflicts)+'. These are concrete ambiguities for a context-only classifier, not grounds to delete cases or silently change labels. Other teacher-label concerns need case-by-case review. The archive also contains known non-math material; domain flags below reproduce the earlier screen and are not a complete new subject audit.\n\nCasebook\n'
for i in errors:
 m=M[i];p=m['provenance'];teacher=annotation(m);wrong=[n for n,v in runs.items() if v[i]!=G[i]]
 context='\n\n'.join(f"Turn {x['turn_number']} | {x['role']}: {x['text']}" for x in m['context'])
 excerpt='\n\n'.join(f"Turn {x['turn_number']} | {x['role']}: {x['text']}" for x in m['context'][-8:])
 title=f'Moment {i+1:03d}'
 pred='\n'.join(f"{n}: {v[i]} {'[disagrees]' if v[i]!=G[i] else '[matches]'}" for n,v in runs.items())
 recent='; '.join(f"{n}: {runs[n][i]}" for n in latestnames)
 astro=''
 if i in api:astro=f"Astra API publisher prompt: {api[i]['publisher_prompt_decision']}; earlier API prompt: {api[i]['previous_prompt_decision']}; fresh subagent: {blind.get(i,'pending')}.\n"
 flag=f"Identical full released context also has opposite category in moment(s) {conflictmap[i]}.\n" if i in conflictmap else ''
 note=m['rubric']['hint']
 full=f"# {title}\n\nSource ID: `{m['id']}`\n\nCut turn: {p['cut_turn']}. Teacher episode: {p['turn_start']}–{p['turn_end']}.\n\n## Conversation available before the decision\n\n{context}\n\n## Reference and model decisions\n\nReference: **{G[i]}**\n\n{flag}\n{pred}\n\n{astro}\n## Released teacher hint (never sent to decision models)\n\n{note}\n\n## Exact source annotation match\n\n"
 if teacher:
  for a in teacher:
   full+='\n'.join(f"**{k}:** {a.get(k,'')}" for k in ['situation','action','result','strategy_label','situation_label','situation_label_agg','action_direction_agg'])+'\n\n'
 else:full+='No exact annotator-plus-turn-range match found. No alternative annotation was substituted.\n'
 full+='\n## Derived results, not additional model calls\n\n'+'\n'.join(f'{n}: {v[i]}' for n,v in derived.items())+'\n'
 (casefolder/f'moment-{i+1:03d}.md').write_text(full)
 section=f"{title}\nDomain from prior screen: {latest[i]['review_domain']}. Cut turn: {p['cut_turn']}.\nFull conversation and original annotation: {base}moment-{i+1:03d}.md\n\nConversation preview (last eight source records)\n{excerpt}\n\nReference: {G[i]}\n{recent}\n{astro}{flag}Other archived raw runs that disagreed: {', '.join(n for n in wrong if n not in latestnames) or 'None'}.\nTeacher hint for review only: {note}\n\n"
 sections.append(section)
 esc=html.escape
 rows=''.join(f'<tr><td>{esc(n)}</td><td>{v[i]}</td><td>{"Disagrees" if v[i]!=G[i] else "Matches"}</td></tr>' for n,v in runs.items())
 pages.append(f'<article id="m{i+1}" data-gold="{G[i]}" data-all="{str(i in allthree).lower()}"><h2>{title}</h2><p>{esc(latest[i]["review_domain"])} · cut turn {p["cut_turn"]}</p><details><summary>Read the full conversation ({len(m["context"])} records)</summary><pre>{esc(context)}</pre></details><details><summary>Reveal reference, model decisions and teacher comments</summary><p>Reference: <b>{G[i]}</b></p><p>{esc(flag)}</p><table><tr><th>Run</th><th>Decision</th><th>Agreement</th></tr>{rows}</table><p>{esc(astro)}</p><h3>Teacher hint, not model input</h3><pre>{esc(note)}</pre><h3>Exact original annotation</h3><pre>{esc(json.dumps(teacher,indent=2,ensure_ascii=False))}</pre><p>Source: {esc(m["id"])}</p></details></article>')
body=intro+'\n'.join(sections)
(out/'Google Doc content.txt').write_text(body)
style='body{font:17px/1.6 system-ui;margin:auto;max-width:1050px;padding:32px;color:#222;background:#fafafa}h1,h2,h3{line-height:1.2}article{background:white;border:1px solid #ddd;border-radius:8px;padding:22px;margin:24px 0}summary{cursor:pointer;font-weight:600;margin:15px 0}pre{white-space:pre-wrap;font:16px/1.55 system-ui}table{border-collapse:collapse;width:100%}td,th{text-align:left;padding:8px;border-bottom:1px solid #ddd}nav{position:sticky;top:0;background:#fafafa;padding:12px 0;border-bottom:1px solid #ccc}input,select{font:inherit;padding:7px;margin-right:8px}'
script='''const cases=[...document.querySelectorAll('article')];function filter(){let q=document.getElementById('q').value.toLowerCase(),g=document.getElementById('g').value,a=document.getElementById('a').checked;let n=0;for(let c of cases){let show=(!q||c.textContent.toLowerCase().includes(q))&&(!g||c.dataset.gold===g)&&(!a||c.dataset.all==='true');c.hidden=!show;if(show)n++;}document.getElementById('count').textContent=n+' cases';}for(let e of document.querySelectorAll('input,select'))e.addEventListener('input',filter);filter();'''
viewer=f'<!doctype html><html><meta charset="utf-8"><title>TutorMoments Decision Error Review</title><style>{style}</style><body><h1>TutorMoments Decision Error Review</h1><p>Read the full context first, then reveal the reference and model decisions. All source text is preserved. No labels have been changed.</p><details><summary>Study summary and scoring explanation</summary><pre>{html.escape(intro)}</pre></details><nav><input id="q" placeholder="Search conversations or moment"><select id="g"><option value="">Either reference</option><option>scaffolding</option><option>rigor</option></select><label><input type="checkbox" id="a">All three revised models wrong</label> <span id="count"></span></nav>'+''.join(pages)+f'<script>{script}</script></body></html>'
(out/'TutorMoments Decision Error Review.html').write_text(viewer)
print(json.dumps({k:v for k,v in summary.items() if k not in ['runs','source_files']},indent=2));print('doc_chars',len(body),'html_bytes',len(viewer.encode()),'exact_annotations',sum(bool(annotation(M[i])) for i in errors))
