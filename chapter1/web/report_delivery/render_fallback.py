"""Render the exact DOCX content to print HTML; used if Word PDF export stalls."""
from pathlib import Path
import sys,html,json,base64
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE/'_tools'))
from docx import Document
from docx.oxml.ns import qn
D=Document(HERE/'BIEN_BAN_KIEM_THU_PHAN_MEM_CHUONG_1.docx');assets=HERE/'quality_checks/print_assets';assets.mkdir(exist_ok=True)
H=lambda s:html.escape(str(s))
def para(node):
    style=node.find('w:pPr/w:pStyle',node.nsmap);style=style.get(qn('w:val')) if style is not None else ''
    tag='h1' if style=='Heading1' else 'h2' if style=='Heading2' else 'h3' if style=='Heading3' else 'p'
    cls={'Title':'title','Subtitle':'subtitle','Caption':'caption'}.get(style,'')
    bits=[]
    for item in node.iter():
        if item.tag==qn('w:t'):bits.append(H(item.text or ''))
        elif item.tag==qn('w:br'):
            bits.append('<span class="page-break"></span>' if item.get(qn('w:type'))=='page' else '<br>')
        elif item.tag=='{http://schemas.openxmlformats.org/drawingml/2006/main}blip':
            ident=item.get(qn('r:embed'));part=D.part.related_parts[ident];imgpath=assets/(ident+'.png');imgpath.write_bytes(part.blob)
            # Keep original proportions; browser scales down to page area.
            bits.append('<img src="'+imgpath.as_uri()+'" class="record-image">')
    return '<'+tag+' class="'+cls+'">'+''.join(bits)+'</'+tag+'>'
def tbl(node):
    grid=node.find('w:tblGrid',node.nsmap);widths=[int(x.get(qn('w:w'))) for x in grid];total=sum(widths)
    cols='<colgroup>'+''.join(f'<col style="width:{100*x/total:.3f}%">' for x in widths)+'</colgroup>'
    rows=[]
    for i,row in enumerate(node.findall('w:tr',node.nsmap)):
        values=[]
        for cell in row.findall('w:tc',node.nsmap):
            text=''.join(cell.itertext())
            content=''.join(para(n) for n in cell if n.tag==qn('w:p'))
            values.append('<'+('th' if i==0 else 'td')+(' class="pass"' if text.startswith('PASS') else '')+'>'+content+'</'+('th' if i==0 else 'td')+'>')
        rows.append('<tr>'+''.join(values)+'</tr>')
    return '<table>'+cols+'<thead>'+rows[0]+'</thead><tbody>'+''.join(rows[1:])+'</tbody></table>'
sections=[];parts=[]
for n in D.element.body:
    if n.tag==qn('w:p'):
        parts.append(para(n));sect=n.find('w:pPr/w:sectPr',n.nsmap)
    elif n.tag==qn('w:tbl'):parts.append(tbl(n));sect=None
    elif n.tag==qn('w:sectPr'):sect=n
    else:sect=None
    if sect is not None:
        size=sect.find('w:pgSz',sect.nsmap);land=int(size.get(qn('w:w')))>int(size.get(qn('w:h')))
        sections.append('<section class="'+('landscape' if land else 'portrait')+'">'+''.join(parts)+'</section>');parts=[]
css='''@page portrait{size:A4 portrait;margin:17mm 20mm 17mm;}@page landscape{size:A4 landscape;margin:15mm 17mm 15mm;}@page{@bottom-center{content:"BBKT-CH1-2026-01 · Trang " counter(page) " / " counter(pages);font:8pt Arial;color:#607884;}}*{box-sizing:border-box}body{font:10.5pt/1.12 Arial,sans-serif;color:#172f40;margin:0}.portrait{page:portrait}.landscape{page:landscape}.portrait+.portrait,.landscape+.landscape{break-before:page}h1{font-size:16pt;color:#12354a;margin:13pt 0 7pt;break-after:avoid}h2{font-size:12.5pt;color:#147869;margin:13pt 0 7pt;break-after:avoid}h3{font-size:11pt;color:#284d60}p{margin:0 0 6pt;orphans:2;widows:2}.title{font-size:25pt;font-weight:bold;color:#12354a;margin:13pt 0 7pt}.subtitle{font-size:12pt;color:#58717f;margin:7pt 0}.caption{font-size:9pt;color:#607884}.page-break{display:block;break-after:page}table{width:100%;border-collapse:collapse;table-layout:fixed;margin-bottom:8pt;font-size:9.5pt;line-height:1.05}thead{display:table-header-group}tr{break-inside:avoid}th,td{border:.5pt solid #b2bec7;padding:5pt;vertical-align:middle;overflow-wrap:anywhere}th{background:#173e52;color:white;font-weight:bold}td p,th p{font-size:inherit;margin:0 0 2pt;line-height:inherit}tbody tr:nth-child(even){background:#f2f6f8}.landscape table{font-size:9pt}.pass{color:#14735e;font-weight:bold}.record-image{display:block;width:auto;height:auto;max-width:100%;max-height:148mm;margin:0 auto 3pt}.portrait .record-image{max-height:180mm}img{break-inside:avoid}'''
output=HERE/'quality_checks/print_record.html';output.write_text('<!doctype html><html lang="vi"><meta charset="utf-8"><title>BIÊN BẢN KIỂM THỬ PHẦN MỀM — CHƯƠNG 1</title><style>'+css+'</style><body>'+''.join(sections)+'</body></html>',encoding='utf-8');print(output)
