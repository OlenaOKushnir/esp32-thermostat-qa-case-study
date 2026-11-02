"""Validate portfolio links, document structure, recorded identity and report counts."""
from pathlib import Path
import csv,hashlib,json,re
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
required=['README.md','master-test-plan.md','acceptance-criteria.md','risk-matrix.md',
          'test-matrix.md','release-decision.md','qa-conclusion.md','requirements-test.txt',
          'pytest.ini','tests/test_recorded_evidence.py','evidence/README.md']
for name in required: assert (ROOT/name).is_file(),name
mtp=(ROOT/'master-test-plan.md').read_text(encoding='utf-8-sig')
assert re.findall(r'^## (\d+)\.',mtp,re.M)==[str(i) for i in range(1,18)]
for i in range(1,13):
    assert f'RTH-{i:02}' in (ROOT/'acceptance-criteria.md').read_text(encoding='utf-8-sig')
for i in range(1,9):
    assert f'RISK-T{i:02}' in (ROOT/'risk-matrix.md').read_text(encoding='utf-8-sig')
links=0
files=[*ROOT.glob('*.md'),*ROOT.glob('docs/*.md'),*ROOT.glob('bug-reports/*.md'),*ROOT.glob('evidence/**/*.md'),*ROOT.glob('validation/**/*.md')]
for p in files:
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8-sig')):
        if '://' in target or target.startswith('#'):continue
        assert (p.parent/target.split('#')[0]).exists(),f'{p.name}: {target}'
        links+=1
with (ROOT/'evidence-manifest.csv').open(encoding='utf-8-sig',newline='') as f:
    rows=list(csv.DictReader(f))
for row in rows:
    data=(ROOT/row['path']).read_bytes()
    assert len(data)==int(row['bytes']),row['path']
    assert hashlib.sha256(data).hexdigest()==row['sha256'],row['path']
manifest=json.loads((ROOT/'evidence/support/tested-build.json').read_text(encoding='utf-8'))
for name,identity in manifest['files'].items():
    p=ROOT/name
    assert p.is_file(),f'Missing recorded build artifact: {name}; see README'
    assert hashlib.sha256(p.read_bytes()).hexdigest()==identity['sha256'],name
    assert p.stat().st_size==identity['bytes'],name
for name,identity in manifest['auxiliary_artifacts'].items():
    data=(ROOT/name).read_bytes()
    assert len(data)==identity['bytes'] and hashlib.sha256(data).hexdigest()==identity['sha256'],name
expected={'test_sensor_failure_must_not_request_heating','test_long_press_release_bounce_must_not_advance_mode_twice','test_display_mode_must_meet_proposed_feedback_budget'}
fresh=ET.parse(ROOT/'evidence/bugs/sensor-fault/pytest-current.xml').findall('.//testcase')
assert len(fresh)==20
assert {c.get('name') for c in fresh if c.find('failure') is not None}==expected
assert not any(c.find('error') is not None or c.find('skipped') is not None for c in fresh)
raw=(ROOT/manifest['runtime_evidence']).read_text(encoding='utf-8')
reboot=raw.split('rst:0x1 (POWERON_RESET)',1)[1]
assert reboot.index('Failed to read from DHT sensor!')<reboot.index('Relay Activated.')
component=json.loads((ROOT/'evidence/components/baseline/results.json').read_text(encoding='utf-8'))
assert hashlib.sha256((ROOT/'evidence/support/sources/main.cpp').read_bytes()).hexdigest()==component['source_sha256']
assert hashlib.sha256((ROOT/'scripts/run_negative_harness.py').read_bytes()).hexdigest()==component['harness_sha256']
assert hashlib.sha256((ROOT/'tests/component/hardware_doubles.c').read_bytes()).hexdigest()==component['doubles_sha256']
assert len(component['scenarios'])==27
for relative,counts,failure_names in [
 ('evidence/components/baseline/pytest.xml',19,set()),
 ('evidence/runs/recovery/pytest.xml',19,{'test_disconnect_from_off_must_not_start_heating'}),
 ('evidence/bugs/input-feedback/pytest.xml',3,{'test_release_bounce_is_one_action','test_mode_feedback_meets_proposed_500ms'}),
 ('evidence/support/offline.xml',58,{'test_disconnect_from_off_must_not_start_heating',
    'test_sensor_failure_must_not_request_heating','test_long_press_release_bounce_must_not_advance_mode_twice',
    'test_display_mode_must_meet_proposed_feedback_budget'})]:
    records=ET.parse(ROOT/relative).findall('.//testcase')
    assert len(records)==counts,relative
    assert {c.get('name') for c in records if c.find('failure') is not None}==failure_names,relative
    assert not any(c.find('error') is not None or c.find('skipped') is not None for c in records),relative
for relative in ['evidence/bugs/input-feedback/identity.json','evidence/runs/sensor/identity.json']:
    record=json.loads((ROOT/relative).read_text())
    for name,expected_identity in record['files'].items():
        data=(ROOT/name).read_bytes()
        assert len(data)==expected_identity['bytes'] and hashlib.sha256(data).hexdigest()==expected_identity['sha256'],name
