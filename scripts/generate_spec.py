import sys, re, json, subprocess, hashlib, shutil, textwrap
from pathlib import Path
from datetime import datetime
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / '.codex-tools'))
sys.stdout.reconfigure(encoding='utf-8')
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.comments import Comment
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
EXE = shutil.which('NuSMV')
assert EXE, 'NuSMV is required'
PROJECT = ROOT / 'Smart-Traffic-Light-Verification'
HEADERS = {
'ThongTin':['Truong','GiaTri'],
'YeuCauChucNang':['ID','MoTa','DanhMuc','MucUuTien'],
'YeuCauPhiChucNang':['ID','MoTa','MucUuTien'],
'RangBuoc':['ID','MoTa','MucUuTien'],
'MoHinhTrangThai':['TrangThai','KhoiTao','Nhan','ChuyenDenCacTrangThai'],
'ThuocTinhAnToan':['CongThucCTL'],
'LoaiTruLanNhau':['MenhDe1','MenhDe2'],
'HamSinhMa':['Ten','NgonNgu','Loai','ThamSo','KichThuocBuffer','Loi','GiaTriBiMat1','GiaTriBiMat2'],
'KiemTraSoHoc':['Ten','BienSoNguyen','DieuKien','BieuThucTran'],
'TestCase':['ID','YeuCauLienQuan','TieuDe','DieuKienTienQuyet','CacBuoc','KetQuaMongDoi','MucUuTien']}
data = {s:[] for s in HEADERS}
origins = {s:[] for s in HEADERS}
def add(sheet, row, origin):
    assert len(row) == len(HEADERS[sheet])
    data[sheet].append(row)
    origins[sheet].append(origin)
def req(i, desc, cat, origin, priority='HIGH'):
    add('YeuCauChucNang',[f'REQ-{i}',desc,cat,priority],origin)
def tc(ref, title, pre, steps, expected, origin, priority='HIGH'):
    add('TestCase',[f'TC-{len(data["TestCase"])+1}',ref,title,pre,'\n'.join(f'{i+1}. {s}' for i,s in enumerate(steps)),expected,priority],origin)
