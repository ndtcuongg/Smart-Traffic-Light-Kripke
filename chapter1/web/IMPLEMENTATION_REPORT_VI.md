# Báo cáo triển khai ứng dụng web Chương 1

Ứng dụng Giao Lộ đã được triển khai trong `chapter1/web/`, chạy độc lập với SecLabFramework. Có đủ sáu khu vực: mô phỏng, Kripke, kiểm chứng, cấu hình, Before/After và bằng chứng. Mô hình v1 chính thức, các nguồn v0 và bằng chứng có trước nhiệm vụ web được giữ nguyên.

Báo cáo tổng hợp lúc **2026-10-22T15:40:44.885539+00:00** (UTC), từ kết quả checker và kiểm thử đã thực thi. Không dùng dữ liệu mô phỏng làm kết quả kiểm chứng mới.

## Chạy và trình bày

Từ thư mục gốc dự án:

```powershell
python chapter1/web/server.py
```

Mở **http://127.0.0.1:8765**. Python 3.11+, không cần gói pip/npm để sử dụng. NuSMV trên PATH dùng cho nút chạy kiểm chứng; nếu thiếu, vẫn xem bằng chứng cũ và dùng mô phỏng. [README](README.md) có kịch bản trình bày và lệnh chạy lại hai bộ thử.

## Thành phần bàn giao và phần tái sử dụng

| Thành phần mới | Vai trò / nguồn tái sử dụng |
|---|---|
| `server.py` | HTTP cục bộ, phiên mô phỏng, API đồ thị/bằng chứng và tác vụ kiểm chứng nền |
| `domain.py` | Adapter gọi `intersection.initial/step/lamps/label/exact_graph`; đọc config, JSON, properties và audit có sẵn |
| `static/index.html`, `styles.css`, `app.js`, `favicon.svg` | Giao diện tiếng Việt, SVG ngã tư, 12 đèn, sáu khu vực, màn hình điện thoại; frontend không định nghĩa quy tắc chuyển đèn riêng |
| `evidence_store.py` | Đối chiếu công thức với kết quả có thật; gắn nguồn lịch sử/mới và đường dẫn stdout |
| `verification_worker.py` | Gọi lại `verify_nusmv.verify()` hiện có với thư mục đích riêng; chạy đếm BDD; dùng `verify_graph.verify_file()` chỉ đọc |
| `ctl_checker.py` | Kiểm CTL JSON độc lập bằng fixpoint; không import/gọi SecLabFramework |
| `tests/test_backend.py`, `tests/browser.mjs` | Kiểm hồi quy API/kernel và kiểm tích hợp Edge/CDP |
| `REPORT_SUPPORT_VI.md` | Ánh xạ tám phần mẫu báo cáo sang biến/K/CTL/nguồn/log/ảnh; nêu vấn đề CWE/CERT cần xác nhận |
| `evidence/`, `runs/` | Dấu vết bảo toàn, kết quả thử, bảy ảnh thật và kết quả thực thi mới |

Khi chạy lại NuSMV, worker kiểm mã sinh từ cấu hình/Python khớp v1. Chỉ đổi điểm ghi của module kiểm chứng trong tiến trình con; không sửa script nguồn. Không chạy workflow cũ có phụ thuộc giao diện SecLab, không tạo Excel hoặc chương khác.

## Kết quả hình thức vừa thực thi

Lượt được chọn làm bằng chứng báo cáo: **[20261022T153609Z_0d111894](runs/20261022T153609Z_0d111894/metadata.json)**. Bắt đầu `2026-10-22T15:36:10.021100+00:00`, kết thúc `2026-10-22T15:36:46.844501+00:00`. Xem [console thật](runs/20261022T153609Z_0d111894/console.log). Dashboard cho phép chọn lại lượt này sau khi khởi động lại web.

