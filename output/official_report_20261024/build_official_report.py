from pathlib import Path
import sys,json,re,html,hashlib,csv,textwrap,collections
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.stdout.reconfigure(encoding='utf-8')
sys.path[:0]=[str(ROOT/'.codex-tools'),str(ROOT/'chapter1/web/report_delivery/_tools')]
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image,ImageDraw,ImageFont

def read(rel):return (ROOT/rel).read_text(encoding='utf-8-sig')
def obj(rel):return json.loads(read(rel))
def local(name):return obj('output/official_report_20261024/'+name)
def dump(name,d):(OUT/name).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
A=local('audit_summary.json');assert A['all_preexisting_files_unchanged']
R=local('evidence/fresh_nusmv_results.json');P=obj('chapter1/properties.json');BY={p['name']:p for p in P}
norm=lambda s:re.sub(r'[\s()]','',s)
CHECKS={norm(c['formula']):c for c in R[0]['checks']}
assert all(norm(p['formula']) in CHECKS for p in P)
V='chapter1/smart_intersection.smv';T='Smart-Traffic-Light-Verification/02_time_based_model/timed_light.smv';D='Smart-Traffic-Light-Verification/03_adaptive_model/adaptive_light.smv';E='output/official_report_20261024/evidence/'
def line(path,needle):return next(i for i,s in enumerate(read(path).splitlines(),1) if needle in s)
def cite(path,needle=None,start=None,end=None):
 n=start or (line(path,needle) if needle else 1)
 return f'{path}:{n}'+(f'–{end}' if end and end!=n else '')
def prop(name):return BY[name]['formula']
def propref(name):return cite(V,'CTLSPEC NAME '+name+' ')
def logref(name,needle):return cite(E+name+'.log',needle)
def excerpt(path,start,end):return '\n'.join(f'{i:>4} | {s}' for i,s in enumerate(read(path).splitlines(),1) if start<=i<=end)
def match_excerpt(path,needle,before=0,after=0):
 n=line(path,needle);return excerpt(path,max(1,n-before),n+after)
TITLE='Mô hình hóa và kiểm chứng hình thức cho hệ thống các đèn giao thông thông minh sử dụng cấu trúc Kripke.'
SECTIONS=['Trang bìa & Thông tin nhóm','Tổng quan đề tài','Phương pháp luận','Phân tích lỗ hổng & Bản vá','Bảng tổng hợp before/after','Bằng chứng kiểm chứng','Phản biện & Bài học','Phụ lục']
mmd='''flowchart TD
 V0["v0: chu kỳ / timer / thích nghi"] -. "kế thừa; giữ nguồn" .-> CORE
 CFG["config.json"] --> CORE["v1: intersection.py + build.py"]
 CORE --> JSON["JSON exact / JSON chiếu"]
 CORE --> SMV["NuSMV + properties.json"]
 CORE --> WEB["domain.py / server.py / static"]
 JSON --> CHECK["verify_graph / CTL JSON"]
 SMV --> NUSMV["NuSMV BDD / CTL"]
 CHECK --> LOG["evidence: log và counterexample"]
 NUSMV --> LOG
'''
(OUT/'architecture.mmd').write_text(mmd,encoding='utf-8')
im=Image.new('RGB',(1700,660),'white');dr=ImageDraw.Draw(im)
f=ImageFont.truetype('C:/Windows/Fonts/times.ttf',29);fb=ImageFont.truetype('C:/Windows/Fonts/timesbd.ttf',32)
boxes=[(30,20,520,115,'v0: pha / timer / thích nghi','Nguồn giữ nguyên'),(600,20,1100,115,'config.json','Lịch • thời lượng • S0'),(600,170,1100,275,'v1: intersection.py + build.py','Bước giây • nhãn • sinh mô hình'),(30,345,520,455,'JSON exact / JSON chiếu','verify_graph + CTL JSON'),(610,345,1110,455,'NuSMV + properties.json','335 CTL • đếm BDD'),(1190,345,1670,455,'Web: domain / server / static','Trình bày • chạy kiểm chứng'),(600,540,1110,645,'evidence/ và counterexample','Kết quả riêng của từng công cụ')]
for x1,y1,x2,y2,t,s in boxes:
 dr.rounded_rectangle((x1,y1,x2,y2),radius=12,fill='#eef3f6',outline='#253c50',width=3)
 dr.text(((x1+x2)/2,y1+28),t,font=fb,fill='#172d42',anchor='mm');dr.text(((x1+x2)/2,y1+72),s,font=f,fill='#334c60',anchor='mm')
def arrow(a,b):
 dr.line([a,b],fill='#375b73',width=4);x,y=b;dr.polygon([(x,y),(x-9,y-16),(x+9,y-16)],fill='#375b73')
arrow((850,115),(850,170));dr.line([(520,65),(555,65),(555,220),(600,220)],fill='#8b7347',width=4)
for x in [275,860,1430]:dr.line([(850,275),(850,310),(x,310)],fill='#375b73',width=4);arrow((x,310),(x,345))
for x in [275,860]:dr.line([(x,455),(x,505),(850,505)],fill='#375b73',width=4)
arrow((850,505),(850,540));im.save(OUT/'architecture.png')
DEFECTS=[
 {'id':'D01','title':'Timer thêm một khoảng giây ở giá trị 0','v0':cite(T,start=37,end=75),'root':'Pha chỉ đổi khi timer hiện tại bằng 0. Cập nhật đồng bộ đưa 1 về 0 nhưng giữ pha. Chú thích gọi GREEN là 30 giây; dưới quy ước một bước = một giây, chuỗi 30,…,0 giữ GREEN qua 31 khoảng giây.','observable':'CTL bổ sung yêu cầu NS_GREEN/timer=1 bước sau phải NS_YELLOW trả FALSE. Trace State 1.30 timer=1 → State 1.31 timer=0, state vẫn NS_GREEN. Hai LTL cận timer gốc vẫn TRUE.','v1':cite(V,start=49,end=50),'property':'advance_NS_GREEN','query':'AG((state = NS_GREEN & timer = 1) -> AX(state = NS_YELLOW))','log':logref('v0_timer_added_query','is false'),'gap':'D+1 phụ thuộc quy ước một bước là một giây; chưa có bộ lập lịch vật lý. V1 đổi cả tham số thời lượng, không so hiệu năng bằng các tham số khác nhau.'},
 {'id':'D02','title':'Guard NORMAL_TIME trùng làm mất hai khung giờ','v0':cite(D,start=110,end=152),'root':'case chọn nhánh đúng đầu tiên. NORMAL_TIME tại dòng 117 che nhánh cùng guard tại 133. Từ init NORMAL_TIME chỉ luân phiên NORMAL_TIME/MORNING_PEAK; EVENING_PEAK và NIGHT_LOW không đạt được. traffic_mode đọc period cũ nên lệch một bước so với period mới.','observable':'EF(time_period = EVENING_PEAK) và EF(time_period = NIGHT_LOW) đều FALSE. NuSMV in trạng thái đầu NORMAL_TIME cho mỗi phản ví dụ khả đạt; đây không phải vết tuần hoàn đầy đủ. Mười LTL gốc TRUE, gồm kéo theo có tiền đề NIGHT_LOW không đạt được.','v1':cite(V,start=23,end=28),'property':'clock_hour_tick_23','query':'EF(time_period = EVENING_PEAK); EF(time_period = NIGHT_LOW)','log':logref('v0_adaptive_added_queries','EF time_period = EVENING_PEAK'),'gap':'Lịch 24 giờ là mở rộng v1, chưa chứng minh tương đương tổng quát v0/v1. EF chỉ chứng minh tồn tại đường đi, không phải mọi nhánh đều đến period.'},
 {'id':'D03','title':'Nạp thời lượng pha nguồn vào pha đích','v0':cite(D,start=216,end=282),'root':'next(state) và next(timer) cùng tính từ trạng thái cũ. GREEN hết giờ đi sang YELLOW nhưng reset lại nạp 45/30/20; YELLOW hết giờ đi sang GREEN lại nạp 5. LTL cũ X timer=45 kiểm đúng chính hành vi nạp sai nên vẫn TRUE.','observable':'CTL bổ sung yêu cầu hết NS_GREEN vào NS_YELLOW/timer=5 trả FALSE. State 3.31: NS_GREEN, timer=0, traffic_mode=PEAK; State 3.32: NS_YELLOW, timer=45. Đây là kiểm trực tiếp mới, khác N2 cố ý reset thành 1.','v1':cite(V,start=29,end=32),'property':'reset_NS_GREEN_NORMAL','query':'AG((state = NS_GREEN & timer = 0) -> AX(state = NS_YELLOW & timer = 5))','log':logref('v0_adaptive_added_queries','AG ((state = NS_GREEN & timer = 0)'),'gap':'Vàng v0 là 5 theo chú thích/nhánh Yellow duration; v1 là 3 theo config. Sửa cách chọn pha đích kèm đổi tham số; không chạy cùng một công thức nguyên văn trên hai mô hình.'}]
