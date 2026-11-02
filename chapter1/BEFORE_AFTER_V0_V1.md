# Đối chiếu Before (v0) / After (v1) — Chương 1

**Đề tài:** Mô hình hóa và kiểm chứng hệ thống đèn giao thông thông minh bằng cấu trúc Kripke.  
**Mục đích:** Tài liệu đối chiếu để đưa vào báo cáo học phần. Ngày lập: 22/10/2026.

**Before (v0)** gồm 14 file mô hình gốc, được giữ nguyên từng byte. **After (v1) chính thức** là [chapter1/smart_intersection.smv](smart_intersection.smv). Các bản sao `negative_*.smv` chỉ là mẫu cố ý lỗi để kiểm thử, không phải bản After chính thức.

## 1. Phạm vi và nguyên tắc đối chiếu

- Đã đối chiếu SHA-256 từng nguồn v0 với [preserved_work.json](evidence/preserved_work.json) và hash trong bản ghi chạy lịch sử [output/nusmv_results.json](../output/nusmv_results.json). Hash v1 được đối chiếu với manifest và bản mô hình đã dùng trong lượt chạy E1. Kết quả và hash đầy đủ ở [before_after_audit.json](evidence/before_after_audit.json).
- Không sửa, đổi tên hoặc chạy lại bất kỳ file `.smv` nào để viết tài liệu này. Không tạo ra kết quả kiểm chứng mới. Các stdout v0 bên dưới được trích nguyên văn từ JSON lịch sử, không phải log của một lần chạy mới.
- “Tái sử dụng” ở đây là kế thừa ý tưởng/quy tắc nghiệp vụ được chỉ rõ; không ngụ ý 14 file được import hoặc ghép nguyên vẹn thành v1. Chưa có chứng minh bisimulation/refinement tổng quát giữa mọi v0 và v1.
- TRUE chỉ xác nhận công thức đã chạy trên mô hình tương ứng. Nhận xét từ đọc code được ghi rõ; không biến suy luận nguồn thành một FAIL hoặc counterexample chưa được công cụ phát ra.
- Yêu cầu v1 có thay đổi: bốn cột, 12 đèn ON/OFF, timer từng giây và clearance all-red. Không giữ nguyên mọi công thức cũ, đặc biệt công thức cấm cả hai hướng cùng RED.
- **Chức năng ưu tiên xe khẩn cấp trong ví dụ v0 chưa được tích hợp vào v1.** V1 hiện kiểm chứng vận hành bình thường với lịch thích nghi theo giờ.

### Phân loại lỗi và giới hạn

| Loại | Cách hiểu |
|---|---|
| Lỗi logic/ngữ nghĩa hiện hữu | Nhánh thời gian bị che, nạp timer theo pha nguồn thay vì pha đích trong adaptive; khác biệt timer=0 so với yêu cầu đúng D giây. Nguồn không gắn nhãn cấy lỗi cho các đoạn này; không suy đoán động cơ tác giả. |
| Giới hạn mô hình/thuộc tính | Thiếu timer, đèn vật lý hoặc all-red; safety enum quá yếu; yêu cầu cấm mọi trạng thái cùng RED không phù hợp v1. Không tự động đồng nghĩa có FAIL đã được chạy. |
| Mẫu lỗi v0 để thực hành | `init_bug` và hai `transition_bug`; các file chuyển tiếp ghi rõ cạnh sai trong chú thích. `init_bug` có vai trò mẫu lỗi khởi tạo theo tên và cấu hình GREEN/GREEN. |
| Bản sửa đối chứng v0 | `transition_bug_fixed.smv` đã có thuộc tính TRUE; không xếp nó là file còn lỗi chỉ vì chú thích cũ chưa đổi. |
| Fault trên bản sao v1 | Ba `negative_*.smv`, dùng kiểm độ nhạy thuộc tính. Thuộc tính của bản lỗi phải FALSE; harness PASS nghĩa là phát hiện đúng lỗi mong đợi. |
| Chưa có thuộc tính/ngoài nghiệp vụ | File chỉ `MODULE main`, hai fixture chưa có SPEC và ví dụ đăng nhập. Không công bố PASS nghiệp vụ khi không có thuộc tính. |

## 2. Danh mục bằng chứng có sẵn

| Mã | Nguồn | Phạm vi sử dụng |
|---|---|---|
| E0 | [output/nusmv_results.json](../output/nusmv_results.json) | 14 bản ghi chạy trực tiếp v0, có stdout/stderr, hash nguồn, exit code và từng kết quả. Bản trích stdout ở `evidence/before_v0_logs/`. |
| E0G | [excel_graph_check.log](../output/excel_graph_check.log), [mô hình dẫn xuất](../output/excel_graph_check.smv), [validation.json](../output/validation.json) | Artifact lịch sử của tác vụ đã hủy. Chỉ đọc lại bằng chứng Kripke/CTL đã có, không tái tạo Excel. Kết quả trên đồ thị tổng hợp không phải kết quả chạy trực tiếp công thức trong file v0. |
| E1 | [nusmv_main.log](evidence/nusmv_main.log), [nusmv_results.json](evidence/nusmv_results.json), [properties.json](properties.json) | 335/335 CTL TRUE trên v1 chính thức, clock khởi tạo cố định. |
| E1A | [nusmv_any_start_time.log](evidence/nusmv_any_start_time.log) | 335/335 CTL TRUE khi clock khởi tạo bất kỳ; pha khởi tạo vẫn theo cấu hình. |
| E1R | [nusmv_period_reachability.log](evidence/nusmv_period_reachability.log) | Bốn EF(period=...) TRUE trực tiếp trên NuSMV có đồng hồ. |
| E1N | [nusmv_reachable.json](evidence/nusmv_reachable.json), [log BDD](evidence/nusmv_reachable.log) | 86.400 trạng thái đạt được của mô hình đầy đủ; không dùng số trạng thái của cone reduction thay số này. |
| E1G | [graph_results.json](evidence/graph_results.json), [build_summary.json](evidence/build_summary.json) | Mọi trạng thái/cạnh và 12 đèn của JSON; 42 ca ranh giới, 24 ca thời lượng; phép chiếu exact→GUI. |
| E1S | [seclab_results.json](evidence/seclab_results.json) | Parser/CTL Chương 1 gốc: 26/26 CTL PASS trên JSON GUI, mutex PASS, 0 deadlock; parser cũng nạp JSON exact. Kiểm headless, không phải thao tác nút GUI. |
| N1 | [negative_conflicting_green.log](evidence/negative_conflicting_green.log) | Fault bật e_green cùng NS_GREEN; thuộc tính FALSE có counterexample. |
| N2 | [negative_timer_reset.log](evidence/negative_timer_reset.log) | Fault reset timer thành 1; thuộc tính FALSE có counterexample. |
| N3 | [negative_skip_all_red.log](evidence/negative_skip_all_red.log) | Fault NS_YELLOW→EW_GREEN bỏ all-red; thuộc tính FALSE có counterexample. |

