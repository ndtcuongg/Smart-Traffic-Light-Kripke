# Giao Lộ — ứng dụng web Chương 1

Giao diện cục bộ để trình bày mô hình giao lộ bốn hướng, cấu trúc Kripke, kiểm chứng CTL và so sánh v0/v1. Mã mới nằm trong `chapter1/web/`. Không cần SecLabFramework, npm hoặc kết nối Internet để sử dụng ứng dụng.

## Chạy ứng dụng

Từ thư mục gốc `NuSMV_project`, chạy:

```powershell
python chapter1/web/server.py
```

Mở **http://127.0.0.1:8765** trong trình duyệt. Dừng máy chủ bằng Ctrl+C. Cần Python 3.11 trở lên; backend chỉ dùng thư viện chuẩn. Giữ nguyên cây thư mục dự án vì web tái sử dụng tài nguyên trong `chapter1/` và các nguồn v0.

Nếu cổng đang được sử dụng:

```powershell
python chapter1/web/server.py --port 8766
```

NuSMV cần có trên PATH để bấm **Chạy kiểm chứng mới**. Trong môi trường đã kiểm thử, NuSMV 2.7.1 có sẵn. Nếu không có NuSMV, ứng dụng vẫn mô phỏng, khám phá Kripke và đọc bằng chứng đã lưu; nút chạy mới bị vô hiệu hóa. Không cần cài gói Python bổ sung.

## Kịch bản trình bày khoảng năm phút

1. **Mô phỏng ngã tư:** Bắt đầu, chọn tốc độ 4× hoặc 8×, quan sát đủ sáu pha và hai lần đỏ toàn hướng. 12 chấm đèn trên hình và bảng BẬT/TẮT đều lấy từ backend. Xe chạy chỉ để minh họa.
2. **Đổi khung giờ:** chọn 06:59:59 rồi +1 giây. Đồng hồ thành 07:00:00, khung giờ chuyển cao điểm sáng; timer giảm một, thời lượng pha cũ không bị nạp lại. Nút mốc chuẩn bị 12 bước từ trước mốc bằng logic nguồn, để đến mốc vẫn đang trong pha xanh. Áp dụng giờ thủ công khởi tạo lại pha mặc định, không chạy chuẩn bị.
3. **Kripke:** xem bốn góc nhìn, chọn bản chiếu hoặc bản giữ đồng hồ; lọc pha, chọn trạng thái và đi theo cạnh R. Nút **Xem trạng thái mô phỏng** hiển thị đúng trạng thái đang chạy. Đối với giờ khởi tạo tùy chọn, trạng thái có thể nằm ngoài quỹ đạo S mặc định; màn hình cảnh báo rõ điều này.
4. **Kiểm chứng:** xem kết quả đã lưu, mở stdout gốc; sau đó chạy mới. Không đóng máy chủ khi đang chạy. Lượt mới thường cần vài chục giây trên máy đã thử; thời gian phụ thuộc máy. Xem riêng đối chứng cố ý lỗi và phản ví dụ.
5. **Before/After:** chọn từng nguồn trong 14 file; đọc đủ năm mục và mở stdout v0. Xem danh mục bằng chứng và kiểm tra bảo toàn tệp.

## Kiến trúc và nguồn có thẩm quyền

```text
Trình duyệt HTML / CSS / JS
        │ GET/POST localhost, một bước logic = một giây
server.py → domain.py → chapter1/intersection.py + config.json
        │
        ├─ evidence_store.py → JSON / stdout / audit gốc
        ├─ Kripke JSON chiếu + exact_graph(config) khi cần
        └─ verification_worker.py → verify_nusmv.py hiện có
                                  + NuSMV thật
                                  + ctl_checker.py độc lập
                                  + verify_graph.verify_file (chỉ đọc)
```

`smart_intersection.smv` v1 chính thức được giữ nguyên. Backend đối chiếu mã sinh từ Python/cấu hình với file này. JavaScript chỉ điều khiển nhịp gửi yêu cầu và hiển thị phản hồi; không có máy chuyển đèn riêng ở frontend. Các khoảng chờ đèn xanh và thời gian còn lại của mỗi màu được backend tính bằng cách đi tiếp trên mô hình nguồn, kể cả qua ranh giới khung giờ.

