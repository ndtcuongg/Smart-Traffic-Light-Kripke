"""NuSMV BDD checks only; no bounded model checking or other chapters."""
from pathlib import Path
import subprocess,json,re,shutil,time
from intersection import Config,PHASES
from nusmv_model import generate
HERE=Path(__file__).resolve().parent; EXE=shutil.which('NuSMV')

def run(name,text,expected=True,timeout=180):
    folder=HERE/'evidence'; path=folder/(name+'.smv');path.write_text(text,encoding='utf-8')
    command=[EXE,'-dynamic','-df','-coi',str(path)];start=time.perf_counter()
    try:
        result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
        output=result.stdout; error=result.stderr; code=result.returncode; timedout=False
    except subprocess.TimeoutExpired as e:
        def txt(x): return x.decode('utf-8',errors='replace') if isinstance(x,bytes) else x or ''
        output=txt(e.stdout);error=txt(e.stderr);code=None;timedout=True
    (folder/(name+('_timeout' if timedout else '')+'.log')).write_text(output+'\nSTDERR\n'+error,encoding='utf-8')
    checks=[{'formula':m.group(1).strip(),'result':m.group(2)=='true'} for m in re.finditer(r'-- specification (.*?) is (true|false)',output,re.S)]
    expected_count=len(re.findall(r'^CTLSPEC',text,re.M))
    ok=not timedout and code==0 and len(checks)==expected_count and all(c['result']==expected for c in checks)
    record={'name':name,'command':command,'seconds':round(time.perf_counter()-start,3),'returncode':code,'timeout':timedout,'expected_properties':expected_count,
        'checks':checks,'expected_truth':expected,'status':'PASS' if ok else 'FAIL','counterexample_log':name+'.log' if any(not c['result'] for c in checks) else None}
    print(json.dumps({k:v for k,v in record.items() if k!='checks'}),flush=True)
    return record

def verify():
    cfg=Config(HERE/'config.json');model,props=generate(cfg); reports=[]
    reports.append(run('nusmv_main',model))
    arbitrary,_=generate(cfg,any_clock=True)
    reports.append(run('nusmv_any_start_time',arbitrary))
    base=model.split('-- PROPERTIES')[0]
    reach=''.join('CTLSPEC EF(period = '+p+');\n' for p in ('MORNING_PEAK','NORMAL','EVENING_PEAK','NIGHT_LOW'))
    reports.append(run('nusmv_period_reachability',base+reach,True,120))
    # Non-vacuity controls: these defects change outputs/reset/transition behavior.
    bad=base.replace('next(e_green) := (phase_next = EW_GREEN);','next(e_green) := (phase_next = EW_GREEN | phase_next = NS_GREEN);')
    assert bad!=base
    reports.append(run('negative_conflicting_green',bad+'CTLSPEC AG(!conflicting_green);\n',False,60))
    bad=base.replace('timer = 1 : next_phase_duration;','timer = 1 : 1;')
    assert bad!=base
    reports.append(run('negative_timer_reset',bad+'CTLSPEC AG((phase = ALL_RED_EW_TO_NS & timer = 1 & period_next = NIGHT_LOW) -> AX(timer = 15));\n',False,60))
    bad=base.replace('phase = NS_YELLOW : ALL_RED_NS_TO_EW;','phase = NS_YELLOW : EW_GREEN;')
    assert bad!=base
    reports.append(run('negative_skip_all_red',bad+'CTLSPEC AG((phase = NS_YELLOW & timer = 1) -> AX(all_red));\n',False,60))
    (HERE/'evidence/nusmv_results.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
    if any(r['status']!='PASS' for r in reports): raise RuntimeError('A NuSMV check failed or timed out; see logs')

if __name__=='__main__': verify()
