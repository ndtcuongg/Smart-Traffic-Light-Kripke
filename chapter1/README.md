# Chương 1 — Kripke & kiểm chứng giao lộ thông minh

Đã hoàn thành mô hình bốn hướng có 12 đèn ON/OFF, all-red, timer từng giây, đồng hồ 24 giờ và bốn khung giờ thích nghi. JSON được nạp và kiểm chứng bằng **mã Chương 1 thật đóng gói trong SecLabFramework.exe**. Chỉ triển khai Chương 1; không gọi pipeline đa chương.

## Mở các kết quả chính

- [Đối chiếu Before (v0) / After (v1)](BEFORE_AFTER_V0_V1.md).
- [smart_intersection.json](smart_intersection.json): JSON cho nút **Nạp từ file khác...** trong tab **Ch1: Kripke & Verification**.
- [smart_intersection.smv](smart_intersection.smv): mô hình NuSMV chuẩn, dùng clock giờ/phút/giây và 12 biến boolean đèn.
- [kripke_explorer.html](kripke_explorer.html): mở trực tiếp bằng trình duyệt, duyệt mọi trạng thái và mọi cạnh đi ra; không cần máy chủ.
- [kripke_overview.svg](kripke_overview.svg): tổng quan có đầy đủ đèn, timer và quy tắc chuyển tiếp.
- [kripke_boundary.svg](kripke_boundary.svg): 34 trạng thái liên tiếp qua 07:00, liệt kê đủ 12 trạng thái đèn ở mỗi giây.
- [kripke_full.dot](kripke_full.dot): đồ thị đầy đủ của JSON cho GUI; [kripke_exact.dot](kripke_exact.dot): đồ thị đầy đủ có clock chính xác.
- [smart_intersection_exact.json](smart_intersection_exact.json): bản giữ nguyên clock 24 giờ, cùng schema Chương 1; khoảng 55 MB, ưu tiên kiểm tra headless.

## Phạm vi và công việc được giữ lại

Đã kiểm tra toàn bộ file dự án hiện có. Các file cũ được bảo toàn, đối chiếu SHA-256 trước/sau trong [preserved_work.json](evidence/preserved_work.json). Không có file cũ nào bị sửa hoặc xóa. Thư mục output và scripts/generate_spec.py thuộc tác vụ Excel đã hủy, chỉ được giữ như kết quả lịch sử, không được gọi trong quy trình này.

Các ý tưởng/mô hình được kế thừa:

| File hiện có | Nội dung tái sử dụng/đối chiếu |
|---|---|
| Smart-Traffic-Light-Verification/01_basic_model/traffic_light_model.smv | Thứ tự chu kỳ NS/EW |
| Smart-Traffic-Light-Verification/02_time_based_model/timed_light.smv | Timer đếm giảm; xác định lỗi thêm một bước timer=0 |
| Smart-Traffic-Light-Verification/03_adaptive_model/adaptive_light.smv | Ý tưởng điều chỉnh thời lượng theo giờ; xác định nhánh NORMAL_TIME trùng và nạp sai thời lượng pha mới |
| Smart-Traffic-Light-Verification/04_verification/safety_liveness.smv | Mục tiêu safety/liveness giữa hai luồng |
| Smart-Traffic-Light-Verification/05_bug_analysis/transition_bug*.smv | Cách dùng lỗi chuyển tiếp làm đối chứng; không sửa ví dụ lỗi |
| output/nusmv_results.json | Kết quả chạy cũ dùng làm đối chiếu lịch sử |

File 03_bmc/traffic_light_bmc_bug.smv chỉ có MODULE main và chưa có mô hình/thuộc tính. Đây là dữ liệu cũ, không tiếp tục triển khai BMC. Thư mục login.smv rỗng; test.smv ở gốc là ví dụ đăng nhập, không ghép vào giao lộ. File mới smart_intersection.smv là mô hình chuẩn đã sửa timer/time-period; các ví dụ cũ vẫn giữ nguyên để so sánh.

## Yêu cầu và giả định

