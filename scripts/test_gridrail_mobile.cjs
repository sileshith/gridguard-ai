/* Mobile visual/focus regression. Local assets only, no live GPT calls. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),checks=[];function check(n,v){assert.ok(v,n);checks.push(n);}
(async()=>{const browser=await chromium.launch({headless:true,executablePath:process.env.GRIDGUARD_BROWSER_EXECUTABLE});try{
for(const motion of ['no-preference','reduce'])for(const position of ['top','bottom']){
 const tag=motion+'/'+position,context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,reducedMotion:motion});await context.addInitScript(()=>Object.defineProperty(navigator,'clipboard',{value:{writeText:async q=>{window.__copied=q;}}}));const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 await page.route('**/*',r=>{const u=new URL(r.request().url());assert.equal(u.origin,'http://dashboard.test');const n=u.pathname==='/'?'index.html':u.pathname.slice(1);return r.fulfill({body:fs.readFileSync(path.join(root,'dashboard/dist',n)),contentType:n.endsWith('.html')?'text/html':n.endsWith('.js')?'text/javascript':n.endsWith('.css')?'text/css':n.endsWith('.svg')?'image/svg+xml':'application/json'});});
 await page.goto('http://dashboard.test/');await page.locator('#starters button').nth(3).waitFor({state:'attached'});await page.locator('.page').evaluate((e,pos)=>{e.style.scrollBehavior='auto';e.scrollTop=pos==='bottom'?e.scrollHeight:0;},position);const scroll=await page.locator('.page').evaluate(e=>e.scrollTop);
 const panel=page.locator('#gridrail-panel'),launcher=page.locator('#guide-launcher');await launcher.tap();
 check(tag+' pointer opens immediately',await panel.isVisible()&&await launcher.getAttribute('aria-expanded')==='true');
 const inside=async locator=>locator.evaluate(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&r.left>=0&&r.top>=0&&r.right<=innerWidth&&r.bottom<=innerHeight;});
 check(tag+' immediate panel box inside viewport',await inside(panel));
 check(tag+' fixed visible overlay',await panel.evaluate(e=>{const s=getComputedStyle(e);return s.position==='fixed'&&s.display!=='none'&&s.visibility==='visible'&&Number(s.opacity)>0&&s.transform==='none'&&Number(s.zIndex)>5;}));
 check(tag+' close not occluded',await page.locator('#close-guide').evaluate(e=>{const r=e.getBoundingClientRect();return e.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2));}));
 check(tag+' close fully visible',await inside(page.locator('#close-guide')));
 for(let i=0;i<4;i++)check(tag+' starter '+(i+1)+' fully visible',await inside(page.locator('#starters button').nth(i)));
 check(tag+' not-live message fully visible',await inside(page.locator('#guide-status'))&&(await page.locator('#guide-status').innerText()).includes('currently available by invitation'));
 check(tag+' no horizontal overflow',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 check(tag+' opening focuses close',await page.locator('#close-guide').evaluate(e=>e===document.activeElement));
 for(let i=0;i<6;i++)await page.keyboard.press('Tab');check(tag+' forward focus trap wraps',await page.locator('#close-guide').evaluate(e=>e===document.activeElement));
 await page.keyboard.press('Shift+Tab');check(tag+' reverse focus trap wraps',await page.locator('#request-invitation').evaluate(e=>e===document.activeElement));
 check(tag+' background inert',await page.locator('main').evaluate(e=>e.inert));
 check(tag+' no scroll needed for opening',await page.locator('.page').evaluate(e=>e.scrollTop)===scroll);
 const starter=page.locator('#starters button').first(),question=await starter.innerText();await starter.tap();await page.waitForFunction(()=>document.querySelector('#guide-status').textContent.includes('Your question has been copied'));
 check(tag+' starter copy unchanged',await page.evaluate(()=>window.__copied)===question);
 check(tag+' fallback status unchanged',(await page.locator('#guide-status').innerText()).includes('GridRail AI is currently available by invitation and is not yet publicly accessible. Your question has been copied.'));
 check(tag+' feedback remains inside viewport',await inside(page.locator('#guide-status')));
 check(tag+' panel remains bounded after copy',await inside(panel));
 check(tag+' all four starters remain visible after copy',await page.locator('#starters button').evaluateAll(a=>a.length===4&&a.every(e=>{const r=e.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight;})));
 await page.keyboard.press('Escape');check(tag+' Escape closes',await panel.isHidden());check(tag+' Escape restores launcher',await launcher.evaluate(e=>e===document.activeElement));
 await launcher.focus();await page.keyboard.press('Enter');check(tag+' keyboard open immediately visible',await panel.isVisible()&&await inside(panel));check(tag+' keyboard initial focus',await page.locator('#close-guide').evaluate(e=>e===document.activeElement));
 await page.locator('#close-guide').tap();check(tag+' close restores focus',await panel.isHidden()&&await launcher.evaluate(e=>e===document.activeElement));check(tag+' no dashboard console errors',errors.length===0);
 if(tag==='no-preference/top'){await launcher.tap();await page.screenshot({path:path.join(root,'audit/GRIDRAIL_MOBILE_VISIBLE.png')});}
 await context.close();
}
fs.writeFileSync(path.join(root,'audit/GRIDRAIL_MOBILE_VISIBILITY_CHECKS.json'),JSON.stringify({passed:checks.length,failed:0,checks,viewport:'390x844',modes:['normal motion','reduced motion'],positions:['top','bottom'],network:'offline intercepted local assets',deployed:false},null,2)+'\n');console.log(JSON.stringify({passed:checks.length,failed:0}));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exit(1)});
