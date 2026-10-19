from pathlib import Path
from lxml import html as lhtml
from html import escape
import json, hashlib, sys, os, shutil, urllib.request

ROOT=Path(__file__).resolve().parents[1]
DATE=sys.argv[1]
WORK=Path(sys.argv[2]).resolve()
WORK.mkdir(parents=True,exist_ok=True)
fonts=WORK/'fonts';fonts.mkdir(exist_ok=True)
font=fonts/'NotoSansJP.ttf'
expected='f4b373b226668ee33a6e54b02823dcd2d1209f17159f777421ae8c2275160369'
if os.environ.get('PRINT_REFERENCE_FONT'):
    shutil.copyfile(os.environ['PRINT_REFERENCE_FONT'],font)
else:
    urllib.request.urlretrieve('https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/Variable/TTF/Subset/NotoSansJP-VF.ttf',font)
if hashlib.sha256(font.read_bytes()).hexdigest()!=expected:
    raise SystemExit('日本語フォントのハッシュが一致しません')
SUBJECTS=[('japanese','国語','#813cff','#171b2e'),('english','英語','#087f80','#10242a'),('social','社会','#c96a18','#171b21'),('math-summary','数学 要点整理','#2453df','#111b31'),('math-practice','数学 実践問題詳細','#2453df','#111b31'),('science','理科','#d72e67','#231529')]
CSS='''
@font-face{font-family:Noto;src:url(fonts/NotoSansJP.ttf);font-weight:100 900}
*{box-sizing:border-box} @page{size:A4;margin:8.5mm 20mm 18mm}
body{margin:0;color:#202a3f;font:11pt/1.75 Noto,sans-serif;-webkit-print-color-adjust:exact;print-color-adjust:exact}
p{margin:10px 0;orphans:3;widows:3}strong{font-weight:700}h2,h3{break-after:avoid;line-height:1.5}h2{font-size:17.4pt;border-left:4px solid var(--accent);padding-left:10px;margin:0 0 16px}h3{font-size:13pt;margin:18px 0 9px}ul,ol{padding-left:22px}li{margin:4px 0}
.overview{break-after:page}.hero{background:linear-gradient(125deg,var(--accent),var(--dark));color:white;padding:27px 25px 25px;margin-bottom:14px}.eyebrow{font-size:9.84pt;font-weight:700;letter-spacing:1px;color:#e8e6ff}.hero h1{font-size:12pt;margin:2px 0 7px}.hero p{font-size:11.4pt;margin:5px 0 12px}.pills{display:flex;gap:7px;flex-wrap:wrap}.pill{font-size:10.56pt;background:#ffffff25;border:1px solid #ffffff55;border-radius:20px;padding:2px 10px}
.panel,.lesson>section{border:1px solid #dce1ec;border-radius:14px;padding:20px;margin:0 0 16px;background:#fff}.lesson>section{break-before:page;box-decoration-break:clone;-webkit-box-decoration-break:clone}.lead{font-size:12.6pt;line-height:1.8}.grid2,.grid3{display:grid;grid-template-columns:1fr 1fr;gap:10px}.card{border:1px solid #dce1ec;border-radius:12px;padding:12px;break-inside:avoid}.card strong{color:var(--accent)}.overview .card{font-size:10.5pt}.overview .grid2{margin-top:14px}.label{font-size:10pt;font-weight:700;color:var(--accent)}
.callout,.formula{background:var(--tint);border-left:3px solid var(--accent);border-radius:8px;padding:12px 14px;margin:14px 0;break-inside:avoid}.formula{font-size:11pt}.warn{background:#fff4d6;border-left-color:#c98d15}.good{background:#edf8f1;border-left-color:#418864}.danger{background:#fff0f0}.table-wrap{margin:14px 0}table{width:100%;border-collapse:collapse;font-size:10pt}th,td{text-align:left;vertical-align:top;border-bottom:1px solid #dce1ec;padding:9px 7px}th{background:#f5f7fb}tr{break-inside:avoid}thead{display:table-header-group}
details{border:1px solid #e0e4ef;border-radius:8px;margin:12px 0;padding:11px 13px;break-inside:avoid}summary{font-weight:700;font-size:10.5pt;color:var(--accent);list-style:none}summary::-webkit-details-marker{display:none}details p:last-child{margin-bottom:0}.diagram{border:1px solid #dde4ef;background:#f8fbfe;border-radius:8px;padding:10px;margin:14px 0;break-inside:avoid}.diagram svg{display:block;width:100%;height:auto;max-height:82mm}.step{display:flex;gap:10px}.num{color:white;background:var(--accent);border-radius:50%;min-width:24px;height:24px;text-align:center}.exam{border:1px solid var(--accent);border-radius:8px;padding:14px;margin:14px 0}.source{font-size:9pt;color:#677189;margin-top:14px}a{color:inherit;text-decoration:none}
'''

CSS+='''.lesson>section{break-before:auto;break-inside:avoid}.lesson>section>:nth-last-child(2){break-after:avoid}'''
manifest=[]
for date in [DATE]:
    src=ROOT/'content'/date
    meta=json.loads((src/'session.json').read_text())
    items=[]
    for key,label,accent,dark in SUBJECTS:
        raw=(src/(key+'.html')).read_text()
        soup=lhtml.fragment_fromstring(raw,create_parent='div')
        for detail in soup.iter('details'):detail.set('open','')
        headings=[h.text_content().strip() for h in soup.xpath('.//section/h2')]
        theme=meta['themes']['math' if key.startswith('math') else key]
        cards=''.join('<div class="card"><strong>'+escape(h)+'</strong></div>' for h in headings)
        header=f'''<div class="overview"><header class="hero"><div class="eyebrow">{date.replace('-','.')}　入試実戦オンラインゼミ</div><h1>{label}</h1><p>{escape(theme)}</p><div class="pills"><span class="pill">講義の復習ノート</span><span class="pill">{'途中式・検算・類題' if key=='math-practice' else '要点整理・確認問題'}</span><span class="pill">解答を掲載</span></div></header><section class="panel"><h2>この回の要点</h2><p class="lead">{escape(theme)}</p><div class="grid2">{cards}</div><p class="source">{escape(meta['print_basis'])}</p></section></div>'''
        name=f'{date}-{key}.html'
        html='<!doctype html><html lang="ja"><meta charset="utf-8"><title>'+label+' '+date+'</title><style>'+CSS+'</style><body style="--accent:'+accent+';--dark:'+dark+';--tint:'+accent+'0c">'+header+'<main class="lesson">'+''.join(lhtml.tostring(x,encoding='unicode') for x in soup)+'</main></body></html>'
        (WORK/name).write_text(html)
        items.append({'key':key,'label':label,'html':name,'source_sha256':hashlib.sha256(raw.encode()).hexdigest()})
    manifest.append({'date':date,'subjects':items})
(WORK/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('印刷用HTMLを作成:',DATE)