for d in DEFECTS:
 d['v1_validation']=prop(d['property']);d['v1_property_location']=propref(d['property']);d['v1_log']=R[0]['log']+':'+str(CHECKS[norm(prop(d['property']))]['log_line']);d['classification']='Lỗi/ngữ nghĩa hiện hữu, không có dấu hiệu fault-injection; không gán CWE/CERT'
dump('evidence_inventory.json',DEFECTS)
cases=[]
def case(i,category,expected,actual,source,notes=''):cases.append({'id':i,'category':category,'expected':str(expected),'actual':str(actual),'evidence':source,'notes':notes})
for p in P:
 c=CHECKS[norm(p['formula'])];case('CTL-'+p['name'],'fresh NuSMV',True,c['result'],f"{R[0]['log']}:{c['log_line']}",p['formula'])
for n,c in enumerate(local('evidence/json_ctl_recheck.json')['properties'],1):case(f'JSON-{n:02d}','fresh Python JSON',True,c['result'],E+'json_ctl_recheck.json',c['formula'])
for r in R[1:]:
 for n,c in enumerate(r['checks'],1):case(r['id']+f'-{n:02d}','fresh supplemental v0' if r['id'].startswith('v0') else 'fresh negative v1',r['expected'][n-1],c['result'],f"{r['log']}:{c['log_line']}",c['formula'])
for n,g in enumerate(local('evidence/json_graph_recheck.json'),1):case(f'GRAPH-{n:02d}','fresh exhaustive graph','PASS',g['status'],E+'json_graph_recheck.json',f"{g['states']} states / {g['edges']} edges; all lamp labels and edges checked")
case('BDD-01','fresh full-state count',86400,local('evidence/v1_reachable_recheck.json')['reachable_states'],E+'v1_reachable_recheck.log')
hist=obj('chapter1/evidence/graph_results.json')
for key,prefix in [('boundary_tests','BOUND'),('exact_duration_tests','DURATION'),('invalid_configuration_tests','INVALID')]:
 for n,c in enumerate(hist[key],1):case(f'{prefix}-{n:02d}','archived graph test','PASS',c['status'],'chapter1/evidence/graph_results.json',json.dumps(c,ensure_ascii=False))
case('CONFIG-ALT','archived graph test','PASS',hist['alternate_configuration_test'],'chapter1/evidence/graph_results.json')
for r in obj('chapter1/evidence/nusmv_results.json'):
 if r['name'] in ['nusmv_any_start_time','nusmv_period_reachability']:
  for n,c in enumerate(r['checks'],1):case(r['name']+f'-{n:03d}','archived NuSMV',True,c['result'],'chapter1/evidence/'+r['name']+'.log',c['formula'])
