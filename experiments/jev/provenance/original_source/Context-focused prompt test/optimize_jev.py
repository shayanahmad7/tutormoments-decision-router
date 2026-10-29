"""Prompt-only Jev experiment. Original source, baseline and submitted files are read-only."""
from __future__ import annotations
import argparse
import collections
import csv
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import statistics
import time

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
spec = importlib.util.spec_from_file_location('original_jev_experiment', BASE / 'jev_experiment.py')
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)
MODEL = original.MODEL
PRICE = original.PRICE_PER_MILLION

PROMPTS = {
    'A - Current learner evidence': {
        'instructions': (
            'Which next tutoring move best fits what the learner has demonstrated on the current math task? '
            'Read the sequence of student work, tutor help, and described screen actions. '
            'Give greatest weight to the current task and the most recent substantive student contribution, '
            'using earlier turns to interpret it. A correct answer supplied by the tutor, or a student saying yes, '
            'does not by itself demonstrate understanding. An earlier error does not require more help after '
            'the learner has independently corrected and explained it.'
        ),
        'criteria': {
            'scaffolding': 'The learner needs targeted support to access or complete the current mathematical step: unresolved confusion, an uncorrected error, inability to begin, or difficulty understanding the required concept or representation. Help with the specific obstacle while leaving meaningful participation.',
            'rigor': 'The learner is ready to attempt the next step independently, explain or justify a successful step, connect ideas, or transfer a method. Build on demonstrated understanding or self-correction instead of repeating mastered work or supplying the next operation.',
        },
    },
    'B - Explicit context checks': {
        'instructions': (
            'At the stopping point of this math tutoring conversation, should the next move provide scaffolding '
            'or push for rigor? Ground the choice in the full dialogue, including described student writing and actions. '
            'Identify the current problem and the mathematical step now at issue. Check what the student has actually '
            'done or explained, which parts the tutor already supplied, and whether a specific difficulty remains unresolved. '
            'Choose for this point in the conversation, not for an earlier task. Do not treat agreement with a tutor '
            'explanation as independent mastery. Do not treat hesitation, an old mistake, or a new problem alone as proof '
            'that the tutor should explain more. A student who corrects their own error can be ready for justification '
            'or a new challenge. Select the instructional opportunity; do not write a tutor reply.'
        ),
        'criteria': {
            'scaffolding': 'Support is needed now. The learner lacks access to the current mathematical idea or step, remains stuck or confused, or has a mathematical error they have not resolved. The appropriate move reduces that specific obstacle through a hint, representation, worked substep, or clarification.',
            'rigor': 'The learner can take more responsibility now. They have succeeded on the relevant step, demonstrated a usable method or relationship, self-corrected, or can productively attempt the next step without being given its solution. Ask for reasoning, justification, connections, an independent attempt, or transfer instead of unnecessary reteaching.',
        },
    },
    'C - Observable evidence criteria': {
        'instructions': (
            'Which instructional opportunity is supported by the learner evidence at the end of this conversation? '
            'Use the current mathematical problem, student utterances and student screen actions. '
            'Interpret the last utterance in its preceding exchange. Distinguish the learner doing the thinking '
            'from the tutor doing it. Choose the move that fits the learner now.'
        ),
        'criteria': {
            'scaffolding': {
                'meaning': 'Give targeted support for a mathematical obstacle that is still unresolved.',
                'evidence': ['Student cannot start or continue the relevant step.', 'Student shows an uncorrected misunderstanding or cannot access the representation.', 'Student explicitly needs help with the current mathematical idea.'],
                'boundary': 'Support is not automatically needed because the topic is new, the student once made an error, or the tutor has an explanation available.',
            },
            'rigor': {
                'meaning': 'Increase independent mathematical work, explanation, connection, or challenge.',
                'evidence': ['Student completes the relevant work or gives a coherent method.', 'Student identifies and corrects their own mistake.', 'Student is ready for an independent attempt or a why/how question rather than further explanation.'],
                'boundary': 'A correct option or yes/no agreement immediately after the tutor supplied the answer is not enough, by itself, to infer mastery.',
            },
        },
    },
    'D - Support versus demonstrated readiness': {
        'instructions': (
            'Does the learner at this moment primarily need support to access the mathematics, or further challenge '
            'to deepen understanding they have demonstrated? Read the chronological conversation around the current '
            'task and the earlier work needed to interpret it. Track who supplied the mathematical ideas. '
            'If the learner made an error and the tutor then supplied the solution, a final yes or correct repetition '
            'does not show that the learner has resolved the difficulty. If the learner independently explains, '
            'successfully applies an idea, or corrects their own reasoning, do not keep helping merely because they '
            'struggled earlier. Distinguish support for access from increasing mathematical demand; the fact that '
            'a tutor could ask a question or request an explanation does not by itself make the moment a rigor opportunity. '
            'Use student speech and described student actions, not tutor claims that the student understands.'
        ),
        'criteria': {
            'scaffolding': 'The current mathematics is still challenging for the learner. A targeted hint, representation, guided substep, or focused check is needed to help them access it. The learner may give a short correct answer after heavy prompting while still needing this support. The aim is to bridge the present conceptual or procedural gap, not add difficulty yet.',
            'rigor': 'The learner has demonstrated enough understanding of the relevant mathematics to take on greater independence, justification, a connection, transfer, or a harder version. Build on their own successful work or self-correction. The aim is to deepen or extend demonstrated understanding rather than reteach the same step.',
        },
    },
}


