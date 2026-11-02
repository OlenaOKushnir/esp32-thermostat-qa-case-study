"""Live Wokwi acceptance oracles for the separately instrumented device image."""
from datetime import datetime,timezone
import hashlib,json,re,time
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[3]

@pytest.fixture(scope='module')
def live_run(request):
    import serial
    destination=Path(request.config.getoption('--run-dir'))
    destination.mkdir(parents=True,exist_ok=False)
    duration=request.config.getoption('--capture-seconds')
    assert 0<duration<=300, 'Capture duration must be 0..300 seconds'
    metadata={'started_utc':datetime.now(timezone.utc).isoformat(),
              'port':request.config.getoption('--serial-url'),
              'time_basis':'Serial timestamps are host RX; VAL fields are ESP32 millis',
              'files':{}}
    for relative in ['validation/device/src/main.cpp','validation/device/diagram.json',
                     'validation/device/platformio.ini','validation/device/wokwi.toml',
                     'validation/device/.pio/build/live_validation/firmware.bin',
                     'validation/device/.pio/build/live_validation/firmware.elf']:
        data=(ROOT/relative).read_bytes()
        metadata['files'][relative]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    (destination/'identity.json').write_text(json.dumps(metadata,indent=2)+'\n')
    connection=serial.serial_for_url(metadata['port'],baudrate=115200,timeout=.2)
    print('\nLIVE CAPTURE CONNECTED: restart the device validation simulator now.',flush=True)
    start=time.monotonic(); lines=[]; began=False
    try:
        with (destination/'serial.log').open('x',encoding='utf-8') as output:
            while time.monotonic()-start<duration:
                data=connection.readline()
                if data:
                    text=data.decode(errors='replace').rstrip('\r\n')
                    output.write(f'{time.monotonic()-start:.3f} RX {text}\n');output.flush()
                    lines.append(text)
                    if '[VAL_BEGIN]' in text:began=True
                    if began and ('[VAL_END]' in text or '[VAL_ABORT]' in text):break
    finally:
        connection.close()
    text='\n'.join(lines)
    assert '[VAL_BEGIN]' in text and '[VAL_END]' in text and '[VAL_ABORT]' not in text, 'Incomplete live run; inspect serial.log'
    results={}
    for line in lines:
        if '[VAL_RESULT]' not in line:continue
        fields=dict(re.findall(r'(\w+)=([^ ]+)',line))
        case=fields.pop('case')
        results[case]={k:int(v) for k,v in fields.items()}
    (destination/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    return results

def test_clean_long_press(live_run):
    assert live_run['T04_CLEAN']['actual_mode']==1

def test_release_bounce_is_one_action(live_run):
    assert live_run['T04_BOUNCE']['actual_mode']==1, 'BUG-T04: release bounce accepted as another press'

def test_mode_feedback_meets_proposed_500ms(live_run):
    result=live_run['T05']
    assert result['frame_mode']==result['actual_mode']
    assert result['elapsed_ms']<=500, 'BUG-T05: completed mode frame exceeds proposed 500 ms budget'
