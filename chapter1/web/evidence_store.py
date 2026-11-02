"""Read genuine archived evidence and describe it without manufacturing checker results."""
from pathlib import Path
import re,json
from domain import ROOT,CHAPTER,HERE,read_json,digest,normal_formula,describe_property,CATEGORY_VI

class Evidence:
    def __init__(self,model):
        self.model=model
        self.archived=read_json(CHAPTER/'evidence/nusmv_results.json')
        self.seclab=read_json(CHAPTER/'evidence/seclab_results.json')
        self.reachable=read_json(CHAPTER/'evidence/nusmv_reachable.json')
        self.graph=read_json(CHAPTER/'evidence/graph_results.json')
        expected=model.audit['evidence_sha256']
        self.changed=[p for p,h in expected.items() if not (ROOT/p).is_file() or digest(ROOT/p)!=h]
        self.integrity=model.integrity and model.generator_matches and not self.changed
        self.version=re.search(r'NuSMV ([0-9.]+)',(CHAPTER/'evidence/nusmv_main.log').read_text(encoding='utf-8'))[1]
    def bundle(self,run_dir=None):
        if run_dir:
            meta=read_json(run_dir/'metadata.json')
            if meta['status']!='completed':raise ValueError('Lượt kiểm chứng chưa hoàn tất; không được coi là đã xác minh.')
            reports=read_json(run_dir/'evidence/nusmv_results.json');ctl=read_json(run_dir/'ctl_results.json')
            count=read_json(run_dir/'reachable.json');prefix=run_dir.relative_to(ROOT).as_posix()+'/evidence/'
            kind='executed';tool='Bộ kiểm CTL độc lập bằng Python';started=meta['started_at'];ident=run_dir.name
        else:
            reports=self.archived;ctl=self.seclab;count=self.reachable;prefix='chapter1/evidence/'
            kind='recorded';tool='SecLabFramework · bản ghi lịch sử';started=None;ident='recorded'
        main=next(r for r in reports if r['name']=='nusmv_main');any_start=next(r for r in reports if r['name']=='nusmv_any_start_time')
        byformula={normal_formula(c['formula']):c for c in main['checks']}
        rows=[]
        for prop in self.model.props:
            match=byformula.get(normal_formula(prop['formula']));value=match['result'] if match else None
            category='mutex' if prop['name']=='physical_green_exclusion' else prop['category']
            rows.append({'id':prop['name'],'name':prop['name'],'formula':prop['formula'],'category':category,'category_vi':CATEGORY_VI[category],
                'explanation':describe_property(prop['name'],prop['formula']),'result':value,'status':'PASS' if value is True else 'FAIL' if value is False else 'UNVERIFIED',
                'tool':'NuSMV '+self.version+' · BDD/CTL','source_kind':kind,'log':prefix+'nusmv_main.log','counterexample':None})
        ctl_rows=[]
        for i,item in enumerate(ctl['properties']):
            result=item.get('result',item.get('status')=='PASS')
            ctl_rows.append({'id':'json_'+str(i+1),'name':'CTL JSON '+str(i+1),'formula':item['formula'],
                'explanation':describe_property('',item['formula']),'result':result,'status':'PASS' if result else 'FAIL',
                'category':'json','category_vi':'Kripke từ JSON','tool':tool,'source_kind':kind,
                'satisfying_states':item.get('satisfying_states'),'log':(run_dir.relative_to(ROOT).as_posix()+'/ctl_results.json') if run_dir else 'chapter1/evidence/seclab_results.json'})
        negative=[]
        for r in reports:
            if not r['name'].startswith('negative_'):continue
            titles={'negative_conflicting_green':'Cố ý cho hai luồng cùng xanh','negative_timer_reset':'Cố ý nạp timer sai','negative_skip_all_red':'Cố ý bỏ pha đỏ toàn hướng'}
            negative.append({'id':r['name'],'title':titles[r['name']],'formula':r['checks'][0]['formula'],
                'property_result':r['checks'][0]['result'],'harness_status':r['status'],'source_kind':kind,'tool':'NuSMV '+self.version,
                'log':prefix+r['counterexample_log'],'model':prefix+r['name']+'.smv'})
        period=next(r for r in reports if r['name']=='nusmv_period_reachability')
        return {'id':ident,'kind':kind,'started_at':started,'integrity':self.integrity if not run_dir else meta['preservation']['status']=='PASS',
            'rows':rows,'ctl_rows':ctl_rows,'negative':negative,
            'summary':{'passed':sum(r['result'] is True for r in rows),'total':len(rows),'failed':sum(r['result'] is False for r in rows),
                'any_start_passed':sum(c['result'] is True for c in any_start['checks']),'any_start_total':len(any_start['checks']),
                'ctl_passed':sum(r['result'] is True for r in ctl_rows),'ctl_total':len(ctl_rows),
                'reachable_states':count.get('reachable_states'),'reachable_status':count['status'],
                'periods_passed':sum(c['result'] is True for c in period['checks']),'periods_total':len(period['checks'])},
            'reachable_log':(run_dir.relative_to(ROOT).as_posix()+'/reachable.log') if run_dir else 'chapter1/evidence/nusmv_reachable.log',
            'changed_evidence':self.changed if not run_dir else []}
    def catalog(self):
        items=[
        ('Mô hình và cấu hình','chapter1/smart_intersection.smv','Mô hình v1 chính thức'),
        ('Mô hình và cấu hình','chapter1/config.json','Tham số thời gian nguồn'),
        ('Mô hình và cấu hình','chapter1/properties.json','Danh mục CTL đặt tên'),
        ('Mô hình và cấu hình','chapter1/smart_intersection.json','Kripke có timer, chiếu khung giờ'),
        ('Mô hình và cấu hình','chapter1/smart_intersection_exact.json','Kripke đồng hồ chính xác · tệp lớn'),
        ('Kiểm chứng đã lưu','chapter1/evidence/nusmv_main.log','335 CTL · giờ cố định'),
        ('Kiểm chứng đã lưu','chapter1/evidence/nusmv_any_start_time.log','335 CTL · giờ khởi tạo bất kỳ'),
        ('Kiểm chứng đã lưu','chapter1/evidence/nusmv_period_reachability.log','Khả đạt bốn khung giờ'),
        ('Kiểm chứng đã lưu','chapter1/evidence/nusmv_reachable.log','Số trạng thái đạt được bằng BDD'),
        ('Kiểm chứng đã lưu','chapter1/evidence/nusmv_results.json','Kết quả NuSMV có cấu trúc'),
        ('Kiểm chứng đã lưu','chapter1/evidence/seclab_results.json','CTL JSON · bản ghi công cụ cũ'),
        ('Kiểm chứng đã lưu','chapter1/evidence/graph_results.json','Kiểm tra JSON và ranh giới'),
        ('Đối chứng cố ý lỗi','chapter1/evidence/negative_conflicting_green.log','Phản ví dụ xung đột xanh'),
        ('Đối chứng cố ý lỗi','chapter1/evidence/negative_timer_reset.log','Phản ví dụ reset timer'),
        ('Đối chứng cố ý lỗi','chapter1/evidence/negative_skip_all_red.log','Phản ví dụ bỏ clearance'),
        ('Báo cáo và so sánh','chapter1/BEFORE_AFTER_V0_V1.md','Đối chiếu đủ 14 nguồn v0'),
        ('Báo cáo và so sánh','chapter1/evidence/before_after_audit.json','Hash và nguồn bằng chứng Before/After'),
        ('Báo cáo và so sánh','chapter1/web/REPORT_SUPPORT_VI.md','Hỗ trợ tám phần báo cáo học phần'),
        ('Báo cáo và so sánh','chapter1/web/IMPLEMENTATION_REPORT_VI.md','Báo cáo triển khai và kiểm thử web')]
        return [{'group':g,'path':p,'title':t,'exists':(ROOT/p).is_file(),'bytes':(ROOT/p).stat().st_size if (ROOT/p).is_file() else None,
            'sha256':digest(ROOT/p) if (ROOT/p).is_file() else None} for g,p,t in items]
