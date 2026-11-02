"""Chapter 1 controller and explicit Kripke graphs. Standard library only."""
from dataclasses import dataclass
from pathlib import Path
import json

PHASES=('NS_GREEN','NS_YELLOW','ALL_RED_NS_TO_EW','EW_GREEN','EW_YELLOW','ALL_RED_EW_TO_NS')
PERIODS=('MORNING_PEAK','NORMAL','EVENING_PEAK','NIGHT_LOW')
NEXT=dict(zip(PHASES,PHASES[1:]+PHASES[:1]))
POLES=('n','s','e','w')
COLORS=('red','yellow','green')

def seconds(text):
    h,m,s=map(int,text.split(':'))
    if not (0<=h<=24 and 0<=m<60 and 0<=s<60 and (h<24 or m==s==0)):
        raise ValueError('Invalid clock: '+text)
    return h*3600+m*60+s

def hhmmss(value):
    return f'{value//3600:02d}:{value//60%60:02d}:{value%60:02d}'

class Config:
    def __init__(self,path):
        self.raw=json.loads(Path(path).read_text(encoding='utf-8-sig'))
        self.ranges=[(seconds(r['start']),seconds(r['end']),r['period']) for r in self.raw['period_ranges']]
        end=0
        for a,b,p in self.ranges:
            if a!=end or a>=b or p not in PERIODS: raise ValueError('Ranges must partition [0,86400)')
            end=b
        if end!=86400 or set(p for a,b,p in self.ranges)!=set(PERIODS): raise ValueError('Missing period')
        self.durations=self.raw['durations_seconds']
        if set(self.durations)!=set(PERIODS): raise ValueError('Invalid duration periods')
        for p,phases in self.durations.items():
            if set(phases)!=set(PHASES): raise ValueError('Missing phase duration')
            if any(type(x)!=int or not 1<=x<=120 for x in phases.values()):
                raise ValueError('Each phase duration must be an integer from 1 to 120 seconds')
        self.clock=self.raw['initial_clock_seconds']; self.phase=self.raw['initial_phase']
        if type(self.clock)!=int or not 0<=self.clock<86400 or self.phase not in PHASES: raise ValueError('Invalid initial state')
        self.maximum=max(x for row in self.durations.values() for x in row.values())
        self.context_next={p:{p} for p in PERIODS}
        for i,(_,_,p) in enumerate(self.ranges): self.context_next[p].add(self.ranges[(i+1)%len(self.ranges)][2])
    def period(self,clock):
        for a,b,p in self.ranges:
            if a<=clock<b: return p
        raise ValueError(clock)
    def duration(self,phase,period): return self.durations[period][phase]

@dataclass(frozen=True)
class State:
    phase:str
    remaining:int
    period:str
    entry_period:str
    clock:int|None=None

def lamps(phase):
    ns='green' if phase=='NS_GREEN' else 'yellow' if phase=='NS_YELLOW' else 'red'
    ew='green' if phase=='EW_GREEN' else 'yellow' if phase=='EW_YELLOW' else 'red'
    return {f'{p}_{c}': (ns if p in ('n','s') else ew)==c for p in POLES for c in COLORS}

def initial(cfg,clock=None,phase=None):
    clock=cfg.clock if clock is None else clock; phase=cfg.phase if phase is None else phase
    p=cfg.period(clock)
    return State(phase,cfg.duration(phase,p),p,p,clock)

def advance(cfg,s,next_period,next_clock=None):
    if s.remaining>1: return State(s.phase,s.remaining-1,next_period,s.entry_period,next_clock)
    phase=NEXT[s.phase]
    return State(phase,cfg.duration(phase,next_period),next_period,next_period,next_clock)

def step(cfg,s):
    if s.clock is None: raise ValueError('Exact step needs the 24-hour clock')
    clock=(s.clock+1)%86400
    return advance(cfg,s,cfg.period(clock),clock)

def abstract(s): return State(s.phase,s.remaining,s.period,s.entry_period)

def sid(s):
    prefix='' if s.clock is None else f't{s.clock:05d}__'
    return f'{prefix}{s.phase}__r{s.remaining:03d}__now_{s.period}__entry_{s.entry_period}'