LAB = 'BỔ SUNG THEO PDF: thiết kế bài thực hành, chưa có trong mã nguồn SMV; chưa chạy Spec Verification Lab.'
add('ThongTin',['name','smart_traffic_light_verification'], 'PDF mục 3.1; tên dự án hiện có.')
add('ThongTin',['description','Đặc tả các mô hình NuSMV điều khiển đèn Bắc–Nam/Đông–Tây: chu kỳ cơ bản, bộ đếm thời gian, thích nghi, lỗi khởi tạo/chuyển trạng thái và xe ưu tiên. Đồ thị Excel giữ các giá trị trạng thái đạt được của từng file SMV trong các thành phần độc lập, không mô tả các file chạy đồng thời. Theo PDF, bổ sung riêng bài thực hành tranh chấp khóa giữa worker điều khiển và worker ghi log, hàm C/Python cố ý lỗi và bộ đếm SMT; các phần này là đề xuất, chưa tồn tại trong code. Kết quả kiểm chứng gốc và giới hạn nằm trong BAO_CAO_SPEC.md và nusmv_results.json.'], 'Phạm vi đọc từ toàn bộ file SMV; các phần mở rộng theo PDF được phân biệt rõ.')
req(1,'Mô hình đèn cơ bản phải thực hiện đúng NS_GREEN → NS_YELLOW → EW_GREEN → EW_YELLOW → NS_GREEN.','functional','01_basic_model/traffic_light_model.smv')
req(2,'Trong chu kỳ cơ bản, sau NS_GREEN cuối cùng phải có EW_GREEN.','liveness','01_basic_model/traffic_light_model.smv: LTLSPEC')
req(3,'Mô hình timed khởi tạo timer=30, pha NS_GREEN có timer≤30 và NS_YELLOW có timer≤5.','safety','02_time_based_model/timed_light.smv: 2 LTLSPEC')
req(4,'Mô hình adaptive không đồng thời có state=NS_GREEN và state=EW_GREEN.','safety','03_adaptive_model/adaptive_light.smv; thuộc tính đúng do state là enum đơn.')
req(5,'Mô hình adaptive cuối cùng chuyển mỗi pha xanh sang pha vàng tương ứng.','liveness','03_adaptive_model/adaptive_light.smv')
req(6,'Trong adaptive, khi NS_GREEN hết timer, timer kế tiếp là 45/30/20 theo traffic_mode hiện tại PEAK/NORMAL/LOW. Đây là hành vi code hiện tại, chưa khẳng định cấp đúng thời lượng pha mới.','functional','03_adaptive_model/adaptive_light.smv: next(timer)')
req(7,'Mô hình init_bug phải bị phát hiện vi phạm do hai hướng cùng GREEN ngay ở trạng thái đầu.','safety','03_bmc/init_bug.smv')
req(8,'Quy tắc S0 → S1 phải thất bại ở hai transition_bug.smv và đúng ở transition_bug_fixed.smv.','safety','03_bmc/transition_bug.smv; 05_bug_analysis/transition_bug*.smv')
req(9,'Trong safety_liveness, hai hướng không đồng thời xanh/đỏ; mỗi hướng đang đỏ cuối cùng phải xanh.','safety','04_verification/safety_liveness.smv; mô hình trừu tượng không có khoảng all-red.')
req(10,'Khi emergency=TRUE, cuối cùng phải có EMERGENCY_GREEN và sau đó cuối cùng quay lại NS_GREEN.','liveness','06_extension/emergency_mode.smv')
req(11,'[Bổ sung PDF] Worker điều khiển và worker log không được giữ đồng thời khóa cập nhật tín hiệu; bài lỗi cố ý có trạng thái conflict để kiểm tra phát hiện.','safety',LAB)
req(12,'[Bổ sung PDF] Mỗi trạng thái bài tranh chấp khóa có ít nhất 1 chuyển tiếp đi ra; khóa phải có trạng thái giữ đạt được.','liveness',LAB)
req(13,'[Bổ sung PDF] parse_signal_id không được sao chép vượt buffer 16 byte; bản bài tập cố ý dùng buffer-overflow.','memory',LAB)
req(14,'[Bổ sung PDF] write_phase_log phải giải phóng vùng cấp phát 32 byte; bản bài tập cố ý memory-leak.','memory',LAB)
req(15,'[Bổ sung PDF] close_control_session chỉ được free vùng nhớ 8 byte đúng 1 lần; bản bài tập cố ý double-free.','memory',LAB)
req(16,'[Bổ sung PDF] release_sensor_cache không được dùng vùng 16 byte sau khi free; bản bài tập cố ý use-after-free.','memory',LAB)
req(17,'[Bổ sung PDF] Phép tính traffic_ratio phải xử lý mẫu số 0; mẫu divide cố ý chưa bảo vệ.','functional',LAB)
req(18,'[Bổ sung PDF] emergency_override_code phải xử lý cặp mã 6284/4917; mẫu magic_value cố ý raise tại nhánh đó.','functional',LAB)
req(19,'[Bổ sung PDF] Phải phân tích 5 bộ đếm cộng dồn theo ngưỡng nghiệp vụ và khả năng vượt miền int32.','safety',LAB)
for i,desc in enumerate([
'[Mục tiêu đề xuất] Mỗi mô hình SMV nhỏ phải hoàn tất kiểm chứng trong 60 giây trên máy chạy; lưu thời gian thực tế.',
'[Mục tiêu đề xuất] 100% công thức gốc được lưu kết quả true/false cùng stdout/stderr và hash SHA-256 của file.',
'[Mục tiêu đề xuất] Workbook có đúng 10 sheet, 100% tên cột khớp PDF; không có tham chiếu trạng thái/yêu cầu bị thiếu.',
'[Mục tiêu đề xuất] Với cùng hash đầu vào và phiên bản NuSMV, 2 lần chạy phải cho cùng chuỗi kết quả thuộc tính.',
'[Mục tiêu đề xuất] Thực hiện 300 vòng fuzzing với seed=1 cho mỗi mẫu Python; báo rõ đầu vào gây crash.',
'[Mục tiêu đề xuất] 100% dữ liệu tiếng Việt trong workbook dùng Unicode; mỗi bước kiểm thử nằm trên 1 dòng trong ô.'
],1): add('YeuCauPhiChucNang',[f'NFR-{i}',desc,'MEDIUM'],LAB)
constraints=[
'Code hiện tại là NuSMV MODULE main; các mô hình là các file độc lập, không ghép thành tiến trình đồng thời.',
'timer có miền 0..60; timed khởi tạo 30, nạp pha vàng 5 và pha xanh 30. Đơn vị bước, chưa có đồng hồ thời gian thực.',
'NuSMV case chọn nhánh đúng đầu tiên; cập nhật next đồng thời theo giá trị hiện tại, trừ biểu thức next(state) phụ thuộc được khai báo rõ.',
'[Bổ sung PDF] Signal ID dùng ASCII, buffer parse_signal_id là 16 byte gồm NUL; tối đa 15 ký tự nội dung. Buffer 16 phải khớp HamSinhMa.',
'[Bổ sung PDF] Hai worker điều khiển/log cùng dùng khóa tín hiệu trong mô hình lab, không suy diễn thành cơ chế khóa đã triển khai.',
'[Bổ sung PDF] Vùng log/session/cache lần lượt 32/8/16 byte; chỉ dùng khuôn sinh mã c và python do PDF quy định.',
'[Bổ sung PDF] Kiểm tra overflow dùng int32 [-2147483648,2147483647] độc lập DieuKien; ngưỡng 32767/65535/2000000000/4294967295 là ngưỡng nghiệp vụ.',
'Không xem LTLSPEC G trong code là công thức CTL tổng quát. CTL trong Excel được viết trên đồ thị đã liệt kê; các mô hình gốc hiện đều xác định.',
'Các trạng thái bổ sung lab và các lỗi C/Python chỉ phục vụ phát hiện lỗi; không sửa file SMV gốc.'
]
for i,desc in enumerate(constraints,1): add('RangBuoc',[f'CON-{i}',desc,'HIGH'],LAB if '[Bổ sung' in desc else 'Đối chiếu cú pháp và hành vi file SMV hiện có.')