E0 không lưu timestamp hoặc full command line, nên tài liệu không bổ sung hồi tố các thông tin đó. Cách gọi còn trong `scripts/generate_spec.py` là `NuSMV <file>`, không có `-bmc`. Tên thư mục `03_bmc` không đủ để gọi các log này là kết quả SAT/BMC. Lượt v1 ghi rõ command `NuSMV -dynamic -df -coi`; phép đếm reachable chạy riêng. Script Excel lịch sử không được chạy lại.

## 3. Tổng hợp đủ 14 file Before

Đường dẫn dưới đây tính từ `Smart-Traffic-Light-Verification/`, trừ file `test.smv` ở gốc workspace. TRUE/FALSE là kết quả **công thức gốc đã chạy**, không phải đánh giá toàn bộ chất lượng file.

| Mã | File | TRUE / FALSE | Vai trò |
|---|---|---:|---|
| V0-01 | `01_basic_model/traffic_light_model.smv` | 1 / 0 | Mô hình cơ bản |
| V0-02 | `02_time_based_model/timed_light.smv` | 2 / 0 | Mô hình timer |
| V0-03 | `03_adaptive_model/adaptive_light.smv` | 10 / 0 | Mô hình thích nghi còn lỗi logic |
| V0-04 | `03_bmc/init_bug.smv` | 0 / 1 | Mẫu lỗi khởi tạo |
| V0-05 | `03_bmc/traffic_light_bmc.smv` | 1 / 0 | Mẫu safety enum |
| V0-06 | `03_bmc/traffic_light_bmc_bug.smv` | 0 / 0 | File khung, không có thuộc tính |
| V0-07 | `03_bmc/transition_bug.smv` | 1 / 1 | Mẫu lỗi chuyển tiếp, có biến đèn |
| V0-08 | `04_verification/safety_liveness.smv` | 4 / 0 | Mô hình hai luồng và tập yêu cầu cũ |
| V0-09 | `05_bug_analysis/transition_bug.smv` | 0 / 1 | Mẫu lỗi chuyển tiếp chỉ có enum |
| V0-10 | `05_bug_analysis/transition_bug_fixed.smv` | 1 / 0 | Bản sửa đối chứng đã đúng |
| V0-11 | `06_extension/emergency_mode.smv` | 4 / 0 | Mở rộng emergency, khác phạm vi v1 |
| V0-12 | `test/traffic_light2.smv` | 0 / 0 | Fixture chưa có SPEC |
| V0-13 | `test/traffic_light_basic.smv` | 0 / 0 | Fixture chưa có SPEC |
| V0-14 | `test.smv` ở gốc workspace | 1 / 0 | Ví dụ đăng nhập |

E0 có tổng **28 công thức: 25 TRUE, 3 FALSE**; ba file không có SPEC/LTLSPEC. Ba FALSE nằm trong ba file mẫu lỗi, gồm hai loại lỗi khởi tạo/chuyển tiếp; không phải ba lỗi của bản v1.

## 4. Ánh xạ chi tiết từng file

### V0-01 — 01_basic_model/traffic_light_model.smv

[Nguồn v0](../Smart-Traffic-Light-Verification/01_basic_model/traffic_light_model.smv) · [stdout gốc trích nguyên văn](evidence/before_v0_logs/V0-01_traffic_light_model.stdout.log)

1. **Tái sử dụng:** Chu kỳ tương đối NS_GREEN→NS_YELLOW→EW_GREEN→EW_YELLOW→NS_GREEN và mục tiêu cuối cùng phục vụ EW sau NS.
2. **Giới hạn:** Chỉ một enum và bốn pha; không timer, đồng hồ, 12 đèn riêng hoặc all-red. `G(state=NS_GREEN -> F state=EW_GREEN)` không chứng minh đồng bộ bốn cột hay thời gian dọn giao lộ. Đây là hạn chế trừu tượng, không phải fault được cấy.
3. **V1 cải tiến:** Giữ thứ tự xanh/vàng, chèn hai pha all-red; thêm timer giây, clock và đầu ra từng cột. Kiểm phục vụ GREEN lặp lại ở cả bốn hướng.
4. **Thuộc tính v1:** `advance_NS_GREEN`, `advance_NS_YELLOW`, `clearance_all_red`, `recurring_green_n`, `recurring_green_e`.
5. **Bằng chứng:** E0/V0-01 có 1 TRUE, không có counterexample. E1/E1A chứng minh các thuộc tính trên; N3 xác nhận phép kiểm bắt được bỏ all-red. N3 là fault trên bản sao v1, không phải counterexample của file gốc này.

### V0-02 — 02_time_based_model/timed_light.smv

