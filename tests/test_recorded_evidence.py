"""Evaluate recorded thermostat evidence. No live Wokwi/device interaction."""
from pathlib import Path
import hashlib
import json
import re
import pytest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / 'evidence/tested-build.json').read_text(encoding='utf-8'))

def fault_log():
    return (ROOT / MANIFEST['runtime_evidence']).read_text(encoding='utf-8-sig')

def captured_reboot():
    text = fault_log()
    marker = 'rst:0x1 (POWERON_RESET)'
    assert marker in text, 'No complete reboot segment in evidence'
    return text.split(marker, 1)[1]

@pytest.mark.parametrize('relative', sorted(MANIFEST['files']))
def test_recorded_build_identity(relative):
    """Evidence must refer to the actual supplied source/config/binary artifacts."""
    path = ROOT / relative
    assert path.is_file(), f'Missing recorded artifact: {relative}'
    expected = MANIFEST['files'][relative]
    data = path.read_bytes()
    assert len(data) == expected['bytes']
    assert hashlib.sha256(data).hexdigest() == expected['sha256']

def test_recorded_reboot_has_no_previous_interrupt_errors():
    """RTH-09, captured reboot only; not an encoder stress test."""
    text = captured_reboot()
    assert 'entry ' in text
    for error in ['esp_ipc_call_blocking failed', 'GPIO ISR Service Failed',
                  'GPIO ISR service already installed']:
        assert error not in text

def test_recorded_hysteresis_output_transition_order():
    """TT-03 partial evidence: manual input changes are described separately."""
    text = (ROOT / 'evidence/hysteresis-runtime.log').read_text(encoding='utf-8-sig')
    transitions = re.findall(r'RX (Relay (?:Activated|Deactivated)\.)', text)
    assert transitions == ['Relay Activated.', 'Relay Deactivated.']

def test_fault_capture_contains_sensor_error_after_reboot():
    """Verify the fault precondition was actually exercised, not an empty file."""
    assert 'Failed to read from DHT sensor!' in captured_reboot()

def test_sensor_failure_must_not_request_heating():
    """RTH-07/TT-07: intentionally remains a normal FAIL while BUG-T03 is open."""
    reboot = captured_reboot()
    error = 'Failed to read from DHT sensor!'
    assert error in reboot
    after_error = reboot.split(error, 1)[1]
    assert 'Relay Activated.' not in after_error, (
        'BUG-T03 / RTH-07: heating was requested after a missing-sensor read; '
        'see evidence/live-2026-11-01/live-serial.log. This is recorded evidence, '
        'not a new live test execution.'
    )
