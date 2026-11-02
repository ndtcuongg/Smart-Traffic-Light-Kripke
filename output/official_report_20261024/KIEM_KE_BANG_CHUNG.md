# Kiểm kê bằng chứng — hoàn tất trước viết báo cáo

Audit 243 tệp nội dung; mọi hash giữ nguyên; loại runtime/thư viện/cache.

## D01 — Timer thêm một khoảng giây ở giá trị 0

1. V0: Smart-Traffic-Light-Verification/02_time_based_model/timed_light.smv:37–75
2. Nguyên nhân: Pha chỉ đổi khi timer hiện tại bằng 0. Cập nhật đồng bộ đưa 1 về 0 nhưng giữ pha. Chú thích gọi GREEN là 30 giây; dưới quy ước một bước = một giây, chuỗi 30,…,0 giữ GREEN qua 31 khoảng giây.
3. Quan sát: CTL bổ sung yêu cầu NS_GREEN/timer=1 bước sau phải NS_YELLOW trả FALSE. Trace State 1.30 timer=1 → State 1.31 timer=0, state vẫn NS_GREEN. Hai LTL cận timer gốc vẫn TRUE.
4. V1: chapter1/smart_intersection.smv:49–50; chapter1/smart_intersection.smv:366
5. CTL `AG((phase = NS_GREEN & timer = 1) -> AX(phase = NS_YELLOW))` TRUE tại output/official_report_20261024/evidence/v1_main_recheck.log:291; v0 FALSE tại output/official_report_20261024/evidence/v0_timer_added_query.log:17
6. Giới hạn: D+1 phụ thuộc quy ước một bước là một giây; chưa có bộ lập lịch vật lý. V1 đổi cả tham số thời lượng, không so hiệu năng bằng các tham số khác nhau.

## D02 — Guard NORMAL_TIME trùng làm mất hai khung giờ

1. V0: Smart-Traffic-Light-Verification/03_adaptive_model/adaptive_light.smv:110–152
2. Nguyên nhân: case chọn nhánh đúng đầu tiên. NORMAL_TIME tại dòng 117 che nhánh cùng guard tại 133. Từ init NORMAL_TIME chỉ luân phiên NORMAL_TIME/MORNING_PEAK; EVENING_PEAK và NIGHT_LOW không đạt được. traffic_mode đọc period cũ nên lệch một bước so với period mới.
3. Quan sát: EF(time_period = EVENING_PEAK) và EF(time_period = NIGHT_LOW) đều FALSE. NuSMV in trạng thái đầu NORMAL_TIME cho mỗi phản ví dụ khả đạt; đây không phải vết tuần hoàn đầy đủ. Mười LTL gốc TRUE, gồm kéo theo có tiền đề NIGHT_LOW không đạt được.
4. V1: chapter1/smart_intersection.smv:23–28; chapter1/smart_intersection.smv:319
5. CTL `AG((second = 59 & minute = 59 & hour = 23) -> AX(hour = 0))` TRUE tại output/official_report_20261024/evidence/v1_main_recheck.log:244; v0 FALSE tại output/official_report_20261024/evidence/v0_adaptive_added_queries.log:17
6. Giới hạn: Lịch 24 giờ là mở rộng v1, chưa chứng minh tương đương tổng quát v0/v1. EF chỉ chứng minh tồn tại đường đi, không phải mọi nhánh đều đến period.

## D03 — Nạp thời lượng pha nguồn vào pha đích

1. V0: Smart-Traffic-Light-Verification/03_adaptive_model/adaptive_light.smv:216–282
2. Nguyên nhân: next(state) và next(timer) cùng tính từ trạng thái cũ. GREEN hết giờ đi sang YELLOW nhưng reset lại nạp 45/30/20; YELLOW hết giờ đi sang GREEN lại nạp 5. LTL cũ X timer=45 kiểm đúng chính hành vi nạp sai nên vẫn TRUE.
3. Quan sát: CTL bổ sung yêu cầu hết NS_GREEN vào NS_YELLOW/timer=5 trả FALSE. State 3.31: NS_GREEN, timer=0, traffic_mode=PEAK; State 3.32: NS_YELLOW, timer=45. Đây là kiểm trực tiếp mới, khác N2 cố ý reset thành 1.
4. V1: chapter1/smart_intersection.smv:29–32; chapter1/smart_intersection.smv:369
5. CTL `AG((phase = NS_GREEN & timer = 1 & period_next = NORMAL) -> AX(phase = NS_YELLOW & timer = 3 & entry_period = NORMAL))` TRUE tại output/official_report_20261024/evidence/v1_main_recheck.log:314; v0 FALSE tại output/official_report_20261024/evidence/v0_adaptive_added_queries.log:29
6. Giới hạn: Vàng v0 là 5 theo chú thích/nhánh Yellow duration; v1 là 3 theo config. Sửa cách chọn pha đích kèm đổi tham số; không chạy cùng một công thức nguyên văn trên hai mô hình.

## Phân loại khác

L01 enum yếu; L02 siết yêu cầu vàng/all-red; tách khỏi lỗi D01–D03. Mẫu init_bug/transition_bug cố ý sai tách riêng. N1–N3 fault trên bản sao v1, mỗi CTL FALSE dự kiến. Emergency chưa tích hợp; khung/fixture chưa SPEC không PASS nghiệp vụ.

## Kripke và CTLSPEC

18 VAR: phase,timer,hour,minute,second,entry_period,12 boolean. period là DEFINE. S0/R: SMV:39–74, intersection.py:60–74. L: intersection.py:95–104. Exact86400 nút/cạnh, chiếu1012/2548. 335 công thức chính thức trong ctl_catalog.json; mọi khai báo trong all_ctlspec_declarations.json.

## Khoảng trống

- Student names, IDs, class, group, GitHub URL and actual task assignments
- Instructor approval for domain defect identifiers instead of CWE/CERT and actual filename convention
- Course topic guide and its canonical five-step methodology not supplied
- Historical v0 commands/timestamps absent from archived records; fresh supplemental queries are labeled separately
- No physical traffic validation; emergency not implemented in v1; exact GUI import not manually demonstrated

Counterexample mới bù thiếu chứng cứ trực tiếp timer/reset/reachability của archive, không sửa lịch sử.