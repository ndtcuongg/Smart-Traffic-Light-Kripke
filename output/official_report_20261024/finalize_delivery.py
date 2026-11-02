from pathlib import Path
import sys,json,html,re,hashlib
from zipfile import ZipFile,ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.stdout.reconfigure(encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def obj(name):return json.loads((OUT/name).read_text(encoding='utf-8-sig'))
case=obj('verification_test_cases.json');rows=[]
for c in case:
 ref=c['evidence'];path=re.sub(r':\d+$','',ref);target=ROOT/path
 assert target.is_file(),path
 cells=[html.escape(c[k]) for k in ['id','category','expected','actual']]
 anchor='<a href="'+target.as_uri()+'">'+html.escape(ref)+'</a>'
 rows.append('<tr>'+''.join('<td>'+v+'</td>' for v in cells)+'<td>'+anchor+'</td><td>'+html.escape(c['notes'])+'</td></tr>')
(OUT/'verification_test_record.html').write_text('<!doctype html><html lang="vi"><meta charset="utf-8"><title>Truy vết kiểm chứng</title><style>body{font:15px Georgia;margin:24px}table{border-collapse:collapse}td,th{border:1px solid #aaa;padding:7px;text-align:left;overflow-wrap:anywhere}th{position:sticky;top:0;background:#e9eef2}</style><h1>838 dòng truy vết kiểm chứng</h1><p>Phân biệt lượt mới/lưu trữ và đơn vị; số dòng không phải tổng yêu cầu độc lập. Liên kết mở log thật trong kho; số sau dấu hai chấm là dòng cần xem.</p><table><tr><th>ID</th><th>Nguồn</th><th>Expected</th><th>Actual</th><th>Log</th><th>Ghi chú / công thức</th></tr>'+''.join(rows)+'</table></html>',encoding='utf-8')
# Review explicitly records visual inspection, separate from automated checks.
review={'status':'PASS','reviewed':'Four contact sheets covering all 20 report pages, plus full-size injected-fault page','observations':['No clipped text or blank/orphan page','Vietnamese serif typography and numbered pages visible','Code blocks and tables fit page width','Archived screenshots labeled as archived UI evidence'],'note':'DOCX content matches the shared generation structure; Word pagination may differ from Edge PDF.'}
(OUT/'visual_review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
readme='''# Bàn giao báo cáo đồ án — 24/10/2026

- Báo cáo chính thức: [PDF](BAO_CAO_CHINH_THUC.pdf) · [DOCX chỉnh sửa](BAO_CAO_CHINH_THUC.docx), 20 trang PDF, đúng tám mục và độ dài gợi ý.
- Biên bản riêng: [PDF](BIEN_BAN_KIEM_CHUNG.pdf) · [DOCX](BIEN_BAN_KIEM_CHUNG.docx), 2 trang.
- [Kiểm kê trước viết](KIEM_KE_BANG_CHUNG.md) · [Checklist tiêu chí trường](CHECKLIST_TIEU_CHI.md).
- [838 dòng truy vết có liên kết log](verification_test_record.html) · [CSV](verification_test_cases.csv) · [JSON](verification_test_cases.json).
- [Mục lục trang PDF](MUC_LUC_TRANG.md) · [Kết quả kiểm tra](quality_validation.json).
- [Phụ lục nguồn và log nguyên văn](PHU_LUC_NGUON_VA_BANG_CHUNG.zip); nộp cùng báo cáo. Giữ nguyên cấu trúc kho để mở liên kết trong HTML.

Kết quả mới: 335/335 CTL v1 TRUE; BDD 86400 reachable; 26/26 CTL JSON TRUE; graph exact86400/86400, chiếu1012/2548; bốn query bổ sung v0 FALSE đúng dự kiến; ba injected-fault CTL FALSE có trace. Các LTL gốc trong hai harness v0 vẫn TRUE. Đã giữ nguyên 243 tệp dự án kiểm kê, không đổi nguồn v0 hoặc logic ứng dụng.

## Cần hoàn thiện trước nộp

1. Điền tên, MSSV, lớp, số nhóm, GitHub và phân công bằng thông tin thật; xác nhận giảng viên hướng dẫn thực tế.
2. Giảng viên xác nhận dùng mã lỗi mô hình D01–D03 thay CWE/CERT; không có căn cứ gán CWE/CERT trong kho.
3. Xác nhận quy ước tên v0/v1 hiện có thay hậu tố, phụ lục log điện tử và tài liệu quy trình năm bước/tuần học/mã đề tài.
4. V0 archive cũ thiếu timestamp/lệnh đầy đủ; không điền hồi tố. Counterexample trực tiếp mới đã bù thiếu chứng cứ timer/reset/reachability.
5. Chưa có thử nghiệm giao lộ vật lý, emergency hoặc thao tác GUI SecLab; không công bố các phần này PASS.

PDF được xuất bằng Edge từ cùng nội dung cấu trúc với DOCX. Word có thể phân trang khác; PDF là bản đã kiểm định dạng. Không có commit hoặc danh tính cá nhân được tạo giả.
'''
(OUT/'README_BAN_GIAO.md').write_text(readme,encoding='utf-8')
# Source snippets are compared against actual source using caption paths and line numbers.
md=(OUT/'BAO_CAO_CHINH_THUC.md').read_text(encoding='utf-8');last=None;checked=0
for raw in md.splitlines():
 m=re.search(r'((?:chapter1/|Smart-Traffic-Light-Verification/|output/official_report_20261024/)[^: ]+):(\d+)',raw)
 if m and (ROOT/m.group(1)).is_file():last=ROOT/m.group(1)
 n=re.match(r'^\s*(\d+) \| (.*)$',raw)
 if n and last:
  actual=last.read_text(encoding='utf-8-sig').splitlines()[int(n.group(1))-1]
  if actual!=n.group(2):
   candidates=[q for q in (OUT/'evidence').glob('*.log') if len(q.read_text(encoding='utf-8-sig').splitlines())>=int(n.group(1)) and q.read_text(encoding='utf-8-sig').splitlines()[int(n.group(1))-1]==n.group(2)]
   assert candidates,(str(last),n.group(1));last=candidates[0]
  checked+=1
print('Source snippet lines verified',checked)
manifest={p.relative_to(OUT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in OUT.rglob('*') if p.is_file() and 'render_profile' not in p.parts and p.name not in {'delivery_manifest.json','BAN_GIAO_BAO_CAO.zip'}}
(OUT/'delivery_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
with ZipFile(OUT/'BAN_GIAO_BAO_CAO.zip','w',ZIP_DEFLATED) as z:
 for p in OUT.iterdir():
  if p.is_file() and p.name!='BAN_GIAO_BAO_CAO.zip' and not p.name.startswith('contact_sheet_') and not p.name.endswith('_render.log'):z.write(p,p.name)
 for p in (OUT/'evidence').glob('*'):z.write(p,'evidence/'+p.name)
print('Delivery package ready', (OUT/'BAN_GIAO_BAO_CAO.zip').stat().st_size)
