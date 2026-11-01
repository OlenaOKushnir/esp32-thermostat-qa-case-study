"""Static package checks only. Does not compile or run the firmware."""
from pathlib import Path
import argparse,json,tomllib,hashlib
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--refresh-inventory',action='store_true',help='Explicitly regenerate the source inventory after reviewed package edits')
args=parser.parse_args()
r=Path(__file__).resolve().parents[1]
d=json.loads((r/'diagram.json').read_text(encoding='utf-8'))
c=tomllib.loads((r/'wokwi.toml').read_text(encoding='utf-8-sig'))
assert c['wokwi']['firmware']=='.pio/build/esp32dev/firmware.bin'
assert c['wokwi']['elf']=='.pio/build/esp32dev/firmware.elf'
assert c['wokwi']['rfc2217ServerPort']==4000
ids=[p['id'] for p in d['parts']];assert len(ids)==len(set(ids))
assert next(p for p in d['parts'] if p['id']=='sensorSwitch')['attrs']['value']=='0','Restore the normal fixture before checking the submission'
assert (r/'diagram.normal.json').read_bytes()==(r/'diagram.json').read_bytes(),'Normal fixture snapshot differs'
for a,b,*_ in d['connections']:
 for endpoint in (a,b):
  assert endpoint.startswith('$') or endpoint.split(':')[0] in ids,endpoint
pairs={frozenset(conn[:2]) for conn in d['connections']}
for a,b in [('dht1:SDA','sensorSwitch:1'),('sensorSwitch:2','esp:16'),('r1:2','esp:3V3'),('relay1:IN','esp:5'),('lcd1:CS','esp:14'),('lcd1:RST','esp:17'),('lcd1:D/C','esp:4'),('lcd1:MOSI','esp:23'),('lcd1:SCK','esp:18'),('encoder1:CLK','esp:25'),('encoder1:DT','esp:26'),('encoder1:SW','esp:27')]:
 assert frozenset([a,b]) in pairs,(a,b)
from source_identity import verify
verify()
manifest={}
generated_editor_files={'.vscode/c_cpp_properties.json','.vscode/launch.json','.vscode/extensions.json'}
recommendations=(r/'.vscode/extensions.json').read_text(encoding='utf-8-sig')
assert 'platformio.platformio-ide' in recommendations and 'wokwi.wokwi-vscode' in recommendations
for p in sorted(r.rglob('*')):
 if p.is_file() and p.relative_to(r).as_posix() not in generated_editor_files and not any(x in p.relative_to(r).parts for x in ['.pio','__pycache__','.pytest_cache','.git','.venv','runs']) and 'evidence' not in p.relative_to(r).parts:
  manifest[p.relative_to(r).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
inventory=r/'evidence/source-hashes.json'
if args.refresh_inventory:
 inventory.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
else:
 assert json.loads(inventory.read_text(encoding='utf-8'))==manifest,'Package inventory changed; review edits, then explicitly use --refresh-inventory'
print('PASS: config, diagram connections, pin mapping, original logic preserved.')
print('Static checks only. Build and manual runtime results are recorded in docs/validation.md.')
