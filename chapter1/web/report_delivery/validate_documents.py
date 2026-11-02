"""Validate generated deliverables without changing existing product artifacts."""
from pathlib import Path
from zipfile import ZipFile
import sys,json,re,hashlib,unicodedata
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE/'_tools'))
import pymupdf
from docx import Document
from PIL import Image,ImageDraw,ImageFont

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
docx=HERE/'BIEN_BAN_KIEM_THU_PHAN_MEM_CHUONG_1.docx';pdf=docx.with_suffix('.pdf');out=HERE/'quality_checks'
a=read(out/'evidence_audit.json');trace=read(out/'test_case_traceability.json');word=read(out/'word_open.json'); export=read(out/'browser_export.json'); assert word['status']=='DOCX_OPENED' and word['embedded_images']==7
with ZipFile(docx) as z:
    assert z.testzip() is None
    media={n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('word/media/')}
    assert len(media)==7 and set(media.values())=={i['sha256'] for i in a['images']}
D=Document(docx);assert len(D.inline_shapes)==7
caseids=[c['id'] for rows in trace.values() if isinstance(rows,list) for c in rows];assert len(caseids)==62 and len(set(caseids))==62
alltext='\n'.join(p.text for p in D.paragraphs)+'\n'+'\n'.join(c.text for t in D.tables for row in t.rows for c in row.cells)
assert all(s in alltext for s in caseids)
ids={e['id'] for e in a['evidence']}
for group in ['web','backend','formal','negative']:
    for c in trace[group]:
        refs=re.findall(r'EV\d{2}',c['evidence']);assert refs and all(x in ids for x in refs)
for i,c in enumerate(trace['web']):assert c['status']==a['browser']['checks'][i]['status'] and c['native']==a['browser']['checks'][i]['name']
assert all(c['status']=='PASS*' for c in trace['backend']) and a['backend']['tests_run']==13
assert all(c['status']=='PASS (FALSE)' for c in trace['negative'])
assert len(a['properties'])==335 and all(p['verified'] for p in a['properties'])
assert all((ROOT/e['path']).is_file() and sha(ROOT/e['path'])==e['sha256'] for e in a['evidence'])
protected=read(out/'preservation_snapshot.json');changed=[p for p,h in protected.items() if not(ROOT/p).is_file() or sha(ROOT/p)!=h];assert not changed,changed
P=pymupdf.open(pdf);assert P.page_count>10 and export['returncode']==0
pages=[];outside=[];previews=out/'page_previews';previews.mkdir(exist_ok=True)
for i,page in enumerate(P):
    text=unicodedata.normalize('NFC',page.get_text());rect=page.rect
    for block in page.get_text('dict')['blocks']:
        if block.get('type')!=0:continue
        for line in block['lines']:
            for span in line['spans']:
                box=pymupdf.Rect(span['bbox'])
                if box.x0<-.5 or box.y0<-.5 or box.x1>rect.width+.5 or box.y1>rect.height+.5:outside.append({'page':i+1,'text':span['text'],'bbox':list(box)})
    # A near-empty page can indicate accidental section/page breaks.
    pages.append({'page':i+1,'width_pt':rect.width,'height_pt':rect.height,'characters':len(text),'case_ids':sorted(set(re.findall(r'(?:WEB|API|FM|NEG)-\d{2}',text))),'preview':f'page_previews/page_{i+1:02d}.png'})
    page.get_pixmap(matrix=pymupdf.Matrix(1.15,1.15),alpha=False).save(previews/f'page_{i+1:02d}.png')
full='\n'.join(p.get_text() for p in P).replace('\u200b','')
full=re.sub(r'((?:WEB|API|FM|NEG)-)\s+(?=\d{2}\b)',r'\1',full)
assert all(x in full for x in caseids),[x for x in caseids if x not in full]
assert 'BIÊN BẢN' in full and 'KIỂM THỬ PHẦN MỀM' in full and '335/335' in full and '26/26' in full and '[Ký và ghi rõ họ tên]' in full
assert not outside,outside
# Render contact sheets from actual PDF pages; original screenshot files are untouched.
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
for first in range(0,len(pages),20):
    subset=pages[first:first+20];sheet=Image.new('RGB',(1250,((len(subset)+3)//4)*290),'#d9e1e8');draw=ImageDraw.Draw(sheet)
    for j,v in enumerate(subset):
        im=Image.open(out/v['preview']);im.thumbnail((295,257));x=(j%4)*312+(312-im.width)//2;y=(j//4)*290+25;sheet.paste(im,(x,y));draw.text(((j%4)*312+12,(j//4)*290+4),f"Trang {v['page']}",font=font,fill='#173e52')
    sheet.save(out/f'contact_sheet_{first//20+1:02d}.png')
result={'document_date':a['document_date'],'status':'PASS','word_open':word,'pdf_open':'PASS','pdf_export_application':'Microsoft Edge headless; print HTML generated from exact DOCX content','word_pdf_export':'Stalled in this environment; fallback used','docx_word_pages':word['page_count'],'pdf_pages':P.page_count,'docx_tables':len(D.tables),'embedded_original_screenshots':7,'detailed_record_entries':len(caseids),'case_counts':{k:len(trace[k]) for k in ['web','backend','formal','negative']},'all_evidence_references_resolve':True,'all_335_named_properties_match_raw_log':True,'all_source_and_evidence_files_unchanged':not changed,'protected_files':len(protected),'changed_files':changed,'pdf_out_of_page_text':outside,'near_empty_pages':[p['page'] for p in pages if p['characters']<100],'pages':pages,'deliverables':{docx.name:sha(docx),pdf.name:sha(pdf)},'product_tests_rerun':False,'note':'PASS applies to deliverable structure/evidence validation. Visual review is recorded separately after page previews are inspected; no signed manual product test is implied.'}
(out/'document_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['pages']},ensure_ascii=True,indent=2))