extended=json.loads((ROOT/'evidence/components/baseline/results.json').read_text())
assert len(extended['scenarios'])==27
assert hashlib.sha256((ROOT/'scripts/run_component_checks.py').read_bytes()).hexdigest()==extended['orchestrator_sha256']
assert hashlib.sha256((ROOT/'scripts/component_extra_cases.py').read_bytes()).hexdigest()==extended['extra_scenarios_sha256']
validation_builds=json.loads((ROOT/'evidence/support/validation-builds.json').read_text())
for relative,identity in validation_builds['files'].items():
    data=(ROOT/relative).read_bytes()
    assert len(data)==identity['bytes'] and hashlib.sha256(data).hexdigest()==identity['sha256'],relative
campaign_root=ROOT/'evidence/runs/campaign'
campaign_cases=ET.parse(campaign_root/'pytest.xml').findall('.//testcase')
assert len(campaign_cases)==21
assert not any(c.find('error') is not None or c.find('skipped') is not None for c in campaign_cases)
assert {c.get('name') for c in campaign_cases if c.find('failure') is not None}=={
 'test_fault_and_recovery_complete_matrix[250-190]',
 'test_fault_and_recovery_complete_matrix[250-250]'}
for relative,identity in json.loads((campaign_root/'identity.json').read_text())['files'].items():
    data=(ROOT/relative).read_bytes()
    assert len(data)==identity['bytes'] and hashlib.sha256(data).hexdigest()==identity['sha256'],relative
campaign_observations={x['case']:x['data'] for x in json.loads((campaign_root/'observations.json').read_text())}
cycles=campaign_observations['twenty_cycles']
assert len(cycles)==80 and {x['cycle'] for x in cycles}==set(range(1,21))
assert all(int(x['sample']['req'])==x['expected'] and int(x['sample']['pin'])==x['expected'] for x in cycles)
assert all(0<=x['response_ms']<=5000 for x in cycles)
assert int(cycles[-1]['sample']['edges'])==40 and int(cycles[-1]['sample']['high_edges'])==20
assert len(campaign_observations['thirty_valid_presses'])==30
for state in ['ON','OFF','SET_LOWER','SET_UPPER']:assert 'reset_'+state in campaign_observations
for initial in [190,250]:
    for restored in [190,250]:assert f'recovery_{initial}_{restored}' in campaign_observations
for name in ['BUG-T03.md','BUG-T04.md','BUG-T05.md']:
    assert (ROOT/'bug-reports'/name).is_file()
print(f'PASS: 17 MTP sections, 12 criteria, 8 risks, {links} local links, {len(rows)} evidence hashes and recorded build/component identity.')
print('Recorded baseline: 17 passed/3 failures (T03/T04/T05). Integrity PASS is not product acceptance.')
print('Additional reports: extended components 19/0; sensor captures 18/1; live inputs 1/2. Separate instrumented images verified; three independent open findings.')

print("Complete live campaign: 19 passed/2 T03 failures; 20 cycles, encoder, reset, contact and recovery records verified.")

extra_root=ROOT/'evidence/runs/inputs'
extra_cases=ET.parse(extra_root/'pytest.xml').findall('.//testcase')
assert len(extra_cases)==4 and not any(c.find(tag) is not None for c in extra_cases for tag in ['failure','error','skipped'])
for relative,identity in json.loads((extra_root/'identity.json').read_text())['files'].items():
    data=(ROOT/relative).read_bytes()
    assert len(data)==identity['bytes'] and hashlib.sha256(data).hexdigest()==identity['sha256'],relative
extra_observations={x['case']:x['data'] for x in json.loads((extra_root/'observations.json').read_text())}
for period in [199,200,201]:
    record=extra_observations[f'debounce_period_{period}']
    assert len(record['matched_pulse_indices'])==len(set(record['matched_pulse_indices']))
    assert len(record['acknowledgments'])==10
    assert len(record['actual_within_group_intervals_ms'])==8
    assert all(period<=gap<=period+15 for gap in record['actual_within_group_intervals_ms'])
assert 'settled_fault_contacts_and_reset' in extra_observations
debounce_components=json.loads((ROOT/'evidence/components/current/debounce.json').read_text())
assert len(debounce_components['scenarios'])==3
assert all(x['actual_mode']==x['expected_mode'] for x in debounce_components['scenarios'].values())
assert hashlib.sha256((ROOT/'src/main.cpp').read_bytes()).hexdigest()==debounce_components['source_sha256']
assert hashlib.sha256((ROOT/'scripts/run_debounce_components.py').read_bytes()).hexdigest()==debounce_components['orchestrator_sha256']
print('Additional debounce-boundary and settled-fault/reset controls: 4 passed; total live campaign 23 passed/2 T03 failures.')

from source_identity import verify
verify()
fresh_components=json.loads((ROOT/'evidence/components/current/results.json').read_text())
assert fresh_components['scenarios']==extended['scenarios']
assert hashlib.sha256((ROOT/'src/main.cpp').read_bytes()).hexdigest()==fresh_components['source_sha256']

from compare_images import section_hashes
for build in json.loads((ROOT/"evidence/components/current/builds.json").read_text())["images"]:
    assert section_hashes(ROOT/build["captured_elf"])==build["loadable_sections"]
    assert hashlib.sha256((ROOT/build["working_source"]).read_bytes()).hexdigest()==build["source_sha256"]

matrix=(ROOT/"test-matrix.md").read_text(encoding="utf-8")
assert "| ID | Priority |" in matrix
assert len(re.findall(r"^\| TT-\d{2} \| P[01] \|",matrix,re.M))==13
assert {p.name for p in (ROOT/"bug-reports").glob("*.md")}=={"BUG-T03.md","BUG-T04.md","BUG-T05.md"}
