"""Download the pinned public source data, verifying bytes before use."""
from pathlib import Path
import argparse
import hashlib
import urllib.request

REVISION = '3bb0c104d65e29facffca7ba864ef10fa22d0e78'
FILES = {
    'moments.jsonl': 'c447459f80cf6b138512171a015879aaeab09cef7857e9c03655ad64a75c230f',
    'transcripts.jsonl': '34b5d4483302593043f3d9be3bf37f1cde6cba5b031fd2d20d75a15d5498f276',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, default=Path(__file__).resolve().parents[1] / 'data/jev')
    args = parser.parse_args()
    args.destination.mkdir(parents=True, exist_ok=True)
    for name, expected in FILES.items():
        target = args.destination / name
        if target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
                raise RuntimeError(f'{target} exists with unexpected bytes; refusing to overwrite')
            print(f'Already verified: {name}')
            continue
        url = f'https://huggingface.co/datasets/allenai/tutormoments-preview/resolve/{REVISION}/{name}'
        temporary = target.with_suffix('.download')
        digest = hashlib.sha256()
        try:
            with urllib.request.urlopen(url, timeout=120) as response, temporary.open('wb') as out:
                while chunk := response.read(1024 * 1024):
                    digest.update(chunk)
                    out.write(chunk)
            if digest.hexdigest() != expected:
                raise RuntimeError(f'Hash mismatch for {name}; source not accepted')
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
        print(f'Downloaded and verified: {name}')


if __name__ == '__main__':
    main()