[Nguồn v0](../Smart-Traffic-Light-Verification/02_time_based_model/timed_light.smv) · [stdout gốc](evidence/before_v0_logs/V0-02_timed_light.stdout.log)

1. **Tái sử dụng:** Cơ chế đếm giảm, giữ pha khi chưa hết giờ và reset timer khi chuyển pha.
2. **Giới hạn/lỗi ngữ nghĩa:** Miền timer là 0..60; chỉ đổi pha sau khi trạng thái hiện tại đã có timer=0. **Nếu một bước là một giây**, GREEN=30 đi qua 30..0 rồi mới đổi, tương ứng 31 khoảng giây; YELLOW=5 tương ứng 6. Đây là phân tích ASSIGN theo quy ước giây mới, không phải FAIL được báo trong log. Hai cận `timer<=30` và `timer<=5` đều TRUE nhưng không chứng minh đúng thời lượng. Thiếu all-red và lịch 24 giờ.
3. **V1 cải tiến:** Miền timer>=1; chuyển tại timer=1, nạp theo pha đích/period mới. Pha cấu hình D giây giữ đúng D khoảng giây. V1 đổi cả tham số mặc định thành GREEN 15/25/35/45, YELLOW=3, ALL_RED=2; không dùng khác biệt tham số để kết luận hiệu năng tốt hơn.
4. **Thuộc tính v1:** `timer_bounds`, `countdown_2`, `countdown_30`, `hold_NS_GREEN`, `advance_NS_GREEN`, `reset_NS_GREEN_NORMAL`.
5. **Bằng chứng:** E0/V0-02 có 2 TRUE, không có counterexample thời lượng. E0G ghi 74 trạng thái đạt được. E1/E1A kiểm countdown/hold/reset; E1G có 24 phép đo thời lượng (6 pha×4 period). N2 bắt lỗi reset cố ý khác, không phải phản ví dụ cho lỗi timer=0 của v0.

### V0-03 — 03_adaptive_model/adaptive_light.smv

[Nguồn v0](../Smart-Traffic-Light-Verification/03_adaptive_model/adaptive_light.smv) · [stdout gốc](evidence/before_v0_logs/V0-03_adaptive_light.stdout.log)

1. **Tái sử dụng:** Ý tưởng điều chỉnh thời lượng theo cao điểm/bình thường/thấp điểm và các mục tiêu safety, liveness, adaptive.
2. **Lỗi logic hiện hữu:** Hai nhánh `time_period=NORMAL_TIME` ở dòng 117 và 133; `case` chọn nhánh đầu nên EVENING_PEAK bị che, NIGHT_LOW và traffic_mode=LOW cũng không đạt được từ init. `next(traffic_mode)` dùng period hiện tại nên lệch một bước. Khi GREEN hết giờ, state đã sang YELLOW nhưng timer được nạp 45/30/20; khi YELLOW kết thúc lại nạp 5 cho GREEN. Các công thức kiểm chính cách nạp này vẫn có thể TRUE; kéo theo NIGHT_LOW/LOW đúng rỗng do tiền đề không đạt được. Nguồn không đánh dấu các đoạn này là fault-injection.
3. **V1 cải tiến:** Period suy trực tiếp từ clock 24 giờ; reset dùng pha đích và period ở thời điểm mới. `entry_period` chốt đến hết pha, tránh cắt ngắn pha giữa ranh giới giờ. Bốn period đều đạt được; sáng ưu tiên NS, chiều ưu tiên EW.
4. **Thuộc tính v1:** `reset_NS_GREEN_NORMAL`, `reset_ALL_RED_NS_TO_EW_EVENING_PEAK`, `reset_ALL_RED_EW_TO_NS_NIGHT_LOW`, `latch_NORMAL`, `clock_second_59`, `clock_hour_tick_23`; bốn `EF(period=...)` trong E1R.
5. **Bằng chứng:** E0/V0-03 có đủ 10 TRUE, không có FAIL cho yêu cầu mới. E0G ghi `AG(adaptive -> EF(adaptive_time_period_NIGHT_LOW))` FALSE và `AG(adaptive -> EF(adaptive_traffic_mode_LOW))` FALSE, trên **đồ thị dẫn xuất**, cùng thống kê 129 trạng thái đạt được. E1/E1A kiểm reset/latch; E1R chứng minh bốn period trực tiếp trên NuSMV; E1G có 42 ca ranh giới và cấu hình thay thế. Chưa có counterexample gốc trực tiếp cho lỗi nạp nhầm thời lượng; kết luận đó dựa trên code.

### V0-04 — 03_bmc/init_bug.smv

[Nguồn v0](../Smart-Traffic-Light-Verification/03_bmc/init_bug.smv) · [stdout và counterexample gốc](evidence/before_v0_logs/V0-04_init_bug.stdout.log)

1. **Tái sử dụng:** Mục tiêu loại trừ hai luồng GREEN và phương pháp dùng mẫu lỗi để kiểm độ nhạy checker. Không kế thừa init GREEN/GREEN.
2. **Fault mẫu:** `init(NS_light)=GREEN`, `init(EW_light)=GREEN` vi phạm ngay trạng thái đầu; hai đèn còn chạy đồng bộ cùng chu kỳ. Phân loại là mẫu minh họa lỗi khởi tạo theo tên `init_bug` và vai trò bộ ví dụ, không gán thành lỗi vô ý của v1.
3. **V1 cải tiến:** Bắt đầu ALL_RED_EW_TO_NS, timer=2, bốn cột cùng đỏ trước khi cấp GREEN. Kiểm xung đột trên boolean của từng cột.
4. **Thuộc tính v1:** `physical_green_exclusion`, `one_hot_n`, `synchronized_green`, `clearance_all_red`.
5. **Bằng chứng:** E0/V0-04 có safety FALSE; State 1.1 đã có GREEN/GREEN. E1/E1A của v1 TRUE. N1 có FALSE tại t=2s do cấy e_green trên bản sao v1; đó là counterexample khác, không hoán đổi nguồn với lỗi init v0.

