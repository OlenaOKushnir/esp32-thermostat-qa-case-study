"""Compare loadable ELF32 sections; debug information is excluded."""
import argparse,hashlib,json,struct
from pathlib import Path

def section_hashes(path):
    data=Path(path).read_bytes();header=struct.unpack_from('<16sHHIIIIIHHHHHH',data)
    if header[0][:6]!=b'\x7fELF\x01\x01':raise ValueError('Expected little-endian ELF32')
    rows=[struct.unpack_from('<IIIIIIIIII',data,header[6]+i*header[11]) for i in range(header[12])]
    strings=rows[header[13]];names=data[strings[4]:strings[4]+strings[5]]
    return {names[x[0]:].split(b'\0')[0].decode():{'address':hex(x[3]),'bytes':x[5],
            'sha256':hashlib.sha256(bytes(x[5]) if x[1]==8 else data[x[4]:x[4]+x[5]]).hexdigest()}
            for x in rows if x[2]&2}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before',type=Path);parser.add_argument('after',type=Path)
    args=parser.parse_args();before=section_hashes(args.before);after=section_hashes(args.after)
    assert before==after,'Loadable sections differ'
    print(json.dumps({'identical':True,'sections':before},indent=2))
