"""Verify the saved Jev archive; no API key or network required."""
from pathlib import Path
import collections
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1] / 'experiments/jev'
OPT = ROOT / 'Context-focused prompt test'


def read(path):
    return json.loads(path.read_text())


def payload_hash(payload):
    data = json.dumps(payload, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def verify():
    manifest = read(ROOT / 'provenance/publication_manifest.json')['files_sha256']
    for name, expected in manifest.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    labels = list(csv.DictReader((ROOT / 'Reference labels.csv').open()))
    assert len(labels) == 520
    assert [int(r['moment_index']) for r in labels] == list(range(520))
    gold = [r['reference_label'] for r in labels]
    assert collections.Counter(gold) == {'scaffolding': 260, 'rigor': 260}
    requests = [json.loads(line) for line in (ROOT / 'Requests.jsonl').open()]
    assert len(requests) == 520
    assert [r['moment_index'] for r in requests] == list(range(520))

    def answer(entry):
        response = entry['response']
        assert response['model'] == 'jev-1.14.0'
        a = response['answers']['next_move']
        assert a['type'] == 'choice' and a['choice'] in {'scaffolding', 'rigor'}
        assert set(a['probabilities']) == {'scaffolding', 'rigor'}
        assert abs(sum(a['probabilities'].values()) - 1) < .02
        return a['choice']

    old, new = [], []
    for folder in [ROOT / 'Responses', OPT / 'Full rerun/Responses']:
        assert len(list(folder.glob('*.json'))) == 520
    frozen = read(ROOT / 'Frozen experiment.json')
    selected = read(OPT / 'Frozen selected prompt.json')['selected_candidate']
    prompts = read(OPT / 'Frozen candidate prompts.json')
    assert len(prompts) == 4 and selected in prompts
    split = read(OPT / 'Development and evaluation split.json')
    dev, evaluation = set(split['development_indices']), set(split['evaluation_indices'])
    assert len(dev) == 138 and len(evaluation) == 382
    assert not dev & evaluation and dev | evaluation == set(range(520))
    assert len(set(split['development_students'])) == 18
    # Student separation is checked against transcripts by verify_comparison.py.
    reused = 0
    for i in range(520):
        baseline = read(ROOT / 'Responses' / f'{i:03d}.json')
        revised = read(OPT / 'Full rerun/Responses' / f'{i:03d}.json')
        request = requests[i]['payload']
        assert payload_hash(request) == baseline['request_sha256'] == frozen['payload_sha256'][i]
        assert payload_hash(revised['request_payload']) == revised['request_sha256']
        assert revised['request_payload']['state'] == request['state']
        assert set(request) == set(revised['request_payload']) == {'model', 'state', 'questions'}
        assert revised['request_payload']['questions']['next_move'] == {'type': 'choice', **prompts[selected]}
        if i in dev:
            original_dev = read(OPT / 'Development' / selected / 'Responses' / f'{i:03d}.json')
            assert revised['response'] == original_dev['response']
            assert revised.get('reused_from_development')
            reused += 1
        else:
            assert not revised.get('reused_from_development')
        old.append(answer(baseline))
        new.append(answer(revised))
    assert reused == 138
    for name, prompt in prompts.items():
        folder = OPT / 'Development' / name / 'Responses'
        assert len(list(folder.glob('*.json'))) == 138
        for i in sorted(dev):
            entry = read(folder / f'{i:03d}.json')
            assert entry['request_payload']['state'] == requests[i]['payload']['state']
            assert entry['request_payload']['questions']['next_move'] == {'type': 'choice', **prompt}
            assert payload_hash(entry['request_payload']) == entry['request_sha256']
            answer(entry)
    summary = read(OPT / 'Final comparison.json')
    for key, indices in [('all_520', range(520)), ('evaluation_382', sorted(evaluation))]:
        old_n = sum(old[i] == gold[i] for i in indices)
        new_n = sum(new[i] == gold[i] for i in indices)
        assert old_n == summary[key]['baseline']['correct']
        assert new_n == summary[key]['optimized']['correct']
        assert new_n - old_n == summary[key]['paired']['net_correct_change']
    paired = list(csv.DictReader((OPT / 'All 520 - Original versus optimized.csv').open()))
    original_csv = list(csv.DictReader((ROOT / 'Jev decisions.csv').open()))
    assert len(paired) == len(original_csv) == 520
    for i, (r, baseline) in enumerate(zip(paired, original_csv)):
        assert int(r['moment_index']) == int(baseline['moment_index']) == i
        assert r['reference_label'] == baseline['reference_label'] == gold[i]
        assert r['original_decision'] == baseline['jev_decision'] == old[i]
        assert r['optimized_decision'] == new[i]
        assert r['subset'] == ('development' if i in dev else 'evaluation')
        assert (r['optimized_correct'] == 'True') == (new[i] == gold[i])
        assert (baseline['correct'] == 'True') == (old[i] == gold[i])
    assert sum(v == g for v, g in zip(old, gold)) == 367
    assert sum(v == g for v, g in zip(new, gold)) == 375
    print(json.dumps({'status': 'PASS', 'manifest_files': len(manifest), 'original_predictions': 520,
                      'selected_prompt_predictions': 520, 'development_predictions': 552,
                      'reused_development_predictions': reused, 'original_correct': 367,
                      'revised_correct': 375, 'evaluation_original_correct': 277,
                      'evaluation_revised_correct': 280, 'network_or_model_calls': 0}, indent=2))


if __name__ == '__main__':
    verify()
