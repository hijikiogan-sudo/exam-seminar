#!/usr/bin/env python3
"""Build reviewed lessons into self-contained HTML. Standard library only."""
from pathlib import Path
from html.parser import HTMLParser
from html import escape
import argparse, hashlib, json, re, shutil

ROOT=Path(__file__).resolve().parents[1]
SUBJECTS={'japanese':'国語','english':'英語','social':'社会','math':'数学','science':'理科'}
FILES=['japanese.html','english.html','social.html','math-summary.html','math-practice.html','science.html']
TONES={'japanese':'#245c94','english':'#416c42','social':'#a65324','math':'#4b55a0','science':'#217677'}

class ContentCheck(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True); self.ids=set(); self.details=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag in {'script','iframe','object','embed','form','input','link','style','base','meta','video','audio'}:raise ValueError(f'教材内の許可されないタグ: {tag}')
  for k,v in attrs:
   if k.lower().startswith('on') or k in {'src','srcset','action','formaction','style'}:raise ValueError(f'教材内の許可されない属性: {k}')
   if k in {'href','xlink:href'} and not (v or '').startswith('#'):raise ValueError('教材内は文書内リンクのみ使用できます')
   if v and ('javascript:' in v.lower() or ('url(' in v.lower() and not re.fullmatch(r'url\(#[\w-]+\)',v))):raise ValueError('実行・外部参照属性を拒否')
  if 'id' in a:
   if a['id'] in self.ids:raise ValueError('重複ID: '+a['id'])
   self.ids.add(a['id'])
  if tag=='details':self.details+=1

def read_session(folder,metadata=None):
 meta=metadata if metadata is not None else json.loads((folder/'session.json').read_text())
 if meta['status']!='reviewed':raise ValueError(f'{folder.name}: 公開確認が未完了です')
 if meta['date']!=folder.name or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',meta['date']):raise ValueError('日付不一致')
 from datetime import date
 date.fromisoformat(meta['date'])
 if set(meta['themes'])!=set(SUBJECTS):raise ValueError('5教科のテーマが必要です')
 review=meta.get('review',{})
 if not all(review.get(k) is True for k in ('privacy','content','math_variants_distinct')):raise ValueError('公開前確認が未完了')
 parts={}
 for name in FILES:
  data=(folder/name).read_text()
  if hashlib.sha256(data.encode()).hexdigest()!=review.get('sha256',{}).get(name):raise ValueError(f'{folder.name}/{name}: 確認後に変更されています。再確認してください')
  if len(data)<250 or any(x in data for x in ('TODO','ここに記入','未入力')):raise ValueError('空または未完成の教材')
  if re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|(?:0[789]0)[- ]?\d{4}[- ]?\d{4}|受験番号|生徒氏名|偏差値\s*[:：]?\s*\d|得点\s*[:：]?\s*\d|/Users/',data):raise ValueError('個人情報候補を検出。公開原稿を確認してください')
  check=ContentCheck();check.feed(data)
  if check.details==0:raise ValueError(name+': 開閉式の確認問題がありません')
  parts[name]=data
 if re.sub(r'\s+','',parts['math-summary.html'])==re.sub(r'\s+','',parts['math-practice.html']):raise ValueError('数学2版の本文が同一です')
 return meta,parts

def document(title,body,css,js,date=''):
 return '<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="referrer" content="no-referrer"><meta name="description" content="入試実戦オンラインゼミの5教科復習ノート"><title>'+escape(title)+'</title><style>'+css+'</style></head><body data-date="'+escape(date)+'"><a class="skip-link" href="#main">本文へ</a>'+body+'<script>'+js+'</script></body></html>'

def brand(home):
 return '<header class="site-header"><div class="shell"><a class="brand" href="'+home+'"><span class="brand-mark" aria-hidden="true">学</span><span>入試実戦オンラインゼミ</span></a></div></header>'

def footer():return '<footer class="site-footer"><div class="shell">自分の言葉で説明できるまで、少しずつ。<br>講義をもとに整理した復習資料です。確認できない条件は本文中に注記しています。</div></footer>'

