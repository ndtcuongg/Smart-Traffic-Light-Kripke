"""Independent, exhaustive checks on the JSON files, plus boundary/config tests."""
from pathlib import Path
from collections import deque
import json,re,copy
from intersection import Config,initial,step,PHASES,PERIODS,NEXT,POLES,COLORS,hhmmss
HERE=Path(__file__).resolve().parent
EXPECTED={
'NS_GREEN':('green','red'),'NS_YELLOW':('yellow','red'),'ALL_RED_NS_TO_EW':('red','red'),
'EW_GREEN':('red','green'),'EW_YELLOW':('red','yellow'),'ALL_RED_EW_TO_NS':('red','red')}

def decode(name):
    m=re.fullmatch(r'(?:t(\d+)__)?([A-Z_]+)__r(\d+)__now_([A-Z_]+)__entry_([A-Z_]+)',name)
    if not m: raise AssertionError(name)
    clock,phase,timer,period,entry=m.groups()
    return (None if clock is None else int(clock),phase,int(timer),period,entry)

def verify_file(path,cfg):
    doc=json.loads(path.read_text(encoding='utf-8')); names=doc['states']; nodes=set(names)
    assert len(nodes)==len(names) and set(doc['labeling'])==nodes
    assert set(doc['initial'])<=nodes and doc['initial']
    index={n:i for i,n in enumerate(names)}; succ=[set() for n in names]; pred=[set() for n in names]
    for a,b in doc['transitions']:
        assert a in nodes and b in nodes
        x,y=index[a],index[b];succ[x].add(y);pred[y].add(x)
    assert all(succ),'Deadlock'
    seen={index[n] for n in doc['initial']}; q=deque(seen)
    while q:
        for y in succ[q.popleft()]:
            if y not in seen:seen.add(y);q.append(y)
    assert len(seen)==len(names),'Unreachable generated state'
    decoded=[decode(n) for n in names]; lab=[set(doc['labeling'][n]) for n in names]
    for i,(clock,phase,timer,period,entry) in enumerate(decoded):
        assert 1<=timer<=cfg.duration(phase,entry)
        assert {'phase_'+phase,'period_'+period,'entry_'+entry,f'timer_{timer}'}<=lab[i]
        if clock is not None: assert period==cfg.period(clock) and f'clock_{clock:05d}' in lab[i]
        ns,ew=EXPECTED[phase]
        for p in POLES:
            color=ns if p in ('n','s') else ew
            for c in COLORS:
                on=f'{p}_{c}_on';off=f'{p}_{c}_off'
                assert (on in lab[i]) != (off in lab[i])
                assert (on in lab[i])==(c==color),(names[i],on)
        assert not(('ns_go' in lab[i]) and ('ew_go' in lab[i]))
        for y in succ[i]:
            nc,np,nt,nperiod,ne=decoded[y]
            assert nperiod in cfg.context_next[period]
            if clock is not None: assert nc==(clock+1)%86400 and nperiod==cfg.period(nc)
            if timer>1: assert (np,nt,ne)==(phase,timer-1,entry)
            else: assert np==NEXT[phase] and nt==cfg.duration(np,nperiod) and ne==nperiod
    # AF via reverse worklist; proves eventual GREEN from EVERY reachable state,
    # including every nondeterministic branch (therefore recurring liveness).
    waits={}
    for p in POLES:
        goal={i for i,l in enumerate(lab) if p+'_green_on' in l}
        count=[len(t) for t in succ];distance={i:0 for i in goal};q=deque(goal)
        longest=[0]*len(names)
        while q:
            y=q.popleft()
            for x in pred[y]:
                if x in distance:continue
                count[x]-=1;longest[x]=max(longest[x],distance[y]+1)
                if count[x]==0: distance[x]=longest[x];q.append(x)
        assert len(distance)==len(names),(path.name,p,'GREEN can be avoided forever')
        waits[p]=max(distance.values())
    reach={}
    for prefix,vals in [('phase_',PHASES),('period_',PERIODS)]:
        for value in vals:
            match=next((i for i,l in enumerate(lab) if prefix+value in l),None)
            assert match is not None
            reach[prefix+value]={'state':names[match],'enumeration_index':match}
    return {'file':path.name,'status':'PASS','states':len(nodes),'edges':sum(map(len,succ)),
        'reachable_states':len(seen),'deadlocks':0,'max_wait_to_green_seconds':waits,'reachability_witnesses':reach,
        'all_12_lamp_values_checked':True,'all_one_second_edges_checked':True}