def canonical(value):
    return original.encoded(value)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def write(path, value):
    original.write_json(path, value)


def rows_and_split():
    rows = original.source_rows()
    split = json.loads((HERE / 'Development and evaluation split.json').read_text())
    assert not set(split['development_indices']) & set(split['evaluation_indices'])
    assert sorted(split['development_indices'] + split['evaluation_indices']) == list(range(520))
    return rows, split


def payload_for(row, name):
    baseline = original.payload_for(row)
    question = PROMPTS[name]
    baseline['questions'] = {'next_move': {'type': 'choice', **question}}
    return baseline


def freeze_prompts():
    frozen = HERE / 'Frozen candidate prompts.json'
    if frozen.exists():
        prior=json.loads(frozen.read_text())
        assert all(name in PROMPTS and PROMPTS[name]==value for name,value in prior.items()), 'An existing frozen candidate changed'
        if prior!=PROMPTS:
            assert len(PROMPTS)<=rows_and_split()[1]['maximum_candidates']
            assert not (HERE/'Frozen selected prompt.json').exists()
            assert not list((HERE/'Full rerun/Responses').glob('*.json'))
            write(HERE/'Development refinement record.json',{
                'original_candidates_unchanged':list(prior),
                'added_candidates':[n for n in PROMPTS if n not in prior],
                'added_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'feedback_source':'Development cases only; see Development refinement cases.json',
                'new_evaluation_predictions_at_revision':0,
                'original_prompt_file_sha256':sha(frozen.read_bytes()),
            })
            write(frozen,PROMPTS)
    else:
        write(frozen, PROMPTS)


def cost_so_far():
    # Original 520 decisions plus every new successful request. Full reuses count once.
    total = json.loads((BASE / 'Results.json').read_text())['actual_usage_cost_estimate_usd']
    for f in (HERE / 'Development').glob('*/Responses/*.json'):
        e = json.loads(f.read_text())
        total += e['response']['usage']['input_tokens'] * PRICE / 1e6
    for f in (HERE / 'Full rerun/Responses').glob('*.json'):
        e = json.loads(f.read_text())
        if not e.get('reused_from_development'):
            total += e['response']['usage']['input_tokens'] * PRICE / 1e6
    return total


def request_one(row, index, name, dest, key):
    payload = payload_for(row, name)
    request_hash = sha(canonical(payload))
    file = dest / f'{index:03d}.json'
    if file.exists():
        entry = json.loads(file.read_text())
        assert entry['request_sha256'] == request_hash
        original.parse_answer(entry['response'])
        return entry
    # A byte-based allowance for the next request prevents crossing the combined $1 ceiling.
    if cost_so_far() + len(canonical(payload)) * PRICE / 1e6 > 1:
        raise RuntimeError('Combined original-plus-optimization $1 ceiling reached. Progress preserved.')
    response, elapsed = original.api_call('/systemone', key, payload)
    entry = dict(moment_index=index, candidate=name, request_sha256=request_hash, request_payload=payload,
                 response=response, latency_ms=elapsed)
    write(file, entry)
    original.parse_answer(response)
    return entry


