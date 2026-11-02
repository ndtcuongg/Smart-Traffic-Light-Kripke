"""Isolated execution of existing Chapter 1 NuSMV verification; no original evidence writes."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,shutil,subprocess,re,time
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE.parent))
from domain import CHAPTER,ROOT,read_json,digest,verify_preservation
from ctl_checker import check_graph

def now():return datetime.now(timezone.utc).isoformat()
def execute(run_dir):
    run_dir=run_dir.resolve()
    if not run_dir.is_relative_to(HERE):raise ValueError('Thư mục lượt chạy phải ở trong chapter1/web.')
    meta=read_json(run_dir/'metadata.json');baseline=read_json(HERE/'evidence/preservation_baseline.json')
    meta['started_at']=now();meta['status']='running';meta['tools']=['NuSMV BDD/CTL','Bộ kiểm CTL độc lập bằng Python']
    def save(): (run_dir/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    save()
    try:
        import verify_nusmv as existing
        from intersection import Config
        from nusmv_model import generate
        if not shutil.which('NuSMV'):raise RuntimeError('Không tìm thấy NuSMV trên PATH.')
        source=CHAPTER/'smart_intersection.smv';cfg=Config(CHAPTER/'config.json')
        if generate(cfg)[0]!=source.read_text(encoding='utf-8'):raise RuntimeError('Cấu hình/mã sinh không khớp mô hình v1; không chạy bằng chứng sai nguồn.')
        (run_dir/'evidence').mkdir(exist_ok=True)
        shutil.copyfile(CHAPTER/'config.json',run_dir/'config.json')
        shutil.copyfile(source,run_dir/'smart_intersection.smv')
        meta['source_hashes']={p:digest(CHAPTER/p) for p in ['smart_intersection.smv','config.json','properties.json','smart_intersection.json']}
        save();print('GIAIDOAN: Đang chạy lại bộ NuSMV hiện có trong thư mục độc lập.',flush=True)
        existing.HERE=run_dir;existing.EXE=shutil.which('NuSMV');existing.verify()
        print('GIAIDOAN: Đang đếm trạng thái đạt được bằng NuSMV BDD.',flush=True)
        command=[existing.EXE,'-dynamic','-r','-is','-ils','-ii',str(run_dir/'smart_intersection.smv')]
        tick=time.perf_counter();p=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=75)
        (run_dir/'reachable.log').write_text(p.stdout+'\nSTDERR\n'+p.stderr,encoding='utf-8')
        match=re.search(r'reachable states:\s*(\d+)',p.stdout,re.I);expected=read_json(CHAPTER/'evidence/build_summary.json')['concrete_states']
        reachable={'command':command,'returncode':p.returncode,'seconds':time.perf_counter()-tick,'reachable_states':int(match[1]) if match else None,
            'status':'PASS' if p.returncode==0 and match and int(match[1])==expected else 'FAIL'}
        (run_dir/'reachable.json').write_text(json.dumps(reachable,indent=2),encoding='utf-8')
        if reachable['status']!='PASS':raise RuntimeError('Phép đếm trạng thái không khớp bằng chứng nguồn.')
        print('GIAIDOAN: Đang kiểm CTL JSON độc lập, không dùng SecLabFramework.',flush=True)
        ctl=check_graph(read_json(CHAPTER/'smart_intersection.json'))
        (run_dir/'ctl_results.json').write_text(json.dumps(ctl,ensure_ascii=False,indent=2),encoding='utf-8')
        if ctl['overall']!='PASS':raise RuntimeError('Bộ kiểm CTL JSON phát hiện thuộc tính không đúng.')
        from verify_graph import verify_file
        print('GIAIDOAN: Đang đối chiếu mọi cạnh và 12 đèn của hai JSON.',flush=True)
        graphs=[verify_file(CHAPTER/p,cfg) for p in ['smart_intersection.json','smart_intersection_exact.json']]
        (run_dir/'graph_results.json').write_text(json.dumps(graphs,ensure_ascii=False,indent=2),encoding='utf-8')
        meta['preservation']=verify_preservation(baseline)
        if meta['preservation']['status']!='PASS':raise RuntimeError('Một tệp dự án gốc đã thay đổi trong lượt chạy.')
        meta['status']='completed';meta['stage']='Kiểm chứng hoàn tất; log và kết quả đã được lưu riêng.';meta['console']=(run_dir/'console.log').relative_to(ROOT).as_posix();meta['finished_at']=now();save()
        print('HOANTAT: Kiểm chứng Chương 1 hoàn tất; mô hình và bằng chứng cũ giữ nguyên.',flush=True)
    except Exception as exc:
        meta['status']='error';meta['error']=str(exc);meta['finished_at']=now();meta['preservation']=verify_preservation(baseline);save()
        print('LOI: '+str(exc),flush=True);raise

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');execute(Path(sys.argv[1]))