1. North/South đi đồng bộ, East/West đi đồng bộ; hai nhóm vuông góc xung đột phải loại trừ nhau.
2. Mỗi cột có RED, YELLOW, GREEN; đúng một đèn ON và hai đèn OFF trong mọi trạng thái đạt được.
3. Khi NS vàng, EW phải đỏ; khi EW vàng, NS phải đỏ. Giữa hai luồng xanh có hai pha all-red riêng biệt.
4. Một bước mô hình là đúng 1 giây mô phỏng. Không có bước chờ timer=0.
5. Bắt đầu tại 00:00:00, ALL_RED_EW_TO_NS, timer=2. Cấu hình có thể thay giờ/pha khởi tạo.
6. Thời lượng được chốt khi vào pha theo thời điểm mới. Đổi khung giờ giữa pha không đổi timer hoặc cắt ngắn pha đang chạy.
7. Không có yêu cầu ưu tiên vô hạn, lỗi phần cứng, chuyển đèn không đồng thời, người đi bộ hay rẽ trái bảo vệ. Đây là giao lộ cho hai luồng đi thẳng tương thích trong mỗi nhóm; hai hướng đối diện trong cùng nhóm được xanh cùng nhau.
8. Liveness áp dụng cho vận hành bình thường với bước giây tiếp tục chạy; không thêm giả định fairness để che nhánh treo.

## Cấu hình khung giờ và thời lượng

[config.json](config.json) là cấu hình riêng của bộ dựng mô hình, không phải schema JSON đầu vào của ứng dụng. Mọi thời lượng phải là số nguyên 1..120 giây; các khoảng giờ phải phủ kín [00:00:00,24:00:00), không hở hoặc chồng nhau.

| Bắt đầu (bao gồm) | Kết thúc (không bao gồm) | Khung giờ |
|---|---|---|
| 00:00:00 | 06:00:00 | NIGHT_LOW |
| 06:00:00 | 07:00:00 | NORMAL |
| 07:00:00 | 09:00:00 | MORNING_PEAK |
| 09:00:00 | 16:00:00 | NORMAL |
| 16:00:00 | 19:00:00 | EVENING_PEAK |
| 19:00:00 | 22:00:00 | NORMAL |
| 22:00:00 | 24:00:00 | NIGHT_LOW |

| Khung giờ | NS_GREEN | EW_GREEN | NS/EW_YELLOW | Mỗi ALL_RED |
|---|---:|---:|---:|---:|
| MORNING_PEAK | 45s | 35s | 3s | 2s |
| NORMAL | 25s | 25s | 3s | 2s |
| EVENING_PEAK | 35s | 45s | 3s | 2s |
| NIGHT_LOW | 15s | 15s | 3s | 2s |

Đây là lịch thích nghi theo thời gian, chưa có cảm biến đếm xe. MORNING_PEAK ưu tiên NS, EVENING_PEAK ưu tiên EW. Những con số này là tham số mô hình, chưa phải thiết kế giao thông cho một giao lộ ngoài thực tế.

## Trạng thái đèn và quy tắc chuyển tiếp

| Pha | North/South (RED,YELLOW,GREEN) | East/West (RED,YELLOW,GREEN) | Pha sau khi hết giờ |
|---|---|---|
| NS_GREEN | OFF,OFF,ON | ON,OFF,OFF | NS_YELLOW |
| NS_YELLOW | OFF,ON,OFF | ON,OFF,OFF | ALL_RED_NS_TO_EW |
| ALL_RED_NS_TO_EW | ON,OFF,OFF | ON,OFF,OFF | EW_GREEN |
| EW_GREEN | ON,OFF,OFF | OFF,OFF,ON | EW_YELLOW |
| EW_YELLOW | ON,OFF,OFF | OFF,ON,OFF | ALL_RED_EW_TO_NS |
| ALL_RED_EW_TO_NS | ON,OFF,OFF | ON,OFF,OFF | NS_GREEN |

NuSMV lưu riêng n_red/n_yellow/n_green, s_*, e_*, w_* dưới dạng boolean. next() của từng đèn lấy từ phase_next cùng một bước. JSON ghi đủ nhãn _on hoặc _off cho từng đèn, kể cả đèn đang OFF. Safety kiểm trên những boolean/nhãn vật lý này, không kiểm biểu thức tầm thường state=A & state=B.

Quy tắc mỗi giây, với q là pha, r là số giây còn lại, p là khung giờ hiện tại, e là khung giờ chốt đầu pha:

```text
clock_next = (clock + 1) mod 86400
p_next = period(clock_next)
nếu r > 1: q_next=q; r_next=r-1; e_next=e
nếu r = 1: q_next=NEXT(q); r_next=D(q_next,p_next); e_next=p_next
12 đèn của trạng thái mới = bảng đèn(q_next)
```

Ví dụ YELLOW=3: trạng thái vào pha có timer=3, sau 1 giây là 2, sau 2 giây là 1, sau đúng 3 giây sang ALL_RED. Do đó pha kéo dài đúng 3 giây; không phát sinh giây thứ tư do trạng thái timer=0. Khi NS_GREEN bắt đầu 06:59:55 với 25 giây NORMAL, lúc 07:00 timer=20 và entry_period vẫn NORMAL; chỉ khi vào pha mới mới dùng MORNING_PEAK.