def verify():
    cfg=Config(HERE/'config.json');reports=[verify_file(HERE/n,cfg) for n in ['smart_intersection.json','smart_intersection_exact.json']]
    boundaries=sorted({a for a,b,p in cfg.ranges});cases=[]
    for boundary in boundaries:
        for phase in PHASES:
            s=initial(cfg,(boundary-1)%86400,phase);t=step(cfg,s)
            assert t.clock==boundary and t.period==cfg.period(boundary)
            if s.remaining>1:
                assert t.phase==s.phase and t.entry_period==s.entry_period and t.remaining==s.remaining-1
            # Run through at least one expiry after the clock boundary.
            cur=s;transition=None
            for _ in range(cfg.maximum+2):
                nxt=step(cfg,cur)
                if cur.remaining==1:
                    assert nxt.phase==NEXT[cur.phase]
                    assert nxt.remaining==cfg.duration(nxt.phase,nxt.period) and nxt.entry_period==nxt.period
                    transition=(hhmmss(nxt.clock),nxt.phase,nxt.remaining,nxt.entry_period);break
                cur=nxt
            assert transition
            cases.append({'boundary':hhmmss(boundary),'initial_phase':phase,'status':'PASS','first_reset_after_boundary':transition})
    durations=[]
    for period in PERIODS:
        a,b,_=next(r for r in cfg.ranges if r[2]==period);clock=(a+b)//2
        for phase in PHASES:
            start=initial(cfg,clock,phase);s=start;n=0
            while s.phase==phase:
                assert s.remaining==cfg.duration(phase,period)-n
                s=step(cfg,s);n+=1;assert n<=cfg.maximum
            assert n==cfg.duration(phase,period)
            durations.append({'period':period,'phase':phase,'seconds':n,'status':'PASS'})
    # Exercise actual configuration validation, including zero and uncovered time ranges.
    invalid=HERE/'evidence'/'invalid_config_test_input.json';negative=[]
    for defect in ['zero_duration','range_gap','missing_period','bad_initial_clock']:
        raw=copy.deepcopy(cfg.raw)
        if defect=='zero_duration':raw['durations_seconds']['NORMAL']['NS_GREEN']=0
        elif defect=='range_gap':raw['period_ranges'][0]['end']='05:59:59'
        elif defect=='missing_period':del raw['durations_seconds']['NORMAL']
        else:raw['initial_clock_seconds']=86400
        invalid.write_text(json.dumps(raw),encoding='utf-8')
        rejected=False
        try:Config(invalid)
        except ValueError:rejected=True
        assert rejected;negative.append({'case':defect,'status':'PASS (rejected)'})
    invalid.unlink()
    # Non-default timings and a change while green is active.
    variant=HERE/'evidence'/'alternate_config_test_input.json';raw=copy.deepcopy(cfg.raw)
    raw['durations_seconds']['NORMAL']['NS_GREEN']=17;raw['durations_seconds']['MORNING_PEAK']['EW_GREEN']=41
    variant.write_text(json.dumps(raw,indent=2),encoding='utf-8');other=Config(variant)
    s=initial(other,6*3600+59*60+59,'NS_GREEN');assert s.remaining==17
    t=step(other,s);assert t.period=='MORNING_PEAK' and t.entry_period=='NORMAL' and t.remaining==16
    for _ in range(16):t=step(other,t)
    assert t.phase=='NS_YELLOW' and t.entry_period=='MORNING_PEAK' and t.remaining==3
    saved=json.loads((HERE/'evidence/preserved_work.json').read_text(encoding='utf-8'))
    import hashlib
    for rel,record in saved.items():assert hashlib.sha256((HERE.parent/rel).read_bytes()).hexdigest()==record['sha256'],rel
    result={'overall':'PASS','json_graph_checks':reports,'boundary_tests':cases,'exact_duration_tests':durations,
        'invalid_configuration_tests':negative,'alternate_configuration_test':'PASS','old_files_unchanged':'PASS'}
    (HERE/'evidence/graph_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'overall':'PASS','graph_states':[r['states'] for r in reports],'boundary_cases':len(cases),'duration_cases':len(durations),'max_wait':reports[0]['max_wait_to_green_seconds'],'old_files_unchanged':True},indent=2))

if __name__=='__main__':verify()
