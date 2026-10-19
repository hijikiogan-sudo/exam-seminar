# 入試実戦オンラインゼミ 復習サイト

子どもが別端末から開く、閲覧専用の5教科ノートです。GitHubをサイトの正本とし、GitHub ActionsがHTML・印刷PDF・ZIPを生成してGitHub Pagesへ公開します。Macを起動しておく必要はありません。

- 公開URL：<https://hijikiogan-sudo.github.io/exam-seminar/>
- 各回：`sessions/YYYY-MM-DD.html`。国語・英語・社会・数学・理科を切り替えます。
- 数学：要点整理／実践問題詳細の2種類。中身が同一ならビルドを止めます。
- HTMLにはCSS・JavaScript・全教科を内包。確認問題は開閉式。JavaScript無効時も全教科を読めます。
- PDF：同じHTMLからA4縦・カラー・長辺とじ向けに生成。解答も表示します。
- Google Driveは動画・完成教材の保管先、Notionは単元と保存先の索引として維持します。

## クラウドの役割

| 保存先 | 役割 |
| --- | --- |
| Google Drive | 元動画、科目別HTML、5教科HTML、PDF、ZIPの保管 |
| GitHub `main` | 公開確認済みの教材・UI・更新手順の正本 |
| GitHub Actions | 検証、PDF・ZIP生成、公開。実行履歴と生成物を保存 |
| GitHub Pages | 子どもがブックマークする閲覧サイト |
| Notion | 日付・各教科の単元・Drive保存先・サイトへの索引 |
| ローカル | 一時的な制作・確認。公開継続のための常駐は不要 |

動画解析とDrive・Notionの更新にはCodexの接続を使います。このリポジトリへAPIキーやトークンを保存しません。Actionsは動画を解析せず、DriveやNotionへ自動で接続しません。新しい教材の登録後、サイト生成・検証・公開が自動で動きます。

## 初期収録

2026-09-19、2026-09-26、2026-10-03の既存復習HTMLを移行しています。数学の通常版を要点整理、改訂版を実践問題詳細に対応させています。元動画は今回再解析していません。条件が不鮮明な箇所の注記を残しています。サイト移行時の明確な修正は[移行記録](docs/MIGRATION.md)を参照してください。

## フォルダ

```text
content/YYYY-MM-DD/
  session.json              # 日付、5教科の単元、確認済み本文のSHA-256
  japanese.html
  english.html
  social.html
  math-summary.html
  math-practice.html
  science.html
assets/                     # 全ページ共通の見た目・操作
scripts/                    # 作成・確認・ビルド・PDF・ZIP・UI検証
templates/                  # 分析と公開の作業指示
docs/                       # 運用手順、移行記録
.github/workflows/pages.yml # クラウド公開
private/                    # 下書き、元動画情報、私的な保存先。Git除外
_site/                      # 生成物。Git除外、Pages公開対象
```

## 今後の1回分の作業

1. 動画を既存Google Driveの対象日フォルダへアップロードする。
2. Codexに日付と動画を渡し、[次回依頼テンプレート](templates/NEXT_SESSION.md)の内容を依頼する。
3. 5教科を解析し、科目別6ファイル（数学2種）を作成する。根拠・不明点は区別する。
4. 内容と個人情報を確認し、`content/YYYY-MM-DD/`へ登録する。
5. HTML・印刷PDF・ZIPを生成・確認する。
6. 完成物を既存Driveの日付フォルダに**新しい名前で保存し、読み戻して確認**する。
7. GitHubへコミットし、Actionsの成功と実際の公開ページ・PDFを確認する。
8. Notionの既存学習索引に、各教科のテーマ、Drive保存先、公開ページを追記する。

詳しくは[更新手順](docs/OPERATIONS.md)。既存資料の削除・上書きは、必ずユーザー確認後に行います。

## 開発・確認

Python 3.12以上、Node.js 22以上を使用します。

```bash
npm ci
npx playwright install --with-deps chromium
python3 scripts/build.py
node scripts/render-pdf.cjs
python3 scripts/package.py
node scripts/verify.cjs
python3 -m http.server 8000 --directory _site
```

日本語フォントが必要です。Ubuntuでは`fonts-noto-cjk`をインストールします。既に出力先があれば上書きを拒否するので、再確認時は`python3 scripts/build.py --output-dir _site-review2`のように新しい出力先を使い、後続コマンドにもそのディレクトリを渡します。既存のChromeを使う場合は`CHROMIUM_PATH`に実行ファイルを指定できます。

## 公開時の扱い

GitHubリポジトリとPagesは公開です。氏名、成績、答案、受験番号、連絡先、元動画、非公開Drive・NotionのURLは公開原稿やGit履歴へ入れません。検索エンジンへ登録しない設定をしていますが、アクセス制限ではありません。個人情報の自動検出は補助であり、目視確認が必要です。

完成物だけをPagesへデプロイします。公開前の本文確認、ハッシュ一致、数学2版の差異、モバイル・タブレット・PCの操作検証が通らない場合、前の公開状態を維持します。取得元の動画・教材をそのまま転載せず、復習用に整理した内容を掲載します。