## Cấu trúc Kripke K=(S,S₀,R,L)

**Bản chính xác:** S gồm các tuple đạt được (q,r,clock,p,e,12 đèn); p và 12 đèn là thành phần suy ra xác định nhưng vẫn được ghi rõ trong nhãn. S₀ chỉ gồm trạng thái khởi tạo theo config. R là quan hệ bước giây nêu trên. L chứa phase_*, timer_*, clock_*, period_*, entry_*, đủ 12 nhãn đèn ON/OFF và các mệnh đề hành vi. Với config mặc định, S=86.400 và |R|=86.400, toàn bộ một chu kỳ 24 giờ, sau đó trở về S₀.

**Bản cho GUI:** bỏ clock chính xác, giữ (q,r,p,e,12 đèn). Khung giờ có thể giữ nguyên hoặc đi theo cạnh lịch: NIGHT_LOW→NORMAL; MORNING_PEAK→NORMAL; EVENING_PEAK→NORMAL; NORMAL→MORNING_PEAK/EVENING_PEAK/NIGHT_LOW. Việc đổi khung giờ được phép xảy ra ở bất kỳ bước giây nào; đây là phép xấp xỉ bảo thủ có thêm hành vi, không phải lịch đồng hồ chính xác. Timer và chốt đầu pha vẫn đầy đủ, không rút gọn chỉ còn 6 pha.

Đã duyệt tất cả 86.400 cạnh của bản chính xác để chứng minh phép chiếu alpha(q,r,clock,p,e,đèn)=(q,r,p,e,đèn) ánh xạ vào cạnh tồn tại trong bản GUI. Vì vậy kết quả safety và liveness trên mọi nhánh của bản GUI cũng áp dụng cho đường chạy chính xác. Độ chính xác của giờ trong ngày và việc tuần hoàn các khung giờ được giữ và kiểm tra trong NuSMV/bản JSON chính xác. Bản GUI chỉ dùng EF(period_*), không khẳng định AF(period_*) trên xấp xỉ có thể giữ nguyên khung giờ mãi.

Các mệnh đề safe, one_hot, synchronized, yellow_safe, all_red_correct được tính từ 12 đèn thực. countdown_ok/reset_ok/transition_ok được tính bằng so sánh trạng thái nguồn và mọi trạng thái đích với quy tắc timer/pha. Chúng được kiểm lại độc lập từ JSON đã lưu, không chỉ gán tên nhãn là coi như đã chứng minh.

## Schema thực tế của SecLabFramework

Nguồn đích: C:\Users\Admin\Downloads\SecLabFramework.exe. Đã truy cập mẫu dataset/ch1_verification/traffic_light.json đóng gói và đọc bytecode/parser core.kripke. Hash nguồn và thông tin runtime ở runtime_provenance.json, target_runtime.json và seclab_parser_disassembly.txt trong evidence. Mẫu ba luồng/chín trạng thái chỉ dùng xác định định dạng; không dùng làm mô hình của giao lộ mới.

JSON đầu vào có đúng các khóa đã có trong mẫu: description, states, initial, labeling, transitions, suggested_ctl_formulas. states là danh sách chuỗi; initial là danh sách ID; labeling là object ID→list nhãn; transitions là các cặp [nguồn,đích]. Không thêm trường timer, duration, clock hoặc mutual_exclusion lạ vào schema: chúng được mã hóa trong ID/nhãn hoặc config riêng. Không dùng wrapper state_machine/safety_properties của định dạng chương khác.

Parser thật đã chạy: KripkeStructure.from_json_file(). Kiểm chứng dùng CTLChecker.check(), find_deadlock_states(), check_mutual_exclusion(model,"ns_go","ew_go"). Ràng buộc mutex được thể hiện bằng nhãn ns_go/ew_go, AG(!conflicting_green) và lời gọi API Chương 1; không tự bịa trường JSON cho mutex.

Bản CTL đi kèm ứng dụng chỉ đọc một toán tử AG/AF/EF/EG/AX/EX với một nhãn nguyên tử, có thể thêm !. Nó không phân tích công thức lồng nhau hoặc phép hội tùy ý. Vì vậy JSON dùng đúng tập con hỗ trợ; NuSMV kiểm CTL đầy đủ. Ở kết quả thực tế, AF(n_green_on)... có tập trạng thái thỏa bằng toàn bộ S, nên GREEN cuối cùng đạt được từ mọi trạng thái chứ không chỉ một lần từ khởi tạo.

## Thuộc tính và kết quả đã thực thi

