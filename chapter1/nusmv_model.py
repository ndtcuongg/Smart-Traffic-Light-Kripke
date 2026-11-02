"""Generate the explicit 12-lamp NuSMV controller and named CTL properties."""
from intersection import PHASES,PERIODS,POLES,COLORS,NEXT,lamps

def generate(cfg,initial_clock=None,initial_phase=None,any_clock=False):
    clock=cfg.clock if initial_clock is None else initial_clock
    phase=cfg.phase if initial_phase is None else initial_phase
    def period_case(clock_expr):
        prefix='next_' if clock_expr=='clock_next' else ''
        h,m,s=(prefix+x for x in ('hour','minute','second'))
        def ge(value):
            vh,vm,vs=value//3600,value//60%60,value%60
            return f'({h} > {vh} | ({h} = {vh} & ({m} > {vm} | ({m} = {vm} & {s} >= {vs}))))'
        return 'case '+' '.join(f'{ge(a)} & !{ge(b)} : {p};' for a,b,p in cfg.ranges)+' TRUE : NIGHT_LOW; esac'
    def duration_case(phase_expr,period_expr):
        return 'case '+' '.join(f'{phase_expr} = {q} & {period_expr} = {p} : {cfg.duration(q,p)};' for p in PERIODS for q in PHASES)+' TRUE : 1; esac'
    lines=['-- Generated from chapter1/config.json; one transition = one second.','MODULE main','VAR',
        '  phase : {'+', '.join(PHASES)+'};',f'  timer : 1..{cfg.maximum};','  hour : 0..23;','  minute : 0..59;','  second : 0..59;',
        '  entry_period : {'+', '.join(PERIODS)+'};',]
    lines += [f'  {p}_{c} : boolean;' for p in POLES for c in COLORS]
    lines += ['DEFINE', '  clock_sec := hour * 3600 + minute * 60 + second;', '  next_second := case second = 59 : 0; TRUE : second + 1; esac;', '  next_minute := case second < 59 : minute; minute = 59 : 0; TRUE : minute + 1; esac;', '  next_hour := case second < 59 | minute < 59 : hour; hour = 23 : 0; TRUE : hour + 1; esac;',
        '  period := '+period_case('clock_sec')+';','  period_next := '+period_case('clock_next')+';',
        '  phase_after := case '+' '.join(f'phase = {p} : {NEXT[p]};' for p in PHASES)+' TRUE : NS_GREEN; esac;',
        '  phase_next := case timer = 1 : phase_after; TRUE : phase; esac;',
        '  phase_duration := '+duration_case('phase','entry_period')+';',
        '  next_phase_duration := '+duration_case('phase_after','period_next')+';',
        '  initial_duration := '+duration_case(phase,'period')+';',
        '  ns_go := n_green | s_green;','  ew_go := e_green | w_green;',
        '  conflicting_green := ns_go & ew_go;',
        '  all_red := n_red & s_red & e_red & w_red;',
        'ASSIGN',f'  init(phase) := {phase};','  next(phase) := phase_next;']
    if not any_clock: lines += [f'  init(hour) := {clock//3600};', f'  init(minute) := {clock//60%60};', f'  init(second) := {clock%60};']
    lines += ['  next(hour) := next_hour;', '  next(minute) := next_minute;', '  next(second) := next_second;', '  init(entry_period) := period;',
        '  next(entry_period) := case timer = 1 : period_next; TRUE : entry_period; esac;',
        '  init(timer) := initial_duration;',
        '  next(timer) := case timer > 1 : timer - 1; timer = 1 : next_phase_duration; TRUE : timer; esac;']
    for p in POLES:
        for c in COLORS:
            phases=[q for q in PHASES if lamps(q)[f'{p}_{c}']]
            cond=' | '.join('phase_next = '+q for q in phases)
            init='TRUE' if lamps(phase)[f'{p}_{c}'] else 'FALSE'
            lines += [f'  init({p}_{c}) := {init};',f'  next({p}_{c}) := ({cond});']
    props=[]
    def prop(name,formula,category): props.append({'name':name,'formula':formula,'category':category})
    prop('physical_green_exclusion','AG(!conflicting_green)','safety')
    for p in POLES:
        prop('one_hot_'+p,f'AG(({p}_red | {p}_yellow | {p}_green) & !({p}_red & {p}_yellow) & !({p}_red & {p}_green) & !({p}_yellow & {p}_green))','safety')
        prop('recurring_green_'+p,f'AG(AF({p}_green))','liveness')
    for c in COLORS: prop('synchronized_'+c,f'AG((n_{c} = s_{c}) & (e_{c} = w_{c}))','safety')
    prop('yellow_ns_other_red','AG((n_yellow | s_yellow) -> (e_red & w_red))','safety')
    prop('yellow_ew_other_red','AG((e_yellow | w_yellow) -> (n_red & s_red))','safety')
    prop('clearance_all_red','AG((phase = ALL_RED_NS_TO_EW | phase = ALL_RED_EW_TO_NS) -> all_red)','safety')
    prop('deadlock_free','AG(EX(TRUE))','deadlock')
    prop('timer_bounds','AG(timer >= 1 & timer <= phase_duration)','timer')
    for value in range(60):
        prop(f'clock_second_{value}',f'AG(second = {value} -> AX(second = {(value+1)%60}))','clock')
        prop(f'clock_minute_tick_{value}',f'AG((second = 59 & minute = {value}) -> AX(minute = {(value+1)%60}))','clock')
        prop(f'clock_minute_hold_{value}',f'AG((second < 59 & minute = {value}) -> AX(minute = {value}))','clock')
    for value in range(24):
        prop(f'clock_hour_tick_{value}',f'AG((second = 59 & minute = 59 & hour = {value}) -> AX(hour = {(value+1)%24}))','clock')
        prop(f'clock_hour_hold_{value}',f'AG(((second < 59 | minute < 59) & hour = {value}) -> AX(hour = {value}))','clock')
    for t in range(2,cfg.maximum+1): prop(f'countdown_{t}',f'AG(timer = {t} -> AX(timer = {t-1}))','timer')
    for q in PHASES:
        prop('hold_'+q,f'AG((phase = {q} & timer > 1) -> AX(phase = {q}))','transition')
        prop('advance_'+q,f'AG((phase = {q} & timer = 1) -> AX(phase = {NEXT[q]}))','transition')
        prop('reachable_'+q,f'EF(phase = {q})','reachability')
        for p in PERIODS:
            d=cfg.duration(NEXT[q],p)
            prop('reset_'+q+'_'+p,f'AG((phase = {q} & timer = 1 & period_next = {p}) -> AX(phase = {NEXT[q]} & timer = {d} & entry_period = {p}))','adaptive')
    for p in PERIODS:
        prop('latch_'+p,f'AG((entry_period = {p} & timer > 1) -> AX(entry_period = {p}))','adaptive')
    lines += ['-- PROPERTIES']+[f'CTLSPEC NAME {p["name"]} := {p["formula"]};' for p in props]
    return '\n'.join(lines)+'\n',props