# Read and run every real source file. Directory login.smv is intentionally excluded.
results=[]
for p in sorted(list(PROJECT.rglob('*.smv'))+[ROOT/'test.smv']):
    src=p.read_text(encoding='utf-8-sig')
    clean=re.sub(r'--[^\n]*','',src)
    start=datetime.now()
    run=subprocess.run([EXE,str(p)],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=60)
    rel=p.relative_to(ROOT).as_posix()
    props=[{'formula':m.group(1).strip(),'result':m.group(2)} for m in re.finditer(r'-- specification (.*?) is (true|false)',run.stdout,re.S)]
    results.append({'file':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'returncode':run.returncode,'seconds':(datetime.now()-start).total_seconds(),'properties':props,'stdout':run.stdout,'stderr':run.stderr})
(OUT/'nusmv_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')

# Finite reachable graphs, preserving ALL variables and simultaneous updates.
# The evaluator below intentionally supports only the simple deterministic syntax present in this project.
graphs={}
def enumerate_graph(path, prefix):
    src=re.sub(r'--[^\n]*','',path.read_text(encoding='utf-8-sig'))
    decl=src.split('VAR',1)[1].split('ASSIGN',1)[0]
    names=re.findall(r'\b(\w+)\s*:\s*(?:\{[^}]+\}|\d+\.\.\d+|boolean)\s*;',decl,re.S)
    inits=dict(re.findall(r'init\((\w+)\)\s*:=\s*(\w+)\s*;',src))
    assignments={v:re.findall(r'(.*?)\s*:\s*(.*?)\s*;',body,re.S) for v,body in re.findall(r'next\((\w+)\)\s*:=\s*case(.*?)esac\s*;',src,re.S)}
    assert set(names)==set(inits)==set(assignments),path
    def value(x):
        return True if x=='TRUE' else False if x=='FALSE' else int(x) if re.fullmatch(r'\d+',x) else x
    current={v:value(inits[v]) for v in names}
    seen={}; values=[]; edges=[]
    seeds=[current.copy()]
    for v,body in re.findall(r'(\w+)\s*:\s*\{([^}]+)\}',decl,re.S):
        for token in body.split(','):
            seed=seeds[0].copy(); seed[v]=value(token.strip())
            if seed not in seeds: seeds.append(seed)
    first_count=None
    while True:
        if tuple(current.values()) in seen:
            if first_count is None: first_count=len(values)
            if not seeds: break
            current=seeds.pop(0)
            if tuple(current.values()) in seen: continue
        assert len(values)<20000,path
        seen[tuple(current.values())]=len(values); values.append(current.copy())
        cache={}
        def nex(v):
            if v in cache: return cache[v]
            for cond,expr in assignments[v]:
                if ev(cond):
                    cache[v]=ev(expr); return cache[v]
            raise ValueError('No branch '+v)
        def ev(expr):
            expr=re.sub(r'next\((\w+)\)',lambda m:repr(nex(m[1])),expr.strip())
            def token(m):
                t=m.group(0)
                return repr(current[t]) if t in current else 'True' if t=='TRUE' else 'False' if t=='FALSE' else repr(t)
            # next(state) string literals need protection from the token pass.
            pieces=re.split(r"('[^']*')",expr)
            expr=''.join(s if i%2 else re.sub(r'\b[A-Za-z_]\w*\b',token,s) for i,s in enumerate(pieces))
            expr=re.sub(r'(?<![<>=!])=(?!=)','==',expr).replace('&',' and ').replace('|',' or ')
            expr=re.sub(r'!(?!=)',' not ',expr)
            return eval(' '.join(expr.split()),{'__builtins__':{}},{})
        current={v:nex(v) for v in names}
        edges.append(tuple(current.values()))
    edges=[seen[key] for key in edges]
    gids=[f'{prefix}_{i:04d}' for i in range(len(values))]
    all_labels=[]
    for i,vals in enumerate(values):
        labs=[prefix]
        for v,x in vals.items():
            suffix=str(x).upper() if isinstance(x,bool) else str(x)
            labs.append(f'{prefix}_{v}_{suffix}')
        if 'state' in vals and vals['state'] in ('NS_GREEN','EW_GREEN','NS_YELLOW','EW_YELLOW'):
            labs += [f'{prefix}_phase_'+vals['state']]
        all_labels.append(labs)
        add('MoHinhTrangThai',[gids[i],'x' if i==0 else None,', '.join(labs),gids[edges[i]]],path.relative_to(ROOT).as_posix()+'; '+json.dumps(vals,ensure_ascii=False))
    graphs[prefix]={'file':path.relative_to(ROOT).as_posix(),'states':len(values),'reachable_states':first_count,'loop_to':edges[-1],'values':values,'labels':all_labels}
    return prefix
files=[
('basic','01_basic_model/traffic_light_model.smv'),('timed','02_time_based_model/timed_light.smv'),
('adaptive','03_adaptive_model/adaptive_light.smv'),('initbug','03_bmc/init_bug.smv'),
('bmc','03_bmc/traffic_light_bmc.smv'),('bmcbug','03_bmc/transition_bug.smv'),
('verify','04_verification/safety_liveness.smv'),('bug','05_bug_analysis/transition_bug.smv'),
('fixed','05_bug_analysis/transition_bug_fixed.smv'),('emergency','06_extension/emergency_mode.smv'),
('test2','test/traffic_light2.smv'),('testbasic','test/traffic_light_basic.smv')]
for prefix,rel in files: enumerate_graph(PROJECT/rel,prefix)
enumerate_graph(ROOT/'test.smv','login')
for row in [
['signal_free','x','safe','signal_main_holds, signal_log_holds'],
['signal_main_holds',None,'main_locked','signal_free, signal_conflict'],
['signal_log_holds',None,'log_locked','signal_free'],
['signal_conflict',None,'main_locked, log_locked, violation','signal_free']]: add('MoHinhTrangThai',row,LAB+' Cụm khóa cố ý sai theo PDF 3.5, conflict đạt được.')

