from pathlib import Path
from datetime import datetime,timedelta,timezone
import sys,json,re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE/'_tools'))
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION_START,WD_ORIENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from case_data import cases,CATS
from collect_evidence import collect
A=collect();WEB,API,FORMAL,NEG=cases(A)
D=Document();D.core_properties.title='BIÊN BẢN KIỂM THỬ PHẦN MỀM — CHƯƠNG 1';D.core_properties.subject='Đối chiếu kiểm thử tự động và bằng chứng kiểm chứng hình thức';D.core_properties.author='';D.core_properties.last_modified_by='';D.core_properties.keywords='Kripke, CTL, NuSMV, kiểm thử, Chương 1'
S=D.styles['Normal'];S.font.name='Arial';S.font.size=Pt(10.5);S.paragraph_format.space_after=Pt(6);S.paragraph_format.line_spacing=1.12
for name,size,col in [('Title',25,'12354A'),('Subtitle',12,'58717F'),('Heading 1',16,'12354A'),('Heading 2',12.5,'147869'),('Heading 3',11,'284D60')]:
    s=D.styles[name];s.font.name='Arial';s.font.size=Pt(size);s.font.color.rgb=RGBColor.from_string(col)
    s.paragraph_format.space_before=Pt(13);s.paragraph_format.space_after=Pt(7)
D.styles['Caption'].font.name='Arial';D.styles['Caption'].font.size=Pt(9);D.styles['Caption'].font.color.rgb=RGBColor.from_string('607884')

def element(name,**attrs):
    e=OxmlElement(name)
    for k,v in attrs.items():e.set(qn(k),str(v))
    return e

def setup(sec,land=False):
    sec.orientation=WD_ORIENT.LANDSCAPE if land else WD_ORIENT.PORTRAIT
    sec.page_width=Cm(29.7 if land else 21);sec.page_height=Cm(21 if land else 29.7)
    sec.top_margin=Cm(1.55 if land else 1.9);sec.bottom_margin=Cm(1.5 if land else 1.8)
    sec.left_margin=Cm(1.7 if land else 2);sec.right_margin=Cm(1.7 if land else 2)
    sec.header_distance=Cm(.75);sec.footer_distance=Cm(.75)
setup(D.sections[0])
header=D.sections[0].header.paragraphs[0];header.text='CHƯƠNG 1  /  KRIPKE & KIỂM CHỨNG HÌNH THỨC';header.style='Caption'
footer=D.sections[0].footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=footer.add_run('BBKT-CH1-2026-01  •  Bản 1.0  |  Trang ');r.font.size=Pt(8)
r=footer.add_run();footer._p.append(element('w:fldSimple',**{'w:instr':'PAGE'}));r.font.size=Pt(8)
footer.add_run(' / ').font.size=Pt(8);r=footer.add_run();footer._p.append(element('w:fldSimple',**{'w:instr':'NUMPAGES'}));r.font.size=Pt(8)

def p(text='',style=None,bold=False):
    x=D.add_paragraph(style=style);run=x.add_run(text);run.bold=bold;return x

def heading(text,level=1):return D.add_heading(text,level)
def section(land=False):setup(D.add_section(WD_SECTION_START.NEW_PAGE),land)
def soft(s):return str(s).replace('/','/\u200b').replace('_','_\u200b')
def table(headers,rows,widths=None,size=10):
    t=D.add_table(rows=1,cols=len(headers));t.autofit=False;t.style='Table Grid'
    if widths:
        for c,w in zip(t.columns,widths):c.width=Cm(w)
    def rowfill(row,vals,head=False,index=0):
        trPr=row._tr.get_or_add_trPr();trPr.append(element('w:cantSplit'))
        if head:trPr.append(element('w:tblHeader'))
        for j,(c,v) in enumerate(zip(row.cells,vals)):
            if widths:c.width=Cm(widths[j])
            c.vertical_alignment=1
            tcPr=c._tc.get_or_add_tcPr();tcPr.append(element('w:shd',**{'w:fill':'173E52' if head else ('F2F6F8' if index%2 else 'FFFFFF')}))
            margin=element('w:tcMar')
            for edge in ['top','bottom','left','right']:margin.append(element('w:'+edge,**{'w:w':'90' if head else '75','w:type':'dxa'}))
            tcPr.append(margin)
            q=c.paragraphs[0];q.paragraph_format.space_after=Pt(3);q.paragraph_format.space_before=Pt(2);q.paragraph_format.line_spacing=1.04;q.paragraph_format.keep_with_next=False
            r=q.add_run(str(v));r.font.name='Arial';r.font.size=Pt(size)
            if head:r.bold=True;r.font.color.rgb=RGBColor(255,255,255)
            elif str(v).startswith('PASS'):r.bold=True;r.font.color.rgb=RGBColor.from_string('14735E')
    rowfill(t.rows[0],headers,True)
    for i,row in enumerate(rows):rowfill(t.add_row(),row,index=i)
    D.add_paragraph().paragraph_format.space_after=Pt(0)
    return t

