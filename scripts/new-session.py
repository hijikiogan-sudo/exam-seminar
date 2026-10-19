#!/usr/bin/env python3
"""Prepare a private draft. Never overwrite an existing session."""
from pathlib import Path
from datetime import date
import argparse,json
from build import FILES,SUBJECTS,ROOT
p=argparse.ArgumentParser();p.add_argument('date');a=p.parse_args();date.fromisoformat(a.date)
folder=ROOT/'private'/'drafts'/a.date;folder.mkdir(parents=True,exist_ok=False)
for file in FILES:
 (folder/file).write_text('''<section><h2>要点</h2><p>ここに記入</p></section>
<section><h2>講義整理</h2><p>ここに記入</p></section>
<section><h2>なぜそうなるか</h2><p>ここに記入</p></section>
<section><h2>入試での問われ方</h2><p>ここに記入</p></section>
<section><h2>注意点</h2><p>ここに記入</p></section>
<section><h2>確認問題</h2><details><summary>ここに記入</summary><p>ここに記入</p></details></section>
''')
meta={'date':a.date,'status':'draft','themes':dict.fromkeys(SUBJECTS,''),'review':{'privacy':False,'content':False,'math_variants_distinct':False,'basis':'','sha256':{}}}
(folder/'session.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('下書き作成:',folder)
