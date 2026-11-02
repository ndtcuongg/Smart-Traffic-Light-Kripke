# Hỗ trợ báo cáo học phần — Chương 1: Kripke và kiểm chứng giao lộ

Tài liệu ánh xạ tám phần của mẫu báo cáo sang mã, biến, quan hệ Kripke, công thức, log và màn hình thực tế. Phạm vi chỉ Chương 1. Dùng kèm [đối chiếu 14 nguồn v0](../BEFORE_AFTER_V0_V1.md), không thay thế các nhận xét chi tiết trong audit đó.

Thông tin trang bìa cần người học điền: tên trường, môn học, giảng viên, nhóm, họ tên và mã số từng thành viên. Các thông tin này chưa được cung cấp; tài liệu không gán tên hoặc mã số giả.

Quy ước đường dẫn: liên kết dưới đây tính từ `chapter1/web/`. `R_NEW` là thư mục lượt mới được chỉ rõ trong [báo cáo triển khai](IMPLEMENTATION_REPORT_VI.md); khi trích dẫn phải dùng đúng mã lượt đó. Các ảnh trong `evidence/screenshots/` là ảnh Edge chụp từ ứng dụng đang chạy, không phải hình dựng thay cho thí nghiệm.

## 1. Trang bìa và thông tin nhóm

| Yêu cầu | Nguồn và cách đưa vào báo cáo |
|---|---|
| Tên đề tài | Mô hình hóa và kiểm chứng hình thức hệ thống đèn giao thông bốn hướng thích nghi theo thời gian bằng cấu trúc Kripke |
| Thành viên, MSSV, phân công | Chưa có thông tin. Nhóm tự điền thông tin thật và phần việc thực tế |
| Phạm vi | Chương 1; mô hình v1 chính thức là [smart_intersection.smv](../smart_intersection.smv) |
| Ảnh giới thiệu | [Màn hình mô phỏng](evidence/screenshots/01-mo-phong.png); chú thích là giao diện trình bày mô hình, không phải ảnh thiết bị giao thông thật |
| Biến, R, CTL, log | Không áp dụng cho danh tính nhóm; dẫn sang phần 2–6 thay vì tạo số liệu ở trang bìa |

## 2. Tổng quan đề tài

| Yêu cầu | Ánh xạ kỹ thuật |
|---|---|
| Bài toán và giới hạn | [config.json](../config.json), [intersection.py](../intersection.py), [README web](README.md). Điều khiển theo lịch giờ, chưa dùng cảm biến xe |
| Biến trạng thái | Python: `phase`, `remaining`, `period`, `entry_period`, `clock`. NuSMV: `phase`, `timer`, `period`, `entry_period`, `hour`, `minute`, `second`; `clock_sec` là biểu thức định nghĩa. 12 biến đèn vật lý `n/s/e/w` × `red/yellow/green` |
| K | Bản exact: S có 86.400 trạng thái trên quỹ đạo mặc định; S0 tại 00:00:00, ALL_RED_EW_TO_NS, timer 2; R gồm các bước một giây; L chứa giá trị đèn, pha, giờ và các nhãn quy tắc |
| Mục tiêu kiểm chứng | `AG(!conflicting_green)`, `AG(AF(n_green))`, `AG(EX(TRUE))` và các biến thể hướng khác trong [properties.json](../properties.json) |
| Bằng chứng và ảnh | [Log v1 đã lưu](../evidence/nusmv_main.log), `R_NEW/evidence/nusmv_main.log`, [mô phỏng](evidence/screenshots/01-mo-phong.png) và [Kripke](evidence/screenshots/02-kripke.png) |

## 3. Phương pháp thực hiện