expected=[]
def ctl(formula, truth, origin):
    add('ThuocTinhAnToan',[formula],origin); expected.append(truth)
ctl('AG(!violation)',False,LAB+' Phải sai vì signal_conflict đạt được.')
ctl('EF(main_locked)',False,LAB+' Reachable from signal_free, but FALSE globally: other independent initial components cannot reach the lab lock.')
# Guard reachability properties because the workbook has multiple independent initial components.
ctl('AG(basic -> EF(basic_state_NS_GREEN))',True,'REQ-1; đồ thị basic xác định.')
for a,b in [('NS_GREEN','NS_YELLOW'),('NS_YELLOW','EW_GREEN'),('EW_GREEN','EW_YELLOW'),('EW_YELLOW','NS_GREEN')]:
    ctl(f'AG(basic_state_{a} -> AX(basic_state_{b}))',True,'REQ-1; 01_basic_model/traffic_light_model.smv')
ctl('AG(basic_state_NS_GREEN -> AF(basic_state_EW_GREEN))',True,'REQ-2; viết CTL trên đồ thị xác định của mô hình cơ bản.')
for state,bound in [('NS_GREEN',30),('NS_YELLOW',5)]:
    labels=[f'timed_timer_{i}' for i in range(bound+1)]
    ctl(f'AG(timed_state_{state} -> ( '+ ' | '.join(labels)+' ))',True,'REQ-3; kiểm tra trên giá trị timer đầy đủ, không trừu tượng bỏ bộ đếm.')
ctl('AG(!(adaptive_state_NS_GREEN & adaptive_state_EW_GREEN))',True,'REQ-4; bất biến cấu trúc enum, không đủ chứng minh an toàn phần cứng.')
for d in ['NS','EW']:
    ctl(f'AG(adaptive_state_{d}_GREEN -> AF(adaptive_state_{d}_YELLOW))',True,'REQ-5; đồ thị adaptive xác định.')
for mode,n in [('PEAK',45),('NORMAL',30),('LOW',20)]:
    ctl(f'AG((adaptive_traffic_mode_{mode} & adaptive_state_NS_GREEN & adaptive_timer_0) -> AX(adaptive_timer_{n}))',True,'REQ-6; LOW là tiền đề không đạt được trong code hiện tại.')
ctl('AG(!(initbug_NS_light_GREEN & initbug_EW_light_GREEN))',False,'REQ-7; hai hướng cùng xanh ngay lúc init.')
for prefix in ['bmcbug','bug','fixed']:
    ctl(f'AG({prefix}_state_S0 -> AX({prefix}_state_S1))',prefix=='fixed','REQ-8; hai bản bug sai, bản fixed đúng.')
for color in ['GREEN','RED']:
    ctl(f'AG(!(verify_NS_light_{color} & verify_EW_light_{color}))',True,'REQ-9; chỉ đúng trong mô hình trừu tượng này.')
for d in ['NS','EW']:
    ctl(f'AG(verify_{d}_light_RED -> AF(verify_{d}_light_GREEN))',True,'REQ-9; liveness của mô hình verify.')
ctl('AG(emergency_emergency_TRUE -> AF(emergency_state_EMERGENCY_GREEN))',True,'REQ-10; cảm biến trong code luân phiên FALSE/TRUE.')
ctl('AG(emergency_state_EMERGENCY_GREEN -> AF(emergency_state_NS_GREEN))',True,'REQ-10; đồ thị emergency xác định.')
ctl('AG(adaptive -> EF(adaptive_time_period_NIGHT_LOW))',False,'Kiểm tra bổ sung: NIGHT_LOW không đạt được do nhánh NORMAL_TIME thứ hai bị che.')
ctl('AG(adaptive -> EF(adaptive_traffic_mode_LOW))',False,'Kiểm tra bổ sung: LOW không đạt được; công thức kéo theo LOW trong code đúng rỗng.')
ctl('AG(!(login_state_logged_in & login_state_logged_out))',True,'test.smv ngoài dự án traffic: ví dụ đăng nhập; không phải chức năng traffic.')
for a,b in [('main_locked','log_locked'),('safe','violation'),('basic_state_NS_GREEN','basic_state_EW_GREEN'),('timed_state_NS_GREEN','timed_state_NS_YELLOW'),('emergency_state_EMERGENCY_GREEN','emergency_state_NS_GREEN'),('initbug_NS_light_GREEN','initbug_EW_light_GREEN')]:
    add('LoaiTruLanNhau',[a,b],LAB if a in ['main_locked','safe'] else 'Nhãn lấy từ đồ thị code gốc. Cặp initbug cố ý vi phạm; ngoài dòng đầu phải dùng CTL tương ứng.')

