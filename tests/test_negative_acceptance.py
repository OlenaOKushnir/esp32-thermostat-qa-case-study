"""Checks of component-harness evidence; not a new Wokwi run."""
from pathlib import Path
import hashlib,json
import pytest
ROOT=Path(__file__).resolve().parents[1]
REPORT=json.loads((ROOT/'evidence/components/baseline/results.json').read_text(encoding='utf-8'))
CASES=REPORT['scenarios']

def test_component_evidence_matches_current_firmware():
    assert hashlib.sha256((ROOT/'evidence/support/sources/main.cpp').read_bytes()).hexdigest()==REPORT['source_sha256']
    assert hashlib.sha256((ROOT/'scripts/run_negative_harness.py').read_bytes()).hexdigest()==REPORT['harness_sha256']
    assert hashlib.sha256((ROOT/'tests/component/hardware_doubles.c').read_bytes()).hexdigest()==REPORT['doubles_sha256']

@pytest.mark.parametrize('name',[
    'long_press_without_bounce','short_bounce_after_press','mode_feedback_after_refresh',
    'hysteresis_control','lower_below_minimum','upper_above_maximum','lower_crosses_upper'])
def test_negative_testing_control_cases(name):
    case=CASES[name]
    if name in ['long_press_without_bounce','short_bounce_after_press']:
        assert case['actual_mode']==case['expected_mode']
    elif name=='mode_feedback_after_refresh':
        assert case['actual_mode']==case['displayed_mode']
    elif name=='hysteresis_control':
        assert case['expected_sequence_matches'] is True
    elif name=='lower_below_minimum':
        assert case['actual_lower']==case['expected_lower']
    elif name=='upper_above_maximum':
        assert case['actual_upper']==case['expected_upper']
    else:
        assert case['upper']-case['actual_lower']==pytest.approx(case['expected_gap'])

def test_long_press_release_bounce_must_not_advance_mode_twice():
    case=CASES['long_press_release_bounce']
    assert case['actual_mode']==case['expected_mode'], (
        'BUG-T04 / RTH-06: one long press plus release bounce advances two modes; '
        'component reproduction; separate instrumented Wokwi evidence is also recorded.'
    )

def test_display_mode_must_meet_proposed_feedback_budget():
    case=CASES['mode_feedback_510ms']
    assert case['elapsed_since_press_ms']>case['budget_ms']
    assert case['displayed_mode']==case['actual_mode'], (
        'BUG-T05 / proposed RTH-12: displayed mode is stale after 510 ms; '
        'fake-clock component reproduction, not a measured ESP32 latency.'
    )
