from pathlib import Path
import json,hashlib
base=Path('chapter1/web/report_delivery');qa=base/'quality_checks'
review={'document_date':'2026-10-23','status':'PASS','review_type':'Rà soát trực quan tài liệu do trợ lý thực hiện; không phải kiểm thử sản phẩm thủ công có người ký','pdf_pages_reviewed_as_contact_sheets':list(range(1,25)),'detail_pages_reviewed':[3,7,11,15,24],'findings':{'tables':'Các bảng tám cột có tiêu đề lặp, nội dung trong ô đọc được; một số mã/đường dẫn xuống dòng trong ô hẹp.','vietnamese':'Tiếng Việt và công thức hiển thị đầy đủ ở các trang đã kiểm tra chi tiết.','images':'Bảy ảnh chụp gốc xuất hiện đúng tỷ lệ, không bị cắt mất nội dung.','signatures':'Họ tên, MSSV, ngày xác nhận và chữ ký giữ nguyên chỗ trống.','layout':'Không có trang trống bất thường; không có chữ vượt mép trang theo kiểm tọa độ.'},'word_pdf_limitation':'Word mở thành công DOCX 26 trang; native ExportAsFixedFormat bị treo. PDF 24 trang xuất bằng Edge từ cùng nội dung DOCX; số trang khác do bộ dựng trang.'}
(qa/'visual_review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
manifest={}
for p in [base/'BIEN_BAN_KIEM_THU_PHAN_MEM_CHUONG_1.docx',base/'BIEN_BAN_KIEM_THU_PHAN_MEM_CHUONG_1.pdf',base/'README.md',qa/'evidence_audit.json',qa/'document_validation.json',qa/'visual_review.json',qa/'test_case_traceability.json',qa/'preservation_snapshot.json',qa/'word_open.json']:
    manifest[p.relative_to(base).as_posix()]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(qa/'delivery_manifest.json').write_text(json.dumps({'document_date':'2026-10-23','files':manifest},ensure_ascii=False,indent=2),encoding='utf-8')
root=Path.cwd();before=json.loads((qa/'preservation_snapshot.json').read_text(encoding='utf-8'));changed=[n for n,h in before.items() if not(root/n).is_file() or hashlib.sha256((root/n).read_bytes()).hexdigest()!=h];assert not changed,changed
print(json.dumps({'documents_created':list(manifest)[:2],'protected_files':len(before),'changed_files':changed,'visual_review':'PASS','pdf_pages':24,'docx_word_pages':26},ensure_ascii=True,indent=2))
