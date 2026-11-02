"""Evaluate instrumented Wokwi sensor samples and explicit input histories."""
from pathlib import Path
import hashlib,json,re
import pytest
ROOT=Path(__file__).resolve().parents[2]
FIRST=ROOT/'evidence/runs/sensor'
RECOVERY=ROOT/'evidence/runs/recovery'

def case(folder,name):
    record=json.loads((folder/'cases.json').read_text(encoding='utf-8'))[name]
    raw=(folder/'serial.log').read_text()
    assert len(record['samples'])>=2
    for sample in record['samples']:
        expected=f"[SAMPLE] ms={sample['ms']} temp={sample['temperature']:.1f} output={sample['output']}"
        assert expected in raw, 'Summary must be supported by raw device data'
    return record,raw

def test_sensor_build_identity():
    manifest=json.loads((FIRST/'identity.json').read_text())
    for relative,expected in manifest['files'].items():
        data=(ROOT/relative).read_bytes()
        assert hashlib.sha256(data).hexdigest()==expected['sha256'] and len(data)==expected['bytes']

@pytest.mark.parametrize('name',[f'B{i:02}' for i in range(1,13)])
def test_live_boundary_samples(name):
    record,_=case(FIRST,name)
    assert all(s['output']==record['expected_output'] for s in record['samples'])

def test_valid_zero_is_a_real_sensor_reading():
    record,raw=case(FIRST,'Z01')
    assert all(s['temperature']==0 and s['output']==1 for s in record['samples'])
    end=max(s['rx'] for s in record['samples'])
    for line in raw.splitlines():
        m=re.match(r'([\d.]+) RX (.*)',line)
        if m and record['host_elapsed']<=float(m[1])<=end:
            assert 'Failed to read' not in m[2]

@pytest.mark.parametrize('name',['R01','R02'])
def test_reconnection_recovers_valid_control(name):
    record,_=case(RECOVERY,name)
    assert all(s['output']==record['expected_output'] for s in record['samples'])

@pytest.mark.parametrize('folder,name',[(FIRST,'F01'),(RECOVERY,'F02')])
def test_dynamic_fault_precondition_is_present(folder,name):
    record,raw=case(folder,name)
    assert 'Failed to read from DHT sensor!' in raw
    assert all(s['temperature']==0 and s['output']==1 for s in record['samples'])

def test_disconnect_from_off_must_not_start_heating():
    record,_=case(RECOVERY,'F02')
    assert all(s['output']==0 for s in record['samples']), 'BUG-T03: dynamic sensor fault creates a new heat request'
