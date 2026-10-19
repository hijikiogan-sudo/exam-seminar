#!/usr/bin/env python3
"""Freeze reviewed source hashes; requires explicit review declarations."""
from pathlib import Path
import argparse,hashlib,json,shutil
from build import FILES,ROOT,read_session
p=argparse.ArgumentParser();p.add_argument('folder',type=Path)
p.add_argument('--confirm-content',action='store_true',required=True)
p.add_argument('--confirm-privacy',action='store_true',required=True)
p.add_argument('--confirm-math-variants',action='store_true',required=True)
a=p.parse_args();src=a.folder.resolve();meta=json.loads((src/'session.json').read_text());dest=ROOT/'content'/meta['date']
if dest.exists():raise SystemExit('公開原稿が既にあります。既存回の変更は差分提示と上書き確認後に行ってください。')
meta['status']='reviewed';meta['review'].update(privacy=True,content=True,math_variants_distinct=True)
meta['review']['sha256']={f:hashlib.sha256((src/f).read_bytes()).hexdigest() for f in FILES}
if not meta['review'].get('basis'):raise SystemExit('出典・判別できなかった点をreview.basisに記録してください。')
read_session(src,meta)
dest.mkdir(parents=True)
for f in FILES:shutil.copyfile(src/f,dest/f)
(dest/'session.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
read_session(dest)
print('確認済み原稿を登録:',dest)
