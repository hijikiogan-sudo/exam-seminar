#!/usr/bin/env python3
"""Create per-session offline packages from one validated build."""
from pathlib import Path
import argparse,json,zipfile
p=argparse.ArgumentParser();p.add_argument('site',type=Path,nargs='?',default=Path('_site'));a=p.parse_args()
for item in json.loads((a.site/'sessions.json').read_text()):
 date=item['date'];dest=a.site/'downloads'/f'{date}.zip'
 with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED) as z:
  import re
  page=(a.site/'sessions'/f'{date}.html').read_text()
  page=re.sub(r'<a class="button secondary" href="../downloads/[^\"]+">まとめて保存</a>','',page)
  z.writestr(f'sessions/{date}.html',page)
  z.write(a.site/'pdf'/f'{date}.pdf',f'pdf/{date}.pdf')
  z.writestr('index.html',f'<!doctype html><html lang="ja"><meta charset="utf-8"><title>{date} 復習教材</title><h1>{date} 復習教材</h1><p><a href="sessions/{date}.html">5教科まとめを開く</a></p><p><a href="pdf/{date}.pdf">印刷用PDFを開く</a></p></html>')
  src=Path(__file__).resolve().parents[1]/'content'/date
  for s in src.glob('*.html'):
   # Standalone subject HTML uses the same CSS, with all content visible.
   from build import document,ROOT
   css=(ROOT/'assets/site.css').read_text()
   from build import SUBJECTS
   label={'math-summary':'数学 要点整理','math-practice':'数学 実践問題詳細'}.get(s.stem,SUBJECTS.get(s.stem,s.stem))
   html=document(f'{date} {label}',f'<main class="shell"><h1>{date} {label}</h1><div class="lesson">{s.read_text()}</div></main>',css,'')
   z.writestr('科目別/'+s.name,html)
 print('ZIP生成:',date)