| Nội dung | Công cụ/thuộc tính | Kết quả thực tế |
|---|---|---|
| Safety và mutex | NuSMV AG(!conflicting_green); API mutex ns_go/ew_go | PASS, không trạng thái vi phạm |
| Đúng một đèn, đồng bộ NS/EW | 12 boolean trong NuSMV và nhãn JSON | PASS |
| Vàng an toàn và all-red | Các thuộc tính yellow_*/clearance_all_red | PASS |
| Liveness lặp lại | NuSMV AG(AF(n_green)), tương tự S/E/W; reverse-worklist độc lập | PASS; chờ GREEN tối đa 55s ở mỗi hướng trong xấp xỉ |
| Deadlock | AG(EX(TRUE)); kiểm mọi cạnh và find_deadlock_states() thật | PASS, 0 deadlock |
| Đếm giảm, nạp lại, chốt đầu pha | countdown_*, reset_*, latch_*, timer_bounds | PASS |
| Đồng hồ 24 giờ | 228 công thức tick/hold giờ/phút/giây; kiểm cạnh JSON | PASS, có vòng 23:59:59→00:00:00 |
| Reachability | EF sáu pha và bốn period trực tiếp trong NuSMV; EF trong SecLab; BFS bản chính xác | PASS, đủ sáu pha và bốn period |
| Thứ tự chuyển pha | hold_*/advance_*, kiểm mọi cạnh JSON | PASS |
| Đổi giờ giữa pha | 42 ca ranh giới; NuSMV cho clock ban đầu bất kỳ | PASS |
| Thời lượng đúng D giây | 24 ca (6 pha × 4 period) | PASS |
| Cấu hình | 4 cấu hình sai bị từ chối; thời lượng thay thế 17/41 giây | PASS |
| Trình xem sơ đồ | Edge headless: 8 kiểm tra tương tác, không exception | PASS |

Kết quả chính:

- SecLabFramework Chương 1: **26/26 CTL PASS**; parser nạp được cả JSON GUI và JSON chính xác.
- NuSMV cấu hình mặc định: **335/335 CTL PASS**; khởi tạo clock bất kỳ: **335/335 PASS**.
- Số trạng thái đạt được đo trực tiếp bằng NuSMV BDD: **86400**, khớp đồ thị JSON chính xác; phép đếm chạy 16.68s.
- Đồ thị GUI: **1012 trạng thái, 2548 cạnh**. Bản chính xác: **86400 trạng thái/cạnh**.
- Bốn EF(period) chạy riêng trong nusmv_period_reachability.log đều PASS. Không báo PASS chỉ dựa trên exit code; bộ chạy yêu cầu đúng số công thức và kiểm từng kết quả true/false.

Phân nhóm 335 công thức NuSMV trong [properties.json](properties.json):

| Nhóm | Số công thức |
|---|---:|
| safety | 11 |
| liveness | 4 |
| deadlock | 1 |
| timer | 45 |
| clock | 228 |
| transition | 12 |
| reachability | 6 |
| adaptive | 28 |

Đối chứng có lỗi — thuộc tính thật phải FAIL, harness chỉ PASS khi tìm đúng FAIL:

| Bản lỗi | Kết quả thuộc tính | Phản ví dụ |
|---|---|---|
| Cho e_green bật cùng NS_GREEN | FAIL như dự kiến | [negative_conflicting_green.log](evidence/negative_conflicting_green.log): t=2s, N/S/E cùng GREEN |
| Mọi lần reset timer đều nạp 1 | FAIL như dự kiến | [negative_timer_reset.log](evidence/negative_timer_reset.log): vào NS_GREEN chỉ 1 thay vì 15s NIGHT_LOW |
| NS_YELLOW đi thẳng EW_GREEN | FAIL như dự kiến | [negative_skip_all_red.log](evidence/negative_skip_all_red.log): t=20s vào EW_GREEN, không qua all-red |

Log/báo cáo: [seclab_results.json](evidence/seclab_results.json), [nusmv_results.json](evidence/nusmv_results.json), [nusmv_main.log](evidence/nusmv_main.log), [nusmv_any_start_time.log](evidence/nusmv_any_start_time.log), [nusmv_reachable.log](evidence/nusmv_reachable.log), [graph_results.json](evidence/graph_results.json), [diagram_results.json](evidence/diagram_results.json).

## Các file thay đổi và file mới

