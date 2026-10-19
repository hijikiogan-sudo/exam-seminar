// Generate the approved print layout from the same reviewed lesson fragments.
const fs=require('node:fs');
const path=require('node:path');
const os=require('node:os');
const {execFileSync}=require('node:child_process');
const {pathToFileURL}=require('node:url');

module.exports=async function renderReference(browser,root,date){
  const work=fs.mkdtempSync(path.join(os.tmpdir(),'exam-reference-print-'));
  const python=process.env.PRINT_PYTHON||'python3';
  const run=(script,args)=>execFileSync(python,[path.join(__dirname,script),...args],{stdio:'inherit'});
  run('prepare-reference-print.py',[date,work]);
  const manifest=JSON.parse(fs.readFileSync(path.join(work,'manifest.json'),'utf8'));
  const rendered=path.join(work,'render-v2');fs.mkdirSync(rendered);
  for(const sub of manifest[0].subjects){
    const p=await browser.newPage();
    try{
      await p.goto(pathToFileURL(path.join(work,sub.html)).href);
      await p.evaluate(()=>document.fonts.ready);
      await p.pdf({path:path.join(rendered,sub.html.replace('.html','.pdf')),format:'A4',preferCSSPageSize:true,printBackground:true,tagged:true});
    }finally{await p.close()}
  }
  run('plan-reference-print.py',[work]);
  const front=await browser.newPage();
  try{
    await front.goto(pathToFileURL(path.join(work,date+'-front.html')).href);
    await front.evaluate(()=>document.fonts.ready);
    await front.pdf({path:path.join(rendered,date+'-front.pdf'),preferCSSPageSize:true,printBackground:true,tagged:true});
  }finally{await front.close()}
  run('assemble-reference-print.py',[work,root]);
};