def case_table(rows):
    vals=[]
    for c in rows:
        ev=c['evidence']
        if c['id'].startswith('API-'):ev='EV01, EV03; test_'+c['id'][-2:]
        vals.append([c['id'],c['function'],c['pre'],c['steps'],c['expected'],c['actual'],c['status'],ev])
    return table(['Mã ca','Chức năng','Điều kiện trước','Các bước đã thực hiện','Kết quả mong đợi','Kết quả thực tế','Trạng thái','Bằng chứng'],vals,[1.35,2.9,3.05,5.3,4.3,5.1,1.55,2.75],9)

def localtime(v):return datetime.fromisoformat(v.replace('Z','+00:00')).astimezone(timezone(timedelta(hours=7))).strftime('%d/%m/%Y %H:%M:%S')

p('HỒ SƠ KIỂM THỬ HỌC PHẦN',bold=True)
D.add_paragraph('BIÊN BẢN\nKIỂM THỬ PHẦN MỀM','Title')
D.add_paragraph('Chương 1 · Cấu trúc Kripke và kiểm chứng hình thức','Subtitle')
p('Mô hình hóa và kiểm chứng hình thức hệ thống đèn giao thông thông minh bốn hướng bằng cấu trúc Kripke',bold=True)
p('Formal Modeling and Verification of an Intelligent Four-Way Traffic Light System Using Kripke Structures','Caption')
heading('1. Thông tin tài liệu và dự án')
table(['Hạng mục','Thông tin'],[
('Mã tài liệu / phiên bản','BBKT-CH1-2026-01 / 1.0 — mã quản lý biên bản'),('Ngày lập biên bản','23/10/2026; múi giờ trình bày: UTC+7 (Asia/Bangkok)'),('Sản phẩm kiểm thử','Giao Lộ — ứng dụng web Chương 1 và mô hình NuSMV v1'),('Đường dẫn chính','chapter1/web/ và chapter1/smart_intersection.smv'),('Trường / học phần / lớp','[Điền thông tin thực tế]'),('Giảng viên / nhóm','[Điền thông tin thực tế]'),('Thành viên / MSSV','[Điền họ tên, MSSV và phân công thực tế]'),('Trạng thái hồ sơ','Đã tổng hợp bằng chứng; chờ người thực hiện và người rà soát xác nhận, ký tên')],[4.5,12.5])
p('Tài liệu này là hồ sơ kiểm thử riêng, bổ sung cho báo cáo đồ án và mã nguồn. Các mã WEB/API/FM/NEG được đặt để truy vết trong biên bản, không biểu thị các lần thử mới được thực hiện ngày lập tài liệu.')
p('Cơ sở kết quả: 13 ca backend, 32 kiểm tra trình duyệt và lượt checker '+A['browser']['fresh_run']+'. Chỉ tổng hợp/đối chiếu chứng cứ hiện có; không chạy lại kiểm thử sản phẩm khi lập biên bản.',bold=True)
D.add_page_break()
heading('2. Mục tiêu và phạm vi kiểm thử')
p('Xác nhận giao diện biểu diễn đúng ngữ nghĩa nguồn Python/NuSMV; kiểm chu kỳ, timer, lịch giờ, API và Kripke; xác nhận các thuộc tính CTL và khả năng phát hiện ba lỗi cố ý. Mọi kết luận gắn với mô hình, cấu hình và lượt thực thi cụ thể.')
table(['Trong phạm vi','Ngoài phạm vi / chưa xác nhận'],[
('Bốn hướng, 12 đèn, sáu pha, đồng bộ, loại trừ xanh, ALL_RED','Thiết bị vật lý, va chạm xe thực tế, hỏng đèn và trễ tín hiệu'),('Clock 24 giờ, lịch theo config, latching entry_period','Cảm biến lưu lượng, tối ưu giao thông thực tế, emergency, người đi bộ'),('Điều khiển mô phỏng; API; Kripke chiếu/exact; bằng chứng v0/v1','Chương 2–6; Excel; chứng nhận phần mềm điều khiển giao thông ngoài thực tế'),('CTL NuSMV, CTL JSON độc lập, kiểm đồ thị và fault injection','LTL chưa có chứng cứ; kiểm tải/hiệu năng, pentest toàn diện, mọi trình duyệt')],[8.5,8.5])
p('Quy ước: PASS = kết quả phù hợp mong đợi trong đúng phạm vi phép thử. FAIL = kết quả không phù hợp mong đợi. FALSE là giá trị logic; trong negative test, FALSE và phản ví dụ là mong đợi nên harness PASS. PASS* ở bảng backend dựa bản ghi tổng hợp 13 ca, không có stdout riêng từng ca.')
p('Kiểm thử tự động là nguồn các kết quả sản phẩm trong tài liệu. Đối chiếu log, xem ảnh, kiểm định dạng Word/PDF phục vụ rà soát hồ sơ; không được gọi là phiên kiểm thử sản phẩm thủ công có người ký. Chưa có biên bản thực hiện thủ công độc lập.')
heading('3. Môi trường và công cụ')
table(['Công cụ / thành phần','Căn cứ và giới hạn xác nhận'],[
('NuSMV 2.7.1; BDD/CTL','Phiên bản lấy trực tiếp header stdout EV07–EV17. CUDD 2.4.1 được header ghi nhận. Không dùng kết quả BMC để thay cho CTL.'),('Python, unittest, HTTP cục bộ','EV03 và EV23 dùng thư viện chuẩn, phiên cookie và API 127.0.0.1. Log backend không lưu phiên bản Python tại thời điểm thử.'),('Node.js, Microsoft Edge headless / CDP','EV04 và EV02 xác nhận công cụ, Windows path và cấu hình cửa sổ 1440×1100; emulation 390×844. Không có phiên bản Edge chính xác trong bản ghi cũ.'),('Bộ kiểm CTL JSON độc lập','EV21: fixpoint AG/AF/EF/EG/AX/EX với AP hoặc !AP. Không phải trình kiểm CTL tổng quát; không phụ thuộc SecLabFramework.'),('Máy soạn biên bản hiện tại','Quan sát ngày lập hồ sơ: '+A['environment_now']['platform']+'; Python '+A['environment_now']['python']+'; Node '+A['environment_now']['node']+'. Không gán các phiên bản quan sát hiện tại cho lần chạy lịch sử.'),('CPU / RAM / người thao tác lúc thử','Không có metadata đủ để xác nhận. Để trống, không suy đoán từ máy đang dùng.')],[4.5,12.5],9.5)
p('Lượt checker chọn theo fresh_run trong EV02 và báo cáo EV29: bắt đầu '+localtime(A['metadata']['started_at'])+', kết thúc '+localtime(A['metadata']['finished_at'])+' (UTC+7). Bản ghi Edge kết thúc '+localtime(A['browser']['executed_at'])+'. Backend JSON không ghi thời điểm thực thi.')
p('Nguồn v1 SHA-256: '+A['metadata']['source_hashes']['smart_intersection.smv'],'Caption')
section(True)
heading('4. Bảng ca kiểm thử chi tiết')
p('Tất cả các mục dưới đây ánh xạ tới phép thử/nhóm công thức thực sự đã chạy. Không cộng các nhóm CTL, các kiểm tra Edge và ca unittest thành một số lượng ca độc lập. Các bước mô tả được đọc từ script, không là biên bản thao tác thủ công mới.')
heading('4.1. Web / Edge — 32 mục kiểm tra tự động',2)
p('EV02 checks[0]…checks[31] là chỉ số 0-based trong JSON. EV04 chứa câu lệnh assert và chuỗi thao tác thực thi. Với các tab giải thích, phép thử chỉ kiểm có nội dung theo độ dài, không chứng minh toàn bộ ngữ nghĩa hình vẽ. Mốc đổi giờ được xác nhận thêm tại API-03.')
case_table(WEB)
heading('4.2. Backend/API và kernel — 13 ca unittest',2)
p('PASS* = bộ unittest ghi tests_run=13, failures=[], errors=[] và status=PASS (EV01); EV03 hiện có đúng 13 hàm test_01…test_13, không có cơ chế skip trong script. EV01 không ghi kết quả/timestamp/stdout độc lập từng hàm. API-01 là kiểm kernel, API-12/13 là kiểm checker; không phải mọi ca đều gọi HTTP.')
case_table(API)
heading('4.3. Kiểm chứng hình thức — các nhóm đã thực thi',2)
p('Chín nhóm đầu phân loại 335 CTL mặc định theo properties.json; physical_green_exclusion được tách thành nhóm loại trừ để dễ đối chiếu. Đây là phân nhóm cùng một bộ, không phải 335 thuộc tính cộng thêm chín lần chạy. FM-10…FM-14 là các phép kiểm bổ sung đã có chứng cứ.')
case_table(FORMAL)
heading('4.4. Negative test — ba bản cố ý gây lỗi',2)
p('Các mô hình negative_*.smv nằm riêng cùng log; v1 chính thức không bị sửa. Ở trace NuSMV dạng rút gọn, biến không xuất hiện ở trạng thái kế tiếp giữ giá trị trước đó; áp dụng quy tắc này khi đọc timer=1 và all_red=FALSE.')
case_table(NEG)
section(False)
heading('5. Kiểm thử chức năng web')
p('WEB-01…WEB-32 xác nhận hành vi/hiển thị trong phiên Edge đã lưu. Bảng sau liên kết các chức năng yêu cầu với các kiểm tra thích hợp, không tạo thêm ca kiểm mới.')
table(['Chức năng','Kiểm tra / bằng chứng'],[
('Bốn hướng, 12 đèn, đồng bộ và loại trừ','WEB-01/02/11; API-01/07; EV14. So 12 trạng thái DOM với API, bất biến kernel toàn ngày và nhãn JSON.'),('Sáu pha và ALL_RED','WEB-02; API-02; CTL advance_*, hold_* và clearance_all_red. Hai pha đỏ toàn hướng được nạp 2 giây.'),('Countdown và thời gian từng hướng','API-02/04/05; WEB-02. API-05 kiểm until_green và color_remaining theo bước nguồn qua mốc giờ.'),('Thích nghi / latching / clock 24 giờ','WEB-03…08; API-03; nhóm CTL adaptive/clock. WEB-08 có 23:59:59 → 00:00:00.'),('Start, Pause, Resume, Reset, Step, tốc độ','WEB-09/10/11; chỉ quan sát tốc độ 8× và dừng trong cửa sổ 500 ms. Không là kiểm chuẩn thời gian thực.'),('Kripke, S0, L(s), AP, tìm kiếm','WEB-12…18; API-07; bốn tab có nội dung, bộ lọc pha hoạt động và exact inspector khớp state ID.'),('Dashboard, nguồn lịch sử/mới, counterexample','WEB-19…25; EV07–EV17. Đúng tên công cụ lịch sử và checker độc lập ở lượt mới.'),('Before/After, bảo toàn, điện thoại','WEB-27…31; API-09/10. 14 nguồn gốc; baseline 93 tệp; emulation 390 px.')],[5.2,11.8])
heading('5.1. Dấu vết sáu ranh giới giờ',2)
rows=[]
for c in A['browser']['checks'][2:8]:
    x,y=c['details']['before'],c['details']['after'];rows.append([x['clock']+' → '+y['clock'],x['period']+' → '+y['period'],f"{x['timer']} → {y['timer']}; D={y['duration']}",'Giữ '+y['entry']])