| Phép kiểm | Kết quả thực tế | Bằng chứng |
|---|---|---|
| NuSMV 2.7.1, CTL mặc định | 335/335 TRUE | [nusmv_main.log](runs/20261022T153609Z_0d111894/evidence/nusmv_main.log) |
| NuSMV, CTL giờ khởi tạo bất kỳ | 335/335 TRUE | [nusmv_any_start_time.log](runs/20261022T153609Z_0d111894/evidence/nusmv_any_start_time.log) |
| Khả đạt bốn khung giờ | 4/4 TRUE | [nusmv_period_reachability.log](runs/20261022T153609Z_0d111894/evidence/nusmv_period_reachability.log) |
| CTL JSON, bộ kiểm Python độc lập | 26/26 đúng | [ctl_results.json](runs/20261022T153609Z_0d111894/ctl_results.json) |
| Đếm trạng thái đạt được NuSMV BDD | 86,400 trạng thái, returncode 0 | [reachable.log](runs/20261022T153609Z_0d111894/reachable.log), [lệnh và thời gian](runs/20261022T153609Z_0d111894/reachable.json) |
| Kiểm hai JSON: đèn, cạnh một giây, khả đạt | Cả hai PASS, không bế tắc | [graph_results.json](runs/20261022T153609Z_0d111894/graph_results.json) |
| Ba bản cố ý lỗi | Cả ba FALSE như mong đợi, có trace | [nusmv_results.json](runs/20261022T153609Z_0d111894/evidence/nusmv_results.json) và ba log dưới đây |

- [Xung đột xanh cố ý](runs/20261022T153609Z_0d111894/evidence/negative_conflicting_green.log).
- [Reset timer sai cố ý](runs/20261022T153609Z_0d111894/evidence/negative_timer_reset.log).
- [Bỏ ALL_RED cố ý](runs/20261022T153609Z_0d111894/evidence/negative_skip_all_red.log).

PASS của harness ba đối chứng nghĩa là phát hiện đúng lỗi được tạo; không phải ba lỗi của v1 hợp lệ. Bản chiếu có 1,012 trạng thái / 2,548 cạnh; bản exact có 86,400 trạng thái / 86,400 cạnh. Dấu phẩy trong bảng này phân cách hàng nghìn. Kết quả đếm BDD 86.400 áp dụng khởi tạo mặc định, không phải số trạng thái hợp mọi giờ khởi tạo của mô hình kiểm bổ sung.

Các bằng chứng cũ vẫn ở `chapter1/evidence/`. Kết quả 26 CTL cũ được ghi nhãn SecLabFramework lịch sử; lượt mới ghi đúng bộ kiểm Python. Chưa có kết quả LTL để công bố.

## Kiểm thử web và ma trận yêu cầu

Backend: **13/13 ca unittest PASS**, không failure/error. Browser: **32/32 kiểm tra PASS**, không lỗi JavaScript, Microsoft Edge headless/CDP; thời điểm bản ghi `2026-10-22T15:36:54.644Z`. [backend_tests.json](evidence/backend_tests.json), [browser_tests.json](evidence/browser_tests.json) chứa kết quả thực tế.

| # yêu cầu | Kiểm tra đã chạy / bằng chứng tương ứng | Kết quả |
|---|---|---|
| 1. Đúng 12 đèn | Backend `test_01`; DOM 12 circle và 12 chỉ báo so với API ở S0, suốt chu kỳ và qua mốc giờ | PASS |
| 2. Đồng bộ Bắc/Nam, Đông/Tây | Toàn bộ 86.400 bước kernel, đối chiếu DOM/API; mẫu HTTP qua một chu kỳ | PASS |
| 3. Không xanh xung đột | Toàn bộ ngày; NuSMV physical_green_exclusion; đối chứng cố ý xanh được bắt | PASS |
| 4. Đúng sáu pha | Backend `test_02`; browser ghi lại 43 bước và thứ tự chuyển pha | PASS |
| 5. Giảm timer đúng | Mỗi cạnh mẫu HTTP; DOM/API trong chu kỳ; CTL countdown | PASS |
| 6. Reload thời lượng pha đích | Backend `test_02/04`, các CTL reset; không lấy duration pha nguồn | PASS |
| 7. ALL_RED đủ thời lượng | Backend xác nhận reload 2 giây và giữ pha khi r>1; CTL clearance/hold/advance | PASS |
| 8. Đổi đúng khung giờ | Backend cả 7 mốc, kể cả 06:00; browser 6 nút mốc yêu cầu, kiểm không reset pha | PASS |
| 9. Quay ngày lúc nửa đêm | 23:59:59 → 00:00:00 qua API và UI; nhóm CTL clock | PASS |
| 10. Start/Pause/Resume/Reset/Step | Edge bấm điều khiển, chọn tốc độ 8×, xác nhận dừng không đổi và tiếp tục thay đổi | PASS |
| 11. Web khớp ngữ nghĩa nguồn | Backend đối chiếu 5 điểm khởi tạo × 120 cạnh với initial/step; DOM/API ở mỗi mẫu | PASS |
| 12. Chi tiết Kripke/AP | S0, L(s), cạnh R so trực tiếp JSON; lọc, bốn góc nhìn, exact và trạng thái mô phỏng | PASS |
| 13. Kết quả thật | Đọc stdout cũ; chạy worker thật từ nút UI; kiểm 335+335+4, 26 JSON, BDD và mở trace | PASS |
| 14. Đối chiếu đúng file | Audit đủ 14 nguồn, năm mục/file, hash/stdout; browser xác nhận danh sách v0 và file v1 | PASS |