def build(out):
 if out.exists():raise ValueError(f'出力先が既にあります。上書きせず、新しい --output-dir を指定してください: {out}')
 sessions=[read_session(p) for p in sorted((ROOT/'content').iterdir()) if p.is_dir()]
 if not sessions:raise ValueError('公開する回がありません')
 css=(ROOT/'assets/site.css').read_text();js=(ROOT/'assets/site.js').read_text()
 out.mkdir(parents=True);(out/'sessions').mkdir();(out/'pdf').mkdir();(out/'downloads').mkdir()
 home=brand('./')+'<main class="shell" id="main"><section class="intro"><div><h1>今日の復習を、<br>ここから。</h1><p>授業の日付を選んで、5教科をひとつずつ。<br>要点を読み、確認問題を自分で解いてみよう。</p></div><div class="subject-spines" aria-hidden="true">'+''.join('<span class="spine">'+n+'</span>' for n in SUBJECTS.values())+'</div></section><div class="section-heading"><h2>授業の記録</h2><span class="small" data-count>'+str(len(sessions))+'回</span></div><label class="search"><span>単元を探す</span><input data-search type="search" placeholder="例：不定詞、イオン、面積比"></label><ul class="session-list">'
 for meta,parts in reversed(sessions):
  d=meta['date'];shown=d.replace('-','/');themes=meta['themes']
  topics='<dl class="topics">'+''.join('<div><dt>'+name+'</dt><dd>'+escape(themes[key])+'</dd></div>' for key,name in SUBJECTS.items())+'</dl>'
  home+='<li class="session-item" data-session><time datetime="'+d+'">'+shown+'<br><span class="weekday">土曜日の授業</span></time>'+topics+'<a class="button" href="sessions/'+d+'.html">復習を開く</a></li>'
  print_basis=meta.get('print_basis','既存の復習資料から移行したサイト版です。元動画は今回再確認していません。')
  body=brand('../')+'<main class="shell" id="main"><nav class="breadcrumb" aria-label="現在位置"><a href="../">授業の記録</a> / '+shown+'</nav><header class="session-header"><h1>'+shown+' の復習ノート</h1><p>教科を選んで復習しよう。数学は要点と実践の2つに分かれています。</p><div class="tools"><a class="button" href="../pdf/'+d+'.pdf">印刷用PDFを開く</a><button type="button" class="button secondary" data-print>このページを印刷</button><a class="button secondary" href="../downloads/'+d+'.zip">まとめて保存</a></div></header><section class="print-cover"><p>入試実戦オンラインゼミ</p><h1>'+shown+'<br>5教科 復習ノート</h1><h2>この回の内容</h2><ul>'+''.join('<li>'+name+'：'+escape(themes[key])+'</li>' for key,name in SUBJECTS.items())+'</ul><p>数学は「要点整理」「実践問題詳細」をそれぞれ収録。<br>確認問題は解答も掲載しています。</p><p class="notice">A4縦・カラー・両面（長辺とじ）向け。<br>'+escape(print_basis)+'</p></section><nav class="subject-nav" aria-label="教科を選ぶ">'
  for key,name in SUBJECTS.items():body+='<a href="#'+key+'" data-subject-link="'+key+'" style="--tone:'+TONES[key]+'">'+name+'</a>'
  body+='</nav>'
  for key,name in SUBJECTS.items():
   body+='<section class="subject-panel" data-subject="'+key+'" style="--accent:'+TONES[key]+'"><header class="subject-heading"><h2>'+name+'</h2><p>'+escape(themes[key])+'</p></header>'
   if key=='math':
    body+='<nav class="variant-nav" aria-label="数学の教材を選ぶ"><a href="#math/summary" data-variant-link="summary">要点整理</a><a href="#math/practice" data-variant-link="practice">実践問題詳細</a></nav>'
    for variant,label in [('summary','要点整理'),('practice','実践問題詳細')]:body+='<section class="variant-panel" data-variant="'+variant+'"><h3 class="variant-title">数学 '+label+'</h3><div class="print-subject-label">数学 '+label+'</div><div class="lesson">'+parts['math-'+variant+'.html']+'</div></section>'
   else:body+='<div class="print-subject-label">'+name+'</div><div class="lesson">'+parts[key+'.html']+'</div>'
   body+='</section>'
  body+='<aside class="source-note">'+escape(meta['review']['basis'])+'<br>'+escape(meta.get('source_note','講義そのものの転載ではなく、既存の復習資料をまとめたノートです。'))+'</aside></main>'+footer()
  (out/'sessions'/f'{d}.html').write_text(document(d+' 入試実戦オンラインゼミ',body,css,js,d))
 home+='</ul><p class="no-results" data-no-results hidden>一致する授業がありません。短い単元名でもう一度探してみよう。</p><aside class="usage"><h2>復習の進め方</h2><ol><li>要点を読んで、授業のテーマを思い出す。</li><li>確認問題を解く。答えは問題を押すと開きます。</li><li>数学は「要点整理」の後に「実践問題詳細」へ進む。</li></ol></aside></main>'+footer()
 (out/'index.html').write_text(document('入試実戦オンラインゼミ｜復習ノート',home,css,js))
 (out/'404.html').write_text(document('ページが見つかりません',brand('./')+'<main class="shell"><h1>ページが見つかりません</h1><p><a href="/exam-seminar/">授業の記録へ戻る</a></p></main>',css,''))
 (out/'.nojekyll').touch()
 (out/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
 (out/'sessions.json').write_text(json.dumps([{'date':m['date'],'themes':m['themes']} for m,_ in sessions],ensure_ascii=False,indent=2)+'\n')
 print(f'{len(sessions)}回分を生成: {out}')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,default=ROOT/'_site');a=p.parse_args();build(a.output_dir.resolve())