### V0-05 — 03_bmc/traffic_light_bmc.smv

[Nguồn v0](../Smart-Traffic-Light-Verification/03_bmc/traffic_light_bmc.smv) · [stdout gốc](evidence/before_v0_logs/V0-05_traffic_light_bmc.stdout.log)

1. **Tái sử dụng:** Chu kỳ bốn pha và mục tiêu mutual exclusion; không kế thừa safety enum như bằng chứng duy nhất cho đầu ra vật lý.
2. **Giới hạn:** `G !(state=NS_GREEN & state=EW_GREEN)` hiển nhiên đúng vì một enum không nhận hai giá trị. Chưa có timer, all-red hoặc bốn cột riêng. Đây là thuộc tính quá yếu, không phải lỗi được cấy đã bị phát hiện. Tên `bmc` không chứng minh đã chạy BMC.
3. **V1 cải tiến:** 12 boolean; safety giữa ns_go/ew_go, one-hot từng cột, đồng bộ và clearance. Công cụ hiện dùng BDD/CTL Chương 1.
4. **Thuộc tính v1:** `physical_green_exclusion`, `one_hot_n`, `synchronized_green`, `clearance_all_red`, `deadlock_free`.
5. **Bằng chứng:** E0/V0-05 có 1 TRUE, không có counterexample; lần chạy mặc định không có cờ `-bmc`. E1 kiểm safety vật lý; N1 cho thấy thuộc tính mới có thể FALSE khi lỗi tác động một boolean đèn thật. Không công bố kết quả BMC mới.

### V0-06 — 03_bmc/traffic_light_bmc_bug.smv

[Nguồn v0](../Smart-Traffic-Light-Verification/03_bmc/traffic_light_bmc_bug.smv) · [stdout gốc](evidence/before_v0_logs/V0-06_traffic_light_bmc_bug.stdout.log)

1. **Tái sử dụng:** Không có hành vi giao thông để tái sử dụng; chỉ có `MODULE main`.
2. **Chưa hoàn thiện:** Không có VAR/init/next/SPEC. Tên `bug` không chứng minh đã cấy hoặc phát hiện lỗi. Exit code 0 không phải PASS safety/liveness.
3. **V1 cải tiến:** Cung cấp mô hình đầy đủ, chuyển tiếp, đầu ra và thuộc tính thực thi được. File khung v0 vẫn nguyên trạng, không được điền lại.
4. **Thuộc tính v1:** `physical_green_exclusion`, `recurring_green_n`, `deadlock_free`, `advance_NS_YELLOW`.
5. **Bằng chứng:** E0/V0-06 chỉ có banner, `properties=[]`; phải ghi CHƯA CÓ THUỘC TÍNH, không phải TRUE hay FALSE. E1/E1A có 335 công thức mỗi lượt. Không có counterexample gốc cho file khung.

### V0-07 — 03_bmc/transition_bug.smv

[Nguồn v0](../Smart-Traffic-Light-Verification/03_bmc/transition_bug.smv) · [stdout và counterexample gốc](evidence/before_v0_logs/V0-07_transition_bug.stdout.log)

1. **Tái sử dụng:** Đồng bộ đèn theo trạng thái đích qua `next(state)` và yêu cầu kiểm đúng thứ tự pha bên cạnh không trùng GREEN.
2. **Fault có chủ đích:** Chú thích nguồn nêu S0→S2 thay vì S0→S1. LTL thứ tự FALSE trong khi LTL không cùng GREEN TRUE; chỉ safety GREEN không bắt được bỏ YELLOW. Thiếu timer/all-red.
3. **V1 cải tiến:** Giữ pha khi timer>1; hết giờ NS_GREEN phải sang NS_YELLOW, rồi ALL_RED_NS_TO_EW trước EW_GREEN. Đèn cập nhật theo phase_next cùng bước.
4. **Thuộc tính v1:** `hold_NS_GREEN`, `advance_NS_GREEN`, `advance_NS_YELLOW`, `yellow_ns_other_red`, `physical_green_exclusion`.
5. **Bằng chứng:** E0/V0-07 có 1 TRUE, 1 FALSE và trace S0→S2→S3→S0, có giá trị NS/EW. E1/E1A kiểm các quy tắc có timer. N3 bỏ all-red trên bản sao v1, không phải cùng fault bỏ S1. Không thay nguyên xi LTL `X(S1)` bằng `AX(YELLOW)` ở mọi giây của pha GREEN dài nhiều giây.

### V0-08 — 04_verification/safety_liveness.smv

[Nguồn v0](../Smart-Traffic-Light-Verification/04_verification/safety_liveness.smv) · [stdout gốc](evidence/before_v0_logs/V0-08_safety_liveness.stdout.log)

1. **Tái sử dụng:** Quan sát riêng đèn NS/EW, không cùng GREEN và liveness đỏ cuối cùng được xanh.
2. **Giới hạn thiết kế/yêu cầu:** Hai máy đèn có thể đi từ (NS GREEN,EW RED) sang (NS YELLOW,EW GREEN). Đây là vết **suy ra từ ASSIGN**, không phải counterexample đã có trong log. Bốn thuộc tính gốc đều TRUE nhưng chưa kiểm hướng kia phải đỏ khi một hướng vàng. Thuộc tính cấm đồng thời RED không phù hợp với clearance all-red mới. Nguồn không đánh dấu là fault-injection.
3. **V1 cải tiến:** EW đỏ khi NS vàng và ngược lại; thêm all-red, kiểm liveness bốn cột. Không duy trì công thức cấm mọi ALL_RED: đây là thay đổi yêu cầu có chủ đích, không phải regression cần sửa để ép công thức cũ TRUE.
4. **Thuộc tính v1:** `yellow_ns_other_red`, `yellow_ew_other_red`, `clearance_all_red`, `advance_NS_YELLOW`, `recurring_green_n`, `recurring_green_e`.
5. **Bằng chứng:** E0/V0-08 có 4 TRUE; không có counterexample yellow-safe vì chưa khai báo yêu cầu đó. E1/E1A chứng minh vàng/all-red/liveness; N3 bắt bỏ clearance. Không ghi rằng cả bốn LTL cũ vẫn được bảo toàn trong v1.

