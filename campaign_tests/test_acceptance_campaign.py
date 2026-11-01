"""Remaining simulation acceptance gates, executed against live ESP32 firmware."""
import pytest

def test_startup_defaults_and_pin_level(campaign):
    boot,sample=campaign.reset();campaign.result('startup',{'boot':boot,'sample':sample})
    assert int(sample['pin'])==0 and int(sample['req'])==0
    assert int(sample['mode'])==0 and float(sample['lower'])==20 and float(sample['upper'])==25

def test_encoder_both_directions_and_half_steps(campaign):
    campaign.reset();campaign.mode(1)
    plus=campaign.turn(1);minus=campaign.turn(-1)
    campaign.mode(2);upperplus=campaign.turn(1);upperminus=campaign.turn(-1)
    campaign.result('half_steps',[plus,minus,upperplus,upperminus])
    assert float(plus['lower'])==20.5 and float(minus['lower'])==20
    assert float(upperplus['upper'])==25.5 and float(upperminus['upper'])==25

@pytest.mark.parametrize('case,mode,counts,key,target,reverse_target',[
    ('lower_min',1,-140,'lower',-50,-49.5),('lower_gap',1,9,'lower',24.5,24),
    ('upper_max',2,150,'upper',100,99.5),('upper_gap',2,-9,'upper',20.5,21)])
def test_setpoint_exact_boundary_clamp_and_reversal(campaign,case,mode,counts,key,target,reverse_target):
    campaign.reset();campaign.mode(mode)
    edge=campaign.turn(counts);beyond=campaign.turn(1 if counts>0 else -1);reverse=campaign.turn(-1 if counts>0 else 1)
    campaign.result(case,[edge,beyond,reverse])
    assert float(edge[key])==target and float(beyond[key])==target
    assert float(reverse[key])==reverse_target
    assert all(float(r['upper'])-float(r['lower'])>=.5 for r in [edge,beyond,reverse])

def test_rotation_in_view_keeps_thresholds(campaign):
    campaign.reset();first=campaign.turn(100);second=campaign.turn(-100)
    campaign.result('view_rotation',[first,second])
    assert all(int(r['mode'])==0 and float(r['lower'])==20 and float(r['upper'])==25 for r in [first,second])

def test_thirty_valid_presses_cycle_modes(campaign):
    campaign.reset();observations=[]
    for index in range(30):
        sample=campaign.press();observations.append(sample)
    campaign.result('thirty_valid_presses',observations)
    assert all(int(sample['mode'])==(index+1)%3 for index,sample in enumerate(observations))

def test_rapid_press_train_does_not_corrupt_state(campaign):
    campaign.reset();before=len(campaign.records)
    for _ in range(20):campaign.command('PRESS',30,70)
    sample=campaign.sample();events=[r for r in campaign.records[before:] if r['type']=='MODE']
    campaign.result('rapid_train',{'accepted':len(events),'injected':20,'sample':sample})
    assert 0<len(events)<=20
    assert 0<=int(sample['mode'])<=2 and float(sample['upper'])-float(sample['lower'])>=.5

@pytest.mark.parametrize('state',['OFF','ON','SET_LOWER','SET_UPPER'])
def test_reset_from_each_operating_state(campaign,state):
    campaign.reset()
    if state=='ON':_,pre=campaign.temperature(190)
    elif state=='OFF':_,pre=campaign.temperature(250)
    else:
        campaign.mode(1 if state=='SET_LOWER' else 2);pre=campaign.turn(1)
    boot,after=campaign.reset();campaign.result('reset_'+state,{'pre':pre,'boot':boot,'after':after})
    assert int(after['mode'])==0 and float(after['lower'])==20 and float(after['upper'])==25
    assert int(after['pin'])==0 and int(after['req'])==0

def test_twenty_hysteresis_cycles_and_response_budget(campaign):
    campaign.reset();observations=[]
    for cycle in range(20):
        for temperature,expected in [(190,1),(220,1),(250,0),(220,0)]:
            ack,sample=campaign.temperature(temperature)
            observations.append({'cycle':cycle+1,'stimulus':ack,'sample':sample,'expected':expected,
                                 'response_ms':int(sample['ms'])-int(ack['begin'])})
        campaign.result('twenty_cycles_progress',observations)
        print(f'Completed hysteresis cycle {cycle+1}/20',flush=True)
    campaign.result('twenty_cycles',observations)
    assert all(int(x['sample']['pin'])==x['expected'] and int(x['sample']['req'])==x['expected'] for x in observations)
    assert all(0<=x['response_ms']<=5000 for x in observations)

def test_relay_contact_polarity_on_low_and_high(campaign):
    campaign.reset();_,first=campaign.temperature(250)
    low=campaign.sample(after=int(first['ms']))
    _,first=campaign.temperature(190)
    high=campaign.sample(after=int(first['ms']))
    campaign.result('relay_contacts',{'low':low,'high':high})
    assert int(low['pin'])==0 and int(high['pin'])==1
    assert (int(low['no']),int(low['nc']))==(1,0), 'RTH-10: LOW request must leave COM-NC closed'
    assert (int(high['no']),int(high['nc']))==(0,1), 'RTH-10: HIGH request must close COM-NO'

@pytest.mark.parametrize('initial,restored',[(190,190),(190,250),(250,190),(250,250)])
def test_fault_and_recovery_complete_matrix(campaign,initial,restored):
    campaign.reset();_,pre=campaign.temperature(initial)
    ack=campaign.command('FAULT',1)
    fault=campaign.sample(lambda r:int(r['valid'])==0,after=int(ack['begin']))
    campaign.command('TEMP',restored);reconnect=campaign.command('FAULT',0)
    recovered=campaign.sample(lambda r:int(r['valid'])==1 and abs(float(r['temp'])-restored/10)<.01,after=int(reconnect['begin']))
    campaign.result(f'recovery_{initial}_{restored}',{'pre':pre,'fault_stimulus':ack,'fault':fault,'reconnect':reconnect,'recovered':recovered})
    assert int(recovered['pin'])==(1 if restored<200 else 0)
    assert int(recovered['ms'])-int(reconnect['begin'])<=5000
    assert int(fault['ms'])-int(ack['begin'])<=5000
    if initial>=250:
        assert int(fault['pin'])==0,'BUG-T03: fault from OFF creates a new heat request'

def test_display_fields_match_stable_normal_and_edit_state(campaign):
    campaign.reset();observations=[]
    for mode in [0,1,2]:
        sample=campaign.mode(mode)
        if mode:sample=campaign.turn(1)
        frame=campaign.wait(lambda r:r['type']=='FRAME' and int(r['ms'])>int(sample['ms']))
        observations.append({'sample':sample,'frame':frame})
        assert int(frame['mode'])==int(sample['mode'])
        assert all(float(frame[key])==float(sample[key]) for key in ['temp','lower','upper'])
    campaign.result('display_fields',observations)

def test_valid_zero_and_negative_sensor_temperature(campaign):
    campaign.reset();observations=[]
    for temperature in [0,-100]:
        ack,sample=campaign.temperature(temperature);observations.append(sample)
        assert int(sample['valid'])==1 and int(sample['pin'])==1
    campaign.result('valid_zero_and_negative',observations)