funcs=[
['parse_signal_id','c','buffer_copy','raw_id',16,'buffer-overflow',None,None],
['write_phase_log','c','alloc_release',None,32,'memory-leak',None,None],
['close_control_session','c','alloc_release',None,8,'double-free',None,None],
['release_sensor_cache','c','alloc_release',None,16,'use-after-free',None,None],
['traffic_ratio','python','divide','passed, detected',16,None,None,None],
['emergency_override_code','python','magic_value','code_a, code_b',16,None,6284,4917],
['add_vehicle_counts','c','arithmetic','ns_count, ew_count',16,None,None,None]]
for row in funcs: add('HamSinhMa',row,LAB+' Ô trống theo quy tắc riêng PDF 3.8: trường không áp dụng, không dùng chuỗi N/A.')
checks=[('daily_vehicle_counter','ns_count','ew_count',32767),('queued_vehicle_counter','queued_ns','queued_ew',65535),('phase_log_byte_counter','stored_bytes','pending_bytes',2000000000),('emergency_event_counter','handled_events','pending_events',32767),('archive_byte_counter','archive_a','archive_b',4294967295)]
for name,a,b,n in checks:
    add('KiemTraSoHoc',[name,f'{a}, {b}',f'{a} >= 0 and {b} >= 0 and {a} + {b} > {n}',f'{a} + {b}'],LAB+' Hai phép kiểm tra SAT riêng biệt; không suy ra timer SMV bị tràn.')

for prefix,rel in files:
    record=next(r for r in results if r['file'].endswith(rel))
    refs={'basic':'REQ-1, REQ-2','timed':'REQ-3','adaptive':'REQ-4, REQ-5, REQ-6','initbug':'REQ-7','bmcbug':'REQ-8','bug':'REQ-8','fixed':'REQ-8','verify':'REQ-9','emergency':'REQ-10'}.get(prefix,'REQ-1')
    summary=', '.join(p['result'] for p in record['properties']) or 'Không có SPEC/LTLSPEC; chỉ kiểm tra nạp mô hình, chưa có thuộc tính được chứng minh.'
    tc(refs,f'Kiểm chứng {rel}',f'NuSMV khả dụng; file {rel} giữ nguyên.',[f'Chạy NuSMV "Smart-Traffic-Light-Verification/{rel}".','Đọc từng kết quả và phản ví dụ; đối chiếu nusmv_results.json.'],f'Exit code {record["returncode"]}; {summary}',record['file'])
tc('REQ-11, REQ-12','Phát hiện xung đột khóa lab','Mô hình signal_* bổ sung từ PDF.', ['Dựng đồ thị từ MoHinhTrangThai.','Kiểm tra AG(!violation), EF(main_locked), deadlock và cặp mutex dòng đầu.'],'AG(!violation)=false; EF(main_locked)=false (global multi-initial check); true from signal_free only; mutex vi phạm; không có deadlock. Đây là kết quả mong đợi của bài lỗi cố ý.',LAB)
for idx,code in [(0,'CWE-120'),(1,'CWE-401'),(2,'CWE-415'),(3,'CWE-416')]:
    f=funcs[idx]
    tc(f'REQ-{idx+13}',f'Phát hiện {f[5]} trong {f[0]}',f'HamSinhMa khai báo {f[0]}, Loi={f[5]}.',[f'Sinh mã C cho {f[0]} bằng Spec Verification Lab.','Chạy check_c_source() và đọc báo cáo.'],f'Dự kiến phát hiện {f[5]} ({code}); CHƯA CHẠY pipeline vì thiếu mã core của Spec Verification Lab.',LAB)
tc('REQ-17, NFR-5','Mẫu số 0 của traffic_ratio','Mẫu Python divide đã được sinh.', ['Chạy blackbox_fuzz() 300 vòng, seed=1.','Bổ sung đầu vào trực tiếp passed=1, detected=0 nếu lượt ngẫu nhiên chưa tìm được.'],'Đầu vào mẫu số 0 gây ZeroDivisionError; số crash ngẫu nhiên phải đo thực tế, chưa được xác nhận.',LAB)
tc('REQ-18, NFR-5','Nhánh bí mật emergency_override_code','Mẫu Python magic_value với 6284/4917.', ['Chạy black-box và concolic fuzzer theo cùng ngân sách.','Thử trực tiếp cặp 6284/4917 và lưu đầu vào gây lỗi.'],'Dự kiến raise tại cặp bí mật; so sánh khả năng tìm nhánh của hai fuzzer. Chưa chạy.',LAB)
for name,a,b,n in checks:
    tc('REQ-19, CON-7',f'SMT {name}',f'KiemTraSoHoc có dòng {name}.',[f'Chạy check_satisfiability() trên {a}>=0 and {b}>=0 and {a}+{b}>{n}.',f'Chạy riêng check_int32_overflow() trên {a}+{b}.'],'Dự kiến SAT cho cả hai truy vấn độc lập; lưu mô hình minh họa. Không xem DieuKien là ràng buộc của overflow checker. Chưa chạy Z3.',LAB)