table(['Clock','Period trước → sau','Timer / giây','Entry period'],rows,[3.6,5.8,2.7,4.9],9)
p('Các giá trị trên được trích trực tiếp từ before/after của EV02, không phải trace tự dựng. Backend còn thử mốc 05:59:59 → 06:00:00 (API-03); không có ảnh chụp riêng từng mốc trong bộ bảy ảnh hiện có.')
heading('5.2. Phạm vi Kripke đã xác nhận',2)
p('K=(S,S0,R,L). JSON chiếu giữ phase, remaining, period, entry_period: 1.012 nút/2.548 cạnh. JSON exact giữ thêm clock, có 86.400 nút/cạnh trên quỹ đạo S0 mặc định. Giao diện tải lân cận khi cần. Trạng thái từ giờ khởi động tùy ý có thể nằm ngoài S mặc định; không được coi bản exact là hợp mọi trạng thái khởi tạo.')
heading('6. Kiểm thử backend/API')
p('Bộ 13 ca đã chạy gồm kiểm kernel, HTTP, toàn vẹn nguồn và checker JSON. API-04 đối chiếu 600 cạnh HTTP trên năm điểm khởi tạo với initial/step nguồn; API-01 kiểm 86.400 bước kernel. Hai số này có phạm vi khác nhau và không phải số yêu cầu HTTP cộng gộp.')
p('API-06 thử phiên độc lập, reset và count=0/121/true cùng token sai; API-11 thử hai đường dẫn artifact bị chặn. Script chỉ xác nhận ngoại lệ HTTPError, không lưu/khẳng định mã 400/403 cụ thể. Đây là kiểm đầu vào/quyền đọc có mẫu, không là chứng nhận an ninh toàn diện.')
p('API-12 dùng fixture có nhánh bad và trạng thái unreachable: EF(goal)=TRUE, AF(goal)=FALSE, AG(safe)=TRUE, EG(safe)=TRUE, AX(goal)=FALSE, EX(goal)=TRUE; reachable=3. FALSE tại fixture là kết quả đúng mong đợi. Quan hệ không toàn phần bị từ chối bằng ValueError.')
heading('7. Kiểm chứng hình thức')
p('Đối chiếu EV10 với từng dòng “-- specification … is true/false” trong stdout EV07/08/09/15/16/17. Số lượng và công thức trùng khớp; returncode=0, timeout=false. Đối chiếu 335 công thức đặt tên trong EV18 bằng chuẩn hóa khoảng trắng/dấu ngoặc; không chỉ đọc số tổng từ báo cáo triển khai.')
rows=[]
for cat,items in A['property_groups'].items():rows.append([CATS[cat],str(len(items)),items[0]['name'],items[0]['formula']])
table(['Nhóm CTL mặc định','Số TRUE','Thuộc tính mẫu','Công thức thực tế'],rows,[3.1,1.4,4.3,8.2],9)
p('Tổng chín nhóm = 335 TRUE / 335, không có FALSE. NuSMV giờ khởi tạo bất kỳ cũng có 335/335 TRUE (EV08), nhưng đó là bộ chạy bổ sung, không phải 670 thuộc tính khác nhau. Bốn EF(period=…) đúng trong EV09. Chưa có bằng chứng LTL; biên bản không kết luận LTL đã kiểm thử.')
p('CTL JSON: EV11 lưu 26/26 PASS từ bộ kiểm độc lập EV21 trên 1.012 trạng thái/2.548 cạnh. Tập công thức được so với suggested_ctl_formulas của JSON nguồn. EV26 là kết quả lịch sử của SecLabFramework, được phân biệt về công cụ và thời điểm; không tính là một lần checker cũ chạy lại khi lập hồ sơ.')
p('EV12 ghi reachable states: 86400; EV13 ghi lệnh thực tế và returncode 0. EV14 kiểm mọi cạnh một giây và 12 đèn của cả hai JSON; cả hai không bế tắc. Con số 86.400 áp dụng S0 mặc định, không áp dụng số trạng thái hợp mọi cách khởi tạo của mô hình giờ bất kỳ.')
heading('8. Kiểm thử âm và phản ví dụ')
p('NEG-01…03 là fault injection có chủ đích trong các bản mô hình riêng. Điều kiện nghiệm thu từng đối chứng: một công thức FALSE, có CTL Counterexample, tiến trình thành công và harness PASS. Nếu công thức TRUE hoặc thiếu trace mới là không đạt yêu cầu đối chứng.')
for i,c in enumerate(NEG,1):
    heading(c['id']+' — '+c['function'],2)
    p('Thay đổi được thực thi: '+c['steps'])
    job=A['raw_log_checks'][i+2];text=(ROOT/job['file']).read_text(encoding='utf-8')
    spec=re.search(r'-- specification (.*?) is false',text,re.S)[1].strip();p('Công thức trả FALSE: '+spec,'Caption')
    p(c['actual']+' Tham chiếu '+c['evidence']+'.')
