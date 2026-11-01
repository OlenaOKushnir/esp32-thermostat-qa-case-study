"""Short-pulse trains around the source's 200 ms acceptance interval."""
import json,time
import pytest

@pytest.mark.parametrize('period',[199,200,201])
def test_short_pulse_train_at_debounce_boundary(campaign,period):
    campaign.reset();start=len(campaign.records);acks=[]
    # Five queued commands fit the UART receive buffer. Each group has four
    # consecutive target-period intervals; inter-group host gaps are measured.
    for group in range(2):
        requests=[]
        for _ in range(5):
            campaign.counter+=1;identity=f'C{campaign.counter:04}'
            request={'id':identity,'operation':'PRESS','a':30,'b':period-30,
                     'host_elapsed':time.monotonic()-campaign.started,'group':group}
            campaign.events.write(json.dumps(request)+'\n');requests.append(identity)
        campaign.events.flush()
        campaign.port.write(''.join(f'{identity} PRESS 30 {period-30}\n' for identity in requests).encode())
        for identity in requests:
            acks.append(campaign.wait(lambda r:r['type']=='ACK' and r.get('id')==identity))
    sample=campaign.sample(after=int(acks[-1]['end']))
    events=[r for r in campaign.records[start:] if r['type']=='MODE']
    accepted=[int(r['ms']) for r in events]
    # MODE is logged after Serial output, not at the debounce decision. Match
    # each observed transition to one injected LOW window instead of using its
    # delayed timestamp as an exact decision-clock measurement.
    pulse_indices=[]
    for timestamp in accepted:
        matches=[i for i,ack in enumerate(acks) if int(ack['begin'])<=timestamp<=int(ack['begin'])+45]
        assert len(matches)==1
        pulse_indices.append(matches[0])
    intervals=[int(acks[i+1]['begin'])-int(acks[i]['begin']) for i in range(9) if i!=4]
    campaign.result(f'debounce_period_{period}',{'requested_period_ms':period,
        'actual_within_group_intervals_ms':intervals,'acknowledgments':acks,
        'accepted_modes':events,'matched_pulse_indices':pulse_indices,'final_sample':sample})
    assert len(acks)==10 and len(intervals)==8
    assert all(period<=gap<=period+15 for gap in intervals), 'Fixture scheduling outside measured boundary window'
    assert 0<len(events)<=10
    assert len(set(pulse_indices))==len(pulse_indices), 'One clean short pulse produced multiple mode transitions'
    assert int(sample['mode'])==len(events)%3
    assert float(sample['lower'])==20 and float(sample['upper'])==25

def test_settled_fault_contacts_and_reset_from_fault(campaign):
    campaign.reset();campaign.temperature(250)
    ack=campaign.command('FAULT',1)
    first=campaign.sample(lambda r:int(r['valid'])==0,after=int(ack['begin']))
    settled=campaign.sample(lambda r:int(r['valid'])==0,after=int(first['ms'])+500)
    boot,recovered=campaign.reset()
    campaign.result('settled_fault_contacts_and_reset',{'fault':settled,'boot':boot,'recovered':recovered})
    # Electrical correlation control, not approval of unsafe fault handling.
    assert int(settled['pin'])==1 and (int(settled['no']),int(settled['nc']))==(0,1)
    assert int(recovered['pin'])==0 and (int(recovered['no']),int(recovered['nc']))==(1,0)