- File cũ được sửa: **không có**. File cũ được xóa: **không có**.
- Toàn bộ phần triển khai mới nằm trong chapter1/. CHAPTER1.md ở gốc là trang hướng dẫn vào phần này.
- Mô hình/cấu hình/JSON: config.json, intersection.py, nusmv_model.py, build.py, smart_intersection.smv, properties.json, smart_intersection.json, smart_intersection_exact.json.
- Kiểm chứng: run.py, verify_graph.py, verify_nusmv.py, verify_target.py, count_nusmv.py; bằng chứng thực thi ở evidence/.
- Tích hợp runtime gốc: bootstrap_seclab.py, run_seclab.ps1, inspect_runtime.py, probe_target.py; runtime tái trích nằm ở ../.chapter1-tools/, không phải mã mô hình.
- Sơ đồ/tài liệu: make_diagrams.py, make_docs.py, check_diagrams.mjs, kripke_*.svg/.dot/.html, README.md.
- Danh sách file mới và hash cuối cùng ở [artifact_manifest.json](evidence/artifact_manifest.json).

## Lệnh chạy chính xác (PowerShell, từ gốc NuSMV_project)

NuSMV phải có trên PATH; Python 3.11 là đủ cho bộ dựng/kiểm JSON. Không cần openpyxl hoặc thư viện Excel. Các lệnh sau chỉ chạy Chương 1:

```powershell
python chapter1/run.py
```

Ho?c ch?y ri?ng t?ng b??c:

```powershell
python chapter1/build.py
python chapter1/verify_graph.py
python chapter1/verify_nusmv.py
python chapter1/count_nusmv.py
powershell -NoProfile -ExecutionPolicy Bypass -File chapter1/run_seclab.ps1 -ScriptPath chapter1/verify_target.py
python chapter1/make_diagrams.py
node chapter1/check_diagrams.mjs
python chapter1/make_docs.py
```

Chạy trực tiếp mô hình NuSMV, không cần bộ script:

```powershell
NuSMV -dynamic -df -coi chapter1/smart_intersection.smv
NuSMV -dynamic -r -is -ils -ii chapter1/smart_intersection.smv
```

Để tái tạo môi trường kiểm chứng gốc nếu thư mục .chapter1-tools chưa có:

```powershell
python chapter1/bootstrap_seclab.py --exe C:/Users/Admin/Downloads/SecLabFramework.exe
```

run_seclab.ps1 nạp runtime Python 3.14 từ chính ứng dụng trong tiến trình PowerShell riêng, rồi chỉ gọi API Chương 1. Không mở GUI hoặc chạy run_pipeline(). Lệnh kiểm giao diện sơ đồ cần Node.js và Edge ở đường dẫn Windows mặc định; kiểm chứng hình thức không phụ thuộc trình xem HTML.

Thay thời lượng/khung giờ trong config.json rồi dựng và kiểm chứng lại. Bản xuất giới hạn tối đa 1.000.000 trạng thái của quỹ đạo chính xác để tránh tệp quá lớn; có thể đặt python chapter1/build.py --state-limit N. Cấu hình mới có thể cho chu kỳ nhiều ngày, không mặc định luôn có 86.400 trạng thái.

## Giới hạn và phần chưa xác nhận

- Tất cả yêu cầu hình thức đã liệt kê có kết quả thực thi; không còn thuộc tính yêu cầu nào bị bỏ qua trong cấu hình hiện tại.
- Bản cho GUI là xấp xỉ thời gian trong ngày; không dùng nó để khẳng định đúng mốc HH:MM:SS. Bản exact/NuSMV giữ mốc này. Hai bản đều giữ timer từng giây.
- Bộ CTL gốc hạn chế cú pháp; công thức CTL lồng dùng NuSMV. Không nâng cấp hoặc thay thế parser của ứng dụng.
- Đã xác minh bằng parser/checker gốc ở chế độ headless; chưa thao tác trực tiếp nút nạp JSON trong cửa sổ SecLabFramework. GUI có thể bố trí 1.012 nút chậm; dùng trình xem cục bộ hoặc SVG/DOT khi cần đọc rõ. Bản 86.400 nút không nên bố trí toàn bộ bằng GUI.
- BDD dùng -dynamic -df -coi để tránh tốn tài nguyên vào thứ tự biến không phù hợp. Phép đếm reachable chạy riêng với mô hình đầy đủ; không nhầm thống kê của cone reduction với 86.400 trạng thái thật.
- Bảo đảm hiện tại là mô hình logic trong vận hành bình thường, chưa bao gồm trễ scheduler, thiết bị hỏng, giao thông rẽ hoặc người đi bộ. Không kết luận đây là chứng nhận an toàn phần cứng thực tế.
- Không tạo Excel mới, không chạy phân tích C, SMT/BMC, fuzzing hay phân loại bảo mật. Các artifact Excel cũ được giữ nguyên theo yêu cầu bảo toàn.
