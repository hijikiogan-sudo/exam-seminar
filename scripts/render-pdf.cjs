const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require('playwright');
const referenceDates = require('../assets/print-layouts.json')['reference-v1'];
const renderReference = require('./render-reference-print.cjs');

(async () => {
  const root = path.resolve(process.argv[2] || '_site');
  const sessions = JSON.parse(fs.readFileSync(path.join(root,'sessions.json'),'utf8'));
  for (const {date} of sessions) if (fs.existsSync(path.join(root,'pdf',date+'.pdf'))) throw new Error('PDFが既にあります。新しいビルド先を使用してください。');
  const browser = await chromium.launch({headless:true, ...(process.env.CHROMIUM_PATH ? {executablePath:process.env.CHROMIUM_PATH} : {})});
  try {
    for (const {date} of sessions) {
      if(referenceDates.includes(date)){
        await renderReference(browser,root,date);
        console.log('PDF生成（承認済み統一レイアウト）:',date);
        continue;
      }
      const page = await browser.newPage();
      await page.goto(pathToFileURL(path.join(root,'sessions',date+'.html')).href);
      await page.evaluate(() => { document.querySelectorAll('[hidden]').forEach(x=>x.hidden=false); document.querySelectorAll('details').forEach(x=>x.open=true); });
      await page.emulateMedia({media:'print'});
      await page.pdf({path:path.join(root,'pdf',date+'.pdf'),format:'A4',printBackground:true,preferCSSPageSize:true,displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="font-size:8px;width:100%;text-align:center;color:#52647a"><span class="pageNumber"></span> / <span class="totalPages"></span></div>',tagged:true});
      console.log('PDF生成:',date);
      await page.close();
    }
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exit(1);});
