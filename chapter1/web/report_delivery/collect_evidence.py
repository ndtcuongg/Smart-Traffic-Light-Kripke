from pathlib import Path
from datetime import datetime,timezone,timedelta
import sys,json,re,ast,hashlib,platform,subprocess,struct
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def normalize(s):return re.sub(r'[\s()]','',s)
def collect():
    before={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and not p.is_relative_to(HERE) and not any(x in p.parts for x in ['__pycache__','.git','.codex-tools','.chapter1-tools','.browser-profile'])}
    out=HERE/'quality_checks';out.mkdir(exist_ok=True)
    snapshot=out/'preservation_snapshot.json'
    if not snapshot.exists():snapshot.write_text(json.dumps(before,indent=2),encoding='utf-8')
    backend=read('chapter1/web/evidence/backend_tests.json');web=read('chapter1/web/evidence/browser_tests.json')
    assert backend['status']=='PASS' and backend['tests_run']==13 and not backend['failures'] and not backend['errors']
    assert web['status']=='PASS' and len(web['checks'])==32 and all(c['status']=='PASS' for c in web['checks']) and not web['errors']
    tree=ast.parse((ROOT/'chapter1/web/tests/test_backend.py').read_text(encoding='utf-8-sig'))
    methods=[n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')];assert len(methods)==13
    run='chapter1/web/runs/'+web['fresh_run'];meta=read(run+'/metadata.json');assert meta['status']=='completed'
    for p,h in meta['source_hashes'].items():assert sha(ROOT/'chapter1'/p)==h,p
    reports=read(run+'/evidence/nusmv_results.json');raw=[]
    for job in reports:
        path=run+'/evidence/'+job['name']+'.log';text=(ROOT/path).read_text(encoding='utf-8')
        parsed=[{'formula':m[1].strip(),'result':m[2]=='true'} for m in re.finditer(r'-- specification (.*?) is (true|false)',text,re.S)]
        assert parsed==job['checks'],path
        assert job['status']=='PASS' and job['returncode']==0 and not job['timeout']
        assert len(parsed)==job['expected_properties'] and all(c['result']==job['expected_truth'] for c in parsed)
        if job['expected_truth'] is False:assert 'Trace Type: Counterexample' in text
        raw.append({'file':path,'count':len(parsed),'true':sum(c['result'] for c in parsed),'false':sum(not c['result'] for c in parsed),'sha256':sha(ROOT/path)})
    assert [r['count'] for r in raw]==[335,335,4,1,1,1]
    ctl=read(run+'/ctl_results.json');doc=read('chapter1/smart_intersection.json');assert ctl['overall']=='PASS' and len(ctl['properties'])==26 and all(p['result'] and p['status']=='PASS' for p in ctl['properties'])
    assert [p['formula'] for p in ctl['properties']]==doc['suggested_ctl_formulas']
    reach=read(run+'/reachable.json');reachtext=(ROOT/run/'reachable.log').read_text(encoding='utf-8');assert reach['status']=='PASS' and reach['returncode']==0 and reach['reachable_states']==86400 and re.search(r'reachable states:\s*86400\b',reachtext)
    graphs=read(run+'/graph_results.json');assert len(graphs)==2 and all(g['status']=='PASS' and g['deadlocks']==0 and g['all_12_lamp_values_checked'] and g['all_one_second_edges_checked'] for g in graphs)
    props=read('chapter1/properties.json');main=reports[0];index={normalize(c['formula']):c for c in main['checks']};assert len(props)==335
    grouped={};prop_audit=[]
    for p in props:
        match=index[normalize(p['formula'])];assert match['result'] is True
        category='mutex' if p['name']=='physical_green_exclusion' else p['category'];grouped.setdefault(category,[]).append(p)
        prop_audit.append({**p,'category_for_record':category,'verified':True,'evidence':raw[0]['file']})
    old=read('chapter1/evidence/nusmv_results.json');assert len(old)==6
    oldctl=read('chapter1/evidence/seclab_results.json');assert len(oldctl['properties'])==26 and all(p['status']=='PASS' for p in oldctl['properties'])
    oldgraph=read('chapter1/evidence/graph_results.json')
    history=[]
    for p in (ROOT/'chapter1/web/evidence/test_history').glob('*.json'):
        d=json.loads(p.read_text(encoding='utf-8-sig'));history.append({'path':p.relative_to(ROOT).as_posix(),'status':d['status'],'checks':len(d['checks']),'passed':sum(c['status']=='PASS' for c in d['checks']),'failed':[c['name'] for c in d['checks'] if c['status']!='PASS'],'executed_at':d['executed_at']})
    sources=[('EV01','Kết quả backend','chapter1/web/evidence/backend_tests.json'),('EV02','Kết quả Edge','chapter1/web/evidence/browser_tests.json'),('EV03','Script backend','chapter1/web/tests/test_backend.py'),('EV04','Script Edge','chapter1/web/tests/browser.mjs'),('EV05','Thông tin lượt đã chọn',run+'/metadata.json'),('EV06','Stdout tiến trình',run+'/console.log'),('EV07','CTL mặc định',raw[0]['file']),('EV08','CTL giờ bất kỳ',raw[1]['file']),('EV09','EF bốn khung giờ',raw[2]['file']),('EV10','Kết quả NuSMV có cấu trúc',run+'/evidence/nusmv_results.json'),('EV11','Kết quả CTL JSON',run+'/ctl_results.json'),('EV12','Stdout đếm trạng thái',run+'/reachable.log'),('EV13','Lệnh đếm trạng thái',run+'/reachable.json'),('EV14','Kiểm hai đồ thị JSON',run+'/graph_results.json'),('EV15','Phản ví dụ đồng xanh',raw[3]['file']),('EV16','Phản ví dụ sai timer',raw[4]['file']),('EV17','Phản ví dụ bỏ ALL_RED',raw[5]['file']),('EV18','335 thuộc tính có tên','chapter1/properties.json'),('EV19','Mô hình v1 chính thức','chapter1/smart_intersection.smv'),('EV20','Cấu hình nguồn','chapter1/config.json'),('EV21','Bộ kiểm CTL độc lập','chapter1/web/ctl_checker.py'),('EV22','Script kiểm NuSMV','chapter1/verify_nusmv.py'),('EV23','Worker độc lập','chapter1/web/verification_worker.py'),('EV24','Kiểm đồ thị/ràng buộc','chapter1/verify_graph.py'),('EV25','Audit Before/After','chapter1/evidence/before_after_audit.json'),('EV26','Bản ghi CTL JSON lịch sử','chapter1/evidence/seclab_results.json'),('EV27','Bản ghi kiểm đồ thị lịch sử','chapter1/evidence/graph_results.json'),('EV28','Audit bảo toàn web','chapter1/web/evidence/final_audit.json'),('EV29','Báo cáo triển khai','chapter1/web/IMPLEMENTATION_REPORT_VI.md'),('EV30','Ánh xạ báo cáo học phần','chapter1/web/REPORT_SUPPORT_VI.md')]
    if history:sources.append(('EV31','Lần thử trung gian FAIL',history[0]['path']))
    evidence=[{'id':i,'title':t,'path':p,'sha256':sha(ROOT/p),'bytes':(ROOT/p).stat().st_size} for i,t,p in sources]
    images=[]
    for i,p in enumerate(sorted((ROOT/'chapter1/web/evidence/screenshots').glob('*.png')),1):
        data=p.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n';width,height=struct.unpack('>II',data[16:24]);images.append({'id':f'IMG{i:02d}','path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'width':width,'height':height})
    assert len(images)==7
    audit={'document_date':'2026-10-23','selected_run':run,'backend':backend,'backend_methods':methods,'browser':web,'metadata':meta,'raw_log_checks':raw,'ctl':ctl,'reachable':reach,'graphs':graphs,'property_groups':grouped,'properties':prop_audit,'history':history,'evidence':evidence,'images':images,'old_graph_summary':{'boundary_cases':len(oldgraph['boundary_tests']),'duration_cases':len(oldgraph['exact_duration_tests']),'invalid_configuration_tests':oldgraph['invalid_configuration_tests'],'overall':oldgraph['overall']},'environment_now':{'python':platform.python_version(),'platform':platform.platform(),'node':subprocess.check_output(['node','--version'],text=True).strip()},'limitations':['Backend chỉ lưu tổng hợp, không stdout/thời điểm/skip riêng từng ca.','Không có biên bản kiểm thử thủ công có người ký.','Không có bằng chứng kiểm LTL.','Bản ghi Edge không lưu chính xác phiên bản trình duyệt/OS/CPU/RAM lúc chạy.'],'product_checks_rerun_for_this_document':False}
    (out/'evidence_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'backend':13,'browser':32,'nusmv_raw':raw,'json_ctl':26,'selected_run':run,'source_files_snapshotted':len(before)},ensure_ascii=True))
    return audit
if __name__=='__main__':collect()