p('NEG-02: timer không được in lại ở State 1.3 nên kế thừa timer=1 của State 1.2. NEG-03: all_red không được in lại ở State 1.21 nên kế thừa FALSE từ State 1.3. Đây là cách đọc trace rút gọn NuSMV, không phải giá trị tự thêm vào log.')
p('Các lỗi có chủ đích khác trong nguồn v0 được phân loại sẵn ở EV25. Không coi ba đối chứng trên là ba lỗi đang tồn tại của v1. Lỗi logic thích nghi v0, các file chưa có SPEC và mẫu đăng nhập ngoài nghiệp vụ phải giữ đúng phân loại trong tài liệu Before/After, không gán trace negative mới cho chúng.')
heading('8.1. FAIL trung gian và xử lý hồi quy',2)
for hist in A['history']:
    p('EV31: '+localtime(hist['executed_at'])+' (UTC+7), trạng thái '+hist['status']+f"; {hist['passed']}/{hist['checks']} mục đã ghi PASS; mục không đạt: "+'; '.join(hist['failed'])+'.')
p('Báo cáo triển khai EV29 mô tả phép dò Kripke chờ cố định 200 ms đọc trước phản hồi. Script hiện tại EV04 chờ đúng state ID, giao diện có chốt phản hồi. Lần cuối EV02 đạt đủ 32 mục. Đây là lỗi đồng bộ của phép dò/tương tác cần theo dõi; không được xóa lịch sử hoặc suy ra v1 vi phạm safety từ FAIL này.')
heading('9. Tổng hợp kết quả')
table(['Lớp bằng chứng','Kết quả được xác nhận','Tham chiếu'],[
('Backend/kernel/API','13/13 ca; 0 failure, 0 error; bản ghi tổng hợp','EV01, EV03'),('Trình duyệt Edge','32/32 mục PASS; danh sách lỗi thu được rỗng','EV02, EV04'),('NuSMV CTL mặc định','335/335 TRUE','EV07, EV10, EV18'),('NuSMV CTL giờ bất kỳ','335/335 TRUE; chạy bổ sung','EV08, EV10'),('Khả đạt bốn khung giờ','4/4 TRUE','EV09, EV10'),('CTL JSON độc lập','26/26 PASS','EV11, EV21'),('BDD, S0 mặc định','86.400 trạng thái đạt được','EV12, EV13'),('Hai đồ thị JSON','Cả hai PASS; 0 deadlock; nút/cạnh và đèn đúng','EV14'),('Ba đối chứng cố ý lỗi','3/3 FALSE đúng mong đợi; có counterexample; harness PASS','EV15–EV17, EV10'),('Kiểm đồ thị lịch sử bổ sung',f"{A['old_graph_summary']['boundary_cases']} ranh giới theo pha; {A['old_graph_summary']['duration_cases']} trường hợp thời lượng; overall {A['old_graph_summary']['overall']}",'EV27; không chạy lại'),('Thử trung gian','Có một mục FAIL trong bản ghi cũ; bản cuối 32/32 PASS','EV31 → EV02'),('Kiểm thủ công sản phẩm / LTL','Chưa có bằng chứng thực thi để công bố PASS','Không áp dụng')],[4.8,9.7,2.5],9.5)
p('Không tính một “tỷ lệ PASS tổng” bằng cách cộng 13, 32, 335 và 26 vì khác đơn vị, có trùng phạm vi và có các nhóm công thức được phân loại lại. Phần xác nhận người thực hiện/người rà soát vẫn để trống đến khi có người chịu trách nhiệm ký.')
heading('10. Giới hạn và kết luận')
for s in [
'Chỉ kết luận theo log, script và nguồn đang có. Không chạy lại sản phẩm trong nhiệm vụ lập biên bản; việc kiểm hash/tệp tài liệu không là một lần kiểm chức năng mới.',
'Backend JSON thiếu stdout/timestamp riêng từng ca và trường skip; dựa số ca, lỗi rỗng và script không có skip. Bản ghi Edge không lưu phiên bản Edge/OS/CPU/RAM tại lần thử.',
'Chưa có phiên kiểm thử sản phẩm thủ công độc lập, chữ ký nghiệm thu, thử tải, kiểm an ninh toàn diện hoặc dữ liệu bao phủ đa trình duyệt.',
'Không có kết quả LTL. Bộ kiểm JSON chỉ hỗ trợ cú pháp đã nêu; các CTL phức tạp được NuSMV kiểm. Kiểm giao diện không thay thế kiểm chứng hình thức.',
'Thích nghi dựa giờ trong ngày, chưa có cảm biến, người đi bộ hoặc emergency. Một giây logic không là bảo đảm đáp ứng thời gian thực của thiết bị.',
'Exact là quỹ đạo S0 mặc định; bản chiếu bỏ clock có thể có thêm nhánh. Các kết luận không chứng minh tối ưu lưu lượng hoặc tránh mọi va chạm vật lý.',
'Mẫu môn học yêu cầu CWE/CERT cần giảng viên xác nhận áp dụng cho lỗi logic giao thông. Chưa có căn cứ gán mã CWE/CERT; không tự bổ sung mã.',
]:p('• '+s)
p('Kết luận kỹ thuật: các kiểm tra tự động và CTL được liệt kê đạt kết quả mong đợi trong phạm vi mô hình Chương 1, có chứng cứ truy vết. Hồ sơ phù hợp để bổ sung cho báo cáo học phần; không thay thế xác nhận của người thực hiện/người rà soát và không là chứng nhận an toàn triển khai giao thông thực tế.',bold=True)
section(False)
heading('11. Phụ lục và bảng truy vết bằng chứng')
heading('11.1. Ma trận yêu cầu → kiểm tra → bằng chứng',2)
table(['Yêu cầu','Mã ca / nhóm','Chứng cứ chính'],[
('12 đèn, đồng bộ và mutex','WEB-01/02/11; API-01/07; FM mutex/safety','EV02–EV04, EV07, EV14, EV18; IMG01'),('Sáu pha, ALL_RED và timer','WEB-02; API-02/04/05; FM timer/transition','EV01–EV04, EV07, EV14; IMG01'),('Lịch thích nghi, latching, clock 24 giờ','WEB-03…08; API-03; FM adaptive/clock','EV02–EV04, EV07, EV09, EV20; IMG04'),('Điều khiển mô phỏng','WEB-09…11','EV02, EV04; IMG01'),('Kripke S/S0/R/L/AP, exact/chiếu','WEB-12…18; API-07; FM-14','EV01–EV04, EV14, EV24; IMG02'),('Dashboard, nguồn mới/cũ','WEB-19…25; API-08','EV02, EV04–EV17, EV26; IMG03'),('API, đầu vào và quyền đọc mẫu','API-04/06/11/12','EV01, EV03, EV21'),('Before/After và bảo toàn','WEB-27/28; API-09/10','EV02–EV04, EV25, EV28; IMG05/06'),('Điện thoại và lỗi JS','WEB-29…32','EV02, EV04; IMG07'),('Safety/liveness/deadlock/reachability','FM-01…14 theo bảng 4.3','EV07–EV14, EV18, EV21, EV24'),('Fault injection và trace','NEG-01…03','EV10, EV15–EV17, EV22'),('Lịch sử FAIL và hồi quy','WEB-18; bản ghi trung gian','EV31, EV02, EV04, EV29')],[5.1,5.2,6.7],9.2)
heading('11.2. Danh mục tệp nguồn / log',2)
p('Đường dẫn tính từ thư mục gốc NuSMV_project; xuống dòng trong đường dẫn chỉ để trình bày. SHA trong bảng là 12 ký tự đầu để nhận diện. Hash đầy đủ và chỉ mục từng công thức được lưu trong quality_checks/evidence_audit.json. Khi giao nộp cần giữ cây thư mục dự án để mở các chứng cứ ngoài DOCX/PDF.')
rows=[[e['id'],e['title'],soft(e['path']),e['sha256'][:12]] for e in A['evidence']]
table(['Mã','Chứng cứ','Đường dẫn tương đối từ gốc dự án','SHA-256 rút gọn'],rows,[1.3,3.8,9.3,2.6],8.8)
heading('11.3. Định vị trong log và dữ liệu',2)
table(['Mã','Định vị kết quả'],[
('EV01','status; tests_run; failures; errors; preservation. Không có stdout riêng từng hàm.'),('EV02','checks[0]…checks[31]; errors; fresh_run; executed_at. Tên gốc từng check lưu trong evidence_audit.json.'),('EV07/08/09','Các dòng -- specification … is true. Đối chiếu EV10 checks[].formula/result.'),('EV11','properties[].formula/result/status; overall; mutex; deadlock_states.'),('EV12','Dòng reachable states: 86400; không lấy giá trị out of làm số trạng thái đạt được.'),('EV14','Hai bản ghi file/status/states/edges/deadlocks và cờ all_12_lamp_values_checked, all_one_second_edges_checked.'),('EV15/16/17','Dòng specification … is false; Trace Description/Type; State 1.1… theo từng phản ví dụ.'),('EV31','checks[17] không đạt trong lần trung gian; lần cuối tương ứng WEB-18 = EV02 checks[17].')],[3.1,13.9],9.5)
heading('11.4. Hash mô hình và bảo toàn nguồn',2)
p('SHA-256 v1 chính thức: '+A['metadata']['source_hashes']['smart_intersection.smv'],'Caption')
p('SHA-256 config: '+A['metadata']['source_hashes']['config.json'],'Caption')
p('EV28 ghi 93/93 tệp gốc và 22 file .smv giữ nguyên ở lần bàn giao web. Khi lập biên bản, snapshot riêng trong quality_checks/preservation_snapshot.json được dùng kiểm lại toàn bộ tệp hiện có ngoài report_delivery. Kết quả kiểm bảo toàn và mở tài liệu nằm trong quality_checks/document_validation.json; không ghi đè baseline/log cũ.')
heading('11.5. Danh mục ảnh thật',2)
for img in A['images']:
    p(img['id']+' — '+soft(img['path'])+f" ({img['width']} × {img['height']} px)",'Caption')