Các kiểm tra bổ sung: phiên độc lập, đầu vào sai, POST thiếu token, giới hạn đọc file, checker CTL trên đồ thị phân nhánh với EF đúng/AF sai, AG bỏ trạng thái không đạt được, AX/EX/EG và từ chối deadlock. Kiểm giao diện điện thoại rộng 390 px không tràn ngang, điều hướng đóng/mở được.

Trong lần chạy lại trung gian, phép dò Kripke dùng chờ cố định 200 ms đã đọc trước phản hồi API và báo FAIL. Bản ghi được giữ trong [test_history](evidence/test_history/). Đã thay bằng chờ đúng mã trạng thái cần hiển thị; thêm chốt phản hồi để lựa chọn mới không bị phản hồi cũ ghi đè. Kết quả PASS nêu trên lấy từ lần kiểm cuối sau sửa, không xóa dấu vết FAIL.

Kiểm thử trình duyệt xác nhận tích hợp/hiển thị; không thay thế kiểm chứng hình thức.

## Ảnh giao diện thực tế

Bảy PNG do bộ thử Edge chụp trực tiếp:

| Ảnh | Nội dung |
|---|---|
| [01 — Mô phỏng](evidence/screenshots/01-mo-phong.png) | Bốn hướng, 12 đèn, timer và nguồn v1 |
| [02 — Kripke](evidence/screenshots/02-kripke.png) | Lân cận exact, chọn trạng thái chạy và cảnh báo quỹ đạo |
| [03 — Kiểm chứng mới](evidence/screenshots/03-kiem-chung-moi.png) | Dashboard từ lượt thực thi được chọn |
| [04 — Cấu hình](evidence/screenshots/04-cau-hinh.png) | Lịch và thời lượng lấy từ config.json |
| [05 — Before/After](evidence/screenshots/05-before-after.png) | Nguồn v0, phân tích và v1 chính thức |
| [06 — Bằng chứng](evidence/screenshots/06-bang-chung.png) | Danh mục artifact và kiểm bảo toàn |
| [07 — Điện thoại](evidence/screenshots/07-dien-thoai.png) | Màn hình 390 px |

## Bảo toàn và phạm vi

Đối chiếu SHA-256: **93/93 tệp có trước web giữ nguyên**, danh sách thay đổi rỗng. Bao gồm toàn bộ 22 file .smv có trước, 14 nguồn v0, v1 chính thức, cấu hình, script, JSON, tài liệu và bằng chứng gốc trong baseline. [Baseline](evidence/preservation_baseline.json), [kiểm cuối](evidence/final_audit.json). Chỉ bộ nhớ đệm Python được loại khỏi danh sách artifact nguồn.

Hash v1: `c177eb76351a2e1b12a0bdcd202f0f02da4284b3e9b03380d039d52b2c121239`. Các bản .smv mới dưới web/runs là bản chép/lượt kiểm riêng, không thay thế v0/v1 chính thức.

Đây là mô hình vận hành bình thường, thích nghi theo lịch giờ, không có cảm biến lưu lượng, emergency, người đi bộ, trễ thiết bị hoặc mô hình va chạm vật lý. Thời gian phát frontend không phải bảo đảm thời gian thực phần cứng. Bản chiếu bỏ clock có thêm nhánh; exact 86.400 nút chỉ là quỹ đạo S0 mặc định. Trạng thái chọn giờ tùy ý nằm ngoài quỹ đạo được ghi rõ trên UI. Bộ kiểm CTL Python hỗ trợ tập cú pháp AP/!AP với AG/AF/EF/EG/AX/EX của JSON hiện tại, không nhận CTL tổng quát.

Không còn lỗi chặn vận hành trong các kiểm tra đã thực hiện. Nhóm cần điền thông tin sinh viên thật và xác nhận yêu cầu CWE/CERT với giảng viên. Không gán mã CWE/CERT cho lỗi logic giao thông khi chưa có căn cứ. [Tài liệu hỗ trợ báo cáo](REPORT_SUPPORT_VI.md) ánh xạ đầy đủ tám phần của mẫu.