browser=obj('chapter1/web/evidence/browser_tests.json');backend=obj('chapter1/web/evidence/backend_tests.json')
for n,c in enumerate(browser['checks'],1):case(f'WEB-{n:02d}','archived browser','PASS',c['status'],'chapter1/web/evidence/browser_tests.json',c['name'])
methods=re.findall(r'^    def (test_\w+)\(',read('chapter1/web/tests/test_backend.py'),re.M);assert len(methods)==backend['tests_run']==13
for n,m in enumerate(methods,1):case(f'API-{n:02d}','archived backend','PASS','PASS (aggregate record)','chapter1/web/evidence/backend_tests.json',m+'; archive gives aggregate result, not individual stdout')
dump('verification_test_cases.json',cases)
with (OUT/'verification_test_cases.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(cases[0]));w.writeheader();w.writerows(cases)
pages=[];current=None

def page(title=None,level=2):
 global current
 current=[];pages.append(current)
 if title:current.append(('heading',title,level))
def heading(s,level=2):current.append(('heading',s,level))
def p(s):current.append(('p',s))
def code(s):current.append(('code',s))
def table(headers,rows):current.append(('table',headers,rows))
def picture(path,caption,width=16):current.append(('image',str(path),caption,width))
def cap(s):current.append(('caption',s))
def snippet(path,start,end,label):cap(label+' — '+cite(path,start=start,end=end));code(excerpt(path,start,end))
def formula(name):cap(propref(name));code(prop(name))
page('1. '+SECTIONS[0],1)
p('TRƯỜNG CÔNG NGHỆ THÔNG TIN — ĐẠI HỌC PHENIKAA')
p('BÁO CÁO ĐỒ ÁN MÔN HỌC\nCSE703153 — Kỹ thuật Lập trình An toàn\nNăm học 2026–2027');current.append(('title',TITLE))
table(['Thông tin','Nội dung'],[['Nhóm / lớp','[SỐ NHÓM] / [MÃ LỚP]'],['Thành viên 1','[HỌ TÊN] — [MSSV]'],['Thành viên 2','[HỌ TÊN] — [MSSV]'],['Thành viên 3','[HỌ TÊN] — [MSSV]'],['Giảng viên hướng dẫn','MSc. Vũ Quang Dũng [nhóm xác nhận phân công thực tế]'],['Kho mã nguồn','[GITHUB URL]'],['Địa điểm, thời gian','Hà Nội, tháng 10 năm 2026']])
p('Lập ngày 24/10/2026 (Asia/Bangkok), sau kiểm kê và kiểm chứng. Nhóm phải điền thông tin thật trong các trường ngoặc vuông trước khi nộp.')
p('Căn cứ: report_guide.pdf, 9 trang PDF, tìm tại Downloads; bản sao và hash trong gói bàn giao. Đây là đồ án Kripke/CTL/NuSMV. D01–D03 là mã lỗi mô hình nội bộ, không phải CWE. Áp dụng CWE/CERT cần giảng viên xác nhận.')
cap('Mục lục trang PDF được tạo ở MUC_LUC_TRANG.md sau phân trang.')
page('2. '+SECTIONS[1],1)
p('Bài toán là điều khiển giao lộ bốn hướng Bắc–Nam và Đông–Tây. Hai hướng đối diện trong cùng nhóm xanh đồng bộ; hai nhóm vuông góc phải loại trừ nhau. Mỗi cột có ba đèn đỏ/vàng/xanh; hết vàng phải có khoảng toàn đỏ để mô hình hóa thời gian dọn giao lộ.')
p('V0 là tập ví dụ độc lập: chu kỳ bốn pha, timer đếm giảm, thích nghi theo time_period, safety/liveness và ví dụ cố ý sai. Chúng chưa tạo bộ điều khiển thống nhất. V1 kế thừa ý tưởng chu kỳ/timer/thích nghi rồi triển khai mới trong chapter1/, không import hay sửa trực tiếp nguồn v0.')
p('Mục tiêu: xác định trạng thái và quan hệ chuyển tiếp, kiểm safety trên 12 đèn, liveness lặp lại, đúng D giây, lịch 24 giờ, thứ tự pha và khả đạt khung giờ. Phạm vi gồm SMV, hai JSON, checker độc lập, log NuSMV và giao diện trình bày.')
picture(OUT/'architecture.png','Hình 2.1. Kiến trúc v1 và phần kế thừa v0. Nguồn: build.py:10–49, intersection.py:48–137, web/verification_worker.py:11–46. Các khối v1 là phần bổ sung; kiến trúc chỉnh sửa được ở architecture.mmd.',16.5)
p('Ngôn ngữ: NuSMV SMV, Python, JavaScript/HTML/CSS. Chủ đề: máy trạng thái, Kripke, CTL, model checking; tuần học/mã đề tài: [TUẦN HỌC / MÃ ĐỀ TÀI] do tài liệu “5 đề tài” chưa cung cấp.')
p('Ngoài phạm vi: cảm biến đếm xe, ưu tiên khẩn cấp, người đi bộ, rẽ trái bảo vệ, hỏng đèn và trễ truyền thông. “Thông minh” là thích nghi theo lịch giờ. Kết quả TRUE của mô hình không chứng minh an toàn vật lý hoặc tối ưu thông lượng giao lộ thực.')
page('3. '+SECTIONS[2],1)
p('Năm bước áp dụng: (1) kiểm kê baseline/yêu cầu; (2) xây Kripke và giả định; (3) sinh JSON/SMV/CTL; (4) kiểm chứng, đọc trace và đối chứng lỗi; (5) đối chiếu trước/sau, hash và giới hạn. Đây là vận dụng của nhóm; guide PDF tr.5 yêu cầu năm bước nhưng không định nghĩa đầy đủ quy trình gốc trong tài liệu đề tài chưa được cung cấp.')
p('K=(S,S₀,R,L): S là trạng thái đạt được; S₀ là trạng thái đầu; R⊆S×S là quan hệ bước giây toàn phần; L:S→2^AP gán mệnh đề nguyên tử. Python State=(phase,remaining,period,entry_period,clock), intersection.py:48–53. SMV có 18 VAR: phase,timer,hour,minute,second,entry_period và 12 boolean đèn; period/clock_sec là DEFINE (SMV:3–37).')
p('S₀: 00:00:00, ALL_RED_EW_TO_NS, timer=2, entry_period=NIGHT_LOW, bốn đèn đỏ bật, các đèn khác tắt (SMV:39–74; config.json:2–3). Một trạng thái gồm pha, timer, clock và đèn; không đồng nhất một pha với một trạng thái Kripke.')
code('clock′=(clock+1) mod 86400; p′=period(clock′)\nr>1: q′=q, r′=r−1, e′=e\nr=1: q′=NEXT(q), r′=D(q′,p′), e′=p′\nLamps′=lamps(q′)')
cap('R diễn giải từ intersection.py:60–74; đây là ký hiệu toán, không phải mã nguồn.')
p('Chu kỳ: NS_GREEN → NS_YELLOW → ALL_RED_NS_TO_EW → EW_GREEN → EW_YELLOW → ALL_RED_EW_TO_NS. MORNING_PEAK 07–09h, EVENING_PEAK 16–19h, NIGHT_LOW 22–06h, NORMAL còn lại. Xanh NS/EW tương ứng 45/35,35/45,15/15,25/25 giây; vàng 3, ALL_RED 2. Chốt entry_period đến hết pha (config.json:4–20).')
p('L sinh từ label(), intersection.py:95–104: 12 nhãn *_on/*_off, phase_*,period_*,entry_*,timer_*,clock_* ở exact và safe/one_hot/reset_ok/transition_ok… write_spec():130–137 ghi description,states,initial,labeling,transitions,suggested_ctl_formulas. build.py:19–26 sinh SMV và JSON. Exact giữ clock; GUI bỏ clock và cho thêm cạnh đổi period hợp lệ.')
p('CTL: A/E là mọi/tồn tại nhánh, X bước kế, F cuối cùng, G luôn, U cho đến (không dùng hiện tại). AG(!conflicting_green), AG(AF(n_green)), AG(EX(TRUE)) lần lượt kiểm safety/liveness/deadlock. NuSMV BDD kiểm 335 CTL đầy đủ; checker JSON chỉ hỗ trợ một toán tử AG/AF/EF/EG/AX/EX với một atom và phủ định tùy chọn, dùng 26 công thức. Nhãn quy tắc phải được kiểm lại trên cạnh bằng oracle độc lập.')
p('Công cụ: Python 3.11, NuSMV 2.7.1; không C/C++ sanitizer/data_gen/seed. Sinh quỹ đạo xác định từ config, state-limit mặc định 1.000.000. Lệnh và danh mục mọi CTLSPEC tại Phụ lục B–D.')
for idx,d in enumerate(DEFECTS):
 page('4. '+SECTIONS[3] if idx==0 else '4. Phân tích lỗ hổng & Bản vá (tiếp)',1 if idx==0 else 2)
 heading('4.'+str(idx+1)+'. '+d['id']+' — '+d['title']);heading('1. Vị trí & mô tả',3);p(d['v0']+'. '+d['classification']+'.')
 heading('2. Nguyên nhân gốc rễ',3);p(d['root']);heading('3. Bằng chứng lỗi tồn tại',3);p(d['observable']);code(d['query']);cap('Truy vấn CTL mới chỉ thêm đặc tả trên bản sao, giữ nguyên chuyển tiếp v0; '+d['log']+'.')
 heading('4. Cách vá',3)
 if idx==0:snippet(T,42,46,'Trước v0');snippet(V,49,50,'Sau v1');p('Chuyển tại remaining=1, miền timer>=1 (SMV:5,30). Pha D giây có đúng D khoảng giây, không chờ timer=0.')
 elif idx==1:snippet(D,117,119,'Trước v0 — nhánh đầu');snippet(D,133,135,'Trước v0 — nhánh bị che');snippet('chapter1/intersection.py',70,74,'Sau v1 — tra lịch clock mới');p('SMV:27–28 là lịch sinh dài tương đương hàm period. Chốt entry_period riêng tại SMV:47–48, không đổi timer khi qua mốc giờ giữa pha.')
 else:snippet(D,216,222,'Trước v0');snippet('chapter1/intersection.py',65,68,'Sau v1');p('SMV:29–32 chọn phase_after rồi D(phase_after,period_next); SMV:48–50 cập nhật latch và timer cùng bước, kiểm cả pha đích và period mới.')
 heading('5. Bằng chứng đã vá',3);formula(d['property']);p(d['v1_log']+' trả TRUE trong lượt mới 335/335. '+('24 ca thời lượng và 42 ranh giới có ở graph_results.json lịch sử; hai JSON được duyệt lại.' if idx!=1 else 'Bốn EF(period) TRUE trong chapter1/evidence/nusmv_period_reachability.log:17–20 (lịch sử), không đổi thành kết quả mới.'));p('Giới hạn: '+d['gap'])
page('4.4. Giới hạn đặc tả và mở rộng — tách khỏi D01–D03')
p('L01 — Safety enum quá yếu: 03_bmc/traffic_light_bmc.smv kiểm G !(state=NS_GREEN & state=EW_GREEN), hiển nhiên đúng do miền enum. Đây là giới hạn đặc tả, không có bằng chứng đồng xanh trong file đó. V1 kiểm 12 boolean, one-hot, đồng bộ (SMV:76–90). N1 xác nhận thuộc tính mới nhạy với lỗi đầu ra, không phải counterexample v0.')
s='Smart-Traffic-Light-Verification/03_bmc/traffic_light_bmc.smv';n=line(s,'LTLSPEC');snippet(s,n,min(n+14,len(read(s).splitlines())),'Trước v0');snippet(V,34,36,'Sau v1');formula('physical_green_exclusion')
p('L02 — Đổi/siết yêu cầu vàng/all-red: safety_liveness.smv:25–28,37–96 cho (NS=GREEN,EW=RED) → (NS=YELLOW,EW=GREEN). Đây là vết suy từ ASSIGN, không phải counterexample log cũ. Bốn LTL gốc TRUE; yêu cầu vàng đối diện đỏ chưa có. LTL cấm cả hai RED tại 125–135 mâu thuẫn clearance v1, nên không tuyên bố bảo toàn mọi LTL v0.')
snippet('Smart-Traffic-Light-Verification/04_verification/safety_liveness.smv',42,44,'V0 — NS GREEN sang YELLOW');snippet('Smart-Traffic-Light-Verification/04_verification/safety_liveness.smv',76,78,'V0 — EW RED sang GREEN');formula('yellow_ns_other_red');formula('advance_NS_YELLOW')
p('Mở rộng v1: 12 đèn, hai all-red, clock 24 giờ, latch, JSON và web. Không gọi thêm tính năng là vá CWE. Emergency v0 chưa tích hợp. traffic_light_bmc_bug.smv chỉ MODULE main; hai fixture test chưa SPEC; test.smv gốc là đăng nhập ngoài nghiệp vụ.')
p('Mẫu v0 cố ý sai: init_bug.smv khởi tạo GREEN/GREEN; hai transition_bug.smv bỏ S1. Archive có ba FALSE trong 28 công thức. transition_bug_fixed.smv đã TRUE. Không tính những mẫu này vào D01–D03 hoặc gán cho v1.')
page('4.5. Thí nghiệm cấy lỗi N1 và N2')
p('Negative là bản sao v1 kiểm độ nhạy đặc tả. Giữ riêng nguồn hợp lệ; harness đạt khi thuộc tính FALSE dự kiến và có counterexample. Không gán fault chủ đích thành lỗi gốc.')
heading('N1 — Xanh Đông đồng thời NS_GREEN')
snippet(V,68,68,'Trước — v1 chính thức');n=line('chapter1/evidence/negative_conflicting_green.smv','next(e_green)');snippet('chapter1/evidence/negative_conflicting_green.smv',n,n,'Sau — N1');code('CTLSPEC AG(!conflicting_green);');cap(logref('recheck_negative_conflicting_green','is false')+' — FALSE.')
code(match_excerpt(E+'recheck_negative_conflicting_green.log','-> State: 1.3',0,11))
p('t=2s: n_green=s_green=e_green=TRUE, conflicting_green=TRUE; w_green không đổi nên FALSE. Enum phase vẫn NS_GREEN. Đây là lỗi đầu ra mà safety enum không quan sát được.')
heading('N2 — Reset mọi pha thành 1')
snippet(V,50,50,'Trước — v1 chính thức');n=line('chapter1/evidence/negative_timer_reset.smv','next(timer)');snippet('chapter1/evidence/negative_timer_reset.smv',n,n,'Sau — N2')
code('AG((phase = ALL_RED_EW_TO_NS & timer = 1 &\n    period_next = NIGHT_LOW) -> AX(timer = 15))');cap(logref('recheck_negative_timer_reset','is false')+' — FALSE.')
code(match_excerpt(E+'recheck_negative_timer_reset.log','-> State: 1.2',0,13))
p('t=1s timer=1; t=2s vào NS_GREEN nhưng timer không in lại vì vẫn 1, thay vì 15 NIGHT_LOW. Trace NuSMV in theo thay đổi; phải kế thừa giá trị. N2 khác D03 nạp thời lượng pha nguồn.')
page('4.6. Thí nghiệm N3 — Bỏ qua ALL_RED')
p('Fault chỉ đổi nhánh NS_YELLOW trong phase_after để đi thẳng EW_GREEN. Miền enum vẫn có ALL_RED; việc có tên pha không chứng minh clearance được đi qua.')
cap('Trước — '+cite(V,start=29)+'; nguyên dòng được ngắt khi trình bày, không sửa mã:');code(excerpt(V,29,29));n=line('chapter1/evidence/negative_skip_all_red.smv','phase_after :=');cap('Sau — '+cite('chapter1/evidence/negative_skip_all_red.smv',start=n));code(excerpt('chapter1/evidence/negative_skip_all_red.smv',n,n))
code('CTLSPEC AG((phase = NS_YELLOW & timer = 1) -> AX(all_red));');cap(logref('recheck_negative_skip_all_red','is false')+' — FALSE; log đầy đủ trong evidence/.')
code(match_excerpt(E+'recheck_negative_skip_all_red.log','-> State: 1.20',0,21))
p('State 1.20 t=19s: NS_YELLOW/timer=1. State 1.21 t=20s: EW_GREEN, e_red=w_red=FALSE; all_red không in lại nên vẫn FALSE. Không có ALL_RED_NS_TO_EW xen giữa. N3 khác lỗi mẫu v0 bỏ YELLOW.')
heading('Độ nhạy và chuyển tiếp đúng')
p('Ba negative mới: mỗi mô hình đúng một thuộc tính, cả ba FALSE dự kiến. Không có bằng chứng chạy cả 335 CTL trên mỗi negative. PASS harness nghĩa là bắt được lỗi, không phải mô hình lỗi đúng. V1 chính thức TRUE ở safety/reset/advance/clearance.')
formula('advance_NS_YELLOW');formula('clearance_all_red')
p('Cần kiểm giữ pha khi timer>1, đổi đúng pha khi timer=1, reset theo pha đích/period mới, cập nhật 12 đèn theo phase_next. Chỉ mutex không bắt mọi lỗi bỏ pha. verify_graph.py:27–64 kiểm độc lập nhãn và các cạnh JSON đã lưu.')
page('5. '+SECTIONS[4],1)
p('Bảng 5.1. D01–D03 khớp 1–1 với mục 4.1–4.3. CWE/CERT chưa gán vì chưa có căn cứ phân loại. Tên log ngắn trong bảng thuộc thư mục evidence/ của gói báo cáo, trừ khi ghi rõ log gốc.')
table(['Mã / vị trí v0','Trạng thái v0 có thể kiểm','Trạng thái v1 / công cụ'],[
 ['D01\n'+cite(T,start=42,end=46),'CTL mới FALSE: timer=1 → 0, vẫn NS_GREEN; v0_timer_added_query.log:17,80–83.','SMV:30,50 đổi tại timer=1. advance_NS_GREEN TRUE ở log mới; 24 ca thời lượng lưu trữ.'],
 ['D02\n'+cite(D,start=117,end=135),'EF EVENING_PEAK/NIGHT_LOW đều FALSE; v0_adaptive_added_queries.log:17–28.','Clock tra period; 4 EF TRUE ở chapter1/evidence/nusmv_period_reachability.log:17–20; clock_* TRUE mới.'],
 ['D03\n'+cite(D,start=216,end=282),'Reset vàng=5 FALSE; State 3.31 NS_GREEN/0 → 3.32 NS_YELLOW/45 trong log adaptive mới.','SMV:29–32,48–50 reset theo D(pha đích,period mới); reset_NS_GREEN_NORMAL TRUE mới.']])
p('Bảng 5.2. Những hạng mục khác không cộng vào ba lỗi gốc ở trên.')
table(['Loại','Before / giới hạn','After / bằng chứng'],[['L01: đặc tả yếu','Enum không quan sát lỗi đầu ra.','12 boolean + safety/one-hot; N1 FALSE khi bị cấy lỗi.'],['L02: siết yêu cầu','YELLOW/GREEN suy từ code; cấm cả hai RED.','Vàng đối diện đỏ + all-red; CTL TRUE; không bảo toàn yêu cầu cấm cùng RED.'],['Mở rộng','Thiếu mô hình clock/12 đèn/web thống nhất.','Exact 86400 nút/cạnh; chiếu 1012/2548; adapter web.'],['N1–N3 chủ đích','Đồng xanh/reset=1/bỏ ALL_RED.','3 thuộc tính FALSE dự kiến, có trace; khác lỗi gốc v0.']])
p('Số TRUE tăng không phải tỉ lệ sửa lỗi: v0/v1 khác yêu cầu, tham số và biểu diễn. Chưa có bisimulation/refinement tổng quát. Chỉ ghi v0 FALSE cho truy vấn thực sự đã chạy; không biến nhận xét đọc code thành kết quả công cụ.')
page('6. '+SECTIONS[5],1)
heading('6.1. Kết quả tách theo công cụ và thời điểm')
p('Audit hoàn tất trước soạn thảo: '+str(A['inventoried_files'])+' tệp nội dung dự án, loại runtime/thư viện/cache. Mọi tệp có trước khớp hash. Mã sinh từ config/Python trùng toàn văn SMV/properties; v1 trùng bản nusmv_main.smv của archive.')
table(['Phép kiểm / nguồn','Số lượng','Kết quả / log'],[['NuSMV v1, mới','335 CTL','335 TRUE; evidence/v1_main_recheck.log'],['V0 + query, mới','4 CTL mới + 12 LTL gốc','4 FALSE dự kiến; 12 TRUE; evidence/v0_*.log'],['Negative v1, mới','3 mô hình × 1 CTL','3 FALSE có trace; evidence/recheck_negative_*.log'],['BDD toàn bộ v1, mới','86400 reachable','v1_reachable_recheck.log; đếm không -coi'],['Python JSON CTL, mới','26 CTL trên bản chiếu','26 TRUE; json_ctl_recheck.json; khác NuSMV/SecLab'],['Duyệt JSON, mới','2 đồ thị','Exact 86400/86400; chiếu 1012/2548; 0 deadlock'],['NuSMV clock đầu bất kỳ, archive','335 CTL','335 TRUE; chapter1/evidence/nusmv_any_start_time.log'],['NuSMV period, archive','4 EF','4 TRUE; nusmv_period_reachability.log'],['SecLab Ch1 gốc, archive','26 CTL + parser exact','26 PASS, mutex PASS, 0 deadlock; seclab_results.json'],['Biên / thời lượng / config, archive','42 / 24 / 4 sai + 1 thay thế','PASS; graph_results.json'],['Web, archive','13 backend + 32 browser checks','PASS; chapter1/web/evidence/*_tests.json']])
p('Không cộng CTL, số trạng thái và ca giao diện thành một tổng test. Record riêng có '+str(len(cases))+' dòng truy vết, phân loại mới/lưu trữ và đơn vị. Chứng cứ gốc chỉ được đọc lại, không đổi thành lượt mới.')
p('NuSMV 2.7.1 dùng BDD/CTL, -dynamic -df -coi. Banner MiniSat không chứng minh đã chạy SAT/BMC. Harness kiểm đủ số công thức và từng true/false; exit code 0 riêng lẻ chưa đủ. Thời điểm chạy mới từ fresh_nusmv_results.json (UTC), không dùng ngày biên soạn thay ngày chạy archive.')
page('6.2. Log, nhóm CTL và hai đồ thị')
table(['Nhóm CTL','Số công thức'],[[k,str(v)] for k,v in A['v1_property_groups'].items()]+[['Tổng','335']]);cap('Bảng 6.2. Đếm properties.json và CTLSPEC NAME trong SMV:76–410; mọi công thức/file/dòng ở ctl_catalog.json.')
code(match_excerpt(E+'v1_main_recheck.log','AG !conflicting_green',0,4));cap('Trích 6.1. Log v1 mới; '+logref('v1_main_recheck','AG !conflicting_green')+'. Bản đầy đủ ở evidence/.')
code(match_excerpt(E+'v1_reachable_recheck.log','system diameter',0,1));cap('Trích 6.2. '+logref('v1_reachable_recheck','reachable states')+'. Số 86400 dành cho S₀ mặc định, không mặc định cho cấu hình khác hoặc clock đầu bất kỳ.')
p('Exact: 86400 trạng thái/cạnh, một quỹ đạo về chỉ số 0. Bản chiếu giữ (q,r,p,e), bỏ clock, thêm đổi period nên có 1012 trạng thái/2548 cạnh. build.py:28–38 kiểm mọi cạnh exact chiếu vào cạnh abstract; audit mới duyệt lại nhãn, đèn, timer, cạnh và liveness trên cả hai JSON.')
p('Phép chiếu giữ AP chung về đèn/timer. Safety/liveness phổ quát trên abstract áp dụng cho các đường exact được mô phỏng. Không suy EF abstract thành EF exact; khả đạt period exact được kiểm riêng bằng NuSMV. Abstract có thể giữ period mãi nên không dùng AF(period_*) chứng minh lịch chính xác.')
p('AF(green) của JSON được kiểm từ S₀; tập thỏa thực tế là toàn bộ 1012 trạng thái. Reverse-worklist độc lập cũng chứng minh cuối cùng xanh từ mọi trạng thái. NuSMV dùng AG(AF(green)). Chờ xanh lớn nhất 55 giây mỗi hướng trong bản chiếu là số của mô hình, không phải đo xe ngoài đường.')
page('6.3. Ảnh giao diện và nguồn lưu trữ')
picture(ROOT/'chapter1/web/evidence/screenshots/02-kripke.png','Hình 6.1. Ảnh Kripke có sẵn: chapter1/web/evidence/screenshots/02-kripke.png. Minh họa duyệt trạng thái/nhãn, không thay stdout hay đếm BDD.',16)
picture(ROOT/'chapter1/web/evidence/screenshots/03-kiem-chung-moi.png','Hình 6.2. Ảnh web có sẵn: chapter1/web/evidence/screenshots/03-kiem-chung-moi.png. Ngày/mã lượt đối chiếu browser_tests.json; không đại diện lượt báo cáo mới.',16)
p('Ảnh sao chép nguyên byte, hash trong source_inventory.json. 32 browser checks không phải 32 CTL. backend_tests.json ghi tổng hợp 13 unittest, không failures/errors; không có stdout từng method, record ghi rõ mức chứng cứ này.')
p('V0 archive: output/nusmv_results.json có 14 bản ghi, 28 công thức =25 TRUE+3 FALSE; FALSE thuộc mẫu lỗi minh họa. Ba file chưa SPEC không có PASS nghiệp vụ. before_v0_logs/*.stdout.log là trích nguyên văn archive, không có timestamp/lệnh đầy đủ; không bổ sung hồi tố.')
page('7. '+SECTIONS[6],1)
heading('Nếu bắt đầu lại, nhóm thiết kế lại phần nào?')
p('Nhóm sẽ đặc tả đơn vị thời gian, cách lấy thời lượng pha đích và lịch trước ASSIGN. Một nguồn ngữ nghĩa chuyển tiếp cùng oracle độc lập giúp tránh guard trùng và nhầm trạng thái cũ/mới. Safety phải dựa trên đầu ra, kèm thứ tự pha và khả đạt, tránh enum hiển nhiên đúng hoặc kéo theo đúng rỗng.')
heading('Điều gì còn nghi ngờ hoặc thiếu bằng chứng?')
p('Chưa có refinement/bisimulation tổng quát giữa các ví dụ v0 và v1; chưa có lỗi đèn, cảm biến, truyền thông hay ưu tiên khẩn cấp. Đây là phạm vi chưa mô hình hóa, không phải lỗ hổng đã xác nhận. SecLab đã kiểm headless nhưng chưa xác nhận thao tác nạp trong cửa sổ GUI; ảnh web chỉ chứng minh giao diện web.')
heading('Bài học phương pháp luận lớn nhất')
p('Model checking trả lời đặc tả trên tập hành vi đã mô hình hóa. Mười LTL adaptive v0 đều TRUE vẫn đi cùng nhánh giờ không đạt được và reset sai mục đích; cần non-vacuity và đọc vết theo giá trị kế thừa. Fault chủ đích kiểm độ nhạy, không chứng minh tập thuộc tính đầy đủ cho mọi lỗi.')
heading('Giới hạn và phát triển')
p('Đổi thời lượng có thể tạo quỹ đạo nhiều ngày, phải dựng/đếm lại. JSON exact khoảng 55 MB khó dùng trong GUI; graph chiếu dễ xem nhưng mất clock và thêm nhánh. Có thể thiết kế trừu tượng thời gian với chứng minh quan hệ mô phỏng/AP, rồi thêm cảm biến và ưu tiên có giới hạn để kiểm liveness dưới tải thay đổi.')
p('Bước tiếp theo cần mô hình plant/thiết bị, người đi bộ/rẽ trái, trễ thực và thẩm định giao thông. TRUE hiện tại không chứng minh an toàn vật lý hay thông lượng. Không thêm fairness để che nhánh treo; giả định fairness mới phải được nêu và kiểm tác động.')
p('Về bằng chứng: tách ngày viết/ngày chạy, công cụ NuSMV/JSON/SecLab và archive/lượt mới; giữ baseline bằng hash, log nguyên văn, query thêm có nhãn rõ. Báo cáo không tạo commit, danh tính hay mã CWE/CERT giả.')
page('8. '+SECTIONS[7],1)
heading('A. Cấu trúc gói và cách đọc')
p('Đường dẫn tính từ gốc NuSMV_project; tên evidence/ ngắn khi ghi rõ gói báo cáo thuộc output/official_report_20261024/. file:dòng dùng số dòng thật. JSON một dòng dùng khóa/chỉ số, không bịa dòng con. Mọi đầu ra mới nằm riêng trong gói này.')
table(['Tệp / thư mục','Vai trò'],[['BAO_CAO_CHINH_THUC.docx/.pdf','Bản chỉnh sửa và PDF nộp'],['KIEM_KE_BANG_CHUNG.md / evidence_inventory.json','Kiểm kê trước viết, lỗi và khoảng trống'],['BIEN_BAN_KIEM_CHUNG.docx/.pdf','Record riêng expected/actual/log'],['verification_test_cases.csv/.json','Toàn bộ '+str(len(cases))+' dòng truy vết'],['source_inventory.json/.csv','243 tệp nội dung, bytes/hash'],['evidence_index.csv','Mọi bằng chứng/lượt web đã kiểm kê'],['ctl_catalog.json / all_ctlspec_declarations.json','335 công thức chính thức và mọi CTLSPEC artifact'],['evidence/ / appendix_repository/','Log mới / bản sao nguyên văn archive'],['PHU_LUC_NGUON_VA_BANG_CHUNG.zip','Nguồn và log đầy đủ kể cả lượt web, hai JSON; không runtime/cache'],['architecture.mmd/.png','Sơ đồ kiến trúc chỉnh sửa được'],['CHECKLIST_TIEU_CHI.md','Checklist trực tiếp từ PDF trường'],['MUC_LUC_TRANG.md / quality_validation.json','Mục lục trang thật / kiểm tra đầu ra']])
p('Phụ lục điện tử là phần nộp kèm: log nguyên văn tại evidence/, appendix_repository/ và ZIP. Thân bài trích có caption/số dòng; không in lại hàng trăm dòng lặp. Mọi source/log đều truy bằng chỉ mục và SHA-256. Cần giảng viên xác nhận chấp nhận phụ lục điện tử nộp kèm.')
heading('Mục lục')
p('Tám mục và phụ lục có số trang PDF thật ở MUC_LUC_TRANG.md; tạo sau render, không điền số trang giả trước phân trang.')
page('B. Lệnh tái lập và tham số')
p('PowerShell tại gốc dự án, Python 3.11+, NuSMV trên PATH. Không data_gen/seed: dữ liệu xác định từ config. Các lệnh sản phẩm sau có ghi đè artifact sinh; chỉ cung cấp hướng dẫn, không chạy trong tác vụ báo cáo:')
code('python chapter1/build.py --state-limit 1000000\npython chapter1/verify_graph.py\npython chapter1/verify_nusmv.py\npython chapter1/count_nusmv.py\npowershell -NoProfile -ExecutionPolicy Bypass -File chapter1/run_seclab.ps1 -ScriptPath chapter1/verify_target.py\npython chapter1/web/server.py')
p('Tái lập chiến dịch báo cáo trong thư mục riêng:')
code('python -B output/official_report_20261024/audit_report.py\npython -B output/official_report_20261024/build_official_report.py\nnode output/official_report_20261024/render_pdf.mjs\npython -B output/official_report_20261024/validate_delivery.py')
p('Lệnh NuSMV thực tế (đường dẫn tuyệt đối trong results JSON):')
code('NuSMV -dynamic -df -coi <delivery>/evidence/v1_main_recheck.smv\nNuSMV -dynamic -r -is -ils -ii <delivery>/evidence/v1_main_recheck.smv')
p('V0 bổ sung giữ prefix nội dung gốc, chỉ thêm CTLSPEC cuối file. Timer:2 LTL TRUE+1 CTL FALSE. Adaptive:10 LTL TRUE+3 CTL FALSE. NuSMV có thể in CTL trước LTL; đối chiếu công thức và số lượng thay vì mặc định thứ tự nguồn.')
table(['Lượt mới','Bắt đầu UTC','Số thuộc tính'],[[r['id'],r['started_utc'],str(len(r['checks']))+'; '+r['status']+' theo expected'] for r in R])
p('UTC cộng 7 giờ để đổi sang Asia/Bangkok/Việt Nam. Thời gian chạy thật và lệnh trong fresh_nusmv_results.json; không so thời gian checker để kết luận tối ưu giao thông.')
page('C. Nguồn v0 và vai trò')
old=obj('output/nusmv_results.json');mapping=obj('chapter1/evidence/before_after_audit.json')['mapping']
table(['Mã / đường dẫn','TRUE/FALSE gốc','Phân loại'],[[m['id']+'\n'+r['file'],str(sum(x['result']=='true' for x in r['properties']))+'/'+str(sum(x['result']=='false' for x in r['properties'])),m['classification']] for m,r in zip(mapping,old)])
p('Stdout: chapter1/evidence/before_v0_logs/<V0-id>_<stem>.stdout.log; JSON audit có array index/hash; phụ lục giữ bản nguyên văn. output/excel_graph_check.* là đồ thị trộn lịch sử của tác vụ Excel đã hủy; không biến bảy FALSE của nó thành bảy lỗi giao lộ, không chạy lại workflow Excel.')
cap('kripke_model.png gốc: 0 byte, không dùng. Hình 2.1 có nguồn Mermaid, không phải ảnh thí nghiệm.')
page('D. Biến, AP và toàn bộ CTLSPEC')
table(['Thành phần','Vị trí'],[['VAR / DEFINE','SMV:3–37; 18 VAR, 12 boolean; period là DEFINE'],['Init / next','SMV:39–74; intersection.py:60–74'],['S,S₀,R,L JSON','intersection.py:48–53,95–137; build.py:19–38'],['335 CTLSPEC NAME','SMV:76–410; ctl_catalog.json ghi name/formula/category/source_line'],['26 CTL JSON','intersection.py:106–109; suggested_ctl_formulas ở hai JSON'],['Mọi CTLSPEC artifact','all_ctlspec_declarations.json: '+str(A['ctlspec_declarations_all_artifacts'])+' khai báo, gồm snapshot/fault lặp; không phải yêu cầu độc lập'],['Nguồn / bằng chứng đầy đủ','source_inventory.json/.csv; evidence_index.csv có path/bytes/hash và nguồn sao phụ lục']])
for name in ['timer_bounds','hold_NS_GREEN','advance_NS_YELLOW','reset_ALL_RED_EW_TO_NS_NIGHT_LOW','latch_NORMAL','deadlock_free']:formula(name)
p('Các mẫu trên TRUE trong log v1 mới; danh mục máy đọc giữ toàn bộ 335 công thức. all_ctlspec_declarations.json phân biệt v1 chính thức, negative, query thêm và snapshot. Số khai báo tổng không phải số test duy nhất.')
page('E. Phân công và phản hồi giảng viên')
table(['Thành viên / MSSV','Công việc thật','Chứng cứ đóng góp'],[['[HỌ TÊN — MSSV]','[MÔ HÌNH / ĐẶC TẢ / NGÀY]','[FILE / COMMIT THẬT NẾU CÓ]'],['[HỌ TÊN — MSSV]','[KIỂM CHỨNG / TRACE]','[LOG / COMMIT THẬT]'],['[HỌ TÊN — MSSV]','[WEB / TÀI LIỆU / TEST]','[FILE / COMMIT THẬT]']]);cap('Bảng E.1. Placeholder, không suy đoán tác giả từ tên tệp.')
table(['Ngày / người góp ý','Nội dung cần xác nhận','Xử lý / trạng thái'],[['[NGÀY — GIẢNG VIÊN]','D01–D03 thay mã CWE/CERT cho lỗi mô hình?','[PHẢN HỒI] — Chờ'],['[NGÀY — GIẢNG VIÊN]','Giữ tên v0/v1 hiện có, bảng ánh xạ thay hậu tố?','[PHẢN HỒI] — Chờ'],['[NGÀY — GIẢNG VIÊN]','Mã đề tài/tuần học và quy trình 5 bước gốc?','[TÀI LIỆU ĐỀ TÀI] — Thiếu'],['[NGÀY — GIẢNG VIÊN]','Chấp nhận log đầy đủ trong phụ lục điện tử?','[PHẢN HỒI] — Chờ']])
p('Còn thiếu danh tính, lớp, nhóm, GitHub và phân công thật; tài liệu đề tài để xác định tuần/mã đề tài; quyết định chấm CWE/CERT, tên phiên bản và phụ lục điện tử. Audit mới đã bù counterexample trực tiếp timer/reset/reachability; không còn gọi các truy vấn này là chưa chạy.')
p('Chưa có thử giao lộ vật lý, cảm biến, emergency hoặc thao tác GUI SecLab. Timestamp/lệnh đầy đủ của v0 archive vẫn thiếu; lượt query mới có provenance riêng, không sửa lịch sử.')
page('F. Checklist tiêu chí theo report_guide.pdf')
table(['Tiêu chí bảng 3, PDF tr.8','Trọng số','Đối chiếu'],[['Đầy đủ cấu trúc 8 phần','10%','Đủ tám Heading 1, đúng tên/thứ tự'],['Chất lượng phân tích lỗ hổng (Phần 4)','35%','D01–D03 đủ 5 mục; CWE/CERT chờ giảng viên'],['Bảng before/after (Phần 5)','15%','D01–D03 khớp 1–1, trạng thái gắn log'],['Chất lượng bằng chứng (Phần 6)','20%','Log nguyên văn, chỉ mục/hash; tách công cụ và lượt; phụ lục điện tử'],['Chiều sâu phản biện (Phần 7)','10%','Ba câu hỏi, giới hạn Kripke/CTL cụ thể'],['Định dạng & trình bày','10%','Times New Roman 11.5pt, A4 lề2cm, trang/caption; quy ước phiên bản cần duyệt']])
p('Tổng 100%, độc lập tiêu chí mã nguồn. Không tự chấm điểm hoặc hứa mức điểm.')
p('Checklist PDF tr.8–9: đủ tám phần; phân loại lỗi cụ thể; đủ năm mục/lỗi; bảng khớp; log/ảnh có caption; v0 nguyên vẹn; lệnh build; data_gen/seed ghi không áp dụng thay bằng config/hash; phản biện cụ thể; PDF mở/font/đủ trang. CWE/CERT và tên phiên bản chờ giảng viên, không tự đánh dấu đạt.')
p('Độ dài gợi ý: bìa1, tổng quan1–1.5, phương pháp1, phân tích3–6, bảng1, bằng chứng1–3, phản biện0.5–1, phụ lục không giới hạn. Kiểm trang thực trong quality_validation.json.')
p('Tham chiếu: [G1] report_guide.pdf, Phenikaa, CSE703153, 2026–2027, PDF tr.3–9. [R1] Mã/log trong source_inventory.json, truy cập 24/10/2026. [R2] chapter1/BEFORE_AFTER_V0_V1.md và evidence/before_after_audit.json; đối chiếu lại với source/hash/log trước viết.')
REPORT_PAGES=pages
def render_doc(name,content):
 doc=Document();sec=doc.sections[0];sec.page_width=Cm(21);sec.page_height=Cm(29.7)
 sec.top_margin=sec.bottom_margin=sec.left_margin=sec.right_margin=Cm(2)
 normal=doc.styles['Normal'];normal.font.name='Times New Roman';normal.font.size=Pt(11.5)
 normal.paragraph_format.space_after=Pt(5);normal.paragraph_format.line_spacing=1.04
 for s in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption']:
  doc.styles[s].font.name='Times New Roman';doc.styles[s]._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Times New Roman')
 for s,size in [('Heading 1',16),('Heading 2',13),('Heading 3',11.5)]:doc.styles[s].font.size=Pt(size);doc.styles[s].font.color.rgb=RGBColor.from_string('172D42')
 doc.styles['Caption'].font.size=Pt(9);doc.styles['Caption'].font.italic=True
 footer=sec.footer.paragraphs[0];footer.alignment=1;run=footer.add_run('Trang ');run.font.name='Times New Roman';run.font.size=Pt(9)
 field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
 hpages=[];markdown=[]
 for ix,items in enumerate(content):
  if ix:doc.add_page_break()
  bits=[]
  for item in items:
   kind=item[0]
   if kind=='heading':
    _,s,l=item;doc.add_heading(s,l);bits.append(f'<h{l}>'+html.escape(s)+f'</h{l}>');markdown.append('#'*l+' '+s)
   elif kind=='title':
    doc.add_paragraph(item[1],style='Title');bits.append('<p class="title">'+html.escape(item[1])+'</p>');markdown.append(item[1])
   elif kind in ['p','caption']:
    doc.add_paragraph(item[1],style='Caption' if kind=='caption' else 'Normal');bits.append('<p'+(' class="caption"' if kind=='caption' else '')+'>'+html.escape(item[1]).replace('\n','<br>')+'</p>');markdown.append(item[1])
   elif kind=='code':
    for s in item[1].splitlines():
     for j,wrapped in enumerate(textwrap.wrap(s,104,replace_whitespace=False,drop_whitespace=False,break_long_words=True,break_on_hyphens=False) or ['']):
      q=doc.add_paragraph();q.paragraph_format.space_after=Pt(0);q.paragraph_format.line_spacing=1
      r=q.add_run(('      > ' if j else '')+wrapped);r.font.name='Consolas';r.font.size=Pt(8.5)
    bits.append('<pre>'+html.escape(item[1])+'</pre>');markdown.append('```text\n'+item[1]+'\n```')
   elif kind=='table':
    _,headers,rows=item;t=doc.add_table(rows=1,cols=len(headers));t.style='Table Grid';t.autofit=False
    for c in t.columns:c.width=Cm(17/len(headers))
    repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
    for c,s in zip(t.rows[0].cells,headers):c.text=str(s)
    for values in rows:
     for c,s in zip(t.add_row().cells,values):c.text=str(s)
    for i,row in enumerate(t.rows):
     for cell in row.cells:
      for q in cell.paragraphs:
       q.paragraph_format.space_after=Pt(3);q.paragraph_format.line_spacing=1
       for r in q.runs:r.font.name='Times New Roman';r.font.size=Pt(9);r.bold=i==0
    bits.append('<table><thead><tr>'+''.join('<th>'+html.escape(str(s))+'</th>' for s in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(str(s)).replace('\n','<br>')+'</td>' for s in row)+'</tr>' for row in rows)+'</tbody></table>')
    markdown.append('| '+' | '.join(headers)+' |\n|'+'---|'*len(headers)+'\n'+'\n'.join('| '+' | '.join(str(s).replace('\n','; ') for s in row)+' |' for row in rows))
   elif kind=='image':
    _,path,caption,width=item;doc.add_picture(path,width=Cm(width));doc.add_paragraph(caption,style='Caption')
    bits.append('<figure><img src="'+Path(path).as_uri()+'"><figcaption>'+html.escape(caption)+'</figcaption></figure>');markdown.append('!['+caption+']('+Path(path).as_posix()+')')
   markdown.append('')
  hpages.append('<section>'+''.join(bits)+'</section>')
 doc.core_properties.title=TITLE if name=='BAO_CAO_CHINH_THUC' else name
 doc.core_properties.author='[NHÓM THỰC HIỆN]';doc.core_properties.subject='Kripke, CTL, NuSMV — bằng chứng kiểm tra'
 doc.save(OUT/(name+'.docx'))
 css='''@page{size:A4;margin:20mm;@bottom-center{content:"Trang " counter(page);font:9pt "Times New Roman";}}*{box-sizing:border-box}body{margin:0;color:#111;font:11.5pt/1.06 "Times New Roman",serif}section+section{break-before:page}p{margin:0 0 5pt;orphans:2;widows:2}h1{font-size:16pt;margin:0 0 10pt;color:#172d42}h2{font-size:13pt;margin:10pt 0 6pt;color:#172d42}h3{font-size:11.5pt;margin:7pt 0 4pt}h1,h2,h3{break-after:avoid}.title{font-size:22pt;font-weight:bold;text-align:center;margin:20pt 0}pre{font:8.5pt/1.1 Consolas,monospace;white-space:pre-wrap;overflow-wrap:anywhere;word-break:break-word;background:#f4f5f6;padding:5pt;margin:4pt 0 7pt}table{border-collapse:collapse;table-layout:fixed;width:100%;font-size:9pt;line-height:1.08;margin:6pt 0 8pt}td,th{border:.5pt solid #7e8c96;text-align:left;vertical-align:top;padding:4pt;overflow-wrap:anywhere}th{background:#e9eef2}thead{display:table-header-group}tr{break-inside:avoid}.caption,figcaption{font-size:9pt;font-style:italic;color:#364555;margin:3pt 0 7pt}figure{margin:5pt 0 8pt;break-inside:avoid}img{display:block;max-width:100%;max-height:82mm;object-fit:contain;margin:0 auto}'''
 (OUT/(name+'.html')).write_text('<!doctype html><html lang="vi"><meta charset="utf-8"><title>'+name+'</title><style>'+css+'</style><body>'+''.join(hpages)+'</body></html>',encoding='utf-8')
 (OUT/(name+'.md')).write_text('\n'.join(markdown),encoding='utf-8')