p('Bảy ảnh được nhúng nguyên nội dung từ PNG có trước, không tạo ảnh mô phỏng thay cho thí nghiệm. Ảnh giúp trình bày; log/JSON và công thức mới là bằng chứng cho kết quả checker. Phóng to ảnh hoặc mở PNG gốc để đọc chi tiết giao diện nhỏ.')
for i,img in enumerate(A['images']):
    if i<6:
        if i==0:section(True)
        else:D.add_page_break()
    else:section(False)
    names=['Mô phỏng giao lộ và 12 đèn','Kripke và trạng thái có đồng hồ','Kết quả kiểm chứng từ lượt thực thi','Lịch điều khiển và thời lượng nguồn','Đối chiếu Before/After','Danh mục bằng chứng và bảo toàn','Giao diện điện thoại']
    heading('Phụ lục ảnh '+img['id']+' — '+names[i],2)
    width=min(25.7,14.8*img['width']/img['height']) if i<6 else min(8.1,18*img['width']/img['height'])
    q=D.add_paragraph();q.alignment=WD_ALIGN_PARAGRAPH.CENTER;q.paragraph_format.space_after=Pt(3);q.add_run().add_picture(str(ROOT/img['path']),width=Cm(width))
    p(img['id']+' · '+soft(img['path'])+' · SHA-256 '+img['sha256'][:16]+'…','Caption')
    p('Nguồn: ảnh chụp Edge/CDP đã có; tham chiếu EV02/EV04. Không là phiên thao tác thủ công mới.','Caption')
