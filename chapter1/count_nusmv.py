from pathlib import Path
import subprocess,shutil,time,json,re
here=Path(__file__).resolve().parent
cmd=[shutil.which('NuSMV'),'-dynamic','-r','-is','-ils','-ii',str(here/'smart_intersection.smv')]
expected=json.loads((here/'evidence/build_summary.json').read_text(encoding='utf-8'))['concrete_states']
start=time.perf_counter()
try:
    p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=60)
    text=p.stdout+'\nSTDERR\n'+p.stderr
    match=re.search(r'reachable states:\s*(\d+)',text,re.I)
    result={'command':cmd,'returncode':p.returncode,'seconds':time.perf_counter()-start,'reachable_states':int(match[1]) if match else None,'status':'PASS' if p.returncode==0 and match and int(match[1])==expected else 'UNVERIFIED'}
except subprocess.TimeoutExpired as e:
    def tx(x):return x.decode(errors='replace') if isinstance(x,bytes) else x or ''
    text=tx(e.stdout)+'\nSTDERR\n'+tx(e.stderr)
    result={'command':cmd,'status':'UNVERIFIED (60 second timeout)','seconds':time.perf_counter()-start}
(here/'evidence/nusmv_reachable.log').write_text(text,encoding='utf-8')
(here/'evidence/nusmv_reachable.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2),flush=True)
