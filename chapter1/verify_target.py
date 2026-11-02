"""Run only the real Chapter 1 parser/checker bundled in SecLabFramework."""
from pathlib import Path
import json,sys,time,re,hashlib
from core.kripke import KripkeStructure,CTLChecker,find_deadlock_states,check_mutual_exclusion
sys.stdout.reconfigure(encoding='utf-8'); here=Path.cwd()/'chapter1'
sample=Path.cwd()/'.chapter1-tools/seclab/dataset/ch1_verification/traffic_light.json'
original=json.loads(sample.read_text(encoding='utf-8'))
doc=json.loads((here/'smart_intersection.json').read_text(encoding='utf-8'))
assert set(doc)<=set(original), 'Unsupported top-level Chapter 1 fields'
assert set(['states','initial','labeling','transitions'])<=set(doc)
start=time.perf_counter(); model=KripkeStructure.from_json_file(str(here/'smart_intersection.json'))
parse_seconds=time.perf_counter()-start
checker=CTLChecker(model); rows=[]
for formula in doc['suggested_ctl_formulas']:
    assert re.fullmatch(r'(AG|AF|EF|EG|AX|EX)\(!?[A-Za-z_]\w*\)',formula)
    start=time.perf_counter(); holds,sat=checker.check(formula)
    row={'formula':formula,'status':'PASS' if holds else 'FAIL','satisfying_states':len(sat),'seconds':round(time.perf_counter()-start,4)}
    rows.append(row); print(json.dumps(row),flush=True)
start=time.perf_counter(); dead=sorted(find_deadlock_states(model)); mutex,bad=check_mutual_exclusion(model,'ns_go','ew_go')
# Load the full timed JSON through the same actual parser; its large-state checks use
# the exhaustive independent checker and NuSMV, not the quadratic bundled algorithm.
exact=KripkeStructure.from_json_file(str(here/'smart_intersection_exact.json'))
report={'target_executable':r'C:\Users\Admin\Downloads\SecLabFramework.exe','module':'core.kripke (unmodified bundled Python 3.14 bytecode)',
    'schema_sample':'dataset/ch1_verification/traffic_light.json','schema_sample_sha256':hashlib.sha256(sample.read_bytes()).hexdigest(),
    'json_parser':'KripkeStructure.from_json_file','parse_status':'PASS','parse_seconds':parse_seconds,'states':len(model.states),'transitions':len(model.transitions),
    'properties':rows,'deadlock_states':dead,'mutex':{'atoms':['ns_go','ew_go'],'status':'PASS' if mutex else 'FAIL','violating_states':sorted(bad)},
    'exact_json_parse':{'status':'PASS','states':len(exact.states),'transitions':len(exact.transitions)},
    'other_chapters_invoked':False,'overall':'PASS' if all(r['status']=='PASS' for r in rows) and not dead and mutex else 'FAIL'}
(here/'evidence/seclab_results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='properties'},ensure_ascii=False,indent=2),flush=True)
if report['overall']!='PASS': raise RuntimeError('Chapter 1 verification failed')
