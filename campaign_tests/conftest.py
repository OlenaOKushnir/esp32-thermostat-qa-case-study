import hashlib,json,sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from campaign_client import Campaign

def pytest_addoption(parser):
    parser.addoption('--campaign-url',default='rfc2217://localhost:4003')
    parser.addoption('--campaign-output',required=True)

@pytest.fixture(scope='session')
def campaign(request):
    client=Campaign(request.config.getoption('--campaign-url'),request.config.getoption('--campaign-output'))
    files={}
    for name in ['src/main.cpp','platformio.ini','wokwi.toml','diagram.json','instrumentation.diff',
                 '.pio/build/campaign/firmware.bin','.pio/build/campaign/firmware.elf']:
        relative='validation/campaign/'+name;data=(ROOT/relative).read_bytes()
        files[relative]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    (client.directory/'identity.json').write_text(json.dumps({'files':files,'level':'ESP32 GPIO-wire campaign variant'},indent=2)+'\n')
    try:
        client.command('PING')
        client.calibrate()
        yield client
    finally:client.close()
