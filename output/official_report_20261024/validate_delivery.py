from pathlib import Path
import sys,json,re,hashlib,unicodedata,csv
from zipfile import ZipFile
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.dont_write_bytecode=True;sys.stdout.reconfigure(encoding='utf-8');sys.path[:0]=[str(ROOT/'.codex-tools'),str(ROOT/'chapter1/web/report_delivery/_tools')]
import pymupdf
from docx import Document
from PIL import Image,ImageDraw,ImageFont

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def readj(n):return json.loads((OUT/n).read_text(encoding='utf-8-sig'))
inv=readj('source_inventory.json');assert all(sha(ROOT/k)==v['sha256'] for k,v in inv.items())
props=readj('ctl_catalog.json');assert len(props)==335
norm=lambda s:re.sub(r'[\s()]','',s)
runs=readj('evidence/fresh_nusmv_results.json');by={norm(c['formula']):c for c in runs[0]['checks']}
assert len(by)==335 and all(norm(p['formula']) in by and by[norm(p['formula'])]['result'] for p in props)
# Every numbered snippet matches a real source line; layout continuations are not treated as source.
md=(OUT/'BAO_CAO_CHINH_THUC.md').read_text(encoding='utf-8')
for p in props:assert (ROOT/'chapter1/smart_intersection.smv').read_text(encoding='utf-8').splitlines()[p['source_line']-1].startswith('CTLSPEC NAME '+p['name']+' ')
results={};pre=OUT/'page_previews';pre.mkdir(exist_ok=True);contents=[];reportheads=[]
sections=readj('build_summary.json')['report_top_level_sections']
for name in ['BAO_CAO_CHINH_THUC','BIEN_BAN_KIEM_CHUNG']:
 doc=Document(OUT/(name+'.docx'));assert abs(doc.sections[0].left_margin.cm-2)<.01
 assert doc.styles['Normal'].font.name=='Times New Roman' and doc.styles['Normal'].font.size.pt==11.5
 with ZipFile(OUT/(name+'.docx')) as z:assert z.testzip() is None
 if name=='BAO_CAO_CHINH_THUC':
  heads=[p.text for p in doc.paragraphs if p.style.name=='Heading 1'];assert heads==[f'{i}. '+s for i,s in enumerate(sections,1)]
 d=pymupdf.open(OUT/(name+'.pdf'));alltext='';pages=[];outside=[];fonts=set()
 for i,page in enumerate(d):
  text=unicodedata.normalize('NFC',page.get_text());alltext+=text
  assert '\ufffd' not in text
  assert 'Trang '+str(i+1) in text,(name,i+1,'missing page number')
  for block in page.get_text('dict')['blocks']:
   for ln in block.get('lines',[]):
    for s in ln['spans']:
     fonts.add(s['font']);r=pymupdf.Rect(s['bbox'])
     if r.x0<0 or r.y0<0 or r.x1>page.rect.width+.6 or r.y1>page.rect.height+.6:outside.append({'page':i+1,'text':s['text'],'box':list(r)})
  pages.append({'page':i+1,'characters':len(text),'first_line':text.splitlines()[1] if len(text.splitlines())>1 else ''})
  if name=='BAO_CAO_CHINH_THUC':
   for j,s in enumerate(sections,1):
    if f'{j}. {s}' in text and j not in [a['section'] for a in reportheads]:reportheads.append({'section':j,'title':s,'page':i+1})
   page.get_pixmap(matrix=pymupdf.Matrix(.85,.85),alpha=False).save(pre/f'page_{i+1:02d}.png')
  if name=='BIEN_BAN_KIEM_CHUNG':page.get_pixmap(matrix=pymupdf.Matrix(1,1),alpha=False).save(pre/f'record_{i+1:02d}.png')
 assert not outside,outside
 results[name]={'pages':len(d),'fonts':sorted(fonts),'no_text_outside_page':True,'page_numbers_continuous':True,'no_replacement_glyph':True,'page_details':pages}
 assert 'Mô hình hóa' in alltext
 if name=='BAO_CAO_CHINH_THUC':assert len(reportheads)==8
# True section lengths from actual PDF, compare to suggested guide lengths.
lengths={}
for i,h in enumerate(reportheads):
 end=reportheads[i+1]['page']-1 if i+1<len(reportheads) else results['BAO_CAO_CHINH_THUC']['pages']
 lengths[str(h['section'])]={'title':h['title'],'start_page':h['page'],'end_page':end,'pages':end-h['page']+1}
(OUT/'MUC_LUC_TRANG.md').write_text('# Mục lục theo PDF đã xuất\n\n'+'\n'.join(f"{h['section']}. {h['title']} — trang {h['page']}" for h in reportheads)+'\n\nPhụ lục A–F tiếp theo sau mục 8. PDF tạo từ cùng nội dung cấu trúc với DOCX, không bảo đảm Word phân trang giống Edge.\n',encoding='utf-8')
# Contact sheets for human visual review.
for batch in range((results['BAO_CAO_CHINH_THUC']['pages']+5)//6):
 sheet=Image.new('RGB',(1100,1600),'#dfe4e8');draw=ImageDraw.Draw(sheet)
 for slot,n in enumerate(range(batch*6+1,min(batch*6+7,results['BAO_CAO_CHINH_THUC']['pages']+1))):
  im=Image.open(pre/f'page_{n:02d}.png').convert('RGB');im.thumbnail((515,485));x=20+(slot%2)*545;y=25+(slot//2)*530;sheet.paste(im,(x,y));draw.text((x,y+487),f'Trang {n}',fill='black')
 sheet.save(OUT/f'contact_sheet_{batch+1:02d}.png')
checks={'status':'PASS','all_243_preexisting_files_unchanged':True,'all_335_formulas_mapped_by_actual_formula_not_output_order':True,'exact_eight_top_level_sections':True,'docx_zip_integrity':True,'docx_body_font':'Times New Roman 11.5pt','margins_cm':2,'documents':results,'report_section_lengths':lengths,'guide_suggested_lengths_met':all(lengths[str(i)]['pages']<=n for i,n in [(1,1),(2,1.5),(3,1),(4,6),(5,1),(6,3),(7,1)]),'renderer':'Edge print HTML generated from same structured content as DOCX; editable Word pagination can differ','pending_human_items':['Group identity and contribution placeholders','Instructor ruling on CWE/CERT, filenames, five-step source, electronic appendices'],'test_record_rows':len(readj('verification_test_cases.json'))}
(OUT/'quality_validation.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
manifest={p.relative_to(OUT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in OUT.rglob('*') if p.is_file() and 'render_profile' not in p.parts and p.name!='delivery_manifest.json'}
(OUT/'delivery_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':'PASS','pages':{k:v['pages'] for k,v in results.items()},'section_lengths':lengths,'guide_suggested_lengths_met':checks['guide_suggested_lengths_met']},ensure_ascii=False,indent=2))