section(False)
heading('12. Xác nhận người thực hiện, rà soát và chữ ký')
p('Ngày lập hồ sơ: 23/10/2026. Ngày thực thi chứng cứ đã chọn: 22/10/2026 (UTC+7), theo EV02/EV05; thời điểm backend riêng chưa được ghi trong JSON. Người ký phải xác nhận thông tin và phạm vi kết quả trước khi ký. Các ô dưới đây được để trống có chủ đích.')
table(['Vai trò','Họ tên / mã số / đơn vị','Ngày xác nhận','Chữ ký'],[
('Người thực hiện kiểm thử','[Điền người thực hiện thực tế]','[dd/mm/yyyy]','[Ký và ghi rõ họ tên]'),('Người lập biên bản','[Điền người chịu trách nhiệm hồ sơ]','[dd/mm/yyyy]','[Ký và ghi rõ họ tên]'),('Người rà soát','[Điền người rà soát thực tế]','[dd/mm/yyyy]','[Ký và ghi rõ họ tên]'),('Giảng viên / người phê duyệt','[Điền nếu học phần yêu cầu]','[dd/mm/yyyy]','[Ký và ghi rõ họ tên]')],[3.6,6.2,2.5,4.7],10)
p('Ý kiến người rà soát: ..................................................................................................................\n..................................................................................................................................................\n..................................................................................................................................................')
p('Kết luận phê duyệt: ☐ Chấp thuận trong phạm vi nêu trên   ☐ Yêu cầu bổ sung chứng cứ\nNội dung cần bổ sung: ................................................................................................................')
p('Biên bản chưa có chữ ký không được trình bày như văn bản nghiệm thu đã được người có thẩm quyền phê duyệt.','Caption')
D.save(HERE/'BIEN_BAN_KIEM_THU_PHAN_MEM_CHUONG_1.docx')
(HERE/'quality_checks/test_case_traceability.json').write_text(json.dumps({'web':WEB,'backend':API,'formal':FORMAL,'negative':NEG,'note':'Mã ca phục vụ hồ sơ; kết quả lấy từ bằng chứng đã chạy, không là lần thực thi mới.'},ensure_ascii=False,indent=2),encoding='utf-8')
print('DOCX_CREATED',HERE/'BIEN_BAN_KIEM_THU_PHAN_MEM_CHUONG_1.docx')

