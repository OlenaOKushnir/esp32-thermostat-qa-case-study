"""Select a known Wokwi circuit without overwriting unrecognized user wiring."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('fixture', choices=['normal', 'fault'])
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'evidence/support/tested-build.json').read_text())
    paths = {'normal': 'diagram.normal.json', 'fault': 'diagram.sensor-fault.json'}
    expected = {
        'normal': manifest['files']['diagram.json']['sha256'],
        'fault': manifest['files']['diagram.sensor-fault.json']['sha256'],
    }
    data = (ROOT / paths[args.fixture]).read_bytes()
    if hashlib.sha256(data).hexdigest() != expected[args.fixture]:
        parser.error('Requested fixture differs from the recorded baseline; review it before use.')
    target = ROOT / 'diagram.json'
    if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() not in expected.values():
        parser.error('diagram.json is missing or has custom changes. Save/review it first; nothing was changed.')
    target.write_bytes(data)
    print(f'Selected {args.fixture} fixture. Stop, close and reopen Wokwi Simulator to load it.')
    if args.fixture == 'fault':
        print('Fault injection active. Restore with: python scripts/select_fixture.py normal')


if __name__ == '__main__':
    main()