| Yêu cầu | Ánh xạ kỹ thuật |
|---|---|
| Tái sử dụng | `intersection.py` và `nusmv_model.py` là nguồn ngữ nghĩa; `domain.py` là adapter web; frontend lấy trạng thái backend. [server.py](server.py), [domain.py](domain.py), [app.js](static/app.js) |
| Định nghĩa R | Nếu r > 1: tăng clock, cập nhật period, giữ phase và entry_period, giảm r. Nếu r = 1: sang pha kế, lấy D(pha đích, period ở clock mới), chốt entry_period mới |
| Chu kỳ | NS_GREEN → NS_YELLOW → ALL_RED_NS_TO_EW → EW_GREEN → EW_YELLOW → ALL_RED_EW_TO_NS → NS_GREEN |
| Quan hệ đèn | Bắc = Nam; Đông = Tây; mỗi cột đúng một màu; xanh hai cặp vuông góc loại trừ nhau |
| Hai cách biểu diễn S | [JSON chiếu](../smart_intersection.json): 1.012 nút / 2.548 cạnh, giữ timer và hai khung giờ, bỏ clock, có nhánh xấp xỉ. [JSON exact](../smart_intersection_exact.json): 86.400 nút/cạnh từ S0 mặc định. Không cộng hai số này thành tổng trạng thái của cùng một mô hình |
| L và AP | `label()` trong Python sinh AP đèn BẬT/TẮT, `phase_*`, `period_*`, `entry_*`, `timer_*`, `clock_*` khi giữ clock, và các nhãn quy tắc; `L(s)` là danh sách nhãn gán cho s |
| Thuộc tính đại diện | `one_hot_n`, `synchronized_green`, `timer_bounds`, `hold_NS_GREEN`, `advance_NS_YELLOW`, `reset_ALL_RED_NS_TO_EW_MORNING_PEAK` |
| Thực thi kiểm chứng | [verification_worker.py](verification_worker.py) gọi lại [verify_nusmv.py](../verify_nusmv.py) trong R_NEW; [ctl_checker.py](ctl_checker.py) kiểm 26 CTL JSON bằng fixpoint độc lập; [verify_graph.py](../verify_graph.py) kiểm các cạnh/đèn |
| Bằng chứng phương pháp | `R_NEW/metadata.json`, `console.log`, `reachable.json`, `graph_results.json`; [màn hình cấu hình](evidence/screenshots/04-cau-hinh.png) và [Kripke](evidence/screenshots/02-kripke.png) |

## 4. Phân tích lỗi và cách sửa

Dẫn nguyên mã định danh V0-01…V0-14 từ [audit gốc](../evidence/before_after_audit.json). Không biến giới hạn mô hình, công thức yếu hoặc lỗi được cố ý tạo thành cùng một loại lỗi.

| Vấn đề | Nguồn và biến | Quan hệ K / cách xử lý v1 | CTL / bằng chứng |
|---|---|---|---|
| Mô hình bốn pha, chưa biểu diễn 12 đầu ra | V0-01, V0-05; enum `state` | v1 thêm `phase`, 12 đầu ra và hai pha ALL_RED; L biểu diễn từng đèn thật | `physical_green_exclusion`, `one_hot_*`, `synchronized_*`; log v1 và stdout v0 tại `before_v0_logs/` |
| Timer v0 đi qua 0; không tương đương chính xác D giây | V0-02; `timer` | v1 timer từ 1 đến D, R chuyển pha khi r=1 | `timer_bounds`, `countdown_*`, `hold_*`, `reset_*`; kiểm HTTP chu kỳ và log v1. Hai SPEC bounds của v0 đúng không chứng minh độ dài pha |
| Nạp timer không theo pha đích; nhánh period trùng guard | V0-03; `timer`, mode/period | v1 dùng D(q′, period ở đồng hồ mới), tách `entry_period`; đồng hồ thật 24 giờ | Nhóm `reset_*`, `latch_*`, đồng hồ; `nusmv_period_reachability.log` chứng minh bốn khung giờ đạt được. Nhận xét lỗi v0 dựa mã/audit, không gán một phản ví dụ NuSMV mới chưa chạy |
| Safety v0 yếu; cấm mọi all-red khác yêu cầu an toàn v1 | V0-08 | v1 quy định vàng đối diện đỏ và clearance toàn đỏ; R đi qua hai pha dọn giao lộ | `yellow_ns_other_red`, `yellow_ew_other_red`, `clearance_all_red`, `advance_NS_YELLOW`; stdout v0 có TRUE vẫn không chứng minh yêu cầu mới |
| Khởi tạo/chuyển tiếp bị cố ý gây lỗi | V0-04, V0-07, V0-09 | Giữ nguyên baseline và log phản ví dụ đã có; phân loại là đối chứng cố ý lỗi | Mở đúng stdout v0 trong audit. Không gán các lỗi này cho mô hình v1 hợp lệ |
| Ba fault mới kiểm độ nhạy | Các bản `negative_*.smv` riêng trong R_NEW | Cố ý đồng xanh / nạp sai / bỏ ALL_RED; không sửa nguồn v1 | `negative_*.log` trả FALSE và trace; PASS của harness là đúng mong đợi |
| Emergency / file khung / đăng nhập | V0-06, V0-11…14 | Chưa tích hợp emergency; file khung chưa có SPEC; đăng nhập ngoài nghiệp vụ | Không tuyên bố đã kiểm/sửa chức năng chưa có trong v1 |

