"""Execute unchanged C-compatible firmware function bodies using libtcc.

This is a component harness with hardware doubles, NOT a full C++ firmware,
ESP32 timing, Wokwi, TFT rendering or physical-device validation.
Usage: python scripts/run_negative_harness.py --tcc-root PATH_TO_TCC_DIRECTORY
"""
from pathlib import Path
import argparse, ctypes, hashlib, json, platform, re
ROOT = Path(__file__).resolve().parents[1]
FUNCTIONS = ['float readTemperature()', 'void updateRelay(float temperature)',
             'void updateDisplay(float currentTemp)', 'void handleEncoder()',
             'void toggleMode()', 'void loop()']

def extract(source, signature):
    start = source.index(signature + ' {')
    opening = source.index('{', start)
    depth = 0
    for i in range(opening, len(source)):
        if source[i] == '{': depth += 1
        elif source[i] == '}':
            depth -= 1
            if depth == 0: return source[start:i+1]
    raise ValueError('Unbalanced function: ' + signature)

SCENARIOS = {
'long_press_without_bounce': '''
 loop(); button_level=LOW; fake_time=1100; handleEncoder();
 fake_time=2100; handleEncoder(); button_level=HIGH;
 fake_time=2101; handleEncoder();
 sprintf(result,"{\\"actual_mode\\":%d,\\"expected_mode\\":1}",currentMode);
''',
'short_bounce_after_press': '''
 loop(); button_level=LOW; fake_time=1100; handleEncoder();
 button_level=HIGH; fake_time=1101; handleEncoder();
 button_level=LOW; fake_time=1102; handleEncoder();
 sprintf(result,"{\\"actual_mode\\":%d,\\"expected_mode\\":1}",currentMode);
''',
'long_press_release_bounce': '''
 loop(); button_level=LOW; fake_time=1100; handleEncoder();
 fake_time=2100; handleEncoder();
 button_level=HIGH; fake_time=2101; handleEncoder();
 button_level=LOW; fake_time=2102; handleEncoder();
 button_level=HIGH; fake_time=2103; handleEncoder();
 sprintf(result,"{\\"actual_mode\\":%d,\\"expected_mode\\":1,\\"release_bounce_ms\\":1}",currentMode);
''',
'mode_feedback_510ms': '''
 loop(); button_level=LOW; fake_time=1100; loop();
 button_level=HIGH; fake_time=1610; loop();
 sprintf(result,"{\\"actual_mode\\":%d,\\"displayed_mode\\":%d,\\"elapsed_since_press_ms\\":510,\\"budget_ms\\":500}",currentMode,displayed_mode);
''',
'mode_feedback_after_refresh': '''
 loop(); button_level=LOW; fake_time=1100; loop();
 button_level=HIGH; fake_time=2000; loop();
 sprintf(result,"{\\"actual_mode\\":%d,\\"displayed_mode\\":%d}",currentMode,displayed_mode);
''',
'hysteresis_control': '''
 int ok=1; sensor_value=19; loop(); ok &= output_level==HIGH;
 sensor_value=22; fake_time=2000; loop(); ok &= output_level==HIGH;
 sensor_value=25; fake_time=3000; loop(); ok &= output_level==LOW;
 sensor_value=22; fake_time=4000; loop(); ok &= output_level==LOW;
 sprintf(result,"{\\"expected_sequence_matches\\":%s}",ok?"true":"false");
'''}