### V0-09 — 05_bug_analysis/transition_bug.smv

[Nguồn v0](../Smart-Traffic-Light-Verification/05_bug_analysis/transition_bug.smv) · [stdout và counterexample gốc](evidence/before_v0_logs/V0-09_transition_bug.stdout.log)

1. **Tái sử dụng:** Phương pháp dùng thuộc tính chuyển tiếp để phân biệt mẫu lỗi và mẫu đã sửa; không kế thừa cạnh S0→S2.
2. **Fault có chủ đích:** Nguồn có `BUG INTRODUCED HERE` và cạnh S0→S2; bỏ S1. Chỉ enum S0..S3, không đèn vật lý, timer hoặc all-red.
3. **V1 cải tiến:** Đặt tên pha nghiệp vụ; `hold_*` và `advance_*` có điều kiện timer bắt chuyển sớm/thiếu pha; thêm clearance và bốn cột.
4. **Thuộc tính v1:** `hold_NS_GREEN`, `advance_NS_GREEN`, `advance_NS_YELLOW`, `clearance_all_red`.
5. **Bằng chứng:** E0/V0-09 có 1 FALSE và trace S0→S2→S3→S0. V0-10 là bản sửa đối chứng có TRUE; E1/E1A là bằng chứng v1 riêng. Không gộp trace của file này với file cùng tên trong `03_bmc`, vốn có thêm biến đèn.

### V0-10 — 05_bug_analysis/transition_bug_fixed.smv

[Nguồn v0](../Smart-Traffic-Light-Verification/05_bug_analysis/transition_bug_fixed.smv) · [stdout gốc](evidence/before_v0_logs/V0-10_transition_bug_fixed.stdout.log)

1. **Tái sử dụng:** Chu kỳ S0→S1→S2→S3→S0 đã đúng và cách đối chiếu cùng công thức với V0-09.
2. **Giới hạn, không phải lỗi cạnh còn tồn tại:** `G(S0 -> X S1)` đã TRUE. Chỉ có bốn trạng thái trừu tượng, chưa có timer, đèn ON/OFF hoặc all-red. Chú thích `BUG INTRODUCED HERE` vẫn còn, nhưng lệnh thực tế S0→S1 là đúng; phải phân loại theo code và log.
3. **V1 cải tiến:** Mở rộng hành vi đúng thành sáu pha có thời gian. Giữ GREEN khi chưa hết giờ, hết giờ mới sang YELLOW, sau đó có clearance.
4. **Thuộc tính v1:** `hold_NS_GREEN`, `advance_NS_GREEN`, `advance_NS_YELLOW`, `physical_green_exclusion`.
5. **Bằng chứng:** E0/V0-10 có 1 TRUE, không có counterexample. Cặp V0-09/V0-10 chỉ chứng minh sửa cạnh S0→S1 trong v0; E1/E1A chứng minh phần mở rộng v1. Không nói v1 vừa sửa một cạnh còn lỗi trong file `fixed`.

### V0-11 — 06_extension/emergency_mode.smv

[Nguồn v0](../Smart-Traffic-Light-Verification/06_extension/emergency_mode.smv) · [stdout gốc](evidence/before_v0_logs/V0-11_emergency_mode.stdout.log)

1. **Tái sử dụng:** Chỉ tham khảo ý tưởng chế độ vận hành và câu hỏi liveness/phục hồi. **Không tái sử dụng chức năng emergency**; không chuyển EMERGENCY_GREEN thành pha v1.
2. **Giới hạn mô phỏng:** emergency bị lập trình luân phiên FALSE/TRUE mỗi bước, không phải cảm biến môi trường tùy ý hoặc giữ TRUE lâu. Theo ASSIGN, vết từ init là (NS_GREEN,FALSE)→(NS_YELLOW,TRUE)→(EMERGENCY_GREEN,FALSE)→(NS_GREEN,TRUE)→(EMERGENCY_GREEN,FALSE)...; EW_GREEN/EW_YELLOW không đạt được trên đường chạy này. Đây là **suy luận nguồn**, không phải một `EF(EW_GREEN)=FALSE` đã được chạy. Hai công thức cấm đồng thời hai giá trị state là bất biến enum, chưa đủ cho safety vật lý.
3. **V1 xử lý phạm vi:** Chứng minh phục vụ NS/EW lặp lại trong vận hành bình thường theo giờ. V1 không có emergency/preemption hoặc bảo đảm xe ưu tiên; phần này **CHƯA TÍCH HỢP**, không được công bố đã sửa/kiểm chứng tương đương chức năng v0.
4. **Thuộc tính liên quan ở v1:** `recurring_green_n`, `recurring_green_e`, `physical_green_exclusion`; chỉ áp dụng vận hành bình thường.
5. **Bằng chứng:** E0/V0-11 có 4 TRUE dưới cảm biến luân phiên; E0G ghi 4 trạng thái đạt được. E1 có `AG(AF(n_green))`, `AG(AF(e_green))` TRUE nhưng không chứng minh ưu tiên khẩn cấp. Không có counterexample gốc được lưu cho cảm biến giữ TRUE hoặc reachability EW.

### V0-12 — test/traffic_light2.smv

[Nguồn v0](../Smart-Traffic-Light-Verification/test/traffic_light2.smv) · [stdout gốc](evidence/before_v0_logs/V0-12_traffic_light2.stdout.log)

