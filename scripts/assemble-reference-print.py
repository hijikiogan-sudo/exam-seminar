from pathlib import Path
from pypdf import PdfReader,PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import json,io,sys
W=Path(sys.argv[1]).resolve();SITE=Path(sys.argv[2]).resolve()
plan=json.loads((W/'layout-plan.json').read_text())
outputs=[]
for item in plan:
    date=item['date'];writer=PdfWriter();front=PdfReader(W/'render-v2'/f'{date}-front.pdf');assert len(front.pages)==2
    writer.append_pages_from_reader(front)
    blanks=[]
    for sub in item['subjects']:
        if (len(writer.pages)+1)%2==0:
            writer.add_blank_page(*A4);blanks.append(len(writer.pages))
        assert len(writer.pages)+1==sub['start_page']
        writer.append_pages_from_reader(PdfReader(W/'render-v2'/sub['html'].replace('.html','.pdf')))
        writer.add_outline_item(sub['label'],sub['start_page']-1)
    assert len(writer.pages)==item['pages']
    total=len(writer.pages)
    for i,page in enumerate(writer.pages):
        if i==0:continue
        buffer=io.BytesIO();c=canvas.Canvas(buffer,pagesize=A4);c.setFillColorRGB(.36,.42,.53);c.setFont('Helvetica',8.5);c.drawCentredString(A4[0]/2,16,f'{i+1} / {total}')
        if i+1 in blanks:
            c.setFont('Helvetica',8);c.drawCentredString(A4[0]/2,A4[1]-30,date+' | Duplex alignment page')
        c.save();buffer.seek(0);page.merge_page(PdfReader(buffer).pages[0])
    writer.add_metadata({'/Title':f'{date} 入試実戦オンラインゼミ 5科目復習教材 印刷用修正版','/Author':'','/Subject':'過去3回の印刷レイアウトに統一'})
    dest=SITE/'pdf'/f'{date}.pdf'
    with dest.open('xb') as f:writer.write(f)
    outputs.append(dest);print(dest,total,'blank pages',blanks)
