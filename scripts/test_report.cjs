/* Offline exported-report navigation/render checks. Never contacts remote services. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const root=path.resolve(__dirname,'..'),checks=[];
fs.copyFileSync(path.join(root,'reports/GridGuard_AI_Flagship_Report.html'),path.join(root,'dashboard/dist/report.html'));
function check(name,value){assert.ok(value,name);checks.push(name);}
(async()=>{
 console.log('Launching report browser');
 const browser=await chromium.launch({headless:true,...(process.env.GRIDGUARD_BROWSER_EXECUTABLE?{executablePath:process.env.GRIDGUARD_BROWSER_EXECUTABLE}:{channel:'chrome'})});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'}),errors=[],outbound=[];
  page.on('pageerror',e=>errors.push(e.message));await page.route('**/*',r=>{if(r.request().url().startsWith('http://127.0.0.1:8765/'))return r.continue();outbound.push(r.request().url());return r.abort();});
  console.log('Loading report');await page.goto('http://127.0.0.1:8765/report.html',{timeout:15000});
  console.log('Report loaded');await page.addStyleTag({content:'html{scroll-behavior:auto!important}'});check('cover author/date/affiliation visible',(await page.textContent('body')).includes('Sileshi T. Hirpa')&&(await page.textContent('body')).includes('October 2026')&&(await page.textContent('body')).includes('Arizona State University'));
  check('embedded images load from self-contained sources',await page.locator('img').evaluateAll(a=>a.length>=12&&a.every(i=>i.src.startsWith('data:image/')&&i.complete&&i.naturalWidth>0)));
  check('desktop document has no horizontal overflow',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  const notebook=JSON.parse(fs.readFileSync(path.join(root,'notebooks/00_gridguard_ai_flagship_report.ipynb')));
  for(const id of notebook.metadata.gridguard.main_anchors){console.log('Checking',id);
   await page.locator(`a[href="#${id}"]`).first().evaluate(a=>a.click());await page.waitForFunction(id=>location.hash==='#'+id,id,{timeout:5000});
   check('TOC reaches '+id,await page.locator('#'+id).count()===1);
  }
  await page.locator('a[href="#fresh-dataproc"]').first().evaluate(a=>a.click());await page.waitForFunction(()=>location.hash==='#fresh-dataproc');
  check('fresh Dataproc subsection navigation works',await page.locator('#fresh-dataproc').count()===1);
  if(process.env.REPORT_SCREENSHOTS)await page.screenshot({path:path.join(process.env.REPORT_SCREENSHOTS,'report-fresh-dataproc.png')});
  check('one Back to Top per main section',await page.locator('a[href="#top"]').count()===notebook.metadata.gridguard.main_anchors.length);
  await page.locator('a[href="#top"]').last().evaluate(a=>a.click());await page.waitForFunction(()=>location.hash==='#top');
  check('Back to Top reaches cover',await page.evaluate(()=>scrollY<30));
  if(process.env.REPORT_SCREENSHOTS)await page.screenshot({path:path.join(process.env.REPORT_SCREENSHOTS,'report-cover.png')});
  await page.locator('a[href="#executive-summary"]').first().evaluate(a=>a.click());
  if(process.env.REPORT_SCREENSHOTS)await page.screenshot({path:path.join(process.env.REPORT_SCREENSHOTS,'report-summary.png')});
  await page.setViewportSize({width:390,height:844});
  check('mobile document has no horizontal overflow',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  check('mobile images fit containing report',await page.locator('img').evaluateAll(a=>a.every(i=>i.getBoundingClientRect().width<=innerWidth)));
  check('no JavaScript page errors',errors.length===0);check('no external requests',outbound.length===0);
  const result={passed:checks.length,failed:0,checks,offline_html:true,github_render_tested:false};fs.writeFileSync(path.join(root,'audit/REPORT_BROWSER_CHECKS.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
