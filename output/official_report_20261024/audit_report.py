"""Read-only project audit; writes isolated evidence under this delivery only."""
from pathlib import Path
import sys,json,re,hashlib,subprocess,shutil,csv,time,datetime,collections
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path[:0]=[str(ROOT/'chapter1'),str(ROOT/'chapter1/web'),str(ROOT/'.codex-tools'),str(ROOT/'chapter1/web/report_delivery/_tools')]
def read(rel):return (ROOT/rel).read_text(encoding='utf-8-sig')
def obj(rel):return json.loads(read(rel))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
 ev=OUT/'evidence';ev.mkdir(exist_ok=True)
 excludes={'.git','__pycache__','_tools','edge_render_profile','node_modules','.chapter1-tools','.codex-tools'}
 files=[p for p in ROOT.rglob('*') if p.is_file() and not any(x in excludes for x in p.relative_to(ROOT).parts) and OUT not in p.parents]
 inv={p.relative_to(ROOT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in files}
 dump(OUT/'source_inventory.json',inv)
 baseline=obj('chapter1/evidence/preserved_work.json')
 assert all(inv[k]['sha256']==v['sha256'] for k,v in baseline.items())
 props=obj('chapter1/properties.json'); model=read('chapter1/smart_intersection.smv')
 assert len(props)==len(re.findall(r'^CTLSPEC',model,re.M))==335
 assert sha(ROOT/'chapter1/smart_intersection.smv')==sha(ROOT/'chapter1/evidence/nusmv_main.smv')
 logs=obj('chapter1/evidence/nusmv_results.json')
 for r in logs:
  assert r['status']=='PASS' and r['returncode']==0 and not r['timeout']
  assert len(r['checks'])==r['expected_properties']
  assert all(c['result']==r['expected_truth'] for c in r['checks'])
 old=obj('output/nusmv_results.json')
 for r in old:assert sha(ROOT/r['file'])==r['sha256']
 from intersection import Config
 from verify_graph import verify_file
 from ctl_checker import check_graph
 cfg=Config(ROOT/'chapter1/config.json')
 graphs=[verify_file(ROOT/'chapter1'/n,cfg) for n in ['smart_intersection.json','smart_intersection_exact.json']]
 ctl=check_graph(obj('chapter1/smart_intersection.json')); assert ctl['overall']=='PASS' and len(ctl['properties'])==26
 dump(ev/'json_graph_recheck.json',graphs);dump(ev/'json_ctl_recheck.json',ctl)
 # Generated text must be reproducible; do not write any chapter1 artifacts.
 from nusmv_model import generate
 generated,gprops=generate(cfg)
 assert generated==model and gprops==props
 command=shutil.which('NuSMV');assert command
 runs=[]
 def run(name,text,truth,count):
  target=ev/(name+'.smv');target.write_text(text,encoding='utf-8')
  cmd=[command,'-dynamic','-df','-coi',str(target)];start=time.monotonic();stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
  r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=240)
  (ev/(name+'.log')).write_text(r.stdout+'\nSTDERR\n'+r.stderr,encoding='utf-8')
  checks=[{'formula':m.group(1).strip(),'result':m.group(2)=='true','log_line':r.stdout[:m.start()].count('\n')+1} for m in re.finditer(r'-- specification (.*?) is (true|false)',r.stdout,re.S)]
  ok=r.returncode==0 and len(checks)==count and [c['result'] for c in checks]==truth
  record={'id':name,'started_utc':stamp,'command':cmd,'seconds':round(time.monotonic()-start,3),'returncode':r.returncode,'checks':checks,'expected':truth,'status':'PASS' if ok else 'FAIL','model':target.relative_to(ROOT).as_posix(),'log':(ev/(name+'.log')).relative_to(ROOT).as_posix()}
  runs.append(record);dump(ev/'fresh_nusmv_results.json',runs);print(name,record['status'],len(checks),flush=True)
  assert ok,name
 run('v1_main_recheck',model,[True]*335,335)
 timed='Smart-Traffic-Light-Verification/02_time_based_model/timed_light.smv'
 adaptive='Smart-Traffic-Light-Verification/03_adaptive_model/adaptive_light.smv'
 # Append observation-only CTL; exact v0 contents remain a byte-identical prefix.
 run('v0_timer_added_query',read(timed)+'\n-- Added report query; no transition changes.\nCTLSPEC AG((state = NS_GREEN & timer = 1) -> AX(state = NS_YELLOW));\n',[False,True,True],3)
 run('v0_adaptive_added_queries',read(adaptive)+'\n-- Added report queries; no transition changes.\nCTLSPEC EF(time_period = EVENING_PEAK);\nCTLSPEC EF(time_period = NIGHT_LOW);\nCTLSPEC AG((state = NS_GREEN & timer = 0) -> AX(state = NS_YELLOW & timer = 5));\n',[False,False,False]+[True]*10,13)
 # NuSMV can print CTL before original LTL. Validate by formula as well as result count below.
 for name in ['negative_conflicting_green','negative_timer_reset','negative_skip_all_red']:
  run('recheck_'+name,read('chapter1/evidence/'+name+'.smv'),[False],1)
 # Fresh BDD count; no cone reduction for a count of the full model.
 cmd=[command,'-dynamic','-r','-is','-ils','-ii',str(ev/'v1_main_recheck.smv')]
 start=time.monotonic();r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=240)
 (ev/'v1_reachable_recheck.log').write_text(r.stdout+'\nSTDERR\n'+r.stderr,encoding='utf-8')
 match=re.search(r'reachable states:\s*([0-9.e+]+)',r.stdout,re.I);assert match,(r.stdout[-1000:],r.stderr)
 count=int(float(match.group(1)));assert count==86400 and r.returncode==0
 dump(ev/'v1_reachable_recheck.json',{'command':cmd,'returncode':r.returncode,'reachable_states':count,'seconds':round(time.monotonic()-start,3),'status':'PASS'})
 # Archive full, unchanged logs in a digital appendix.
 selected=[p for p in files if p.suffix.lower() in {'.log','.json','.png','.svg','.md'} and ('evidence' in p.parts or p.name in {'nusmv_results.json','excel_graph_check.log','BEFORE_AFTER_V0_V1.md'}) and 'report_delivery' not in p.parts and 'runs' not in p.parts]
 bundle=OUT/'appendix_repository';bundle.mkdir(exist_ok=True)
 for p in selected:
  dest=bundle/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
 with (OUT/'evidence_index.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.writer(f);w.writerow(['repository_path','bytes','sha256','digital_appendix_copy'])
  for k,v in inv.items():
   if 'evidence' in Path(k).parts or 'runs' in Path(k).parts or k.startswith('output/'):
    copied=bundle/k;w.writerow([k,v['bytes'],v['sha256'],copied.relative_to(OUT).as_posix() if copied.exists() else 'original repository'])
 declarations=[]
 for p in files:
  if p.suffix.lower()=='.smv':
   for n,line in enumerate(read(p.relative_to(ROOT)).splitlines(),1):
    if re.match(r'^\s*CTLSPEC\b',line):declarations.append({'file':p.relative_to(ROOT).as_posix(),'line':n,'declaration':line.strip()})
 dump(OUT/'all_ctlspec_declarations.json',declarations)
 dump(OUT/'ctl_catalog.json',[dict(p,source_line=next(i for i,l in enumerate(model.splitlines(),1) if l.startswith('CTLSPEC NAME '+p['name']+' '))) for p in props])
 assert all(sha(ROOT/k)==v['sha256'] for k,v in inv.items()),'Project content changed'
 audit={'phase':'Audit completed before report writing','date_local':'2026-10-24','timezone':'Asia/Bangkok','guide_path':r'C:\Users\Admin\Downloads\report_guide.pdf','guide_sha256':sha(Path(r'C:\Users\Admin\Downloads\report_guide.pdf')),'inventoried_files':len(inv),'all_preexisting_files_unchanged':True,'preserved_baseline_files':len(baseline),'original_v0_records':len(old),'original_v0_properties':sum(len(r['properties']) for r in old),'historical_v0_true':sum(p['result']=='true' for r in old for p in r['properties']),'historical_v0_false':sum(p['result']=='false' for r in old for p in r['properties']),'v1_property_groups':dict(collections.Counter(p['category'] for p in props)),'reproducible_model_and_properties':True,'fresh_runs':[{k:v for k,v in r.items() if k!='checks' and k!='expected'} for r in runs],'fresh_graphs':graphs,'fresh_json_ctl':{'checks':len(ctl['properties']),'overall':ctl['overall']},'ctlspec_declarations_all_artifacts':len(declarations),'missing':['Student names, IDs, class, group, GitHub URL and actual task assignments','Instructor approval for domain defect identifiers instead of CWE/CERT and actual filename convention','Course topic guide and its canonical five-step methodology not supplied','Historical v0 commands/timestamps absent from archived records; fresh supplemental queries are labeled separately','No physical traffic validation; emergency not implemented in v1; exact GUI import not manually demonstrated']}
 dump(OUT/'audit_summary.json',audit)
 from pypdf import PdfReader
 guide=PdfReader(r'C:\Users\Admin\Downloads\report_guide.pdf')
 (OUT/'report_guide_extracted.txt').write_text('\n\n'.join(f'PDF PAGE {i+1}\n'+p.extract_text() for i,p in enumerate(guide.pages)),encoding='utf-8')
 shutil.copyfile(r'C:\Users\Admin\Downloads\report_guide.pdf',OUT/'report_guide.pdf')
 print(json.dumps({k:v for k,v in audit.items() if k in ['inventoried_files','all_preexisting_files_unchanged','v1_property_groups','fresh_json_ctl']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