def entries_in(directory):
    return {int(f.stem): json.loads(f.read_text()) for f in directory.glob('*.json')}


def metrics(rows, entries, indices):
    confusion = {g: {p: 0 for p in original.LABELS} for g in original.LABELS}
    for i in indices:
        answer = original.parse_answer(entries[i]['response'])
        confusion[rows[i]['dimension']][answer['choice']] += 1
    per_label = {}
    for label in original.LABELS:
        n = sum(confusion[label].values())
        tp = confusion[label][label]
        predicted = sum(confusion[g][label] for g in original.LABELS)
        precision = tp / predicted if predicted else 0
        recall = tp / n if n else 0
        per_label[label] = dict(n=n, correct=tp, recall=recall,
                                f1=2*precision*recall/(precision+recall) if precision+recall else 0)
    n = len(indices)
    correct = sum(confusion[g][g] for g in original.LABELS)
    return dict(n=n, correct=correct, accuracy=correct/n,
                balanced_accuracy=statistics.mean(v['recall'] for v in per_label.values()),
                macro_f1=statistics.mean(v['f1'] for v in per_label.values()),
                per_label=per_label, confusion_matrix=confusion)


def baseline_entries():
    return entries_in(BASE / 'Responses')


def development():
    rows, split = rows_and_split()
    freeze_prompts()
    key = original.load_key(BASE / '.env')
    summary = {'baseline': metrics(rows, baseline_entries(), split['development_indices'])}
    for name in PROMPTS:
        directory = HERE / 'Development' / name / 'Responses'
        for k, i in enumerate(split['development_indices'], 1):
            request_one(rows[i], i, name, directory, key)
            if k % 25 == 0:
                print(f'{name}: {k}/{len(split["development_indices"])} development cases saved', flush=True)
        entries = entries_in(directory)
        summary[name] = metrics(rows, entries, split['development_indices'])
        write(HERE / 'Development scores.json', summary)
        print(json.dumps({'candidate': name, 'development': summary[name]}), flush=True)
    print(json.dumps(summary, indent=2), flush=True)


