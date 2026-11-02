"""Audit/document existing evidence only; never runs or writes a .smv model."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parent.parent
HERE=ROOT/'chapter1'
DOC=HERE/'BEFORE_AFTER_V0_V1.md'
PROOF_NAMES=[
['advance_NS_GREEN','advance_NS_YELLOW','clearance_all_red','recurring_green_n','recurring_green_e'],
['timer_bounds','countdown_2','countdown_30','hold_NS_GREEN','advance_NS_GREEN','reset_NS_GREEN_NORMAL'],
['reset_NS_GREEN_NORMAL','reset_ALL_RED_NS_TO_EW_EVENING_PEAK','reset_ALL_RED_EW_TO_NS_NIGHT_LOW','latch_NORMAL','clock_second_59','clock_hour_tick_23'],
['physical_green_exclusion','one_hot_n','synchronized_green','clearance_all_red'],
['physical_green_exclusion','one_hot_n','synchronized_green','clearance_all_red','deadlock_free'],
['physical_green_exclusion','recurring_green_n','deadlock_free','advance_NS_YELLOW'],
['hold_NS_GREEN','advance_NS_GREEN','advance_NS_YELLOW','yellow_ns_other_red','physical_green_exclusion'],
['yellow_ns_other_red','yellow_ew_other_red','clearance_all_red','advance_NS_YELLOW','recurring_green_n','recurring_green_e'],
['hold_NS_GREEN','advance_NS_GREEN','advance_NS_YELLOW','clearance_all_red'],
['hold_NS_GREEN','advance_NS_GREEN','advance_NS_YELLOW','physical_green_exclusion'],
['recurring_green_n','recurring_green_e','physical_green_exclusion'],
['advance_NS_GREEN','advance_NS_YELLOW','physical_green_exclusion','deadlock_free'],
['hold_NS_GREEN','advance_NS_GREEN','advance_NS_YELLOW','physical_green_exclusion'],
['physical_green_exclusion','one_hot_n','synchronized_green']]
CLASSIFICATIONS=[
'Giới hạn mô hình bốn pha',
'Ngữ nghĩa timer=0 khác yêu cầu đúng D giây',
'Lỗi logic thích nghi hiện hữu, nguồn không đánh dấu fault-injection',
'Mẫu lỗi khởi tạo theo tên/vai trò init_bug',
'Giới hạn safety enum, không có lỗi cấy được phát hiện',
'File khung, chưa có thuộc tính hoặc fault thực thi',
'Fault chuyển tiếp có chủ đích, có chú thích nguồn',
'Hạn chế thiết kế/tập yêu cầu, không đánh dấu fault-injection',
'Fault chuyển tiếp có chủ đích, có BUG INTRODUCED HERE',
'Bản sửa đối chứng đã TRUE, không phải lỗi cạnh còn tồn tại',
'Ví dụ emergency, chức năng chưa được tích hợp vào v1',
'Fixture chưa có SPEC',
'Fixture chưa có SPEC',
'Ví dụ đăng nhập ngoài nghiệp vụ giao lộ']
EXPECTED_FILES=[
'01_basic_model/traffic_light_model.smv','02_time_based_model/timed_light.smv','03_adaptive_model/adaptive_light.smv',
'03_bmc/init_bug.smv','03_bmc/traffic_light_bmc.smv','03_bmc/traffic_light_bmc_bug.smv','03_bmc/transition_bug.smv',
'04_verification/safety_liveness.smv','05_bug_analysis/transition_bug.smv','05_bug_analysis/transition_bug_fixed.smv',
'06_extension/emergency_mode.smv','test/traffic_light2.smv','test/traffic_light_basic.smv']
EXPECTED_FILES=['Smart-Traffic-Light-Verification/'+p for p in EXPECTED_FILES]+['test.smv']
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def norm(value):return re.sub(r'[\s()]','',value)
def smv_hashes():
    return {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*.smv') if p.is_file() and not any(x in p.parts for x in ('.chapter1-tools','.codex-tools'))}

def main():
    hashes=smv_hashes();preserved=read('chapter1/evidence/preserved_work.json');manifest=read('chapter1/evidence/artifact_manifest.json')
    for rel,digest in hashes.items():
        previous=preserved[rel]['sha256'] if rel in preserved else manifest[rel]['sha256']
        assert digest==previous,rel
    original=read('output/nusmv_results.json');current=read('chapter1/evidence/nusmv_results.json');properties=read('chapter1/properties.json')
    assert [r['file'] for r in original]==EXPECTED_FILES
    assert len(original)==len(PROOF_NAMES)==len(CLASSIFICATIONS)==14
    assert sum(len(r['properties']) for r in original)==28
    assert sum(p['result']=='false' for r in original for p in r['properties'])==3
    official='chapter1/smart_intersection.smv'
    assert hashes[official]==hashes['chapter1/evidence/nusmv_main.smv']
    positives={r['name']:r for r in current if not r['name'].startswith('negative_')}
    assert set(positives)=={'nusmv_main','nusmv_any_start_time','nusmv_period_reachability'}
    for name,r in positives.items():
        assert r['returncode']==0 and r['timeout'] is False
        assert len(r['checks'])==r['expected_properties']==(4 if name=='nusmv_period_reachability' else 335)
        assert all(c['result'] is True for c in r['checks'])
    byname={r['name']:r for r in properties};used=set();mapping=[]
    dest=HERE/'evidence/before_v0_logs';dest.mkdir(exist_ok=True)
    text=DOC.read_text(encoding='utf-8-sig')
    sections=re.split(r'(?m)^### (V0-\d\d) — ',text)[1:]
    assert sections[::2]==[f'V0-{i:02d}' for i in range(1,15)]
    for i,r in enumerate(original):
        ident=f'V0-{i+1:02d}';rel=r['file'];assert hashes[rel]==preserved[rel]['sha256']==r['sha256']
        assert not r['stderr'],'Unexpected stderr; preserve it explicitly before documenting'
        parsed=[(m.group(1),m.group(2)) for m in re.finditer(r'-- specification (.*?) is (true|false)',r['stdout'],re.S)]
        assert [(norm(f),v) for f,v in parsed]==[(norm(p['formula']),p['result']) for p in r['properties']]
        filename=ident+'_'+Path(rel).stem+'.stdout.log';out=dest/filename;raw=r['stdout'].encode('utf-8')
        if out.exists():assert out.read_bytes()==raw,'Existing extraction differs: '+str(out)
        else:out.write_bytes(raw)
        body=sections[i*2+1].split('\n## ',1)[0]
        assert len(re.findall(r'(?m)^[1-5]\. \*\*',body))==5,(ident,'Missing mapping item')
        for name in PROOF_NAMES[i]:
            assert name in byname and '`'+name+'`' in body,(ident,name)
            for job in ('nusmv_main','nusmv_any_start_time'):
                assert any(c['result'] and norm(c['formula'])==norm(byname[name]['formula']) for c in positives[job]['checks']),(ident,name,job)
            used.add(name)
        mapping.append({'id':ident,'source_file':rel,'classification':CLASSIFICATIONS[i],'source_sha256':hashes[rel],
            'source_matches_preserved_work':True,'source_matches_historical_verification_hash':True,
            'historical_json':'output/nusmv_results.json','historical_array_index':i,
            'historical_exit_code':r['returncode'],'historical_properties':r['properties'],
            'historical_stdout_extraction':out.relative_to(ROOT).as_posix(),'stdout_sha256':sha(out),
            'stdout_is_exact_archived_utf8_string':out.read_bytes()==raw,'stderr_in_archive':r['stderr'],
            'v1_property_names':PROOF_NAMES[i],'v1_named_properties_found_true_in_both_runs':True,
            'documentation_section':ident})
    catalog=['| Tên thuộc tính | CTL đã đối chiếu TRUE trong E1 và E1A |','|---|---|']
    for p in properties:
        if p['name'] in used:
            formula=p['formula'].replace('|',r'\|')
            catalog.append(f'| `{p["name"]}` | `{formula}` |')
    pattern=r'<!-- BEGIN VERIFIED_PROPERTY_CATALOG -->.*?<!-- END VERIFIED_PROPERTY_CATALOG -->'
    replacement='<!-- BEGIN VERIFIED_PROPERTY_CATALOG -->\n'+'\n'.join(catalog)+'\n<!-- END VERIFIED_PROPERTY_CATALOG -->'
    assert len(re.findall(pattern,text,re.S))==1
    text=re.sub(pattern,lambda _:replacement,text,flags=re.S)
    DOC.write_text(text,encoding='utf-8')
    faults=[]
    for r in current:
        if not r['name'].startswith('negative_'):continue
        assert len(r['checks'])==1 and r['checks'][0]['result'] is False and r['expected_truth'] is False and r['status']=='PASS'
        faults.append({'name':r['name'],'actual_property_result':False,'expected_property_result':False,'harness_status':r['status'],
            'model':'chapter1/evidence/'+r['name']+'.smv','log':'chapter1/evidence/'+r['counterexample_log']})
    assert len(faults)==3
    evidence=['output/nusmv_results.json','output/excel_graph_check.smv','output/excel_graph_check.log','output/validation.json',
        'chapter1/properties.json','chapter1/evidence/nusmv_results.json','chapter1/evidence/nusmv_main.log',
        'chapter1/evidence/nusmv_any_start_time.log','chapter1/evidence/nusmv_period_reachability.log',
        'chapter1/evidence/nusmv_reachable.json','chapter1/evidence/graph_results.json','chapter1/evidence/build_summary.json',
        'chapter1/evidence/seclab_results.json']+[f['log'] for f in faults]
    missing=[]
    for target in re.findall(r'\]\(([^)]+)\)',text):
        if target.startswith(('http:','https:','#')) or target=='evidence/before_after_audit.json':continue
        if not (HERE/target.split('#',1)[0]).exists():missing.append(target)
    assert not missing,missing
    assert hashes==smv_hashes(),'A .smv file changed during documentation'
    audit={'documentation_date':'2026-10-22','verification_rerun':False,'documentation_only':True,
        'original_source_count':14,'historical_generated_smv_also_preserved':'output/excel_graph_check.smv',
        'all_existing_smv_files_preserved':len(hashes),'all_existing_smv_hashes':hashes,
        'official_after_implementation':official,'official_after_sha256':hashes[official],
        'official_after_matches_prior_manifest':True,'official_after_matches_verified_snapshot':True,
        'mapping':mapping,'v1_positive_runs':{n:{'properties':len(r['checks']),'all_true':True} for n,r in positives.items()},
        'v1_intentionally_injected_faults':faults,'evidence_sha256':{p:sha(ROOT/p) for p in evidence},
        'documentation_sha256':sha(DOC),'local_document_links':'PASS','mapping_items_per_original':5,
        'unique_v1_properties_cross_referenced':len(used)}
    (HERE/'evidence/before_after_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'document':'chapter1/BEFORE_AFTER_V0_V1.md','original_files':14,'all_existing_smv_unchanged':len(hashes),
        'stdout_extractions':14,'v1_properties_cross_referenced':len(used),'verification_rerun':False},indent=2))

if __name__=='__main__':main()
