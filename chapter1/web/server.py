"""Local-only Chapter 1 web app. Launch: python chapter1/web/server.py"""
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from http.cookies import SimpleCookie
from datetime import datetime,timezone
import argparse,json,threading,secrets,uuid,sys,subprocess,shutil,mimetypes,signal
from domain import HERE,CHAPTER,ROOT,Model,read_json,protected_files,verify_preservation,initial,step,abstract,sid,PHASES,PERIODS,PHASE_VI,PERIOD_VI,POLE_VI,COLOR_VI,CATEGORY_VI,seconds,digest
from evidence_store import Evidence

class Application:
    def __init__(self,data_dir=None):
        self.model=Model();self.evidence=Evidence(self.model)
        self.data_dir=Path(data_dir or HERE/'runs').resolve()
        if not self.data_dir.is_relative_to(HERE):raise ValueError('Thư mục dữ liệu phải ở trong chapter1/web.')
        self.data_dir.mkdir(parents=True,exist_ok=True)
        baseline=HERE/'evidence/preservation_baseline.json'
        if not baseline.exists():baseline.write_text(json.dumps(protected_files(),indent=2),encoding='utf-8')
        self.baseline=read_json(baseline);self.token=secrets.token_urlsafe(24)
        self.sessions={};self.sessions_lock=threading.Lock();self.jobs={};self.jobs_lock=threading.Lock()
        self.comparison_rows=self.model.comparisons()
        self.allowed=set(self.baseline)
        for row in self.comparison_rows:self.allowed.add(row['historical_stdout_extraction'])
        self.port=None
    def session(self,cookie):
        key=cookie if cookie and cookie in self.sessions else secrets.token_hex(20)
        with self.sessions_lock:
            if key not in self.sessions:self.sessions[key]={'state':initial(self.model.config),'lock':threading.Lock(),'origin_clock':self.model.config.clock,'warmup':0}
        return key,self.sessions[key]
    def artifact(self,name):
        path=(ROOT/name).resolve()
        if not path.is_relative_to(ROOT):raise ValueError('Đường dẫn không được phép.')
        allowed=name in self.allowed
        if path.is_relative_to(self.data_dir):allowed=True
        if path.is_relative_to(HERE/'evidence') and path.suffix.lower() in ('.json','.log','.png','.svg','.md'):allowed=True
        if path.parent==HERE and path.name in ('README.md','REPORT_SUPPORT_VI.md','IMPLEMENTATION_REPORT_VI.md'):allowed=True
        if not allowed or not path.is_file():raise ValueError('Không tìm thấy tệp bằng chứng được phép.')
        return path
    def bootstrap(self,session):
        with session['lock']:state=self.model.serialize(session['state'])
        return {'token':self.token,'state':state,'config':self.model.config.raw,
            'names':{'phases':PHASE_VI,'periods':PERIOD_VI,'poles':POLE_VI,'colors':COLOR_VI,'categories':CATEGORY_VI},
            'phases':PHASES,'periods':PERIODS,'graphs':self.model.summary,'source_hashes':self.model.source_hashes,
            'integrity':self.evidence.integrity,'generator_matches_model':self.model.generator_matches,
            'can_verify':bool(shutil.which('NuSMV')) and self.model.generator_matches and self.evidence.integrity,
            'verification_unavailable_reason':None if shutil.which('NuSMV') else 'Chưa tìm thấy NuSMV trên PATH. Vẫn có thể xem bằng chứng đã lưu.',
            'recorded_summary':self.evidence.bundle()['summary'],'boundary_times':['06:59:59','08:59:59','15:59:59','18:59:59','21:59:59','23:59:59']}
    def start_job(self):
        if not self.model.generator_matches:raise ValueError('Nguồn Python/cấu hình không khớp mô hình v1. Chưa thể chạy kiểm chứng.')
        if not shutil.which('NuSMV'):raise ValueError('Không tìm thấy NuSMV trên PATH; đây không phải một lượt kiểm chứng mới.')
        with self.jobs_lock:
            active=next((j for j in self.jobs.values() if j['status'] in ('queued','running')),None)
            if active:return active
            ident=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+uuid.uuid4().hex[:8]
            folder=self.data_dir/ident;folder.mkdir()
            meta={'id':ident,'status':'queued','requested_at':datetime.now(timezone.utc).isoformat(),'started_at':None,'stage':'Đang chuẩn bị kiểm chứng Chương 1.'}
            (folder/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
            self.jobs[ident]=dict(meta)
            threading.Thread(target=self._execute_job,args=(ident,folder),daemon=True).start()
            return dict(meta)
    def _execute_job(self,ident,folder):
        self.jobs[ident]['status']='running'
        options={'creationflags':subprocess.CREATE_NO_WINDOW} if sys.platform=='win32' else {}
        command=[sys.executable,'-u',str(HERE/'verification_worker.py'),str(folder)]
        try:
            with (folder/'console.log').open('w',encoding='utf-8') as log:
                proc=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',**options)
                for line in proc.stdout:
                    log.write(line);log.flush()
                    if line.startswith(('GIAIDOAN:','HOANTAT:','LOI:')):self.jobs[ident]['stage']=line.split(':',1)[1].strip()
                code=proc.wait()
            meta=read_json(folder/'metadata.json')
            if code!=0 or meta.get('status')!='completed':meta['status']='error';meta.setdefault('error','Tiến trình kiểm chứng chưa hoàn tất.')
            meta['returncode']=code;meta['console']=folder.relative_to(ROOT).as_posix()+'/console.log'
            self.jobs[ident]=meta
        except Exception as exc:self.jobs[ident].update(status='error',error=str(exc))
    def job(self,ident):
        if not re_safe_id(ident):raise ValueError('Mã lượt chạy không hợp lệ.')
        if ident in self.jobs:return self.jobs[ident]
        p=self.data_dir/ident/'metadata.json'
        if not p.is_file():raise ValueError('Không tìm thấy lượt kiểm chứng.')
        meta=read_json(p)
        if meta.get('status') in ('running','queued'):meta['status']='error';meta['error']='Lượt trước bị gián đoạn; không coi là đã kiểm chứng.'
        return meta
    def job_list(self):
        result=[]
        for folder in sorted(self.data_dir.iterdir(),reverse=True):
            if folder.is_dir() and(folder/'metadata.json').is_file():result.append(self.job(folder.name))
        return result

def re_safe_id(value):
    import re
    return bool(re.fullmatch(r'\d{8}T\d{6}Z_[a-f0-9]{8}',value))

class Handler(BaseHTTPRequestHandler):
    server_version='GiaoLo/1'
    def log_message(self,format,*args):pass
    @property
    def app(self):return self.server.app
    def context(self):
        cookie=SimpleCookie()
        try:cookie.load(self.headers.get('Cookie',''))
        except Exception:pass
        key=cookie.get('giao_lo_session');self.session_id,self.current_session=self.app.session(key.value if key else None)
    def send(self,status,value):
        raw=json.dumps(value,ensure_ascii=False).encode('utf-8');self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(raw)))
        self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Set-Cookie','giao_lo_session='+self.session_id+'; HttpOnly; SameSite=Strict; Path=/')
        self.end_headers();self.wfile.write(raw)
    def fail(self,error,status=400):self.send(status,{'error':str(error)})
    def authorized(self):
        origin=self.headers.get('Origin')
        if origin and origin not in ('http://127.0.0.1:'+str(self.server.server_port),'http://localhost:'+str(self.server.server_port)):
            raise ValueError('Yêu cầu không đến từ giao diện cục bộ.')
        if self.headers.get('X-Demo-Token')!=self.app.token:raise ValueError('Thiếu mã phiên của ứng dụng cục bộ.')
    def do_GET(self):
        self.context();url=urlparse(self.path);q={k:v[0] for k,v in parse_qs(url.query).items()};route=url.path
        try:
            if route=='/api/bootstrap':return self.send(200,self.app.bootstrap(self.current_session))
            if route=='/api/simulation':
                with self.current_session['lock']:value=self.app.model.serialize(self.current_session['state'])
                return self.send(200,value)
            if route=='/api/verification':
                ident=q.get('run','recorded')
                if ident=='recorded':return self.send(200,self.app.evidence.bundle())
                self.app.job(ident);return self.send(200,self.app.evidence.bundle(self.app.data_dir/ident))
            if route=='/api/jobs':return self.send(200,{'items':self.app.job_list()})
            if route.startswith('/api/jobs/'):return self.send(200,self.app.job(route.rsplit('/',1)[1]))
            if route=='/api/comparisons':return self.send(200,{'items':self.app.comparison_rows,'official_model':'chapter1/smart_intersection.smv','v1_source':(CHAPTER/'smart_intersection.smv').read_text(encoding='utf-8').split('-- PROPERTIES')[0]})
            if route=='/api/evidence':return self.send(200,{'items':self.app.evidence.catalog(),'source_integrity':self.app.evidence.integrity})
            if route=='/api/kripke/states':
                mode=q.get('mode','abstract')
                if mode not in ('abstract','exact'):raise ValueError('Loại đồ thị không hợp lệ.')
                return self.send(200,self.app.model.search(mode,q.get('q','')[:150],q.get('phase',''),q.get('period',''),max(0,int(q.get('offset',0))),min(40,max(1,int(q.get('limit',20))))))
            if route=='/api/kripke/state':return self.send(200,self.app.model.state_item(q.get('id',''),q.get('mode','abstract')))
            if route=='/api/kripke/current':
                with self.current_session['lock']:s=self.current_session['state']
                mode=q.get('mode','exact');ident=sid(s if mode=='exact' else abstract(s))
                return self.send(200,self.app.model.state_item(ident,mode,allow_live=True))
            if route in ('/api/artifact','/api/download'):
                path=self.app.artifact(q.get('path',''))
                if route=='/api/download':
                    self.send_response(200);self.send_header('Content-Type','application/octet-stream');self.send_header('Content-Disposition','attachment; filename="'+path.name+'"');self.send_header('Content-Length',str(path.stat().st_size));self.end_headers()
                    with path.open('rb') as source:shutil.copyfileobj(source,self.wfile)
                    return
                raw=path.read_bytes();cut=len(raw)>250000
                return self.send(200,{'path':path.relative_to(ROOT).as_posix(),'text':raw[:250000].decode('utf-8-sig',errors='replace'),'truncated':cut,'bytes':len(raw),'sha256':digest(path)})
            if route=='/api/preservation':return self.send(200,verify_preservation(self.app.baseline))
            static={'/':'index.html','/index.html':'index.html','/app.js':'app.js','/styles.css':'styles.css','/favicon.svg':'favicon.svg'}
            if route not in static:return self.fail('Không tìm thấy trang yêu cầu.',404)
            path=HERE/'static'/static[route]
            if not path.is_file():return self.fail('Giao diện đang được chuẩn bị.',503)
            raw=path.read_bytes();self.send_response(200);self.send_header('Content-Type',(mimetypes.guess_type(path.name)[0] or 'text/plain')+'; charset=utf-8');self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-cache');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(raw)
        except (ValueError,KeyError,TypeError) as exc:self.fail(exc)
        except Exception as exc:self.fail('Không thể xử lý yêu cầu: '+str(exc),500)
    def do_POST(self):
        self.context()
        try:
            self.authorized();length=int(self.headers.get('Content-Length',0))
            if not 0<=length<=16384:raise ValueError('Nội dung yêu cầu quá lớn.')
            body=json.loads(self.rfile.read(length) or b'{}');route=urlparse(self.path).path
            if route=='/api/simulation/reset':
                clock=body.get('clock',self.app.model.config.clock)
                try:clock=seconds(clock) if isinstance(clock,str) else clock
                except Exception:raise ValueError('Thời điểm bắt đầu không hợp lệ.')
                warm=body.get('warmup',0)
                if type(clock)!=int or not 0<=clock<86400 or type(warm)!=int or not 0<=warm<=120:raise ValueError('Giờ bắt đầu hoặc số giây chuẩn bị không hợp lệ.')
                with self.current_session['lock']:
                    s=initial(self.app.model.config,(clock-warm)%86400)
                    for _ in range(warm):s=step(self.app.model.config,s)
                    self.current_session.update(state=s,origin_clock=clock,warmup=warm)
                    result=self.app.model.serialize(s)
                return self.send(200,result)
            if route=='/api/simulation/step':
                count=body.get('count',1)
                if type(count)!=int or not 1<=count<=120:raise ValueError('Mỗi yêu cầu chỉ được từ 1 đến 120 bước giây.')
                with self.current_session['lock']:
                    s=self.current_session['state'];history=[]
                    for _ in range(count):s=step(self.app.model.config,s);history.append(self.app.model.serialize(s,False))
                    self.current_session['state']=s;value=self.app.model.serialize(s);value['history']=history
                return self.send(200,value)
            if route=='/api/verification/run':return self.send(202,self.app.start_job())
            self.fail('Không tìm thấy thao tác.',404)
        except (ValueError,KeyError,TypeError,json.JSONDecodeError) as exc:self.fail(exc)
        except Exception as exc:self.fail('Không thể thực hiện thao tác: '+str(exc),500)

class LocalServer(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self,port=8765,data_dir=None):
        super().__init__(('127.0.0.1',port),Handler);self.app=Application(data_dir);self.app.port=self.server_port

def main():
    sys.stdout.reconfigure(encoding='utf-8');p=argparse.ArgumentParser(description='Ứng dụng Chương 1: mô phỏng và kiểm chứng giao lộ.')
    p.add_argument('--port',type=int,default=8765);p.add_argument('--data-dir',type=Path);args=p.parse_args()
    server=LocalServer(args.port,args.data_dir)
    print('GIAOLO_URL=http://127.0.0.1:'+str(server.server_port),flush=True)
    print('Ứng dụng cục bộ đã sẵn sàng. Mở địa chỉ trên bằng trình duyệt; Ctrl+C để dừng.',flush=True)
    try:server.serve_forever(poll_interval=.2)
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()

