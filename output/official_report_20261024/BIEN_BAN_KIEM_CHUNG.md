## BIÊN BẢN KIỂM CHỨNG HÌNH THỨC

Đề tài: Mô hình hóa và kiểm chứng hình thức cho hệ thống các đèn giao thông thông minh sử dụng cấu trúc Kripke.

Lập ngày 24/10/2026; nhóm/người kiểm: [HỌ TÊN — MSSV]. Baseline v0/v1 giữ nguyên. Log mới trong output/official_report_20261024/evidence/.

Mục tiêu: tái kiểm v1, xác nhận D01–D03 bằng query thêm trên bản sao v0, đánh giá N1–N3 và JSON. Đây là kiểm chứng mô hình; web archive ghi riêng, không tuyên bố chạy lại.

| Tiền điều kiện / môi trường | Giá trị |
|---|---|
| Công cụ | Python 3.11; NuSMV 2.7.1; checker JSON độc lập |
| Đầu vào | config.json, smart_intersection.smv; hash trong source_inventory.json |
| S₀ | 00:00:00, ALL_RED_EW_TO_NS, timer=2, bốn đỏ bật |
| Lệnh | python -B output/official_report_20261024/audit_report.py |
| Tiêu chí đạt | Đúng số công thức, exit0, từng actual khớp expected; negative phải FALSE |

| Ca / nhóm | Expected | Actual / log |
|---|---|---|
| 335 CTL v1 | 335 TRUE | 335 TRUE; v1_main_recheck.log |
| D01: timer tại 1 | FALSE v0 | FALSE; v0_timer_added_query.log:17 |
| D02: hai EF | 2 FALSE v0 | 2 FALSE; v0_adaptive_added_queries.log:17–28 |
| D03: reset vàng=5 | FALSE v0 | FALSE; v0_adaptive_added_queries.log:29 trở đi |
| 12 LTL v0 đi kèm | Giữ TRUE gốc | 12 TRUE trong hai log query; không sửa R |
| N1/N2/N3 | 1 FALSE/mô hình + trace | 3 FALSE; recheck_negative_*.log |
| JSON CTL | 26 TRUE | 26 TRUE; json_ctl_recheck.json |
| Exact/chiếu | 86400/86400;1012/2548 | Khớp; json_graph_recheck.json |
| BDD reachable | 86400 | 86400; v1_reachable_recheck.log |

CSV/JSON riêng liệt kê 838 dòng expected/actual/evidence/notes. Không coi số dòng là số yêu cầu độc lập; có lượt chạy khác nhau và các đơn vị khác nhau.

## Chi tiết quy trình, phạm vi và kết luận record

## D01 — Timer thêm một khoảng giây ở giá trị 0

Nguồn: Smart-Traffic-Light-Verification/02_time_based_model/timed_light.smv:37–75. Query: AG((state = NS_GREEN & timer = 1) -> AX(state = NS_YELLOW)). Expected=FALSE v0, actual=FALSE; output/official_report_20261024/evidence/v0_timer_added_query.log:17. Sau cải tiến: chapter1/smart_intersection.smv:366 TRUE tại output/official_report_20261024/evidence/v1_main_recheck.log:291.

## D02 — Guard NORMAL_TIME trùng làm mất hai khung giờ

Nguồn: Smart-Traffic-Light-Verification/03_adaptive_model/adaptive_light.smv:110–152. Query: EF(time_period = EVENING_PEAK); EF(time_period = NIGHT_LOW). Expected=FALSE v0, actual=FALSE; output/official_report_20261024/evidence/v0_adaptive_added_queries.log:17. Sau cải tiến: chapter1/smart_intersection.smv:319 TRUE tại output/official_report_20261024/evidence/v1_main_recheck.log:244.

## D03 — Nạp thời lượng pha nguồn vào pha đích

Nguồn: Smart-Traffic-Light-Verification/03_adaptive_model/adaptive_light.smv:216–282. Query: AG((state = NS_GREEN & timer = 0) -> AX(state = NS_YELLOW & timer = 5)). Expected=FALSE v0, actual=FALSE; output/official_report_20261024/evidence/v0_adaptive_added_queries.log:29. Sau cải tiến: chapter1/smart_intersection.smv:369 TRUE tại output/official_report_20261024/evidence/v1_main_recheck.log:314.

N1–N3: bản sao base v1, đổi đúng biểu thức ở mục 4.5–4.6. Expected/actual FALSE cả ba, có counterexample. Chỉ một CTL trên mỗi negative. Trace kế thừa biến không được in lại; EF FALSE có thể chỉ in trạng thái đầu.

JSON: duyệt mọi cạnh/12 đèn/khả đạt/timer/reset/liveness trên hai graph; checker CTL độc lập chạy 26 công thức trên bản chiếu, không gọi NuSMV/SecLab. SecLab archive là công cụ khác.

| Nguồn archive | Số lượng | Mức chứng cứ |
|---|---|---|
| graph_results.json | 42 biên,24 thời lượng,4 sai,1 thay thế | Từng ca lưu trữ; không chạy hàm ghi lại artifact |
| nusmv_any_start_time.log | 335 CTL | Log đầy đủ, results JSON khớp |
| nusmv_period_reachability.log | 4 EF | Log đầy đủ |
| seclab_results.json | 26 CTL,mutex,parser exact | Ch1 nguyên gốc, headless |
| backend_tests.json | 13 unittest | Tổng hợp; không stdout từng method |
| browser_tests.json | 32 checks | Mỗi tên/details/status; khác CTL |

Kết luận: các ca mới đạt expected; hash nguồn kiểm kê giữ nguyên. Không timeout hoặc kết quả ngoài dự kiến trong lượt audit hoàn chỉnh. Danh tính người kiểm và xác nhận nhóm cần điền thật. Chưa có test vật lý/emergency/GUI SecLab.

Người kiểm thử: [HỌ TÊN — MSSV — CHỮ KÝ]
Đại diện nhóm: [HỌ TÊN — CHỮ KÝ]