tc('REQ-6, CON-3','Phát hiện nhánh thời gian bị che','Code adaptive nguyên trạng.', ['Xem thứ tự hai nhánh time_period=NORMAL_TIME.','Kiểm tra khả đạt NIGHT_LOW và LOW trên đồ thị Excel.'],'Hai CTL kiểm tra khả đạt đều false; nhánh EVENING_PEAK bị nhánh MORNING_PEAK che.', '03_adaptive_model/adaptive_light.smv')
tc('NFR-1, NFR-2, NFR-4','Tái lập kiểm chứng gốc','Có cùng hash file nguồn và cùng NuSMV.', ['Chạy lại toàn bộ file SMV hai lần.','So sánh danh sách công thức/kết quả theo từng file; đo thời gian.'],'Hai lần phải cùng kết quả; từng file ≤60 giây là mục tiêu đề xuất, cần lưu thời gian đo.',LAB)
tc('NFR-3, NFR-6, CON-4','Kiểm tra cấu trúc và truy vết Excel','Workbook đã xuất.', ['Kiểm tra đúng 10 sheet và tên cột PDF.','Kiểm tra tham chiếu ID, nhãn CTL, chuyển trạng thái, Unicode và buffer 16.'],'Không tham chiếu thiếu; tối đa 15 ký tự ASCII cộng NUL trong buffer 16; CacBuoc có xuống dòng.',LAB)

# Write workbook, preserving exact import headers and no extra sheets.
wb=Workbook(); wb.remove(wb.active)
for num,(name,headers) in enumerate(HEADERS.items(),1):
    ws=wb.create_sheet(name); ws.append(headers)
    for i,row in enumerate(data[name],2):
        ws.append(row)
        ws.cell(i,1).comment=Comment(origins[name][i-2],'Nguồn / phạm vi')
        for cell in ws[i]:
            cell.alignment=Alignment(vertical='top',wrap_text=True)
            cell.font=Font(name='Calibri',size=11)
        ws.row_dimensions[i].height=65 if name!='MoHinhTrangThai' else 46
    for cell in ws[1]:
        cell.fill=PatternFill('solid',fgColor='16324F'); cell.font=Font(name='Calibri',bold=True,color='FFFFFF',size=11)
        cell.alignment=Alignment(vertical='center',wrap_text=True)
    ws.row_dimensions[1].height=32; ws.freeze_panes='A2'
    table=Table(displayName=f'SpecTable{num}',ref=ws.dimensions)
    table.tableStyleInfo=TableStyleInfo(name='TableStyleMedium2',showRowStripes=True)
    ws.add_table(table)
    for col,h in enumerate(headers,1):
        width=18
        if h in ['MoTa','GiaTri','CongThucCTL','KetQuaMongDoi','CacBuoc']: width=90 if name=='ThuocTinhAnToan' else 65
        elif h in ['Nhan','DieuKien','DieuKienTienQuyet','ChuyenDenCacTrangThai']: width=55
        elif h in ['Ten','TieuDe','TrangThai','BieuThucTran','BienSoNguyen']: width=34
        ws.column_dimensions[get_column_letter(col)].width=width
    ws.sheet_properties.pageSetUpPr.fitToPage=True
    ws.page_setup.orientation='landscape'; ws.page_setup.paperSize=ws.PAPERSIZE_A3
    ws.page_setup.fitToWidth=1; ws.page_setup.fitToHeight=0; ws.print_title_rows='1:1'
    ws.sheet_properties.tabColor='B7791F' if name in ['HamSinhMa','KiemTraSoHoc'] else '216869'
xlsx=OUT/'Smart_Traffic_Light_Spec.xlsx'; wb.save(xlsx)

# Validate the exported artifact rather than only the in-memory data.
read=load_workbook(xlsx,data_only=True)
assert read.sheetnames==list(HEADERS)
for name,headers in HEADERS.items():
    assert [c.value for c in read[name][1]]==headers
    assert read[name].max_row-1==len(data[name])
    if name!='ThongTin': assert read[name].max_row-1>=5
reqids={r[0] for s in ['YeuCauChucNang','YeuCauPhiChucNang','RangBuoc'] for r in data[s]}
for r in data['TestCase']:
    assert all(x.strip() in reqids for x in r[1].split(',')),r
    assert '\n' in r[4]
states={r[0]:r for r in data['MoHinhTrangThai']}
assert len(states)==len(data['MoHinhTrangThai'])
labels=set()
for r in states.values():
    labels.update(x.strip() for x in r[2].split(','))
    assert r[3] and all(x.strip() in states for x in r[3].split(',')),r
for r in data['LoaiTruLanNhau']: assert r[0]!=r[1] and set(r)<=labels
for r in data['ThuocTinhAnToan']:
    atoms=set(re.findall(r'\b[A-Za-z_]\w*\b',r[0]))-{'AG','AF','AX','EF','EG','EX'}
    assert atoms<=labels,atoms-labels
assert {r[2] for r in data['YeuCauChucNang']}=={'safety','liveness','memory','functional'}
assert {r[5] for r in funcs if r[5]}=={'buffer-overflow','memory-leak','double-free','use-after-free'}
# Cross-check the enumerated graph against NuSMV reachable-state counts.
reachable_checks=[]
for prefix,g in graphs.items():
    commands='go\nprint_reachable_states\nquit\n'
    r=subprocess.run([EXE,'-int',str(ROOT/g['file'])],input=commands,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=60)
    m=re.search(r'reachable states:\s*(\d+)',r.stdout,re.I)
    assert r.returncode==0 and m,(g['file'],r.stdout,r.stderr)
    assert int(m[1])==g['reachable_states'],(prefix,m[1],g['states'])
    reachable_checks.append({'model':prefix,'nuSMV_reachable_states':int(m[1]),'excel_reachable_states':g['reachable_states'],'excel_total_states':g['states']})
