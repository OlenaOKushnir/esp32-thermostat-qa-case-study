"""Execute exact 199/200/201 ms debounce decision boundaries with a fake clock."""
import argparse,hashlib,importlib.util,io,json,sys,tempfile,shutil
from contextlib import redirect_stdout
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tcc-root',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():parser.error('Choose a new output; existing evidence is never overwritten.')
    tool=args.tcc_root.resolve()
    if not (tool/'libtcc.dll').is_file():parser.error('TinyCC libtcc.dll is required.')
    spec=importlib.util.spec_from_file_location('debounce_harness',ROOT/'scripts/run_negative_harness.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.SCENARIOS={}
    for delta,expected in [(199,1),(200,1),(201,2)]:
        module.SCENARIOS[f'press_interval_{delta}']=f'''
 loop();button_level=LOW;fake_time=1100;handleEncoder();
 button_level=HIGH;fake_time=1101;handleEncoder();
 button_level=LOW;fake_time={1100+delta};handleEncoder();
 sprintf(result,"{{\\"interval_ms\\":{delta},\\"actual_mode\\":%d,\\"expected_mode\\":{expected}}}",currentMode);
'''
    args.output.parent.mkdir(parents=True,exist_ok=True);parent=args.output.parent.resolve()
    with tempfile.TemporaryDirectory(prefix='debounce-',dir=parent) as directory:
        isolated=Path(directory).resolve();assert isolated.is_relative_to(parent) and isolated!=parent
        for relative in ['src/main.cpp','tests/component/hardware_doubles.c']:
            target=isolated/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/relative,target)
        (isolated/'evidence/negative-testing').mkdir(parents=True)
        module.ROOT=isolated;previous=sys.argv
        try:
            sys.argv=['retained-harness','--tcc-root',str(tool)]
            with redirect_stdout(io.StringIO()):module.main()
        finally:sys.argv=previous
        report=json.loads((isolated/'evidence/negative-testing/component-results.json').read_text(encoding='utf-8'))
    report.update(executed_utc=datetime.now(timezone.utc).isoformat(),date=datetime.now().astimezone().date().isoformat(),
        limitations=['Exact fake-clock component boundary only; no ESP32 scheduler or optical timing claim.'],
        orchestrator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    assert len(report['scenarios'])==3
    assert all(x['actual_mode']==x['expected_mode'] for x in report['scenarios'].values())
    with args.output.open('x',encoding='utf-8') as output:json.dump(report,output,indent=2);output.write('\n')
    print('PASS: exact component intervals 199/200 ms reject a second press; 201 ms accepts it.')
if __name__=='__main__':main()
