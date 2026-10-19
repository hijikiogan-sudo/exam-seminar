const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const {chromium}=require('playwright');
(async()=>{
 const root=path.resolve(process.argv[2]||'_site');
 const shots=process.env.SCREENSHOT_DIR;
 if(shots)fs.mkdirSync(shots,{recursive:true});
 const sessions=JSON.parse(fs.readFileSync(path.join(root,'sessions.json'),'utf8'));
 const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{})});
 try{
  for(const width of [375,768,1440]){
   const page=await browser.newPage({viewport:{width,height:1000}});
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(pathToFileURL(path.join(root,'index.html')).href);
   assert.equal(await page.locator('[data-session]').count(),sessions.length);
   await page.locator('[data-search]').fill('面積比');
   assert.equal(await page.locator('[data-session]:visible').count(),1);
   await page.locator('[data-search]').fill('該当しない語句12345');
   assert.equal(await page.locator('[data-no-results]').isVisible(),true);
   await page.locator('[data-search]').fill('');
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'ホーム画面の横はみ出し');
   if(shots)await page.screenshot({path:path.join(shots,`home-${width}.png`),fullPage:true});
   for(const {date} of sessions){
    await page.goto(pathToFileURL(path.join(root,'sessions',date+'.html')).href);
    const ids=await page.locator('[id]').evaluateAll(xs=>xs.map(x=>x.id));
    assert.equal(new Set(ids).size,ids.length,'重複ID');
    for(const key of ['japanese','english','social','math','science']){
     await page.locator(`[data-subject-link="${key}"]`).click();
     await page.waitForFunction(k=>document.querySelector(`[data-subject="${k}"]`).hidden===false,key);
     assert.equal(await page.locator('[data-subject]:visible').count(),1);
     assert.equal(await page.locator(`[data-subject-link="${key}"]`).getAttribute('aria-current'),'true');
     assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,`${date}/${key}/${width}: 横はみ出し`);
     const detail=page.locator(`[data-subject="${key}"] details:visible`).first();
     await detail.locator('summary').click();assert.equal(await detail.getAttribute('open'),'');
     await detail.locator('summary').click();assert.equal(await detail.getAttribute('open'),null);
    }
    await page.locator('[data-subject-link="math"]').click();
    const summary=await page.locator('[data-variant="summary"]').textContent();
    await page.locator('[data-variant-link="practice"]').click();
    await page.waitForFunction(()=>!document.querySelector('[data-variant="practice"]').hidden);
    assert.equal(await page.locator('[data-variant="summary"]').isVisible(),false);
    assert.notEqual(await page.locator('[data-variant="practice"]').textContent(),summary);
    if(shots&&date==='2026-09-19')await page.screenshot({path:path.join(shots,`math-${width}.png`),fullPage:true});
    await page.reload();assert.equal(await page.locator('[data-variant="practice"]').isVisible(),true,'再読込時の選択復元');
    await page.evaluate(()=>dispatchEvent(new Event('beforeprint')));
    assert.equal(await page.locator('details:not([open])').count(),0);
    assert.equal(await page.locator('[data-subject][hidden]').count(),0);
    await page.evaluate(()=>dispatchEvent(new Event('afterprint')));
    for(const ext of ['pdf','zip']){
     const file=path.join(root,ext==='pdf'?'pdf':'downloads',date+'.'+ext);
     assert.ok(fs.statSync(file).size>1000,file+'が空です');
     if(ext==='pdf')assert.equal(fs.readFileSync(file).subarray(0,4).toString(),'%PDF');
    }
   }
   assert.deepEqual(errors,[]);await page.close();
   console.log(`画面・教科切替・数学2版・確認問題・リンク検証: ${width}px OK`);
  }
  const noJS=await browser.newPage({javaScriptEnabled:false});
  await noJS.goto(pathToFileURL(path.join(root,'sessions',sessions[0].date+'.html')).href);
  assert.equal(await noJS.locator('[data-subject]:visible').count(),5);
  console.log('JavaScript無効時の5教科閲覧: OK');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
