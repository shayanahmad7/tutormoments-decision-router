"""Standalone Jev classification experiment. No tutor, simulated learner, or judge calls."""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import time
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
SOURCE = STUDY / '02 - Original Data/002 - TutorMoments-Preview/Publisher Files/moments.jsonl'
TEMPLATE = STUDY / '18 - TutorMoments Decision Pipeline/src/tm_router/publisher_prompts/tutor/scaffolding_rigor.txt'
TEMPLATE_SHA = 'db8be72a82126753be213c8cc25d57c696e495675a709c9ca527d84428d95e49'
MODEL = 'jev-1.14.0'
API = 'https://api.typesafe.ai/v1'
PRICE_PER_MILLION = 0.042
LABELS = ('scaffolding', 'rigor')
DECISION_INSTRUCTION = (
    'For the conversation supplied in state, return the decision for the next tutor move: '
    'scaffolding or rigor. Make this choice using the tutoring instructions above. '
    'Return the decision rather than generating a tutor response.'
)


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(value).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    tmp.replace(path)


def source_rows():
    rows = [json.loads(line) for line in SOURCE.read_text().splitlines() if line.strip()]
    assert len(rows) == 520
    assert collections.Counter(r['dimension'] for r in rows) == {'scaffolding': 260, 'rigor': 260}
    assert digest(TEMPLATE.read_bytes()) == TEMPLATE_SHA, 'Publisher template changed'
    assert {r['student']['context'] for r in rows} == {'Platform: tutoring_provider_a'}
    return rows


def payload_for(moment):
    # Deliberate allowlist. No id, dimension, rubric, provenance, future reference, or persona.
    context = moment['context']
    assert all(set(t) == {'turn_number', 'role', 'text'} for t in context)
    dialogue = '\n'.join(f"Turn {t['turn_number']}. {t['role'].upper()}: {t['text']}" for t in context)
    instructions = TEMPLATE.read_text().strip().replace('{student_context}', moment['student']['context'])
    return {
        'model': MODEL,
        'state': 'Here is the conversation so far:\n\n' + dialogue,
        'questions': {'next_move': {
            'type': 'choice',
            'instructions': instructions + '\n\n' + DECISION_INSTRUCTION,
            'criteria': {'scaffolding': None, 'rigor': None},
        }},
    }