1. **Tái sử dụng:** Chu kỳ enum bốn pha và cách viết ASSIGN gọn. Không coi tên `test` là đã có bộ kiểm thử đầy đủ.
2. **Giới hạn:** Không SPEC/LTLSPEC; chưa có timer, clock, 12 đèn hoặc all-red. Exit code 0 không đồng nghĩa đã kiểm yêu cầu nào.
3. **V1 cải tiến:** Chuyển tiếp có timer, đầu ra vật lý và 335 CTL đặt tên. Fixture gốc được giữ nguyên.
4. **Thuộc tính v1:** `advance_NS_GREEN`, `advance_NS_YELLOW`, `physical_green_exclusion`, `deadlock_free`.
5. **Bằng chứng:** E0/V0-12 có `properties=[]`; E0G ghi 4 trạng thái đạt được. E1/E1A kiểm v1; không có counterexample hoặc PASS thuộc tính gốc để so sánh trực tiếp.

### V0-13 — test/traffic_light_basic.smv

[Nguồn v0](../Smart-Traffic-Light-Verification/test/traffic_light_basic.smv) · [stdout gốc](evidence/before_v0_logs/V0-13_traffic_light_basic.stdout.log)

1. **Tái sử dụng:** Bốn pha và cách giữ state qua nhánh mặc định khi thích hợp; ở v1, giữ pha thực sự phụ thuộc timer>1.
2. **Giới hạn:** Không SPEC/LTLSPEC, thiếu timer/đầu ra. Nhánh `TRUE:state` không tự nó là lỗi: bốn nhánh enum trước đã bao phủ mọi giá trị hợp lệ.
3. **V1 cải tiến:** Kiểm giữ/đổi pha, timer và safety bốn cột. Không sửa hay thêm SPEC vào fixture v0.
4. **Thuộc tính v1:** `hold_NS_GREEN`, `advance_NS_GREEN`, `advance_NS_YELLOW`, `physical_green_exclusion`.
5. **Bằng chứng:** E0/V0-13 có `properties=[]`; E0G ghi 4 trạng thái đạt được, không có counterexample gốc. Không gán hồi tố kết quả v1 cho fixture chưa có SPEC.

### V0-14 — test.smv ở gốc workspace

[Nguồn v0](../test.smv) · [stdout gốc](evidence/before_v0_logs/V0-14_test.stdout.log)

1. **Tái sử dụng:** Không tái sử dụng hành vi logged_in/logged_out trong v1. Chỉ dùng phân biệt bất biến enum với safety giữa nhiều đầu ra độc lập khi giải thích phương pháp.
2. **Giới hạn/phạm vi:** `AG !(state=logged_in & state=logged_out)` đúng do enum; không chứng minh an toàn giao lộ hoặc một hệ thống xác thực thực tế. Không coi đây là mô hình traffic bị lỗi.
3. **V1 cải tiến về phương pháp:** Kiểm xung đột trên n/s/e/w và one-hot/đồng bộ. Không có chuyển đổi chức năng đăng nhập sang traffic và không tuyên bố sửa lỗi xác thực.
4. **Thuộc tính liên quan ở v1:** `physical_green_exclusion`, `one_hot_n`, `synchronized_green`.
5. **Bằng chứng:** E0/V0-14 có 1 TRUE, không có counterexample; E0G ghi 2 trạng thái đạt được. E1/N1 chứng minh safety mới gắn với đèn thật và nhạy với fault vật lý; đây là so sánh phương pháp, không phải hai chương trình cùng chức năng.

## 5. Công thức v1 dùng trong bảng ánh xạ

Các công thức dưới đây được lấy từ [properties.json](properties.json) và đã đối chiếu với từng kết quả TRUE trong cả E1 và E1A; không chỉ dựa vào exit code. Nhóm `one_hot_*`, `synchronized_*`, `recurring_green_*`, `hold_*`, `advance_*`, `reset_*`, `latch_*`, `clock_*`, `countdown_*` có các công thức tương ứng cho những cột/pha/giá trị còn lại.

<!-- BEGIN VERIFIED_PROPERTY_CATALOG -->
| Tên thuộc tính | CTL đã đối chiếu TRUE trong E1 và E1A |
|---|---|
| `physical_green_exclusion` | `AG(!conflicting_green)` |
| `one_hot_n` | `AG((n_red \| n_yellow \| n_green) & !(n_red & n_yellow) & !(n_red & n_green) & !(n_yellow & n_green))` |
| `recurring_green_n` | `AG(AF(n_green))` |
| `recurring_green_e` | `AG(AF(e_green))` |
| `synchronized_green` | `AG((n_green = s_green) & (e_green = w_green))` |
| `yellow_ns_other_red` | `AG((n_yellow \| s_yellow) -> (e_red & w_red))` |
| `yellow_ew_other_red` | `AG((e_yellow \| w_yellow) -> (n_red & s_red))` |
| `clearance_all_red` | `AG((phase = ALL_RED_NS_TO_EW \| phase = ALL_RED_EW_TO_NS) -> all_red)` |
| `deadlock_free` | `AG(EX(TRUE))` |
| `timer_bounds` | `AG(timer >= 1 & timer <= phase_duration)` |
| `clock_second_59` | `AG(second = 59 -> AX(second = 0))` |
| `clock_hour_tick_23` | `AG((second = 59 & minute = 59 & hour = 23) -> AX(hour = 0))` |
| `countdown_2` | `AG(timer = 2 -> AX(timer = 1))` |
| `countdown_30` | `AG(timer = 30 -> AX(timer = 29))` |
| `hold_NS_GREEN` | `AG((phase = NS_GREEN & timer > 1) -> AX(phase = NS_GREEN))` |
| `advance_NS_GREEN` | `AG((phase = NS_GREEN & timer = 1) -> AX(phase = NS_YELLOW))` |
| `reset_NS_GREEN_NORMAL` | `AG((phase = NS_GREEN & timer = 1 & period_next = NORMAL) -> AX(phase = NS_YELLOW & timer = 3 & entry_period = NORMAL))` |
| `advance_NS_YELLOW` | `AG((phase = NS_YELLOW & timer = 1) -> AX(phase = ALL_RED_NS_TO_EW))` |
| `reset_ALL_RED_NS_TO_EW_EVENING_PEAK` | `AG((phase = ALL_RED_NS_TO_EW & timer = 1 & period_next = EVENING_PEAK) -> AX(phase = EW_GREEN & timer = 45 & entry_period = EVENING_PEAK))` |
| `reset_ALL_RED_EW_TO_NS_NIGHT_LOW` | `AG((phase = ALL_RED_EW_TO_NS & timer = 1 & period_next = NIGHT_LOW) -> AX(phase = NS_GREEN & timer = 15 & entry_period = NIGHT_LOW))` |
| `latch_NORMAL` | `AG((entry_period = NORMAL & timer > 1) -> AX(entry_period = NORMAL))` |
<!-- END VERIFIED_PROPERTY_CATALOG -->

