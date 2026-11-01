"""Run the retained component harness in isolation and save a new dated result."""
import argparse
from contextlib import redirect_stdout
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tcc-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--extended', action='store_true', help='Add exact boundaries, valid-zero and recovery controls')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output exists; choose a new result file. Historical evidence is never overwritten.')
    tool = args.tcc_root.resolve()
    if not (tool / 'libtcc.dll').is_file():
        parser.error('--tcc-root must contain libtcc.dll (Windows x64 TinyCC)')
    runner = ROOT / 'scripts/run_negative_harness.py'
    spec = importlib.util.spec_from_file_location('retained_harness', runner)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    extra_path = ROOT / 'scripts/component_extra_cases.py'
    if args.extended:
        extra_spec = importlib.util.spec_from_file_location('extra_scenarios', extra_path)
        extra = importlib.util.module_from_spec(extra_spec)
        extra_spec.loader.exec_module(extra)
        module.SCENARIOS.update(extra.SCENARIOS)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    workspace_parent = args.output.parent.resolve()
    with tempfile.TemporaryDirectory(prefix='thermostat-components-', dir=workspace_parent) as directory:
        isolated = Path(directory)
        assert isolated.resolve().is_relative_to(workspace_parent) and isolated.resolve() != workspace_parent
        for rel in ['src/main.cpp', 'tests/component/hardware_doubles.c']:
            target = isolated / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, target)
        (isolated / 'evidence/negative-testing').mkdir(parents=True)
        module.ROOT = isolated
        previous = sys.argv
        try:
            sys.argv = [str(runner), '--tcc-root', str(tool)]
            with redirect_stdout(io.StringIO()):
                module.main()
        finally:
            sys.argv = previous
        report = json.loads((isolated / 'evidence/negative-testing/component-results.json').read_text())
    report['date'] = datetime.now().astimezone().date().isoformat()
    report['executed_utc'] = datetime.now(timezone.utc).isoformat()
    report['orchestrator_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if args.extended:
        report['extra_scenarios_sha256'] = hashlib.sha256(extra_path.read_bytes()).hexdigest()
    report['result_scope'] = 'New component execution only; not a Wokwi/device test or acceptance approval.'
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as output:
        json.dump(report, output, indent=2)
        output.write('\n')
    print(f'Executed {len(report["scenarios"])} isolated scenarios; saved {args.output}.')
    print('Historical results are unchanged. Review actual/expected values before accepting the new run.')


if __name__ == '__main__':
    main()
