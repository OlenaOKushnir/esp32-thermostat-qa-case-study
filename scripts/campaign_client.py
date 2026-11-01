"""Live client for validation/campaign only; the main firmware has no command API."""
import json,re,time
from pathlib import Path

class Campaign:
    def __init__(self,url,directory):
        import serial
        self.directory=Path(directory);self.directory.mkdir(parents=True,exist_ok=False)
        self.log=(self.directory/'serial.log').open('x',encoding='utf-8')
        self.events=(self.directory/'commands.jsonl').open('x',encoding='utf-8')
        self.port=serial.serial_for_url(url,baudrate=115200,timeout=.2)
        self.started=time.monotonic();self.counter=0;self.records=[];self.results=[];self.sign=None;self.pending=b''

    def close(self):
        self.port.close();self.log.close();self.events.close()

    def read(self):
        if b'\n' not in self.pending:
            self.pending+=self.port.read(max(1,self.port.in_waiting))
        if b'\n' not in self.pending:return None
        packet,self.pending=self.pending.split(b'\n',1)
        line=packet.decode(errors='replace').strip('\r\n')
        self.log.write(f'{time.monotonic()-self.started:.3f} RX {line}\n');self.log.flush()
        match=re.search(r'\[QA_(\w+)\](.*)',line)
        if not match:return None
        fields=dict(re.findall(r'(\w+)=([^ ]+)',match[2]))
        record={'type':match[1],**fields,'raw':line}
        self.records.append(record);return record

    def wait(self,predicate,timeout=180):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            record=self.read()
            if record and predicate(record):return record
        raise AssertionError('Live fixture timeout; inspect serial.log (no PASS inferred)')

    def command(self,operation,a=0,b=0,timeout=180):
        self.counter+=1;identity=f'C{self.counter:04}'
        request={'id':identity,'operation':operation,'a':a,'b':b,'host_elapsed':time.monotonic()-self.started}
        self.events.write(json.dumps(request)+'\n');self.events.flush()
        self.port.write(f'{identity} {operation} {a} {b}\n'.encode())
        return self.wait(lambda r:r['type']=='ACK' and r.get('id')==identity,timeout)

    def sample(self,predicate=lambda r:True,after=-1,timeout=180):
        return self.wait(lambda r:r['type']=='SAMPLE' and int(r['ms'])>after and predicate(r),timeout)

    def reset(self):
        self.command('RESET')
        boot=self.wait(lambda r:r['type']=='BOOT' and r.get('phase')=='output_init')
        self.wait(lambda r:r['type']=='READY')
        sample=self.sample(lambda r:int(r['valid'])==1 and abs(float(r['temp'])-24)<.01)
        assert int(boot['mode'])==0 and float(boot['lower'])==20 and float(boot['upper'])==25
        assert int(boot['req'])==0 and int(boot['pin'])==0
        return boot,sample

    def temperature(self,tenths):
        ack=self.command('TEMP',tenths)
        sample=self.sample(lambda r:int(r['valid'])==1 and abs(float(r['temp'])-tenths/10)<.01,after=int(ack['begin']))
        return ack,sample

    def press(self,hold=350,release=350):
        ack=self.command('PRESS',hold,release)
        return self.sample(after=int(ack['end']))

    def mode(self,target):
        sample=self.sample()
        for _ in range(3):
            if int(sample['mode'])==target:return sample
            sample=self.press()
        raise AssertionError(f'Could not reach mode {target}: {sample}')

    def calibrate(self):
        self.reset();before=self.sample();ack=self.command('TURN',1,1)
        after=self.sample(after=int(ack['end']))
        delta=int(after['enc'])-int(before['enc'])
        assert abs(delta)==4,f'Quadrature fixture must yield four counts, got {delta}'
        self.sign=1 if delta>0 else -1
        ack=self.command('TURN',1,-1);back=self.sample(after=int(ack['end']))
        assert int(back['enc'])==int(before['enc'])
        return before,after,back

    def turn(self,counts):
        assert self.sign is not None
        ack=self.command('TURN',abs(counts),self.sign*(1 if counts>0 else -1))
        return self.sample(after=int(ack['end'])+1100)

    def result(self,name,data):
        self.results.append({'case':name,'data':data})
        (self.directory/'observations.json').write_text(json.dumps(self.results,indent=2)+'\n',encoding='utf-8')
