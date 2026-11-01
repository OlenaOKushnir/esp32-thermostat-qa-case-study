"""Acceptance checks of the separately executed extended component run."""
import hashlib
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
REPORT = json.loads((ROOT/'evidence/extended-components/results.json').read_text())
CASES = {k:v for k,v in REPORT['scenarios'].items() if k.startswith(('boundary_', 'valid_zero_', 'recovery_'))}

def test_extended_run_identity():
    for relative, key in [('evidence/sources/main.cpp','source_sha256'),
                          ('scripts/run_component_checks.py','orchestrator_sha256'),
                          ('scripts/component_extra_cases.py','extra_scenarios_sha256')]:
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==REPORT[key]
    assert len(CASES)==18

@pytest.mark.parametrize('name', sorted(CASES))
def test_boundary_zero_or_recovery(name):
    case=CASES[name]
    assert case['actual_output']==case['expected_output']
    if name.startswith('valid_zero_'):
        assert case['reading']==0.0
    if name.startswith('recovery_'):
        # Existing BUG-T03 remains visible: invalid reading maps to zero and requests HIGH.
        # This assertion records the precondition; acceptance here concerns restored data.
        assert case['fault_reading']==0.0 and case['fault_output']==1