render_doc('BAO_CAO_CHINH_THUC',REPORT_PAGES)
pages=[];page('BIÊN BẢN KIỂM CHỨNG HÌNH THỨC')
p('Đề tài: '+TITLE);p('Lập ngày 24/10/2026; nhóm/người kiểm: [HỌ TÊN — MSSV]. Baseline v0/v1 giữ nguyên. Log mới trong output/official_report_20261024/evidence/.')
p('Mục tiêu: tái kiểm v1, xác nhận D01–D03 bằng query thêm trên bản sao v0, đánh giá N1–N3 và JSON. Đây là kiểm chứng mô hình; web archive ghi riêng, không tuyên bố chạy lại.')
table(['Tiền điều kiện / môi trường','Giá trị'],[['Công cụ','Python 3.11; NuSMV 2.7.1; checker JSON độc lập'],['Đầu vào','config.json, smart_intersection.smv; hash trong source_inventory.json'],['S₀','00:00:00, ALL_RED_EW_TO_NS, timer=2, bốn đỏ bật'],['Lệnh','python -B output/official_report_20261024/audit_report.py'],['Tiêu chí đạt','Đúng số công thức, exit0, từng actual khớp expected; negative phải FALSE']])
table(['Ca / nhóm','Expected','Actual / log'],[['335 CTL v1','335 TRUE','335 TRUE; v1_main_recheck.log'],['D01: timer tại 1','FALSE v0','FALSE; v0_timer_added_query.log:17'],['D02: hai EF','2 FALSE v0','2 FALSE; v0_adaptive_added_queries.log:17–28'],['D03: reset vàng=5','FALSE v0','FALSE; v0_adaptive_added_queries.log:29 trở đi'],['12 LTL v0 đi kèm','Giữ TRUE gốc','12 TRUE trong hai log query; không sửa R'],['N1/N2/N3','1 FALSE/mô hình + trace','3 FALSE; recheck_negative_*.log'],['JSON CTL','26 TRUE','26 TRUE; json_ctl_recheck.json'],['Exact/chiếu','86400/86400;1012/2548','Khớp; json_graph_recheck.json'],['BDD reachable','86400','86400; v1_reachable_recheck.log']])
p('CSV/JSON riêng liệt kê '+str(len(cases))+' dòng expected/actual/evidence/notes. Không coi số dòng là số yêu cầu độc lập; có lượt chạy khác nhau và các đơn vị khác nhau.')
page('Chi tiết quy trình, phạm vi và kết luận record')
for d in DEFECTS:
 heading(d['id']+' — '+d['title']);p('Nguồn: '+d['v0']+'. Query: '+d['query']+'. Expected=FALSE v0, actual=FALSE; '+d['log']+'. Sau cải tiến: '+d['v1_property_location']+' TRUE tại '+d['v1_log']+'.')