def prepare():
    rows = source_rows()
    payloads = [payload_for(row) for row in rows]
    manifest = {
        'experiment': 'Jev standalone scaffold-versus-rigor classification',
        'model_requested': MODEL,
        'dataset_sha256': digest(SOURCE.read_bytes()),
        'publisher_template_sha256': TEMPLATE_SHA,
        'decision_instruction': DECISION_INSTRUCTION,
        'n_moments': len(rows),
        'reference_counts': dict(collections.Counter(r['dimension'] for r in rows)),
        'payload_sha256': [digest(encoded(p)) for p in payloads],
        'total_payload_utf8_bytes': sum(len(encoded(p)) for p in payloads),
        'largest_payload_utf8_bytes': max(len(encoded(p)) for p in payloads),
        'byte_based_input_cost_estimate_usd': sum(len(encoded(p)) for p in payloads) * PRICE_PER_MILLION / 1e6,
        'price_usd_per_million_input_tokens': PRICE_PER_MILLION,
        'primary_measure': 'Agreement with publisher dimension labels on all 520 records',
        'secondary_measures': ['Per-label recall', 'Confusion matrix', 'Macro F1', 'Brier score',
                               'Predefined confidence/coverage summaries', 'Consistent unique-cut sensitivity',
                               'Same first 49 moments as previous Decisions experiment'],
        'no_prompt_tuning': True,
        'no_response_generation': True,
        'no_gold_labels_in_requests': True,
        'source_reference_used_only_in_local_scoring': True,
        'submitted_materials_edited': False,
    }
    target = HERE / 'Frozen experiment.json'
    if target.exists():
        assert json.loads(target.read_text()) == manifest, 'Frozen experiment changed; do not overwrite'
    else:
        write_json(target, manifest)
    with (HERE / 'Requests.jsonl').open('w') as f:
        for i, p in enumerate(payloads):
            f.write(json.dumps({'moment_index': i, 'payload': p}, ensure_ascii=False) + '\n')
    with (HERE / 'Reference labels.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['moment_index', 'moment_id', 'reference_label', 'conversation_id', 'cut_turn'])
        writer.writeheader()
        for i, r in enumerate(rows):
            writer.writerow(dict(moment_index=i, moment_id=r['id'], reference_label=r['dimension'],
                                 conversation_id=r['provenance']['conv_id'], cut_turn=r['provenance']['cut_turn']))
    (HERE / 'Exact prompt.txt').write_text(payloads[0]['questions']['next_move']['instructions'] + '\n')
    print(json.dumps({k: v for k, v in manifest.items() if k != 'payload_sha256'}, indent=2))
    return rows, payloads


def load_key(env_file):
    key = os.environ.get('TYPESAFE_API_KEY', '').strip()
    p = Path(env_file)
    if not key and p.exists():
        for line in p.read_text().splitlines():
            if line.strip().startswith('TYPESAFE_API_KEY='):
                key = line.split('=', 1)[1].strip().strip('\"\'')
    if not key:
        raise RuntimeError('TYPESAFE_API_KEY is missing. No live requests were sent.')
    return key


def api_call(path, key, payload=None):
    request = urllib.request.Request(API + path, data=encoded(payload) if payload else None,
                                     headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'},
                                     method='POST' if payload else 'GET')
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.load(response)
        return result, (time.perf_counter() - started) * 1000
    except urllib.error.HTTPError as error:
        detail = error.read().decode('utf-8', errors='replace').replace(key, '[REDACTED]')[:2000]
        raise RuntimeError(f'HTTP {error.code}: {detail}') from None


def parse_answer(response):
    if response.get('model') != MODEL:
        raise ValueError(f"Unexpected model: {response.get('model')}; expected pinned {MODEL}")
    answer = response['answers']['next_move']
    assert answer['type'] == 'choice'
    assert answer['choice'] in LABELS
    probs = answer['probabilities']
    assert set(probs) == set(LABELS)
    assert all(isinstance(p, (float, int)) and math.isfinite(p) and 0 <= p <= 1 for p in probs.values())
    assert abs(sum(probs.values()) - 1) <= 0.02
    assert probs[answer['choice']] >= max(probs.values()) - 1e-6
    assert isinstance(answer['confidence'], (float, int)) and 0 <= answer['confidence'] <= 1
    return answer


def accuracy(records):
    return sum(r['correct'] for r in records) / len(records) if records else None


def score(rows, saved):
    records = []
    for i, moment in enumerate(rows):
        if i not in saved:
            continue
        entry = saved[i]
        answer = parse_answer(entry['response'])
        gold = moment['dimension']
        records.append({
            'moment_index': i, 'moment_id': moment['id'], 'reference_label': gold,
            'jev_decision': answer['choice'], 'correct': answer['choice'] == gold,
            'p_scaffolding': answer['probabilities']['scaffolding'], 'p_rigor': answer['probabilities']['rigor'],
            'confidence': answer['confidence'], 'top_probability': max(answer['probabilities'].values()),
            'latency_ms': entry['latency_ms'], 'model': entry['response']['model'],
            'input_tokens': entry['response'].get('usage', {}).get('input_tokens'),
            'conversation_id': moment['provenance']['conv_id'], 'cut_turn': moment['provenance']['cut_turn'],
        })
    if not records:
        return None
    by_group = collections.defaultdict(list)
    for i, m in enumerate(rows):
        by_group[(m['provenance']['conv_id'], m['provenance']['cut_turn'])].append(i)
    contested = {k for k, ids in by_group.items() if len({rows[i]['dimension'] for i in ids}) > 1}
    representative = {ids[0] for k, ids in by_group.items() if k not in contested}
    unique = [r for r in records if r['moment_index'] in representative]
    confusion = {gold: {pred: sum(r['reference_label'] == gold and r['jev_decision'] == pred for r in records)
                        for pred in LABELS} for gold in LABELS}
    per_label = {}
    for label in LABELS:
        tp = confusion[label][label]
        support = sum(confusion[label].values())
        predicted = sum(confusion[g][label] for g in LABELS)
        precision = tp / predicted if predicted else 0
        recall = tp / support if support else 0
        per_label[label] = dict(n=support, correct=tp, recall=recall, precision=precision,
                                f1=2 * precision * recall / (precision + recall) if precision + recall else 0)
    result = {
        'status': 'complete' if len(records) == len(rows) else 'partial',
        'n_completed': len(records), 'n_planned': len(rows),
        'correct': sum(r['correct'] for r in records), 'accuracy': accuracy(records),
        'reference': 'Publisher dimension labels; agreement is not proof of pedagogical correctness or learning gains.',
        'per_label': per_label, 'confusion_matrix_reference_rows_prediction_columns': confusion,
        'balanced_accuracy': statistics.mean(v['recall'] for v in per_label.values()),
        'macro_f1': statistics.mean(v['f1'] for v in per_label.values()),
        'brier_score_rigor': statistics.mean((r['p_rigor'] - (r['reference_label'] == 'rigor')) ** 2 for r in records),
        'latency_ms_median': statistics.median(r['latency_ms'] for r in records),
        'input_tokens': sum(r['input_tokens'] or 0 for r in records),
        'actual_usage_cost_estimate_usd': sum(r['input_tokens'] or 0 for r in records) * PRICE_PER_MILLION / 1e6,
        'confidence_groups': [],
        'unique_consistent_cut_sensitivity': {'n': len(unique), 'correct': sum(r['correct'] for r in unique),
                                             'accuracy': accuracy(unique), 'conflicting_label_cut_groups_excluded': len(contested)},
        'previous_49_comparison_subset': {'n': len([r for r in records if r['moment_index'] < 49]),
                                         'correct': sum(r['correct'] for r in records if r['moment_index'] < 49),
                                         'accuracy': accuracy([r for r in records if r['moment_index'] < 49]),
                                         'previous_openai_decisions_agreement': '37/49; different prompt, descriptive comparison only'},
    }
    for threshold in (0.75, 0.9, 0.95):
        group = [r for r in records if r['top_probability'] >= threshold]
        result['confidence_groups'].append(dict(min_top_probability=threshold, n=len(group),
                                                 coverage=len(group) / len(records), accuracy=accuracy(group)))
    with (HERE / 'Jev decisions.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    write_json(HERE / 'Results.json', result)
    return result


def run(env_file, limit, budget):
    rows, payloads = prepare()
    key = load_key(env_file)
    models, _ = api_call('/models', key)
    write_json(HERE / 'Available models.json', models)
    saved = {}
    for file in (HERE / 'Responses').glob('*.json'):
        entry = json.loads(file.read_text())
        i = entry['moment_index']
        assert entry['request_sha256'] == digest(encoded(payloads[i]))
        parse_answer(entry['response'])
        saved[i] = entry
    allocated = 0.0
    for i, payload in enumerate(payloads[:limit]):
        if i in saved:
            continue
        estimate = len(encoded(payload)) * PRICE_PER_MILLION / 1e6
        if allocated + estimate > budget:
            raise RuntimeError('Prespecified per-launch budget ceiling reached; progress preserved.')
        allocated += estimate
        response, elapsed = api_call('/systemone', key, payload)
        # Preserve every response before validation; invalid output is never turned into a label.
        entry = dict(moment_index=i, request_sha256=digest(encoded(payload)), response=response, latency_ms=elapsed)
        write_json(HERE / 'Responses' / f'{i:03d}.json', entry)
        parse_answer(response)
        saved[i] = entry
        if len(saved) % 25 == 0:
            score(rows, saved)
            print(f'Completed {len(saved)}/520; exact responses saved.', flush=True)
    result = score(rows, saved)
    print(json.dumps(result, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['prepare', 'run', 'score'])
    parser.add_argument('--env-file', default=str(HERE / '.env'))
    parser.add_argument('--limit', type=int, default=520)
    parser.add_argument('--budget-usd', type=float, default=1.0)
    args = parser.parse_args()
    if args.mode == 'prepare':
        prepare()
    elif args.mode == 'run':
        try:
            run(args.env_file, args.limit, args.budget_usd)
        except Exception as error:
            write_json(HERE / 'Run status.json', {'status': 'stopped', 'reason': str(error), 'live_results_must_not_be_invented': True})
            raise
    else:
        rows, payloads = prepare()
        saved = {int(f.stem): json.loads(f.read_text()) for f in (HERE / 'Responses').glob('*.json')}
        print(json.dumps(score(rows, saved), indent=2))


if __name__ == '__main__':
    main()