# Verify every CTL formula against the actual workbook graph using NuSMV.
idx={name:i for i,name in enumerate(states)}
model=['MODULE main','VAR node : {'+', '.join('n'+str(i) for i in idx.values())+'};','ASSIGN',
'init(node) := {'+', '.join('n'+str(idx[r[0]]) for r in states.values() if r[1]=='x')+'};','next(node) := case']
for name,r in states.items():
    targets=['n'+str(idx[t.strip()]) for t in r[3].split(',')]
    model.append('node = n'+str(idx[name])+' : {'+', '.join(targets)+'};')
model+=['esac;','DEFINE']
for label in sorted(labels):
    nodes=['node = n'+str(idx[r[0]]) for r in states.values() if label in [s.strip() for s in r[2].split(',')]]
    model.append(label+' := ('+' | '.join(nodes)+');')
model += ['CTLSPEC '+r[0]+';' for r in data['ThuocTinhAnToan']]
(OUT/'excel_graph_check.smv').write_text('\n'.join(model)+'\n',encoding='utf-8')
r=subprocess.run([EXE,str(OUT/'excel_graph_check.smv')],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=60)
(OUT/'excel_graph_check.log').write_text(r.stdout+'\nSTDERR\n'+r.stderr,encoding='utf-8')
actual=[x=='true' for x in re.findall(r' is (true|false)',r.stdout)]
assert r.returncode==0 and actual==expected,(actual,expected,r.stderr)
validation={'sheet_rows':{s:len(data[s]) for s in HEADERS},'headers':'pass','references':'pass','no_deadlocks':'pass','graph_state_counts':reachable_checks,'ctl_count':len(actual),'ctl_true':sum(actual),'ctl_false':len(actual)-sum(actual),'ctl_matches_expected':True,'spec_verification_lab_pipeline':'NOT RUN: core/spec_excel.py and core/spec_pipeline.py absent','Z3_and_fuzzing':'NOT RUN; proposed lab inputs only'}
(OUT/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf-8')

lines=['# Đặc tả Excel theo PDF — Smart Traffic Light','',
'File chính: **Smart_Traffic_Light_Spec.xlsx**. Đúng 10 sheet và tiêu đề theo PDF 28 trang được cung cấp. Nội dung ô và chú thích phân biệt rõ code hiện có với bài thực hành bổ sung. Không sửa bất kỳ file SMV gốc nào.','',
'## Phạm vi và cách đọc','',
'- Dự án chứa 14 file SMV thật; thư mục `login.smv` rỗng không phải file. `test.smv` ở gốc là ví dụ đăng nhập, được giữ thành thành phần riêng.',
'- Mỗi file có biến được liệt kê thành đồ thị hữu hạn các trạng thái đạt được; timer, traffic_mode, time_period, emergency và NS/EW_light đều được giữ. Các thành phần độc lập có tiền tố nhãn riêng và nhiều trạng thái khởi tạo. Không ngụ ý các mô hình này chạy đồng thời.',
'- Các công thức CTL được viết mới trên đồ thị Excel. Với code xác định hiện tại, thuộc tính thời gian gốc có thể đối chiếu trên đường chạy duy nhất. Không tuyên bố phép thay G/F/X bằng AG/AF/AX đúng cho mọi mô hình bất định.',
'- Bốn trạng thái signal_free/main_holds/log_holds/conflict là bài lab khóa bổ sung theo PDF 3.5; KHÔNG tồn tại trong code gốc. AG(!violation) và mutex dòng đầu phải thất bại để minh họa phát hiện lỗi.',
'- Hàm C/Python, bộ đếm cộng dồn và mục tiêu phi chức năng là thiết kế bổ sung theo PDF, chưa triển khai/chưa đo. Không quy lỗi bộ nhớ C hay tràn int32 cho timer có miền 0..60 trong SMV.',
'- Các ô trống KhoiTao và trường HamSinhMa không áp dụng tuân theo quy tắc riêng PDF 3.5/3.8. Không điền N/A vì có thể làm parser hiểu sai. Buffer 16 byte chứa tối đa 15 ký tự ASCII và NUL.',
'- Sheet LoaiTruLanNhau có nhiều cặp; theo PDF parser chỉ tự kiểm cặp đầu. Các cặp bổ sung quan trọng cũng được thể hiện bằng CTL. TestCase là kế hoạch truy vết, không tự được pipeline thực thi.','',
'## Kết quả NuSMV gốc','',
'| File | Số thuộc tính | True | False | Exit |','|---|---:|---:|---:|---:|']
for r in results:
    lines.append(f'| {r["file"]} | {len(r["properties"])} | {sum(p["result"]=="true" for p in r["properties"])} | {sum(p["result"]=="false" for p in r["properties"])} | {r["returncode"]} |')
lines+=['','Log đầy đủ, stderr, thời gian đo và SHA-256 từng file nằm trong **nusmv_results.json**. Các bản lỗi được kỳ vọng có false; exit code 0 không đồng nghĩa tất cả thuộc tính đúng.','',
'## Điểm cần lưu ý trong code','',
'1. **adaptive_light.smv:** hai nhánh time_period=NORMAL_TIME; nhánh đầu chọn MORNING_PEAK nên nhánh EVENING_PEAK không bao giờ được chọn. Chu kỳ chỉ NORMAL_TIME ↔ MORNING_PEAK; EVENING_PEAK, NIGHT_LOW và traffic_mode=LOW không đạt được. Các thuộc tính kéo theo NIGHT_LOW/LOW vì vậy có thể đúng rỗng. Workbook có hai kiểm tra khả đạt trả false để làm rõ.',
'2. **adaptive_light.smv:** khi pha xanh timer=0, next(state) chuyển vàng trong khi next(timer) nhận 45/30/20 theo mode cũ; khi vàng kết thúc lại nạp 5 cho pha xanh. Do đó đặc tả thời lượng xanh thích nghi chưa phản ánh đúng mục tiêu bình luận. traffic_mode cũng cập nhật theo time_period hiện tại, có độ trễ 1 bước.',
'3. **timed_light.smv:** timer đếm cả giá trị 0 trước khi chuyển pha. Pha xanh 30..0 có 31 trạng thái; pha vàng 5..0 có 6. Không tự suy ra 30/5 giây nếu chưa định nghĩa một bước là gì và cách đo biên.',
'4. **init_bug.smv:** GREEN/GREEN ở init làm safety sai ngay bước đầu. **transition_bug.smv** ở 03_bmc và 05_bug_analysis bỏ S1: S0→S2; bản fixed sửa S0→S1. Safety không đồng thời xanh vẫn có thể đúng khi quy tắc chuyển pha sai.',
'5. **traffic_light_bmc_bug.smv:** chỉ có MODULE main, không có biến/chuyển tiếp/thuộc tính; không được xem là một bài BMC có kết quả. Hai file trong test cũng chưa có SPEC/LTLSPEC.',
'6. **emergency_mode.smv:** cảm biến luân phiên FALSE/TRUE cố định; không bao phủ cảm biến giữ TRUE hay đến ngẫu nhiên. Các điều kiện cấm hai giá trị state enum đồng thời chỉ là bất biến cấu trúc.',
'7. **safety_liveness.smv:** có bước NS_YELLOW/EW_GREEN; mô hình không bảo đảm hướng đối diện phải đỏ khi một hướng vàng, cũng không có khoảng all-red. Các thuộc tính đang có không đủ khẳng định an toàn giao lộ thực tế.',
'8. Tên thư mục 03_bmc không tự biến lần chạy mặc định thành BMC. Kết quả gốc ở đây dùng NuSMV mặc định, chưa phải báo cáo SAT bounded model checking.','',
'## Kiểm tra file Excel','',
'| Sheet | Dòng dữ liệu |','|---|---:|']
lines += [f'| {s} | {len(data[s])} |' for s in HEADERS]
lines += ['',f'- Đã mở lại workbook, kiểm tra header/ID/nhãn/chuyển tiếp, bốn loại lỗi C và hai mẫu Python. Không có deadlock trong đồ thị Excel.',f'- Đã đối chiếu số trạng thái đạt được của {len(graphs)} mô hình với print_reachable_states của NuSMV; mọi số lượng đều khớp.',f'- Đã xuất đồ thị từ dữ liệu Excel sang excel_graph_check.smv và chạy NuSMV: **{len(actual)} CTL, {sum(actual)} true, {len(actual)-sum(actual)} false**, khớp toàn bộ kết quả dự kiến. Log: excel_graph_check.log; tổng kiểm tra: validation.json.',
'- **Chưa chạy** parse_specification_excel(), run_pipeline(), Z3 hoặc fuzzing: workspace không có mã nguồn Spec Verification Lab (core/spec_excel.py, core/spec_pipeline.py...). Kiểm tra NuSMV độc lập không thay thế kiểm tra tương thích với parser/pipeline đó. Chưa thể đánh dấu phần 5.3 của PDF là hoàn tất.',
'- Các CWE được nêu trong TestCase là kết quả dự kiến theo hướng dẫn PDF, chưa phải lỗ hổng được phát hiện hoặc CVE của dự án.','',
'## Cách dùng','',
'1. Mở Smart_Traffic_Light_Spec.xlsx; xem chú thích tại cột đầu của mỗi dòng để biết nguồn.',
'2. Khi có bộ Spec Verification Lab đúng phiên bản PDF, chép workbook sang đó rồi chạy `python -m core.spec_excel duong_dan/Smart_Traffic_Light_Spec.xlsx`.',
'3. Đối chiếu kết quả với các bài lỗi cố ý và TestCase; kiểm tra đủ bốn chương trước khi nộp phần xác nhận pipeline.',
'4. Để tái tạo file từ code: `python scripts/generate_spec.py` (cần openpyxl trong .codex-tools hoặc môi trường Python và NuSMV trên PATH).','']
lines += ['NOTE: EF(main_locked) is TRUE from signal_free, but FALSE over all independent initial states. The workbook intentionally retains the exact PDF formula and records this multi-component limitation. No artificial cross-model edges were added.', '']
(OUT/'BAO_CAO_SPEC.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps(validation,ensure_ascii=False,indent=2))