SCENARIOS.update({'lower_below_minimum': 'currentMode=SET_LOWER; encoder_count=-10000; handleEncoder();\n sprintf(result,"{\\"actual_lower\\":%.1f,\\"expected_lower\\":-50.0}",LOWER_THRESHOLD);\n', 'upper_above_maximum': 'currentMode=SET_UPPER; encoder_count=10000; handleEncoder();\n sprintf(result,"{\\"actual_upper\\":%.1f,\\"expected_upper\\":100.0}",UPPER_THRESHOLD);\n', 'lower_crosses_upper': 'currentMode=SET_LOWER; encoder_count=40; handleEncoder();\n sprintf(result,"{\\"actual_lower\\":%.1f,\\"upper\\":%.1f,\\"expected_gap\\":0.5}",LOWER_THRESHOLD,UPPER_THRESHOLD);\n'})

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--tcc-root',required=True)
    args=parser.parse_args();tool=Path(args.tcc_root).resolve()
    lib=ctypes.CDLL(str(tool/'libtcc.dll'))
    lib.tcc_new.restype=ctypes.c_void_p
    for name in ['tcc_delete','tcc_set_lib_path','tcc_set_output_type','tcc_compile_string','tcc_relocate','tcc_get_symbol']:
        fn=getattr(lib,name)
        fn.argtypes={'tcc_delete':[ctypes.c_void_p], 'tcc_set_lib_path':[ctypes.c_void_p,ctypes.c_char_p],
        'tcc_set_output_type':[ctypes.c_void_p,ctypes.c_int], 'tcc_compile_string':[ctypes.c_void_p,ctypes.c_char_p],
        'tcc_relocate':[ctypes.c_void_p,ctypes.c_void_p], 'tcc_get_symbol':[ctypes.c_void_p,ctypes.c_char_p]}[name]
    lib.tcc_get_symbol.restype=ctypes.c_void_p
    src=(ROOT/'src/main.cpp').read_text(encoding='utf-8')
    bodies={sig:extract(src,sig) for sig in FUNCTIONS}
    start=src.index('float LOWER_THRESHOLD =')
    end=src.index('Mode currentMode = VIEW;')+len('Mode currentMode = VIEW;')
    globals_text=src[start:end]
    mocks=(ROOT/'tests/component/hardware_doubles.c').read_text(encoding='utf-8')
    results={}
    for name,body in SCENARIOS.items():
        code=mocks+'\n'+globals_text+'\n'+'\n\n'.join(bodies.values())
        code+='\nconst char *run_scenario(void) { static char result[512];\n'+body+'\nreturn result; }\n'
        state=lib.tcc_new()
        try:
            lib.tcc_set_lib_path(state,str(tool).encode())
            assert lib.tcc_set_output_type(state,1)==0
            assert lib.tcc_compile_string(state,code.encode('utf-8'))==0, name
            assert lib.tcc_relocate(state,ctypes.c_void_p(1))==0, name
            address=lib.tcc_get_symbol(state,b'run_scenario');assert address
            fn=ctypes.CFUNCTYPE(ctypes.c_char_p)(address)
            results[name]=json.loads(fn().decode())
        finally:lib.tcc_delete(state)
    record={'date':'2026-10-30','level':'host component harness, unchanged C-compatible function bodies with hardware doubles',
      'limitations':['Not a full Arduino C++ build','No ESP32 interrupt, sensor-library or TFT drawing timing validation',
                    'Fake millis and electrical inputs; Wokwi confirmation pending for new findings',
                    '500 ms mode-feedback criterion is the existing proposed RTH-12 budget'],
      'source_sha256':hashlib.sha256((ROOT/'src/main.cpp').read_bytes()).hexdigest(),
      'function_sha256':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in bodies.items()},
      'compiler':'TinyCC 0.9.27 libtcc Windows x64 API',
      'compiler_dll_sha256':hashlib.sha256((tool/'libtcc.dll').read_bytes()).hexdigest(),
      'compiler_source':'https://download.savannah.gnu.org/releases/tinycc/tcc-0.9.27-win64-bin.zip',
      'python':platform.python_version(),'scenarios':results}
    record['harness_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    record['doubles_sha256']=hashlib.sha256((ROOT/'tests/component/hardware_doubles.c').read_bytes()).hexdigest()
    out=ROOT/'evidence/negative-testing/component-results.json'
    out.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(record,indent=2))

if __name__=='__main__': main()