p('N1–N3: bản sao base v1, đổi đúng biểu thức ở mục 4.5–4.6. Expected/actual FALSE cả ba, có counterexample. Chỉ một CTL trên mỗi negative. Trace kế thừa biến không được in lại; EF FALSE có thể chỉ in trạng thái đầu.')
p('JSON: duyệt mọi cạnh/12 đèn/khả đạt/timer/reset/liveness trên hai graph; checker CTL độc lập chạy 26 công thức trên bản chiếu, không gọi NuSMV/SecLab. SecLab archive là công cụ khác.')
table(['Nguồn archive','Số lượng','Mức chứng cứ'],[['graph_results.json','42 biên,24 thời lượng,4 sai,1 thay thế','Từng ca lưu trữ; không chạy hàm ghi lại artifact'],['nusmv_any_start_time.log','335 CTL','Log đầy đủ, results JSON khớp'],['nusmv_period_reachability.log','4 EF','Log đầy đủ'],['seclab_results.json','26 CTL,mutex,parser exact','Ch1 nguyên gốc, headless'],['backend_tests.json','13 unittest','Tổng hợp; không stdout từng method'],['browser_tests.json','32 checks','Mỗi tên/details/status; khác CTL']])
p('Kết luận: các ca mới đạt expected; hash nguồn kiểm kê giữ nguyên. Không timeout hoặc kết quả ngoài dự kiến trong lượt audit hoàn chỉnh. Danh tính người kiểm và xác nhận nhóm cần điền thật. Chưa có test vật lý/emergency/GUI SecLab.')
p('Người kiểm thử: [HỌ TÊN — MSSV — CHỮ KÝ]\nĐại diện nhóm: [HỌ TÊN — CHỮ KÝ]')
render_doc('BIEN_BAN_KIEM_CHUNG',pages)
rows=['# Kiểm kê bằng chứng — hoàn tất trước viết báo cáo','','Audit '+str(A['inventoried_files'])+' tệp nội dung; mọi hash giữ nguyên; loại runtime/thư viện/cache.','']
for d in DEFECTS:rows+=['## '+d['id']+' — '+d['title'],'','1. V0: '+d['v0'],'2. Nguyên nhân: '+d['root'],'3. Quan sát: '+d['observable'],'4. V1: '+d['v1']+'; '+d['v1_property_location'],'5. CTL `'+d['v1_validation']+'` TRUE tại '+d['v1_log']+'; v0 FALSE tại '+d['log'],'6. Giới hạn: '+d['gap'],'']
rows+=['## Phân loại khác','','L01 enum yếu; L02 siết yêu cầu vàng/all-red; tách khỏi lỗi D01–D03. Mẫu init_bug/transition_bug cố ý sai tách riêng. N1–N3 fault trên bản sao v1, mỗi CTL FALSE dự kiến. Emergency chưa tích hợp; khung/fixture chưa SPEC không PASS nghiệp vụ.','','## Kripke và CTLSPEC','','18 VAR: phase,timer,hour,minute,second,entry_period,12 boolean. period là DEFINE. S0/R: SMV:39–74, intersection.py:60–74. L: intersection.py:95–104. Exact86400 nút/cạnh, chiếu1012/2548. 335 công thức chính thức trong ctl_catalog.json; mọi khai báo trong all_ctlspec_declarations.json.','','## Khoảng trống','','\n'.join('- '+x for x in A['missing']),'','Counterexample mới bù thiếu chứng cứ trực tiếp timer/reset/reachability của archive, không sửa lịch sử.']
(OUT/'KIEM_KE_BANG_CHUNG.md').write_text('\n'.join(rows),encoding='utf-8')
check='''# Checklist tiêu chí — report_guide.pdf

Nguồn trực tiếp: PDF tr.3 cấu trúc; tr.4 định dạng; tr.5 năm mục; tr.6–7 bảng; tr.8 trọng số; tr.8–9 checklist. Không tự chấm điểm.

| Tiêu chí | Trọng số | Bằng chứng / trạng thái |
|---|---:|---|
| Đầy đủ cấu trúc 8 phần | 10% | Đủ tám Heading1, đúng tên/thứ tự |
| Chất lượng phân tích lỗ hổng (Phần 4) | 35% | D01–D03 đủ năm mục; CWE/CERT chờ giảng viên |
| Bảng before/after (Phần 5) | 15% | D01–D03 khớp1–1, có log |
| Chất lượng bằng chứng (Phần 6) | 20% | Log đầy đủ/hash/chỉ mục; nộp phụ lục điện tử |
| Chiều sâu phản biện (Phần 7) | 10% | Ba câu hỏi; hạn chế/vacuity/abstraction cụ thể |
| Định dạng & trình bày | 10% | Times New Roman11.5pt, A4 lề2cm, trang/caption; tên phiên bản cần duyệt |

- [x] Đủ tám phần, đúng tên/thứ tự.
- [ ] CWE cụ thể: không tự gán cho lỗi logic; giảng viên xác nhận áp dụng.
- [x] D01–D03 đủ vị trí, nguyên nhân, chứng cứ trước, cách sửa, chứng cứ sau.
- [x] Bảng phần5 khớp phần4; tách giới hạn/mở rộng/fault.
- [x] Log/ảnh có caption; log đầy đủ trong phụ lục điện tử.
- [x] Baseline nguyên vẹn, hash không đổi.
- [x] Cung cấp lệnh build/kiểm; generator khớp model, không ghi đè chapter1.
- [x] data_gen/seed không áp dụng; thay config/hash, nêu state-limit.
- [x] Phản biện cụ thể về Kripke, CTL, vacuity, đồng bộ next.
- [ ] Điền tên/MSSV/lớp/nhóm/GitHub/phân công/tuần/mã đề tài thật.
- [ ] Giảng viên duyệt CWE/CERT, tên phiên bản và phụ lục điện tử.
- [ ] PDF mở/font/đủ trang: xem quality_validation.json sau kiểm kỹ thuật; nhóm kiểm lần cuối trước nộp.

Độ dài gợi ý: bìa1; tổng quan1–1.5; phương pháp1; phân tích3–6; bảng1; bằng chứng1–3; phản biện0.5–1; phụ lục không giới hạn. Đo trang thực sau render, không mặc định đạt.
'''
(OUT/'CHECKLIST_TIEU_CHI.md').write_text(check,encoding='utf-8')
inv=local('source_inventory.json')
with (OUT/'source_inventory.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['path','bytes','sha256']);w.writerows((k,v['bytes'],v['sha256']) for k,v in inv.items())
from zipfile import ZipFile,ZIP_DEFLATED
with ZipFile(OUT/'PHU_LUC_NGUON_VA_BANG_CHUNG.zip','w',ZIP_DEFLATED) as z:
 for rel,record in inv.items():
  path=ROOT/rel
  if path.suffix.lower() in {'.py','.mjs','.js','.css','.html','.smv','.json','.log','.md','.ps1','.png','.svg'}:z.write(path,'repository/'+rel)
 for path in (OUT/'evidence').glob('*'):z.write(path,'fresh_report_evidence/'+path.name)
 for name in ['source_inventory.json','evidence_inventory.json','evidence_index.csv','verification_test_cases.csv','ctl_catalog.json','all_ctlspec_declarations.json','audit_summary.json']:z.write(OUT/name,'report_index/'+name)
assert all(sha(ROOT/k)==v['sha256'] for k,v in inv.items())
dump('build_summary.json',{'report_layout_units':len(REPORT_PAGES),'report_top_level_sections':SECTIONS,'test_record_rows':len(cases),'test_record_categories':dict(collections.Counter(c['category'] for c in cases)),'all_preexisting_inventory_files_unchanged':True,'phase1_before_phase2':True,'docx_body_font':'Times New Roman 11.5pt','margins_cm':2,'pdf_rendering':'Same structured content as DOCX; Edge print HTML; pagination may differ'})
print(json.dumps(local('build_summary.json'),ensure_ascii=False,indent=2))
