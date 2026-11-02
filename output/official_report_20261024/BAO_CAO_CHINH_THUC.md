# 1. Trang bìa & Thông tin nhóm

TRƯỜNG CÔNG NGHỆ THÔNG TIN — ĐẠI HỌC PHENIKAA

BÁO CÁO ĐỒ ÁN MÔN HỌC
CSE703153 — Kỹ thuật Lập trình An toàn
Năm học 2026–2027

Mô hình hóa và kiểm chứng hình thức cho hệ thống các đèn giao thông thông minh sử dụng cấu trúc Kripke.

| Thông tin | Nội dung |
|---|---|
| Nhóm / lớp | [SỐ NHÓM] / [MÃ LỚP] |
| Thành viên 1 | [HỌ TÊN] — [MSSV] |
| Thành viên 2 | [HỌ TÊN] — [MSSV] |
| Thành viên 3 | [HỌ TÊN] — [MSSV] |
| Giảng viên hướng dẫn | MSc. Vũ Quang Dũng [nhóm xác nhận phân công thực tế] |
| Kho mã nguồn | [GITHUB URL] |
| Địa điểm, thời gian | Hà Nội, tháng 10 năm 2026 |

Lập ngày 24/10/2026 (Asia/Bangkok), sau kiểm kê và kiểm chứng. Nhóm phải điền thông tin thật trong các trường ngoặc vuông trước khi nộp.

Căn cứ: report_guide.pdf, 9 trang PDF, tìm tại Downloads; bản sao và hash trong gói bàn giao. Đây là đồ án Kripke/CTL/NuSMV. D01–D03 là mã lỗi mô hình nội bộ, không phải CWE. Áp dụng CWE/CERT cần giảng viên xác nhận.

Mục lục trang PDF được tạo ở MUC_LUC_TRANG.md sau phân trang.

# 2. Tổng quan đề tài

Bài toán là điều khiển giao lộ bốn hướng Bắc–Nam và Đông–Tây. Hai hướng đối diện trong cùng nhóm xanh đồng bộ; hai nhóm vuông góc phải loại trừ nhau. Mỗi cột có ba đèn đỏ/vàng/xanh; hết vàng phải có khoảng toàn đỏ để mô hình hóa thời gian dọn giao lộ.

V0 là tập ví dụ độc lập: chu kỳ bốn pha, timer đếm giảm, thích nghi theo time_period, safety/liveness và ví dụ cố ý sai. Chúng chưa tạo bộ điều khiển thống nhất. V1 kế thừa ý tưởng chu kỳ/timer/thích nghi rồi triển khai mới trong chapter1/, không import hay sửa trực tiếp nguồn v0.

Mục tiêu: xác định trạng thái và quan hệ chuyển tiếp, kiểm safety trên 12 đèn, liveness lặp lại, đúng D giây, lịch 24 giờ, thứ tự pha và khả đạt khung giờ. Phạm vi gồm SMV, hai JSON, checker độc lập, log NuSMV và giao diện trình bày.

![Hình 2.1. Kiến trúc v1 và phần kế thừa v0. Nguồn: build.py:10–49, intersection.py:48–137, web/verification_worker.py:11–46. Các khối v1 là phần bổ sung; kiến trúc chỉnh sửa được ở architecture.mmd.](C:/Users/Admin/Desktop/NuSMV_project/output/official_report_20261024/architecture.png)

Ngôn ngữ: NuSMV SMV, Python, JavaScript/HTML/CSS. Chủ đề: máy trạng thái, Kripke, CTL, model checking; tuần học/mã đề tài: [TUẦN HỌC / MÃ ĐỀ TÀI] do tài liệu “5 đề tài” chưa cung cấp.

Ngoài phạm vi: cảm biến đếm xe, ưu tiên khẩn cấp, người đi bộ, rẽ trái bảo vệ, hỏng đèn và trễ truyền thông. “Thông minh” là thích nghi theo lịch giờ. Kết quả TRUE của mô hình không chứng minh an toàn vật lý hoặc tối ưu thông lượng giao lộ thực.

# 3. Phương pháp luận

Năm bước áp dụng: (1) kiểm kê baseline/yêu cầu; (2) xây Kripke và giả định; (3) sinh JSON/SMV/CTL; (4) kiểm chứng, đọc trace và đối chứng lỗi; (5) đối chiếu trước/sau, hash và giới hạn. Đây là vận dụng của nhóm; guide PDF tr.5 yêu cầu năm bước nhưng không định nghĩa đầy đủ quy trình gốc trong tài liệu đề tài chưa được cung cấp.

K=(S,S₀,R,L): S là trạng thái đạt được; S₀ là trạng thái đầu; R⊆S×S là quan hệ bước giây toàn phần; L:S→2^AP gán mệnh đề nguyên tử. Python State=(phase,remaining,period,entry_period,clock), intersection.py:48–53. SMV có 18 VAR: phase,timer,hour,minute,second,entry_period và 12 boolean đèn; period/clock_sec là DEFINE (SMV:3–37).

S₀: 00:00:00, ALL_RED_EW_TO_NS, timer=2, entry_period=NIGHT_LOW, bốn đèn đỏ bật, các đèn khác tắt (SMV:39–74; config.json:2–3). Một trạng thái gồm pha, timer, clock và đèn; không đồng nhất một pha với một trạng thái Kripke.

```text
clock′=(clock+1) mod 86400; p′=period(clock′)
r>1: q′=q, r′=r−1, e′=e
r=1: q′=NEXT(q), r′=D(q′,p′), e′=p′
Lamps′=lamps(q′)
```

R diễn giải từ intersection.py:60–74; đây là ký hiệu toán, không phải mã nguồn.

Chu kỳ: NS_GREEN → NS_YELLOW → ALL_RED_NS_TO_EW → EW_GREEN → EW_YELLOW → ALL_RED_EW_TO_NS. MORNING_PEAK 07–09h, EVENING_PEAK 16–19h, NIGHT_LOW 22–06h, NORMAL còn lại. Xanh NS/EW tương ứng 45/35,35/45,15/15,25/25 giây; vàng 3, ALL_RED 2. Chốt entry_period đến hết pha (config.json:4–20).

