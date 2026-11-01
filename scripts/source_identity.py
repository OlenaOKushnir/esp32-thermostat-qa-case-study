"""Compare cleaned working sources with the captured firmware baseline."""
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCES={'src/main.cpp':'main.cpp',**{f'validation/{name}/src/main.cpp':f'{name}.cpp' for name in ['device','sensor','campaign']}}

def clean(source):
    pattern=r'"(?:\\.|[^"\\])*"|\x27(?:\\.|[^\x27\\])*\x27|//[^\n]*|/\*[\s\S]*?\*/'
    source=re.sub(pattern,lambda m:'' if m[0].startswith(('//','/*')) else m[0],source)
    result=[];enabled=[True]
    for line in source.splitlines():
        stripped=line.strip()
        if stripped.startswith('#ifdef SENSOR_TYPE_'):
            enabled.append(enabled[-1] and stripped.endswith('DHT22'));continue
        if stripped=='#endif' and len(enabled)>1:enabled.pop();continue
        if not enabled[-1]:continue
        if stripped in ['#define SENSOR_TYPE_DHT22','#include <DHT_U.h>','#include <OneWire.h>','long oldPosition  = -999;']:continue
        if len(enabled)>1 and line.startswith('  '):line=line[2:]
        result.append(line.rstrip())
    return re.sub(r'\n\s*\n(?:\s*\n)+','\n\n','\n'.join(result)).strip()+'\n'

def captured(relative='src/main.cpp'):
    return ROOT/'evidence/sources'/SOURCES[relative]

def verify():
    for relative in SOURCES:
        assert clean(captured(relative).read_text(encoding='utf-8'))==(ROOT/relative).read_text(encoding='utf-8'),relative

if __name__=='__main__':
    verify();print('PASS: working sources differ only by comments, inactive sensor code, unused includes and one unused global.')