Sáu pha theo thứ tự: NS_GREEN → NS_YELLOW → ALL_RED_NS_TO_EW → EW_GREEN → EW_YELLOW → ALL_RED_EW_TO_NS → NS_GREEN. Hai pha vàng dài 3 giây; hai pha ALL_RED dài 2 giây. Thời lượng xanh đọc từ cấu hình, tùy khung giờ.

Backend chỉ lắng nghe 127.0.0.1. Phiên cookie tách mô phỏng từng trình duyệt; POST cần token của trang và kiểm tra Origin. Trình xem tệp chỉ cho đọc danh mục nguồn/bằng chứng đã cho phép. Đây là ứng dụng trình bày cục bộ, không phải dịch vụ nhiều người dùng triển khai công cộng.

## Bằng chứng lịch sử và kết quả mới

- **Đã lưu:** đọc `chapter1/evidence/`; nhãn CTL JSON lịch sử ghi đúng công cụ SecLabFramework từng tạo kết quả. Web không gọi công cụ đó.
- **Mới thực thi:** tạo `chapter1/web/runs/<mã-lượt>/`; chạy lại script NuSMV hiện có sau khi chuyển đích ghi vào thư mục mới. Có `metadata.json`, `console.log`, lệnh thực tế, stdout, kết quả, hash nguồn và thời điểm UTC. Khi mở lại ứng dụng, chọn lại lượt hoàn tất ở danh sách nguồn.
- Bộ kiểm CTL JSON độc lập dùng fixpoint trên đồ thị hữu hạn, hỗ trợ AG/AF/EF/EG/AX/EX với một AP hoặc phủ định AP. Phạm vi này đủ cho 26 công thức hiện có; không phải trình kiểm CTL tổng quát. Công thức NuSMV phức tạp vẫn do NuSMV kiểm.
- Ba `negative_*` dùng bản mô hình riêng bị gây lỗi. NuSMV trả FALSE và có phản ví dụ; PASS của bộ thử nghĩa là phát hiện đúng lỗi mong đợi. Không kết luận v1 chính thức có ba lỗi này.
- Danh mục hiện tại là CTL. Chưa có bằng chứng LTL để công bố.

## Kiểm thử lại

Từ gốc dự án:

```powershell
python chapter1/web/tests/test_backend.py
node chapter1/web/tests/browser.mjs
```

Lệnh đầu chạy unittest/API và kiểm tra toàn bộ 86.400 bước nguồn. Lệnh thứ hai cần Node 22+ hỗ trợ WebSocket tích hợp và Microsoft Edge tại đường dẫn Windows mặc định; tự mở Edge headless, máy chủ cổng trống, chạy kiểm chứng mới, chụp ảnh thật rồi dừng các tiến trình do bộ thử tạo. Bộ thử ghi kết quả dưới `web/evidence/`; lượt NuSMV mới dưới `web/runs/`. Không cần Node/Edge headless để dùng ứng dụng hàng ngày.

Xem kết quả đã chạy thực tế trong [báo cáo triển khai](IMPLEMENTATION_REPORT_VI.md), [backend_tests.json](evidence/backend_tests.json), [browser_tests.json](evidence/browser_tests.json). Cần chạy các lệnh từ gốc dự án để đường dẫn thử đúng. Trình kiểm thử trình duyệt bổ sung kiểm chứng hình thức, không thay thế NuSMV.

## Hồ sơ bàn giao

- [Hỗ trợ tám phần báo cáo học phần](REPORT_SUPPORT_VI.md).
- [Báo cáo triển khai, ma trận 14 yêu cầu và kết quả thật](IMPLEMENTATION_REPORT_VI.md).
- [Đối chiếu v0/v1 sẵn có](../BEFORE_AFTER_V0_V1.md).
- [Ảnh thật giao diện](evidence/screenshots/).
- [Dấu vết 93 tệp trước khi làm web](evidence/preservation_baseline.json).

Các giới hạn cần trình bày: điều khiển thích nghi theo giờ, không có cảm biến lưu lượng; chỉ vận hành bình thường, không tích hợp emergency/người đi bộ; một giây logic không cam kết đồng bộ thời gian thực phần cứng; bản chiếu có thêm đường đi vì bỏ đồng hồ; bản JSON chính xác 86.400 nút là quỹ đạo S0 mặc định, không phải hợp mọi trạng thái khởi động tùy chọn. Thông tin sinh viên/nhóm và việc áp dụng CWE/CERT cần được bổ sung/xác nhận riêng, không được tự suy diễn từ kết quả kỹ thuật.