L sinh từ label(), intersection.py:95–104: 12 nhãn *_on/*_off, phase_*,period_*,entry_*,timer_*,clock_* ở exact và safe/one_hot/reset_ok/transition_ok… write_spec():130–137 ghi description,states,initial,labeling,transitions,suggested_ctl_formulas. build.py:19–26 sinh SMV và JSON. Exact giữ clock; GUI bỏ clock và cho thêm cạnh đổi period hợp lệ.

CTL: A/E là mọi/tồn tại nhánh, X bước kế, F cuối cùng, G luôn, U cho đến (không dùng hiện tại). AG(!conflicting_green), AG(AF(n_green)), AG(EX(TRUE)) lần lượt kiểm safety/liveness/deadlock. NuSMV BDD kiểm 335 CTL đầy đủ; checker JSON chỉ hỗ trợ một toán tử AG/AF/EF/EG/AX/EX với một atom và phủ định tùy chọn, dùng 26 công thức. Nhãn quy tắc phải được kiểm lại trên cạnh bằng oracle độc lập.

Công cụ: Python 3.11, NuSMV 2.7.1; không C/C++ sanitizer/data_gen/seed. Sinh quỹ đạo xác định từ config, state-limit mặc định 1.000.000. Lệnh và danh mục mọi CTLSPEC tại Phụ lục B–D.

# 4. Phân tích lỗ hổng & Bản vá

## 4.1. D01 — Timer thêm một khoảng giây ở giá trị 0

### 1. Vị trí & mô tả

Smart-Traffic-Light-Verification/02_time_based_model/timed_light.smv:37–75. Lỗi/ngữ nghĩa hiện hữu, không có dấu hiệu fault-injection; không gán CWE/CERT.

### 2. Nguyên nhân gốc rễ

Pha chỉ đổi khi timer hiện tại bằng 0. Cập nhật đồng bộ đưa 1 về 0 nhưng giữ pha. Chú thích gọi GREEN là 30 giây; dưới quy ước một bước = một giây, chuỗi 30,…,0 giữ GREEN qua 31 khoảng giây.

### 3. Bằng chứng lỗi tồn tại

CTL bổ sung yêu cầu NS_GREEN/timer=1 bước sau phải NS_YELLOW trả FALSE. Trace State 1.30 timer=1 → State 1.31 timer=0, state vẫn NS_GREEN. Hai LTL cận timer gốc vẫn TRUE.

```text
AG((state = NS_GREEN & timer = 1) -> AX(state = NS_YELLOW))
```

Truy vấn CTL mới chỉ thêm đặc tả trên bản sao, giữ nguyên chuyển tiếp v0; output/official_report_20261024/evidence/v0_timer_added_query.log:17.

### 4. Cách vá

Trước v0 — Smart-Traffic-Light-Verification/02_time_based_model/timed_light.smv:42–46

```text
  42 | state = NS_GREEN
  43 | &
  44 | timer = 0 :
  45 | 
  46 | NS_YELLOW;
```

Sau v1 — chapter1/smart_intersection.smv:49–50

```text
  49 |   init(timer) := initial_duration;
  50 |   next(timer) := case timer > 1 : timer - 1; timer = 1 : next_phase_duration; TRUE : timer; esac;
```

Chuyển tại remaining=1, miền timer>=1 (SMV:5,30). Pha D giây có đúng D khoảng giây, không chờ timer=0.

### 5. Bằng chứng đã vá

chapter1/smart_intersection.smv:366

```text
AG((phase = NS_GREEN & timer = 1) -> AX(phase = NS_YELLOW))
```

output/official_report_20261024/evidence/v1_main_recheck.log:291 trả TRUE trong lượt mới 335/335. 24 ca thời lượng và 42 ranh giới có ở graph_results.json lịch sử; hai JSON được duyệt lại.

Giới hạn: D+1 phụ thuộc quy ước một bước là một giây; chưa có bộ lập lịch vật lý. V1 đổi cả tham số thời lượng, không so hiệu năng bằng các tham số khác nhau.

## 4. Phân tích lỗ hổng & Bản vá (tiếp)

## 4.2. D02 — Guard NORMAL_TIME trùng làm mất hai khung giờ

### 1. Vị trí & mô tả

Smart-Traffic-Light-Verification/03_adaptive_model/adaptive_light.smv:110–152. Lỗi/ngữ nghĩa hiện hữu, không có dấu hiệu fault-injection; không gán CWE/CERT.

### 2. Nguyên nhân gốc rễ

case chọn nhánh đúng đầu tiên. NORMAL_TIME tại dòng 117 che nhánh cùng guard tại 133. Từ init NORMAL_TIME chỉ luân phiên NORMAL_TIME/MORNING_PEAK; EVENING_PEAK và NIGHT_LOW không đạt được. traffic_mode đọc period cũ nên lệch một bước so với period mới.

### 3. Bằng chứng lỗi tồn tại

EF(time_period = EVENING_PEAK) và EF(time_period = NIGHT_LOW) đều FALSE. NuSMV in trạng thái đầu NORMAL_TIME cho mỗi phản ví dụ khả đạt; đây không phải vết tuần hoàn đầy đủ. Mười LTL gốc TRUE, gồm kéo theo có tiền đề NIGHT_LOW không đạt được.

```text
EF(time_period = EVENING_PEAK); EF(time_period = NIGHT_LOW)
```

Truy vấn CTL mới chỉ thêm đặc tả trên bản sao, giữ nguyên chuyển tiếp v0; output/official_report_20261024/evidence/v0_adaptive_added_queries.log:17.

### 4. Cách vá

Trước v0 — nhánh đầu — Smart-Traffic-Light-Verification/03_adaptive_model/adaptive_light.smv:117–119

```text
 117 | time_period = NORMAL_TIME :
 118 | 
 119 | MORNING_PEAK;
```

Trước v0 — nhánh bị che — Smart-Traffic-Light-Verification/03_adaptive_model/adaptive_light.smv:133–135

```text
 133 | time_period = NORMAL_TIME :
 134 | 
 135 | EVENING_PEAK;
```

Sau v1 — tra lịch clock mới — chapter1/intersection.py:70–74

```text
  70 | def step(cfg,s):
  71 |     if s.clock is None: raise ValueError('Exact step needs the 24-hour clock')
  72 |     clock=(s.clock+1)%86400
  73 |     return advance(cfg,s,cfg.period(clock),clock)
  74 | 
```

SMV:27–28 là lịch sinh dài tương đương hàm period. Chốt entry_period riêng tại SMV:47–48, không đổi timer khi qua mốc giờ giữa pha.

### 5. Bằng chứng đã vá

chapter1/smart_intersection.smv:319

```text
AG((second = 59 & minute = 59 & hour = 23) -> AX(hour = 0))
```

output/official_report_20261024/evidence/v1_main_recheck.log:244 trả TRUE trong lượt mới 335/335. Bốn EF(period) TRUE trong chapter1/evidence/nusmv_period_reachability.log:17–20 (lịch sử), không đổi thành kết quả mới.

Giới hạn: Lịch 24 giờ là mở rộng v1, chưa chứng minh tương đương tổng quát v0/v1. EF chỉ chứng minh tồn tại đường đi, không phải mọi nhánh đều đến period.

## 4. Phân tích lỗ hổng & Bản vá (tiếp)

## 4.3. D03 — Nạp thời lượng pha nguồn vào pha đích

### 1. Vị trí & mô tả

Smart-Traffic-Light-Verification/03_adaptive_model/adaptive_light.smv:216–282. Lỗi/ngữ nghĩa hiện hữu, không có dấu hiệu fault-injection; không gán CWE/CERT.

### 2. Nguyên nhân gốc rễ

next(state) và next(timer) cùng tính từ trạng thái cũ. GREEN hết giờ đi sang YELLOW nhưng reset lại nạp 45/30/20; YELLOW hết giờ đi sang GREEN lại nạp 5. LTL cũ X timer=45 kiểm đúng chính hành vi nạp sai nên vẫn TRUE.

### 3. Bằng chứng lỗi tồn tại

CTL bổ sung yêu cầu hết NS_GREEN vào NS_YELLOW/timer=5 trả FALSE. State 3.31: NS_GREEN, timer=0, traffic_mode=PEAK; State 3.32: NS_YELLOW, timer=45. Đây là kiểm trực tiếp mới, khác N2 cố ý reset thành 1.

```text
AG((state = NS_GREEN & timer = 0) -> AX(state = NS_YELLOW & timer = 5))
```

Truy vấn CTL mới chỉ thêm đặc tả trên bản sao, giữ nguyên chuyển tiếp v0; output/official_report_20261024/evidence/v0_adaptive_added_queries.log:29.

### 4. Cách vá

Trước v0 — Smart-Traffic-Light-Verification/03_adaptive_model/adaptive_light.smv:216–222

```text
 216 | state = NS_GREEN
 217 | &
 218 | timer = 0
 219 | &
 220 | traffic_mode = PEAK :
 221 | 
 222 | 45;
```

Sau v1 — chapter1/intersection.py:65–68

```text
  65 | def advance(cfg,s,next_period,next_clock=None):
  66 |     if s.remaining>1: return State(s.phase,s.remaining-1,next_period,s.entry_period,next_clock)
  67 |     phase=NEXT[s.phase]
  68 |     return State(phase,cfg.duration(phase,next_period),next_period,next_period,next_clock)
```

SMV:29–32 chọn phase_after rồi D(phase_after,period_next); SMV:48–50 cập nhật latch và timer cùng bước, kiểm cả pha đích và period mới.

### 5. Bằng chứng đã vá

chapter1/smart_intersection.smv:369

```text
AG((phase = NS_GREEN & timer = 1 & period_next = NORMAL) -> AX(phase = NS_YELLOW & timer = 3 & entry_period = NORMAL))
```

output/official_report_20261024/evidence/v1_main_recheck.log:314 trả TRUE trong lượt mới 335/335. 24 ca thời lượng và 42 ranh giới có ở graph_results.json lịch sử; hai JSON được duyệt lại.

Giới hạn: Vàng v0 là 5 theo chú thích/nhánh Yellow duration; v1 là 3 theo config. Sửa cách chọn pha đích kèm đổi tham số; không chạy cùng một công thức nguyên văn trên hai mô hình.

## 4.4. Giới hạn đặc tả và mở rộng — tách khỏi D01–D03

L01 — Safety enum quá yếu: 03_bmc/traffic_light_bmc.smv kiểm G !(state=NS_GREEN & state=EW_GREEN), hiển nhiên đúng do miền enum. Đây là giới hạn đặc tả, không có bằng chứng đồng xanh trong file đó. V1 kiểm 12 boolean, one-hot, đồng bộ (SMV:76–90). N1 xác nhận thuộc tính mới nhạy với lỗi đầu ra, không phải counterexample v0.

Trước v0 — Smart-Traffic-Light-Verification/03_bmc/traffic_light_bmc.smv:53–63

```text
  53 | LTLSPEC
  54 | 
  55 | G !(
  56 | 
  57 | state = NS_GREEN
  58 | 
  59 | &
  60 | 
  61 | state = EW_GREEN
  62 | 
  63 | );
```

Sau v1 — chapter1/smart_intersection.smv:34–36

```text
  34 |   ns_go := n_green | s_green;
  35 |   ew_go := e_green | w_green;
  36 |   conflicting_green := ns_go & ew_go;
```

chapter1/smart_intersection.smv:76

```text
AG(!conflicting_green)
```

L02 — Đổi/siết yêu cầu vàng/all-red: safety_liveness.smv:25–28,37–96 cho (NS=GREEN,EW=RED) → (NS=YELLOW,EW=GREEN). Đây là vết suy từ ASSIGN, không phải counterexample log cũ. Bốn LTL gốc TRUE; yêu cầu vàng đối diện đỏ chưa có. LTL cấm cả hai RED tại 125–135 mâu thuẫn clearance v1, nên không tuyên bố bảo toàn mọi LTL v0.

V0 — NS GREEN sang YELLOW — Smart-Traffic-Light-Verification/04_verification/safety_liveness.smv:42–44

```text
  42 | NS_light = GREEN :
  43 | 
  44 | YELLOW;
```

V0 — EW RED sang GREEN — Smart-Traffic-Light-Verification/04_verification/safety_liveness.smv:76–78

```text
  76 | EW_light = RED :
  77 | 
  78 | GREEN;
```

chapter1/smart_intersection.smv:88

```text
AG((n_yellow | s_yellow) -> (e_red & w_red))
```

chapter1/smart_intersection.smv:373

```text
AG((phase = NS_YELLOW & timer = 1) -> AX(phase = ALL_RED_NS_TO_EW))
```

Mở rộng v1: 12 đèn, hai all-red, clock 24 giờ, latch, JSON và web. Không gọi thêm tính năng là vá CWE. Emergency v0 chưa tích hợp. traffic_light_bmc_bug.smv chỉ MODULE main; hai fixture test chưa SPEC; test.smv gốc là đăng nhập ngoài nghiệp vụ.

Mẫu v0 cố ý sai: init_bug.smv khởi tạo GREEN/GREEN; hai transition_bug.smv bỏ S1. Archive có ba FALSE trong 28 công thức. transition_bug_fixed.smv đã TRUE. Không tính những mẫu này vào D01–D03 hoặc gán cho v1.

## 4.5. Thí nghiệm cấy lỗi N1 và N2

Negative là bản sao v1 kiểm độ nhạy đặc tả. Giữ riêng nguồn hợp lệ; harness đạt khi thuộc tính FALSE dự kiến và có counterexample. Không gán fault chủ đích thành lỗi gốc.

## N1 — Xanh Đông đồng thời NS_GREEN

Trước — v1 chính thức — chapter1/smart_intersection.smv:68

```text
  68 |   next(e_green) := (phase_next = EW_GREEN);
```

Sau — N1 — chapter1/evidence/negative_conflicting_green.smv:68

```text
  68 |   next(e_green) := (phase_next = EW_GREEN | phase_next = NS_GREEN);
```

```text
CTLSPEC AG(!conflicting_green);
```

output/official_report_20261024/evidence/recheck_negative_conflicting_green.log:17 — FALSE.

```text
  50 |   -> State: 1.3 <-
  51 |     n_green = TRUE
  52 |     s_green = TRUE
  53 |     e_green = TRUE
  54 |     timer = 15
  55 |     phase = NS_GREEN
  56 |     second = 2
  57 |     conflicting_green = TRUE
  58 |     ew_go = TRUE
  59 |     ns_go = TRUE
  60 |     next_phase_duration = 3
  61 |     phase_after = NS_YELLOW
```

t=2s: n_green=s_green=e_green=TRUE, conflicting_green=TRUE; w_green không đổi nên FALSE. Enum phase vẫn NS_GREEN. Đây là lỗi đầu ra mà safety enum không quan sát được.

## N2 — Reset mọi pha thành 1

Trước — v1 chính thức — chapter1/smart_intersection.smv:50

```text
  50 |   next(timer) := case timer > 1 : timer - 1; timer = 1 : next_phase_duration; TRUE : timer; esac;
```

Sau — N2 — chapter1/evidence/negative_timer_reset.smv:50

```text
  50 |   next(timer) := case timer > 1 : timer - 1; timer = 1 : 1; TRUE : timer; esac;
```

```text
AG((phase = ALL_RED_EW_TO_NS & timer = 1 &
    period_next = NIGHT_LOW) -> AX(timer = 15))
```

output/official_report_20261024/evidence/recheck_negative_timer_reset.log:17 — FALSE.

```text
  37 |   -> State: 1.2 <-
  38 |     timer = 1
  39 |     second = 1
  40 |     phase_next = NS_GREEN
  41 |     next_second = 2
  42 |     clock_sec = 1
  43 |   -> State: 1.3 <-
  44 |     phase = NS_GREEN
  45 |     second = 2
  46 |     next_phase_duration = 3
  47 |     phase_next = NS_YELLOW
  48 |     phase_after = NS_YELLOW
  49 |     next_second = 3
  50 |     clock_sec = 2
```

t=1s timer=1; t=2s vào NS_GREEN nhưng timer không in lại vì vẫn 1, thay vì 15 NIGHT_LOW. Trace NuSMV in theo thay đổi; phải kế thừa giá trị. N2 khác D03 nạp thời lượng pha nguồn.

## 4.6. Thí nghiệm N3 — Bỏ qua ALL_RED

Fault chỉ đổi nhánh NS_YELLOW trong phase_after để đi thẳng EW_GREEN. Miền enum vẫn có ALL_RED; việc có tên pha không chứng minh clearance được đi qua.

Trước — chapter1/smart_intersection.smv:29; nguyên dòng được ngắt khi trình bày, không sửa mã:

```text
  29 |   phase_after := case phase = NS_GREEN : NS_YELLOW; phase = NS_YELLOW : ALL_RED_NS_TO_EW; phase = ALL_RED_NS_TO_EW : EW_GREEN; phase = EW_GREEN : EW_YELLOW; phase = EW_YELLOW : ALL_RED_EW_TO_NS; phase = ALL_RED_EW_TO_NS : NS_GREEN; TRUE : NS_GREEN; esac;
```

Sau — chapter1/evidence/negative_skip_all_red.smv:29

```text
  29 |   phase_after := case phase = NS_GREEN : NS_YELLOW; phase = NS_YELLOW : EW_GREEN; phase = ALL_RED_NS_TO_EW : EW_GREEN; phase = EW_GREEN : EW_YELLOW; phase = EW_YELLOW : ALL_RED_EW_TO_NS; phase = ALL_RED_EW_TO_NS : NS_GREEN; TRUE : NS_GREEN; esac;
```

```text
CTLSPEC AG((phase = NS_YELLOW & timer = 1) -> AX(all_red));
```

output/official_report_20261024/evidence/recheck_negative_skip_all_red.log:17 — FALSE; log đầy đủ trong evidence/.

```text
 143 |   -> State: 1.20 <-
 144 |     timer = 1
 145 |     second = 19
 146 |     phase_next = EW_GREEN
 147 |     next_second = 20
 148 |     clock_sec = 19
 149 |   -> State: 1.21 <-
 150 |     phase = EW_GREEN
 151 |     timer = 15
 152 |     n_red = TRUE
 153 |     s_red = TRUE
 154 |     e_red = FALSE
 155 |     w_red = FALSE
 156 |     second = 20
 157 |     next_phase_duration = 3
 158 |     phase_after = EW_YELLOW
 159 |     next_second = 21
 160 |     clock_sec = 20
 161 | 
 162 | STDERR
```

State 1.20 t=19s: NS_YELLOW/timer=1. State 1.21 t=20s: EW_GREEN, e_red=w_red=FALSE; all_red không in lại nên vẫn FALSE. Không có ALL_RED_NS_TO_EW xen giữa. N3 khác lỗi mẫu v0 bỏ YELLOW.

## Độ nhạy và chuyển tiếp đúng

Ba negative mới: mỗi mô hình đúng một thuộc tính, cả ba FALSE dự kiến. Không có bằng chứng chạy cả 335 CTL trên mỗi negative. PASS harness nghĩa là bắt được lỗi, không phải mô hình lỗi đúng. V1 chính thức TRUE ở safety/reset/advance/clearance.

chapter1/smart_intersection.smv:373

```text
AG((phase = NS_YELLOW & timer = 1) -> AX(phase = ALL_RED_NS_TO_EW))
```

chapter1/smart_intersection.smv:90

```text
AG((phase = ALL_RED_NS_TO_EW | phase = ALL_RED_EW_TO_NS) -> all_red)
```

Cần kiểm giữ pha khi timer>1, đổi đúng pha khi timer=1, reset theo pha đích/period mới, cập nhật 12 đèn theo phase_next. Chỉ mutex không bắt mọi lỗi bỏ pha. verify_graph.py:27–64 kiểm độc lập nhãn và các cạnh JSON đã lưu.

# 5. Bảng tổng hợp before/after

Bảng 5.1. D01–D03 khớp 1–1 với mục 4.1–4.3. CWE/CERT chưa gán vì chưa có căn cứ phân loại. Tên log ngắn trong bảng thuộc thư mục evidence/ của gói báo cáo, trừ khi ghi rõ log gốc.

| Mã / vị trí v0 | Trạng thái v0 có thể kiểm | Trạng thái v1 / công cụ |
|---|---|---|
| D01; Smart-Traffic-Light-Verification/02_time_based_model/timed_light.smv:42–46 | CTL mới FALSE: timer=1 → 0, vẫn NS_GREEN; v0_timer_added_query.log:17,80–83. | SMV:30,50 đổi tại timer=1. advance_NS_GREEN TRUE ở log mới; 24 ca thời lượng lưu trữ. |
| D02; Smart-Traffic-Light-Verification/03_adaptive_model/adaptive_light.smv:117–135 | EF EVENING_PEAK/NIGHT_LOW đều FALSE; v0_adaptive_added_queries.log:17–28. | Clock tra period; 4 EF TRUE ở chapter1/evidence/nusmv_period_reachability.log:17–20; clock_* TRUE mới. |
| D03; Smart-Traffic-Light-Verification/03_adaptive_model/adaptive_light.smv:216–282 | Reset vàng=5 FALSE; State 3.31 NS_GREEN/0 → 3.32 NS_YELLOW/45 trong log adaptive mới. | SMV:29–32,48–50 reset theo D(pha đích,period mới); reset_NS_GREEN_NORMAL TRUE mới. |

Bảng 5.2. Những hạng mục khác không cộng vào ba lỗi gốc ở trên.

| Loại | Before / giới hạn | After / bằng chứng |
|---|---|---|
| L01: đặc tả yếu | Enum không quan sát lỗi đầu ra. | 12 boolean + safety/one-hot; N1 FALSE khi bị cấy lỗi. |
| L02: siết yêu cầu | YELLOW/GREEN suy từ code; cấm cả hai RED. | Vàng đối diện đỏ + all-red; CTL TRUE; không bảo toàn yêu cầu cấm cùng RED. |
| Mở rộng | Thiếu mô hình clock/12 đèn/web thống nhất. | Exact 86400 nút/cạnh; chiếu 1012/2548; adapter web. |
| N1–N3 chủ đích | Đồng xanh/reset=1/bỏ ALL_RED. | 3 thuộc tính FALSE dự kiến, có trace; khác lỗi gốc v0. |

Số TRUE tăng không phải tỉ lệ sửa lỗi: v0/v1 khác yêu cầu, tham số và biểu diễn. Chưa có bisimulation/refinement tổng quát. Chỉ ghi v0 FALSE cho truy vấn thực sự đã chạy; không biến nhận xét đọc code thành kết quả công cụ.

# 6. Bằng chứng kiểm chứng

## 6.1. Kết quả tách theo công cụ và thời điểm

Audit hoàn tất trước soạn thảo: 243 tệp nội dung dự án, loại runtime/thư viện/cache. Mọi tệp có trước khớp hash. Mã sinh từ config/Python trùng toàn văn SMV/properties; v1 trùng bản nusmv_main.smv của archive.

| Phép kiểm / nguồn | Số lượng | Kết quả / log |
|---|---|---|
| NuSMV v1, mới | 335 CTL | 335 TRUE; evidence/v1_main_recheck.log |
| V0 + query, mới | 4 CTL mới + 12 LTL gốc | 4 FALSE dự kiến; 12 TRUE; evidence/v0_*.log |
| Negative v1, mới | 3 mô hình × 1 CTL | 3 FALSE có trace; evidence/recheck_negative_*.log |
| BDD toàn bộ v1, mới | 86400 reachable | v1_reachable_recheck.log; đếm không -coi |
| Python JSON CTL, mới | 26 CTL trên bản chiếu | 26 TRUE; json_ctl_recheck.json; khác NuSMV/SecLab |
| Duyệt JSON, mới | 2 đồ thị | Exact 86400/86400; chiếu 1012/2548; 0 deadlock |
| NuSMV clock đầu bất kỳ, archive | 335 CTL | 335 TRUE; chapter1/evidence/nusmv_any_start_time.log |
| NuSMV period, archive | 4 EF | 4 TRUE; nusmv_period_reachability.log |
| SecLab Ch1 gốc, archive | 26 CTL + parser exact | 26 PASS, mutex PASS, 0 deadlock; seclab_results.json |
| Biên / thời lượng / config, archive | 42 / 24 / 4 sai + 1 thay thế | PASS; graph_results.json |
| Web, archive | 13 backend + 32 browser checks | PASS; chapter1/web/evidence/*_tests.json |

Không cộng CTL, số trạng thái và ca giao diện thành một tổng test. Record riêng có 838 dòng truy vết, phân loại mới/lưu trữ và đơn vị. Chứng cứ gốc chỉ được đọc lại, không đổi thành lượt mới.

NuSMV 2.7.1 dùng BDD/CTL, -dynamic -df -coi. Banner MiniSat không chứng minh đã chạy SAT/BMC. Harness kiểm đủ số công thức và từng true/false; exit code 0 riêng lẻ chưa đủ. Thời điểm chạy mới từ fresh_nusmv_results.json (UTC), không dùng ngày biên soạn thay ngày chạy archive.

## 6.2. Log, nhóm CTL và hai đồ thị

| Nhóm CTL | Số công thức |
|---|---|
| safety | 11 |
| liveness | 4 |
| deadlock | 1 |
| timer | 45 |
| clock | 228 |
| transition | 12 |
| reachability | 6 |
| adaptive | 28 |
| Tổng | 335 |

Bảng 6.2. Đếm properties.json và CTLSPEC NAME trong SMV:76–410; mọi công thức/file/dòng ở ctl_catalog.json.

```text
 345 | -- specification AG !conflicting_green  is true
 346 | -- specification AG (n_red = s_red & e_red = w_red)  is true
 347 | -- specification AG (n_yellow = s_yellow & e_yellow = w_yellow)  is true
 348 | -- specification AG (n_green = s_green & e_green = w_green)  is true
 349 | -- specification AG ((n_yellow | s_yellow) -> (e_red & w_red))  is true
```

Trích 6.1. Log v1 mới; output/official_report_20261024/evidence/v1_main_recheck.log:345. Bản đầy đủ ở evidence/.

```text
  17 | system diameter: 86400
  18 | reachable states: 86400 (2^16.3987) out of 3.82206e+11 (2^38.4756)
```

Trích 6.2. output/official_report_20261024/evidence/v1_reachable_recheck.log:18. Số 86400 dành cho S₀ mặc định, không mặc định cho cấu hình khác hoặc clock đầu bất kỳ.

Exact: 86400 trạng thái/cạnh, một quỹ đạo về chỉ số 0. Bản chiếu giữ (q,r,p,e), bỏ clock, thêm đổi period nên có 1012 trạng thái/2548 cạnh. build.py:28–38 kiểm mọi cạnh exact chiếu vào cạnh abstract; audit mới duyệt lại nhãn, đèn, timer, cạnh và liveness trên cả hai JSON.

Phép chiếu giữ AP chung về đèn/timer. Safety/liveness phổ quát trên abstract áp dụng cho các đường exact được mô phỏng. Không suy EF abstract thành EF exact; khả đạt period exact được kiểm riêng bằng NuSMV. Abstract có thể giữ period mãi nên không dùng AF(period_*) chứng minh lịch chính xác.

AF(green) của JSON được kiểm từ S₀; tập thỏa thực tế là toàn bộ 1012 trạng thái. Reverse-worklist độc lập cũng chứng minh cuối cùng xanh từ mọi trạng thái. NuSMV dùng AG(AF(green)). Chờ xanh lớn nhất 55 giây mỗi hướng trong bản chiếu là số của mô hình, không phải đo xe ngoài đường.

## 6.3. Ảnh giao diện và nguồn lưu trữ

![Hình 6.1. Ảnh Kripke có sẵn: chapter1/web/evidence/screenshots/02-kripke.png. Minh họa duyệt trạng thái/nhãn, không thay stdout hay đếm BDD.](C:/Users/Admin/Desktop/NuSMV_project/chapter1/web/evidence/screenshots/02-kripke.png)

![Hình 6.2. Ảnh web có sẵn: chapter1/web/evidence/screenshots/03-kiem-chung-moi.png. Ngày/mã lượt đối chiếu browser_tests.json; không đại diện lượt báo cáo mới.](C:/Users/Admin/Desktop/NuSMV_project/chapter1/web/evidence/screenshots/03-kiem-chung-moi.png)

Ảnh sao chép nguyên byte, hash trong source_inventory.json. 32 browser checks không phải 32 CTL. backend_tests.json ghi tổng hợp 13 unittest, không failures/errors; không có stdout từng method, record ghi rõ mức chứng cứ này.

V0 archive: output/nusmv_results.json có 14 bản ghi, 28 công thức =25 TRUE+3 FALSE; FALSE thuộc mẫu lỗi minh họa. Ba file chưa SPEC không có PASS nghiệp vụ. before_v0_logs/*.stdout.log là trích nguyên văn archive, không có timestamp/lệnh đầy đủ; không bổ sung hồi tố.

# 7. Phản biện & Bài học

## Nếu bắt đầu lại, nhóm thiết kế lại phần nào?

Nhóm sẽ đặc tả đơn vị thời gian, cách lấy thời lượng pha đích và lịch trước ASSIGN. Một nguồn ngữ nghĩa chuyển tiếp cùng oracle độc lập giúp tránh guard trùng và nhầm trạng thái cũ/mới. Safety phải dựa trên đầu ra, kèm thứ tự pha và khả đạt, tránh enum hiển nhiên đúng hoặc kéo theo đúng rỗng.

## Điều gì còn nghi ngờ hoặc thiếu bằng chứng?

Chưa có refinement/bisimulation tổng quát giữa các ví dụ v0 và v1; chưa có lỗi đèn, cảm biến, truyền thông hay ưu tiên khẩn cấp. Đây là phạm vi chưa mô hình hóa, không phải lỗ hổng đã xác nhận. SecLab đã kiểm headless nhưng chưa xác nhận thao tác nạp trong cửa sổ GUI; ảnh web chỉ chứng minh giao diện web.

## Bài học phương pháp luận lớn nhất

Model checking trả lời đặc tả trên tập hành vi đã mô hình hóa. Mười LTL adaptive v0 đều TRUE vẫn đi cùng nhánh giờ không đạt được và reset sai mục đích; cần non-vacuity và đọc vết theo giá trị kế thừa. Fault chủ đích kiểm độ nhạy, không chứng minh tập thuộc tính đầy đủ cho mọi lỗi.

## Giới hạn và phát triển

Đổi thời lượng có thể tạo quỹ đạo nhiều ngày, phải dựng/đếm lại. JSON exact khoảng 55 MB khó dùng trong GUI; graph chiếu dễ xem nhưng mất clock và thêm nhánh. Có thể thiết kế trừu tượng thời gian với chứng minh quan hệ mô phỏng/AP, rồi thêm cảm biến và ưu tiên có giới hạn để kiểm liveness dưới tải thay đổi.

Bước tiếp theo cần mô hình plant/thiết bị, người đi bộ/rẽ trái, trễ thực và thẩm định giao thông. TRUE hiện tại không chứng minh an toàn vật lý hay thông lượng. Không thêm fairness để che nhánh treo; giả định fairness mới phải được nêu và kiểm tác động.

Về bằng chứng: tách ngày viết/ngày chạy, công cụ NuSMV/JSON/SecLab và archive/lượt mới; giữ baseline bằng hash, log nguyên văn, query thêm có nhãn rõ. Báo cáo không tạo commit, danh tính hay mã CWE/CERT giả.

# 8. Phụ lục

## A. Cấu trúc gói và cách đọc

Đường dẫn tính từ gốc NuSMV_project; tên evidence/ ngắn khi ghi rõ gói báo cáo thuộc output/official_report_20261024/. file:dòng dùng số dòng thật. JSON một dòng dùng khóa/chỉ số, không bịa dòng con. Mọi đầu ra mới nằm riêng trong gói này.

| Tệp / thư mục | Vai trò |
|---|---|
| BAO_CAO_CHINH_THUC.docx/.pdf | Bản chỉnh sửa và PDF nộp |
| KIEM_KE_BANG_CHUNG.md / evidence_inventory.json | Kiểm kê trước viết, lỗi và khoảng trống |
| BIEN_BAN_KIEM_CHUNG.docx/.pdf | Record riêng expected/actual/log |
| verification_test_cases.csv/.json | Toàn bộ 838 dòng truy vết |
| source_inventory.json/.csv | 243 tệp nội dung, bytes/hash |
| evidence_index.csv | Mọi bằng chứng/lượt web đã kiểm kê |
| ctl_catalog.json / all_ctlspec_declarations.json | 335 công thức chính thức và mọi CTLSPEC artifact |
| evidence/ / appendix_repository/ | Log mới / bản sao nguyên văn archive |
| PHU_LUC_NGUON_VA_BANG_CHUNG.zip | Nguồn và log đầy đủ kể cả lượt web, hai JSON; không runtime/cache |
| architecture.mmd/.png | Sơ đồ kiến trúc chỉnh sửa được |
| CHECKLIST_TIEU_CHI.md | Checklist trực tiếp từ PDF trường |
| MUC_LUC_TRANG.md / quality_validation.json | Mục lục trang thật / kiểm tra đầu ra |

Phụ lục điện tử là phần nộp kèm: log nguyên văn tại evidence/, appendix_repository/ và ZIP. Thân bài trích có caption/số dòng; không in lại hàng trăm dòng lặp. Mọi source/log đều truy bằng chỉ mục và SHA-256. Cần giảng viên xác nhận chấp nhận phụ lục điện tử nộp kèm.

## Mục lục

Tám mục và phụ lục có số trang PDF thật ở MUC_LUC_TRANG.md; tạo sau render, không điền số trang giả trước phân trang.

## B. Lệnh tái lập và tham số

PowerShell tại gốc dự án, Python 3.11+, NuSMV trên PATH. Không data_gen/seed: dữ liệu xác định từ config. Các lệnh sản phẩm sau có ghi đè artifact sinh; chỉ cung cấp hướng dẫn, không chạy trong tác vụ báo cáo:

```text
python chapter1/build.py --state-limit 1000000
python chapter1/verify_graph.py
python chapter1/verify_nusmv.py
python chapter1/count_nusmv.py
powershell -NoProfile -ExecutionPolicy Bypass -File chapter1/run_seclab.ps1 -ScriptPath chapter1/verify_target.py
python chapter1/web/server.py
```

Tái lập chiến dịch báo cáo trong thư mục riêng:

```text
python -B output/official_report_20261024/audit_report.py
python -B output/official_report_20261024/build_official_report.py
node output/official_report_20261024/render_pdf.mjs
python -B output/official_report_20261024/validate_delivery.py
```

Lệnh NuSMV thực tế (đường dẫn tuyệt đối trong results JSON):

```text
NuSMV -dynamic -df -coi <delivery>/evidence/v1_main_recheck.smv
NuSMV -dynamic -r -is -ils -ii <delivery>/evidence/v1_main_recheck.smv
```

V0 bổ sung giữ prefix nội dung gốc, chỉ thêm CTLSPEC cuối file. Timer:2 LTL TRUE+1 CTL FALSE. Adaptive:10 LTL TRUE+3 CTL FALSE. NuSMV có thể in CTL trước LTL; đối chiếu công thức và số lượng thay vì mặc định thứ tự nguồn.

| Lượt mới | Bắt đầu UTC | Số thuộc tính |
|---|---|---|
| v1_main_recheck | 2026-10-23T23:59:02.402145+00:00 | 335; PASS theo expected |
| v0_timer_added_query | 2026-10-23T23:59:02.670090+00:00 | 3; PASS theo expected |
| v0_adaptive_added_queries | 2026-10-23T23:59:02.715663+00:00 | 13; PASS theo expected |
| recheck_negative_conflicting_green | 2026-10-23T23:59:02.806012+00:00 | 1; PASS theo expected |
| recheck_negative_timer_reset | 2026-10-23T23:59:02.883018+00:00 | 1; PASS theo expected |
| recheck_negative_skip_all_red | 2026-10-23T23:59:07.793543+00:00 | 1; PASS theo expected |

UTC cộng 7 giờ để đổi sang Asia/Bangkok/Việt Nam. Thời gian chạy thật và lệnh trong fresh_nusmv_results.json; không so thời gian checker để kết luận tối ưu giao thông.

## C. Nguồn v0 và vai trò

| Mã / đường dẫn | TRUE/FALSE gốc | Phân loại |
|---|---|---|
| V0-01; Smart-Traffic-Light-Verification/01_basic_model/traffic_light_model.smv | 1/0 | Giới hạn mô hình bốn pha |
| V0-02; Smart-Traffic-Light-Verification/02_time_based_model/timed_light.smv | 2/0 | Ngữ nghĩa timer=0 khác yêu cầu đúng D giây |
| V0-03; Smart-Traffic-Light-Verification/03_adaptive_model/adaptive_light.smv | 10/0 | Lỗi logic thích nghi hiện hữu, nguồn không đánh dấu fault-injection |
| V0-04; Smart-Traffic-Light-Verification/03_bmc/init_bug.smv | 0/1 | Mẫu lỗi khởi tạo theo tên/vai trò init_bug |
| V0-05; Smart-Traffic-Light-Verification/03_bmc/traffic_light_bmc.smv | 1/0 | Giới hạn safety enum, không có lỗi cấy được phát hiện |
| V0-06; Smart-Traffic-Light-Verification/03_bmc/traffic_light_bmc_bug.smv | 0/0 | File khung, chưa có thuộc tính hoặc fault thực thi |
| V0-07; Smart-Traffic-Light-Verification/03_bmc/transition_bug.smv | 1/1 | Fault chuyển tiếp có chủ đích, có chú thích nguồn |
| V0-08; Smart-Traffic-Light-Verification/04_verification/safety_liveness.smv | 4/0 | Hạn chế thiết kế/tập yêu cầu, không đánh dấu fault-injection |
| V0-09; Smart-Traffic-Light-Verification/05_bug_analysis/transition_bug.smv | 0/1 | Fault chuyển tiếp có chủ đích, có BUG INTRODUCED HERE |
| V0-10; Smart-Traffic-Light-Verification/05_bug_analysis/transition_bug_fixed.smv | 1/0 | Bản sửa đối chứng đã TRUE, không phải lỗi cạnh còn tồn tại |
| V0-11; Smart-Traffic-Light-Verification/06_extension/emergency_mode.smv | 4/0 | Ví dụ emergency, chức năng chưa được tích hợp vào v1 |
| V0-12; Smart-Traffic-Light-Verification/test/traffic_light2.smv | 0/0 | Fixture chưa có SPEC |
| V0-13; Smart-Traffic-Light-Verification/test/traffic_light_basic.smv | 0/0 | Fixture chưa có SPEC |
| V0-14; test.smv | 1/0 | Ví dụ đăng nhập ngoài nghiệp vụ giao lộ |

Stdout: chapter1/evidence/before_v0_logs/<V0-id>_<stem>.stdout.log; JSON audit có array index/hash; phụ lục giữ bản nguyên văn. output/excel_graph_check.* là đồ thị trộn lịch sử của tác vụ Excel đã hủy; không biến bảy FALSE của nó thành bảy lỗi giao lộ, không chạy lại workflow Excel.

kripke_model.png gốc: 0 byte, không dùng. Hình 2.1 có nguồn Mermaid, không phải ảnh thí nghiệm.

## D. Biến, AP và toàn bộ CTLSPEC

| Thành phần | Vị trí |
|---|---|
| VAR / DEFINE | SMV:3–37; 18 VAR, 12 boolean; period là DEFINE |
| Init / next | SMV:39–74; intersection.py:60–74 |
| S,S₀,R,L JSON | intersection.py:48–53,95–137; build.py:19–38 |
| 335 CTLSPEC NAME | SMV:76–410; ctl_catalog.json ghi name/formula/category/source_line |
| 26 CTL JSON | intersection.py:106–109; suggested_ctl_formulas ở hai JSON |
| Mọi CTLSPEC artifact | all_ctlspec_declarations.json: 4077 khai báo, gồm snapshot/fault lặp; không phải yêu cầu độc lập |
| Nguồn / bằng chứng đầy đủ | source_inventory.json/.csv; evidence_index.csv có path/bytes/hash và nguồn sao phụ lục |

chapter1/smart_intersection.smv:92

```text
AG(timer >= 1 & timer <= phase_duration)
```

chapter1/smart_intersection.smv:365

```text
AG((phase = NS_GREEN & timer > 1) -> AX(phase = NS_GREEN))
```

chapter1/smart_intersection.smv:373

```text
AG((phase = NS_YELLOW & timer = 1) -> AX(phase = ALL_RED_NS_TO_EW))
```

chapter1/smart_intersection.smv:406

```text
AG((phase = ALL_RED_EW_TO_NS & timer = 1 & period_next = NIGHT_LOW) -> AX(phase = NS_GREEN & timer = 15 & entry_period = NIGHT_LOW))
```

chapter1/smart_intersection.smv:408

```text
AG((entry_period = NORMAL & timer > 1) -> AX(entry_period = NORMAL))
```

chapter1/smart_intersection.smv:91

```text
AG(EX(TRUE))
```

Các mẫu trên TRUE trong log v1 mới; danh mục máy đọc giữ toàn bộ 335 công thức. all_ctlspec_declarations.json phân biệt v1 chính thức, negative, query thêm và snapshot. Số khai báo tổng không phải số test duy nhất.

## E. Phân công và phản hồi giảng viên

| Thành viên / MSSV | Công việc thật | Chứng cứ đóng góp |
|---|---|---|
| [HỌ TÊN — MSSV] | [MÔ HÌNH / ĐẶC TẢ / NGÀY] | [FILE / COMMIT THẬT NẾU CÓ] |
| [HỌ TÊN — MSSV] | [KIỂM CHỨNG / TRACE] | [LOG / COMMIT THẬT] |
| [HỌ TÊN — MSSV] | [WEB / TÀI LIỆU / TEST] | [FILE / COMMIT THẬT] |

Bảng E.1. Placeholder, không suy đoán tác giả từ tên tệp.

| Ngày / người góp ý | Nội dung cần xác nhận | Xử lý / trạng thái |
|---|---|---|
| [NGÀY — GIẢNG VIÊN] | D01–D03 thay mã CWE/CERT cho lỗi mô hình? | [PHẢN HỒI] — Chờ |
| [NGÀY — GIẢNG VIÊN] | Giữ tên v0/v1 hiện có, bảng ánh xạ thay hậu tố? | [PHẢN HỒI] — Chờ |
| [NGÀY — GIẢNG VIÊN] | Mã đề tài/tuần học và quy trình 5 bước gốc? | [TÀI LIỆU ĐỀ TÀI] — Thiếu |
| [NGÀY — GIẢNG VIÊN] | Chấp nhận log đầy đủ trong phụ lục điện tử? | [PHẢN HỒI] — Chờ |

Còn thiếu danh tính, lớp, nhóm, GitHub và phân công thật; tài liệu đề tài để xác định tuần/mã đề tài; quyết định chấm CWE/CERT, tên phiên bản và phụ lục điện tử. Audit mới đã bù counterexample trực tiếp timer/reset/reachability; không còn gọi các truy vấn này là chưa chạy.

Chưa có thử giao lộ vật lý, cảm biến, emergency hoặc thao tác GUI SecLab. Timestamp/lệnh đầy đủ của v0 archive vẫn thiếu; lượt query mới có provenance riêng, không sửa lịch sử.

## F. Checklist tiêu chí theo report_guide.pdf

| Tiêu chí bảng 3, PDF tr.8 | Trọng số | Đối chiếu |
|---|---|---|
| Đầy đủ cấu trúc 8 phần | 10% | Đủ tám Heading 1, đúng tên/thứ tự |
| Chất lượng phân tích lỗ hổng (Phần 4) | 35% | D01–D03 đủ 5 mục; CWE/CERT chờ giảng viên |
| Bảng before/after (Phần 5) | 15% | D01–D03 khớp 1–1, trạng thái gắn log |
| Chất lượng bằng chứng (Phần 6) | 20% | Log nguyên văn, chỉ mục/hash; tách công cụ và lượt; phụ lục điện tử |
| Chiều sâu phản biện (Phần 7) | 10% | Ba câu hỏi, giới hạn Kripke/CTL cụ thể |
| Định dạng & trình bày | 10% | Times New Roman 11.5pt, A4 lề2cm, trang/caption; quy ước phiên bản cần duyệt |

Tổng 100%, độc lập tiêu chí mã nguồn. Không tự chấm điểm hoặc hứa mức điểm.

Checklist PDF tr.8–9: đủ tám phần; phân loại lỗi cụ thể; đủ năm mục/lỗi; bảng khớp; log/ảnh có caption; v0 nguyên vẹn; lệnh build; data_gen/seed ghi không áp dụng thay bằng config/hash; phản biện cụ thể; PDF mở/font/đủ trang. CWE/CERT và tên phiên bản chờ giảng viên, không tự đánh dấu đạt.

Độ dài gợi ý: bìa1, tổng quan1–1.5, phương pháp1, phân tích3–6, bảng1, bằng chứng1–3, phản biện0.5–1, phụ lục không giới hạn. Kiểm trang thực trong quality_validation.json.

Tham chiếu: [G1] report_guide.pdf, Phenikaa, CSE703153, 2026–2027, PDF tr.3–9. [R1] Mã/log trong source_inventory.json, truy cập 24/10/2026. [R2] chapter1/BEFORE_AFTER_V0_V1.md và evidence/before_after_audit.json; đối chiếu lại với source/hash/log trước viết.
