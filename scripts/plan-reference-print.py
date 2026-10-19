from pathlib import Path
import json,sys
from pypdf import PdfReader
W=Path(sys.argv[1]).resolve()
manifest=json.loads((W/'manifest.json').read_text())
for item in manifest:
    position=3
    for sub in item['subjects']:
        if position%2==0:position+=1
        sub['start_page']=position
        sub['pages']=len(PdfReader(W/'render-v2'/sub['html'].replace('.html','.pdf')).pages)
        position+=sub['pages']
    item['pages']=position-1
    date=item['date']; shown='/'.join(str(int(x)) for x in date.split('-'))
    rows=''.join(f'<tr><td>{s["label"]}</td><td>{s["start_page"]}</td></tr>' for s in item['subjects'])
    html=f'''<!doctype html><html lang="ja"><meta charset="utf-8"><title>{date} 印刷用</title><style>
    @font-face{{font-family:Noto;src:url(fonts/NotoSansJP.ttf);font-weight:100 900}}
    @page{{size:A4;margin:0}}*{{box-sizing:border-box}}body{{margin:0;font-family:Noto,sans-serif;color:#202a3f;-webkit-print-color-adjust:exact;print-color-adjust:exact}}.page{{width:210mm;height:297mm;break-after:page;position:relative}}.cover{{background:linear-gradient(135deg,#1b3d72,#176483);color:white;padding:103mm 20mm 0}}.brand{{font-size:12pt;font-weight:700;letter-spacing:1px;color:#d7e5f2}}.line{{height:4px;width:32mm;background:white;border-radius:2px;margin:10mm 0 13mm}}h1{{font-size:31pt;line-height:1.22;margin:0}}.date{{font-size:18pt;font-weight:700;margin:4mm 0 9mm}}.description{{font-size:12pt;line-height:1.7}}.toc{{padding:24mm 20mm}}h2{{font-size:23pt;color:#1a4274;margin:0 0 8mm}}table{{width:100%;border-collapse:collapse;font-size:12pt}}td{{padding:5mm 3mm;border-bottom:1px solid #d7e2ee}}td:last-child{{text-align:right;color:#1a4274;font-weight:700}}.note{{margin-top:10mm;padding:5mm 6mm;border-radius:13px;background:#f1f5fa;font-size:10.5pt;line-height:1.8}}.print-settings{{position:absolute;bottom:14mm;left:20mm;color:#758096;font-size:9pt}}
    </style><body><section class="page cover"><div class="brand">能開センター 2026｜入試実戦オンラインゼミ</div><div class="line"></div><h1>5科目 復習教材<br>印刷用</h1><p class="date">{shown}</p><p class="description">A4縦・カラー・両面・長辺とじ向け<br>数学は「要点整理版」と「実践問題詳細版」を別内容で収録</p></section><section class="page toc"><h2>目次</h2><table>{rows}</table><div class="note"><strong>おすすめ：</strong>各科目の要点を確認し、数学は「要点整理」で考え方を整理してから「実践問題詳細」で途中式・検算・失点ポイントまで確認してください。各科目は両面印刷時に原則として表面（右ページ）から始まるよう調整しています。</div><div class="print-settings">印刷設定：A4 / カラー / 両面 / 長辺とじ / 実際のサイズ（100%）推奨</div></section></body></html>'''
    (W/f'{date}-front.html').write_text(html)
    print(date,item['pages'],[(s['label'],s['start_page'],s['pages']) for s in item['subjects']])
(W/'layout-plan.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