Bốn công thức khả đạt đã chạy riêng trong E1R, tất cả TRUE:

```text
EF(period = MORNING_PEAK)
EF(period = NORMAL)
EF(period = EVENING_PEAK)
EF(period = NIGHT_LOW)
```

Đây là kiểm tra khả đạt để tránh kết luận chỉ dựa trên kéo theo có tiền đề không đạt được. `AG(AF(...))` của NuSMV kiểm liveness lặp lại; không mặc định mọi LTL G/F/X có thể đổi thành CTL AG/AF/AX trên mô hình phân nhánh. Các công thức mới được viết theo yêu cầu v1 và kiểm độc lập.

Với timer, `hold_*` giữ pha khi timer>1; `advance_*` đổi đúng thứ tự ở timer=1; `reset_*` kiểm thời lượng theo pha đích/period mới; `latch_*` giữ khung giờ chốt. Hai lượt 335 công thức ở clock cố định/bất kỳ là hai điều kiện kiểm của cùng tập thuộc tính, không phải 670 yêu cầu khác nhau.

## 6. Các counterexample thật và cách diễn giải

### 6.1 Phản ví dụ trực tiếp từ các mẫu lỗi v0

| File | Công thức FALSE | Phần vết thực tế đã lưu |
|---|---|---|
| V0-04 init_bug | `G !(NS_light=GREEN & EW_light=GREEN)` | State 1.1: GREEN/GREEN; tiếp theo YELLOW/YELLOW, RED/RED rồi GREEN/GREEN. Vi phạm ngay init. |
| V0-07 transition_bug trong 03_bmc | `G(state=S0 -> X(state=S1))` | State 1.1 S0, NS=GREEN/EW=RED → State 1.2 S2, NS=RED/EW=GREEN → S3 → S0. Safety không cùng GREEN vẫn TRUE. |
| V0-09 transition_bug trong 05_bug_analysis | `G(state=S0 -> X(state=S1))` | State 1.1 S0 → State 1.2 S2 → S3 → S0; nguồn này không có biến đèn NS/EW. |

Đây là tóm tắt counterexample từ stdout liên kết ở từng file, không phải vết được tạo mới để minh họa. Với timer/adaptive/yellow-safe/emergency, các suy luận nguồn ở mục 4 không được đổi nhãn thành counterexample trực tiếp của một công thức chưa chạy trên v0.

### 6.2 Fault trên bản sao v1 — không phải lỗi của After chính thức

| Fault | Bản sao và phép kiểm đã thực hiện | Giá trị quan sát trong counterexample |
|---|---|---|
| N1 | [negative_conflicting_green.smv](evidence/negative_conflicting_green.smv): `AG(!conflicting_green)` FALSE | t=2s: n_green=s_green=e_green=TRUE; conflicting_green=TRUE. w_green vẫn FALSE theo trạng thái trước. |
| N2 | [negative_timer_reset.smv](evidence/negative_timer_reset.smv): kiểm vào NS_GREEN NIGHT_LOW phải nạp 15, kết quả FALSE | t=1s timer=1; t=2s phase=NS_GREEN nhưng timer vẫn 1. Log chỉ in thay đổi, nên timer không xuất hiện lại trong State 1.3 vẫn giữ giá trị 1. |
| N3 | [negative_skip_all_red.smv](evidence/negative_skip_all_red.smv): kiểm hết NS_YELLOW phải qua all_red, kết quả FALSE | t=19s phase=NS_YELLOW, timer=1; t=20s phase=EW_GREEN, e_red=w_red=FALSE, bỏ clearance. |

Harness ghi PASS cho ba ca này vì mong đợi FALSE; **thuộc tính của từng bản lỗi vẫn FAIL/FALSE**. Mỗi negative chỉ kiểm công thức ghi trong log, không có bằng chứng đã chạy cả 335 thuộc tính trên mỗi bản lỗi. N2 không sao chép chính xác lỗi nạp timer của adaptive v0; N3 không phải lỗi bỏ YELLOW trong hai transition_bug v0.

### 6.3 Counterexample trong đồ thị dẫn xuất lịch sử

E0G có `AG(adaptive -> EF(adaptive_time_period_NIGHT_LOW))` FALSE và `AG(adaptive -> EF(adaptive_traffic_mode_LOW))` FALSE, kèm trace. Có thể dùng hỗ trợ phân tích nhánh case bị che, nhưng phải nói rõ đây là kết quả trên đồ thị dẫn xuất, dùng nhãn adaptive và các giá trị biến gốc. Không nói file adaptive tự có EF(NIGHT_LOW), hoặc 10 LTL gốc đã FAIL.

## 7. Các file .smv khác và ranh giới phiên bản