Ảnh minh họa: [Before/After](evidence/screenshots/05-before-after.png). Các giới hạn, tái sử dụng, sửa đổi, thuộc tính và bằng chứng cho **từng file** đã có đủ năm mục trong tài liệu gốc và màn hình chọn 14 nguồn.

**CWE/CERT cần giảng viên xác nhận:** mẫu báo cáo nhấn mạnh phân loại yếu điểm an toàn phần mềm. Các vấn đề hiện tại là ngữ nghĩa chuyển pha, timer và đặc tả CTL của mô hình giáo dục. Dự án chưa có căn cứ để gán mã CWE hay quy tắc CERT cụ thể. Đề nghị nhóm xác nhận có thể trình bày theo phân loại lỗi logic/đặc tả hay cần một hạng mục an toàn phần mềm bổ sung. Không tự điền mã để đủ biểu mẫu.

## 5. So sánh Before/After

| Yêu cầu | Ánh xạ |
|---|---|
| Baseline | 14 nguồn v0 giữ nguyên; hash từng file trong [before_after_audit.json](../evidence/before_after_audit.json). Cả 22 file .smv có trước web, gồm mô hình sinh và đối chứng, đều được bảo toàn |
| After chính thức | [smart_intersection.smv](../smart_intersection.smv), SHA-256 `c177eb76351a2e1b12a0bdcd202f0f02da4284b3e9b03380d039d52b2c121239` |
| Bảng so sánh | Chép bảng/file tương ứng từ [BEFORE_AFTER_V0_V1.md](../BEFORE_AFTER_V0_V1.md): tái sử dụng; lỗi/giới hạn; v1 xử lý; CTL/LTL; stdout/trace thực tế |
| Biến và R | So sánh enum trừu tượng với phase/timer/clock/12 đầu ra; chỉ rõ clearance và ngữ nghĩa nạp timer pha đích |
| Công thức và log | V0 có 28 công thức gốc, 25 TRUE, 3 FALSE; ba file không có SPEC không được coi là PASS. V1 kiểm bộ CTL khác theo yêu cầu mới; không lấy chênh lệch số PASS làm tỉ lệ sửa lỗi |
| Hình và giao diện | [Ảnh so sánh](evidence/screenshots/05-before-after.png), mục **So sánh Before/After**; mở mã v0/v1 và stdout liên quan ngay trong trang |

Không chạy lại mô hình v0 trong nhiệm vụ web; bằng chứng v0 được đọc từ audit và stdout đã có. Không trình bày trace của negative v1 như thể là trace phát hiện lỗi hiện hữu của adaptive v0.

## 6. Bằng chứng kiểm chứng

| Yêu cầu | Tệp thực tế cần đính kèm |
|---|---|
| Công cụ, nguồn, thời điểm | `R_NEW/metadata.json`, `console.log`; có UTC bắt đầu/kết thúc, hash nguồn, lệnh checker thực tế trong JSON kết quả |
| 335 CTL mặc định | `R_NEW/evidence/nusmv_main.log` và `nusmv_results.json`; công thức đặt tên đối chiếu [properties.json](../properties.json) |
| 335 CTL giờ khởi tạo bất kỳ | `R_NEW/evidence/nusmv_any_start_time.log`; không suy ra số trạng thái của mô hình này từ số 86.400 của quỹ đạo mặc định |
| Bốn khung giờ đạt được | `R_NEW/evidence/nusmv_period_reachability.log`, bốn công thức EF |
| 26 CTL JSON mới | `R_NEW/ctl_results.json`; bộ kiểm Python độc lập, phân biệt [bản ghi công cụ cũ](../evidence/seclab_results.json) |
| S và R | `R_NEW/reachable.log/json` đếm BDD; `graph_results.json` kiểm từng cạnh/12 đèn trên hai JSON |
| Phản ví dụ | Ba `R_NEW/evidence/negative_*.log` và mô hình đi kèm; ghi rõ nguồn cố ý lỗi, công thức FALSE là kết quả mong đợi |
| Web và tích hợp | [backend_tests.json](evidence/backend_tests.json), [browser_tests.json](evidence/browser_tests.json), [ma trận 14 yêu cầu](IMPLEMENTATION_REPORT_VI.md) |
| Bảo toàn nguồn | [preservation_baseline.json](evidence/preservation_baseline.json), `R_NEW/metadata.json → preservation` và kết quả kiểm cuối trong báo cáo triển khai |
| Ảnh | [Dashboard lượt mới](evidence/screenshots/03-kiem-chung-moi.png), [danh mục bằng chứng](evidence/screenshots/06-bang-chung.png) |