def rule_flags(cfg,s,successors):
    light=lamps(s.phase)
    ns=light['n_green'] or light['s_green']; ew=light['e_green'] or light['w_green']
    onehot=all(sum(light[f'{p}_{c}'] for c in COLORS)==1 for p in POLES)
    sync=all(light[f'n_{c}']==light[f's_{c}'] and light[f'e_{c}']==light[f'w_{c}'] for c in COLORS)
    yellow_safe=(not (light['n_yellow'] or light['s_yellow']) or (light['e_red'] and light['w_red'])) and (not(light['e_yellow'] or light['w_yellow']) or(light['n_red'] and light['s_red']))
    countdown=all(s.remaining<=1 or (t.remaining==s.remaining-1 and t.phase==s.phase and t.entry_period==s.entry_period) for t in successors)
    reset=all(s.remaining!=1 or (t.phase==NEXT[s.phase] and t.remaining==cfg.duration(t.phase,t.period) and t.entry_period==t.period) for t in successors)
    sequence=all(t.phase==(s.phase if s.remaining>1 else NEXT[s.phase]) for t in successors)
    return {'normal_operation':True,'safe':not(ns and ew),'one_hot':onehot,'synchronized':sync,'yellow_safe':yellow_safe,
        'all_red_correct':not s.phase.startswith('ALL_RED') or all(light[f'{p}_red'] for p in POLES),
        'timer_valid':1<=s.remaining<=cfg.duration(s.phase,s.entry_period),
        'countdown_ok':countdown,'reset_ok':reset,'transition_ok':sequence,'transition_enabled':bool(successors)}

def label(cfg,s,successors):
    light=lamps(s.phase)
    result=[f'{k}_{"on" if v else "off"}' for k,v in light.items()]
    result += ['phase_'+s.phase,'period_'+s.period,'entry_'+s.entry_period,f'timer_{s.remaining}']
    if s.clock is not None: result.append(f'clock_{s.clock:05d}')
    result += [k for k,v in rule_flags(cfg,s,successors).items() if v]
    if light['n_green'] or light['s_green']: result.append('ns_go')
    if light['e_green'] or light['w_green']: result.append('ew_go')
    if (light['n_green'] or light['s_green']) and (light['e_green'] or light['w_green']): result.append('conflicting_green')
    return result

PROPERTIES=['AG(safe)','AG(!conflicting_green)','AG(one_hot)','AG(synchronized)','AG(yellow_safe)','AG(all_red_correct)',
    'AG(timer_valid)','AG(countdown_ok)','AG(reset_ok)','AG(transition_ok)','AG(transition_enabled)',
    'AF(n_green_on)','AF(s_green_on)','AF(e_green_on)','AF(w_green_on)','EG(normal_operation)']
PROPERTIES += ['EF(phase_'+p+')' for p in PHASES]+['EF(period_'+p+')' for p in PERIODS]

def exact_graph(cfg,limit=1000000):
    values=[]; seen={}; s=initial(cfg)
    while s not in seen:
        if len(values)>=limit: raise RuntimeError(f'Exact orbit exceeds {limit} states; increase --state-limit explicitly')
        seen[s]=len(values); values.append(s); s=step(cfg,s)
    edges=[[i+1] for i in range(len(values)-1)]+[[seen[s]]]
    return values,edges,seen[s]

def abstract_graph(cfg):
    start=abstract(initial(cfg)); values=[start]; seen={start:0}; edges=[]
    for s in values:
        targets=[]
        for p in sorted(cfg.context_next[s.period]):
            t=advance(cfg,s,p)
            if t not in seen: seen[t]=len(values); values.append(t)
            targets.append(seen[t])
        edges.append(targets)
    return values,edges

def write_spec(path,cfg,values,edges,description):
    ids=[sid(s) for s in values]
    doc={'description':description,'states':ids,'initial':[ids[0]],
        'labeling':{ids[i]:label(cfg,s,[values[j] for j in edges[i]]) for i,s in enumerate(values)},
        'transitions':[[ids[i],ids[j]] for i,targets in enumerate(edges) for j in targets],
        'suggested_ctl_formulas':PROPERTIES}
    Path(path).write_text(json.dumps(doc,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    return doc