### 7.1 output/excel_graph_check.smv — artifact lịch sử, cũng giữ nguyên

File này có trước v1 trong tác vụ đã hủy, nhưng không thuộc 14 nguồn traffic/login gốc. Vẫn ánh xạ riêng để không bỏ sót một file `.smv` đã tồn tại:

1. **Kế thừa:** Kinh nghiệm dựng đồ thị hữu hạn có timer/nhãn và các đối chiếu thành phần E0G; không đưa nguyên đồ thị tổng hợp vào v1.
2. **Giới hạn/fault:** Trộn nhiều mô hình độc lập, nhiều init và cụm khóa bổ sung có conflict cố ý. FALSE của AG(!violation) thuộc cụm khóa, không phải lỗi traffic gốc. FALSE của EF(main_locked) toàn cục liên quan các thành phần không nối nhau, không đủ kết luận deadlock giao lộ.
3. **V1:** Một mô hình giao lộ nhất quán; JSON exact và xấp xỉ GUI có phép chiếu được kiểm. Không ghép login, khóa hoặc phân tích chương khác vào giao lộ.
4. **Thuộc tính liên quan:** E1/E1S kiểm safety/liveness/mutex đúng giao lộ; E1G kiểm phép chiếu, timer và mọi cạnh.
5. **Bằng chứng:** E0G có 29 CTL, 22 TRUE và 7 FALSE thuộc các thành phần/lỗi khác nhau. Không gọi bảy FALSE là bảy lỗi sản phẩm. `validation.json` ghi số trạng thái đạt được từng thành phần đối chiếu với NuSMV. Chỉ dùng lại bằng chứng có sẵn, không chạy workflow Excel.

### 7.2 Các file thuộc chiến dịch kiểm chứng v1

| File | Vai trò |
|---|---|
| [smart_intersection.smv](smart_intersection.smv) | **After (v1) chính thức duy nhất**. |
| [evidence/nusmv_main.smv](evidence/nusmv_main.smv) | Bản thực sự chạy E1, có hash giống hệt v1 chính thức. |
| [evidence/nusmv_any_start_time.smv](evidence/nusmv_any_start_time.smv) | Harness clock khởi tạo bất kỳ, không thay thế file chính thức. |
| [evidence/nusmv_period_reachability.smv](evidence/nusmv_period_reachability.smv) | Harness bốn EF(period), không thay thế file chính thức. |
| `evidence/negative_*.smv` | Ba fault có chủ đích N1–N3, không phải v0 hoặc After chính thức. |

## 8. Đoạn tổng hợp để đưa vào báo cáo học phần

> Đề tài kế thừa chu kỳ pha NS/EW, cơ chế timer, ý tưởng thích nghi theo giờ và các mục tiêu safety/liveness của những mô hình v0. Bản v1 mở rộng thành giao lộ bốn hướng với 12 đầu ra ON/OFF, hai pha all-red và đồng hồ 24 giờ. Timer chuyển tại remaining=1, nạp theo pha đích và khung giờ mới; khung giờ được chốt đến hết pha. NuSMV xác nhận 335 CTL trên cấu hình chuẩn và lặp lại với clock khởi tạo bất kỳ; bốn công thức khả đạt khung giờ cũng TRUE. BDD đếm 86.400 trạng thái đạt được. Parser/checker Chương 1 gốc của SecLabFramework nạp JSON và cho 26 CTL PASS trên bản xấp xỉ vẫn giữ timer từng giây. Mẫu lỗi v0 và fault trên bản sao v1 được giữ riêng để minh họa phát hiện lỗi, không được gán thành lỗi của v1 chính thức.

Các giới hạn phải giữ khi đưa phần so sánh vào báo cáo:

- V1 chưa có emergency/preemption, cảm biến tùy ý, người đi bộ, rẽ trái bảo vệ hoặc lỗi thiết bị. Không kết luận đã sửa/bao phủ chức năng ưu tiên xe của ví dụ v0.
- JSON GUI có 1.012 trạng thái/2.548 cạnh, chiếu clock xuống period và cho thêm hành vi đổi khung giờ. Không dùng nó chứng minh đúng mốc HH:MM:SS; [JSON exact](smart_intersection_exact.json) và NuSMV giữ đồng hồ chính xác. Parser/checker đích đã được chạy headless, chưa xác nhận thao tác nút nạp trong GUI.
- V0/v1 có các tham số thời lượng khác nhau. Cải tiến được kết luận về sự phù hợp yêu cầu và khả năng kiểm chứng, không phải đo hiệu năng ngoài thực tế hoặc tối ưu lưu lượng.
- Nhiều công thức TRUE hơn tự nó không chứng minh hệ thống an toàn hơn: cần xét tính bao phủ và tránh TRUE rỗng/thuộc tính hiển nhiên do enum.
- Đây là tài liệu hóa bằng chứng đã có, không tạo timestamp, counterexample hoặc PASS chưa ghi nhận. Audit lưu hash và nguồn trích để người đọc kiểm tra lại.

## 9. Kiểm tra tính toàn vẹn của tài liệu

[before_after_audit.json](evidence/before_after_audit.json) ghi đủ 14 ánh xạ, hash mọi `.smv`, vị trí bản ghi E0, hash stdout trích và danh sách công thức v1 đã đối chiếu kết quả TRUE. Công cụ dưới đây chỉ đọc mô hình/log, xuất audit và stdout trích, không chạy NuSMV:

```powershell
python chapter1/audit_before_after.py
python chapter1/make_docs.py
```

Nếu thực hiện chiến dịch kiểm chứng v1 mới qua `python chapter1/run.py`, cần lập lại đối chiếu/audit để số liệu và hash tiếp tục khớp. Không chạy `scripts/generate_spec.py` để làm tài liệu này. Không thay đổi v0 hoặc file v1 chính thức.