LTL chưa có kết quả thực thi được công bố. Không ghi “CTL/LTL đều PASS”. Không xem ảnh dashboard hoặc bộ thử trình duyệt là thay thế stdout NuSMV.

## 7. Thảo luận và bài học

Nêu sự khác biệt giữa công thức TRUE và yêu cầu đủ mạnh: enum chỉ có một giá trị vốn không tự chứng minh 12 đầu ra vật lý an toàn. Cần kiểm one-hot, đồng bộ, loại trừ và màu đối diện khi vàng. Hai pha ALL_RED là yêu cầu mới cần thiết cho mô hình này, nên công thức v0 cấm all-red không được giữ nguyên một cách máy móc.

Khung giờ hiện tại và khung giờ đầu pha là hai thành phần khác nhau của S. Nếu gộp chúng, việc đổi giờ có thể vô tình cắt pha. CTL `reset_*`/`latch_*`, kiểm ranh giới API và ảnh 06:59:59/07:00:00 hỗ trợ giải thích; cần trích đúng log và bước trạng thái, không dựng một trace minh họa rồi gọi là phản ví dụ thật.

Bản chiếu bỏ clock có thêm nhánh và khả năng ở mãi trong một period; không dùng nó để tuyên bố thời điểm tuyệt đối trong ngày. Bản exact chỉ mô tả quỹ đạo S0 mặc định. Khi chọn giờ khởi tạo khác, web gắn cảnh báo nếu trạng thái nằm ngoài S này; ngữ nghĩa bước vẫn theo Python, và bộ CTL NuSMV giờ khởi tạo bất kỳ là bằng chứng bổ sung.

Các giả định: đồng hồ rời rạc một giây; vận hành bình thường; không có trễ đầu ra, hỏng đèn, cảm biến, người đi bộ, xe ưu tiên hoặc mô hình va chạm vật lý. Tốc độ phát trình duyệt không bảo đảm thời gian thực. Liveness của đèn không tự chứng minh tối ưu lưu lượng hay thời gian chờ xe trong thế giới thật.

## 8. Phụ lục

Đính kèm [hướng dẫn chạy](README.md), cấu hình, [properties.json](../properties.json), mô hình v1, 14 nguồn v0 kèm audit, hai JSON Kripke, log đã lưu và R_NEW được chọn, phản ví dụ, hai bộ kiểm thử, kết quả JSON và bảy ảnh màn hình. Tệp exact lớn; nên nộp như artifact thay vì chèn toàn bộ vào nội dung báo cáo.

| Hình thật | Nội dung / màn hình |
|---|---|
| [01-mo-phong.png](evidence/screenshots/01-mo-phong.png) | Giao lộ, 12 đèn, timer và mô phỏng tại mốc đổi giờ |
| [02-kripke.png](evidence/screenshots/02-kripke.png) | Trạng thái có clock, cạnh R, cảnh báo ngoài quỹ đạo S mặc định |
| [03-kiem-chung-moi.png](evidence/screenshots/03-kiem-chung-moi.png) | Kết quả NuSMV mới và nguồn thực thi |
| [04-cau-hinh.png](evidence/screenshots/04-cau-hinh.png) | Lịch 24 giờ và thời lượng nguồn |
| [05-before-after.png](evidence/screenshots/05-before-after.png) | Đối chiếu nguồn v0/v1 và phân loại |
| [06-bang-chung.png](evidence/screenshots/06-bang-chung.png) | Tệp, hash và kiểm tra bảo toàn |
| [07-dien-thoai.png](evidence/screenshots/07-dien-thoai.png) | Giao diện tại chiều rộng 390 px |

Các ảnh chỉ chứng minh giao diện tại thời điểm chụp. Kết luận hình thức phải dẫn log checker và đúng mô hình/hash tương ứng.