def select():
    freeze_prompts()
    summary = json.loads((HERE / 'Development scores.json').read_text())
    candidates = [name for name in summary if name != 'baseline']
    assert candidates and all(summary[n]['n'] == rows_and_split()[1]['development_n'] for n in candidates)
    ranked = sorted(candidates, key=lambda n: (-summary[n]['balanced_accuracy'], -summary[n]['macro_f1'],
                   -summary[n]['accuracy'], len(canonical(PROMPTS[n])), n))
    selection = dict(selected_candidate=ranked[0], ranking=ranked,
                     rule='development balanced accuracy, macro F1, accuracy, shorter prompt, name',
                     selected_prompt_sha256=sha(canonical(PROMPTS[ranked[0]])),
                     development_scores=summary, frozen_before_heldout_predictions=True,
                     split_sha256=sha((HERE/'Development and evaluation split.json').read_bytes()))
    target = HERE / 'Frozen selected prompt.json'
    if target.exists():
        prior=json.loads(target.read_text())
        assert all(prior[k]==v for k,v in selection.items()), 'Selection already frozen; do not replace'
    else:
        assert not list((HERE/'Full rerun/Responses').glob('*.json')), 'Selection must precede full rerun'
        selection['frozen_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        selection['new_heldout_predictions_at_freeze']=0
        write(target, selection)
    (HERE / 'Selected prompt.txt').write_text(json.dumps(PROMPTS[ranked[0]], indent=2, ensure_ascii=False)+'\n')
    print(json.dumps(selection, indent=2), flush=True)
    return ranked[0]


def full():
    rows, split = rows_and_split()
    selection = json.loads((HERE / 'Frozen selected prompt.json').read_text())
    name = selection['selected_candidate']
    assert selection['selected_prompt_sha256'] == sha(canonical(PROMPTS[name]))
    key = original.load_key(BASE / '.env')
    dest = HERE / 'Full rerun/Responses'
    development_dir = HERE / 'Development' / name / 'Responses'
    with (HERE/'Full rerun/Requests.jsonl').open('w') if (HERE/'Full rerun').exists() else _requests_file() as out:
        for i,row in enumerate(rows):
            out.write(json.dumps(dict(moment_index=i,payload=payload_for(row,name)),ensure_ascii=False)+'\n')
            if i in set(split['development_indices']):
                entry = json.loads((development_dir/f'{i:03d}.json').read_text())
                assert entry['request_sha256'] == sha(canonical(payload_for(row,name)))
                entry['reused_from_development'] = True
                write(dest/f'{i:03d}.json', entry)
            else:
                request_one(row,i,name,dest,key)
            if (i+1)%50==0:
                print(f'Selected prompt: {i+1}/520 cases saved',flush=True)
    print(json.dumps(report(),indent=2),flush=True)


def _requests_file():
    (HERE/'Full rerun').mkdir(parents=True,exist_ok=True)
    return (HERE/'Full rerun/Requests.jsonl').open('w')


def paired(rows, old, new, indices):
    improved = harmed = same_correct = same_wrong = 0
    for i in indices:
        gold=rows[i]['dimension']
        a=old[i]['response']['answers']['next_move']['choice']==gold
        b=new[i]['response']['answers']['next_move']['choice']==gold
        if not a and b: improved+=1
        elif a and not b: harmed+=1
        elif a and b: same_correct+=1
        else: same_wrong+=1
    return dict(improved=improved,harmed=harmed,correct_both=same_correct,wrong_both=same_wrong,
                net_correct_change=improved-harmed,accuracy_change=(improved-harmed)/len(indices))


def report():
    rows, split=rows_and_split()
    old=baseline_entries();new=entries_in(HERE/'Full rerun/Responses')
    assert set(new)==set(range(520)), 'Do not report a partial run as complete'
    result={'status':'complete','selection':json.loads((HERE/'Frozen selected prompt.json').read_text()),
            'all_520':{'baseline':metrics(rows,old,list(range(520))),'optimized':metrics(rows,new,list(range(520))),
                       'paired':paired(rows,old,new,list(range(520)))},
            'evaluation_382':{'baseline':metrics(rows,old,split['evaluation_indices']),
                              'optimized':metrics(rows,new,split['evaluation_indices']),
                              'paired':paired(rows,old,new,split['evaluation_indices'])},
            'combined_original_and_optimization_cost_estimate_usd':cost_so_far(),
            'median_latency_ms':statistics.median(e['latency_ms'] for e in new.values()),
            'scope_note':split['previous_exposure_note']}
    records=[]
    for i,m in enumerate(rows):
        payload=payload_for(m,result['selection']['selected_candidate'])
        assert sha(canonical(payload))==new[i]['request_sha256']
        a=original.parse_answer(old[i]['response']);b=original.parse_answer(new[i]['response'])
        records.append(dict(moment_index=i,subset='development' if i in set(split['development_indices']) else 'evaluation',
                            reference_label=m['dimension'],original_decision=a['choice'],optimized_decision=b['choice'],
                            original_correct=a['choice']==m['dimension'],optimized_correct=b['choice']==m['dimension'],
                            optimized_p_scaffolding=b['probabilities']['scaffolding'],optimized_p_rigor=b['probabilities']['rigor'],
                            optimized_confidence=b['confidence'],latency_ms=new[i]['latency_ms']))
    with (HERE/'All 520 - Original versus optimized.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
    write(HERE/'Final comparison.json',result)
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','development','select','full','report'])
    args=parser.parse_args()
    if args.mode=='prepare':
        rows,split=rows_and_split();freeze_prompts()
        print(json.dumps({'development':split['development_n'],'evaluation':split['evaluation_n'],'candidates':list(PROMPTS)},indent=2))
    elif args.mode=='development':development()
    elif args.mode=='select':select()
    elif args.mode=='full':full()
    else:print(json.dumps(report(),indent=2))


if __name__=='__main__':main()
