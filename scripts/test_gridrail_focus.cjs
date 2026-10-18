/* Offline GridRail modal keyboard regression checks. No live GPT requests. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),checks=[];
function check(name,value){assert.ok(value,name);checks.push(name);}
(async()=>{const browser=await chromium.launch({headless:true,...(process.env.GRIDGUARD_BROWSER_EXECUTABLE?{executablePath:process.env.GRIDGUARD_BROWSER_EXECUTABLE}:{channel:'chrome'})});
try{
 for(const [label,viewport] of [['desktop',{width:1440,height:1000}],['tablet',{width:768,height:1024}],['mobile',{width:390,height:844}]]){
  const context=await browser.newContext({viewport,reducedMotion:'reduce'});
  await context.addInitScript(()=>Object.defineProperty(navigator,'clipboard',{value:{writeText:async value=>{window.__copiedQuestion=value;}}}));
  const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
  await page.route('**/*',r=>{const u=new URL(r.request().url());assert.equal(u.origin,'http://dashboard.test');const rel=u.pathname==='/'?'index.html':u.pathname.slice(1);assert(!rel.includes('..'));return r.fulfill({body:fs.readFileSync(path.join(root,'dashboard/dist',rel)),contentType:rel.endsWith('.html')?'text/html':rel.endsWith('.js')?'text/javascript':rel.endsWith('.css')?'text/css':rel.endsWith('.svg')?'image/svg+xml':'application/json'});});
  await page.goto('http://dashboard.test/');await page.locator('#starters button').nth(3).waitFor({state:'attached'});
  // An unrelated pre-existing inert state must survive the modal lifecycle.
  await page.locator('footer').evaluate(e=>e.setAttribute('inert',''));
  const launcher=page.locator('#guide-launcher');await launcher.focus();await page.keyboard.press('Enter');
  const focused=()=>page.evaluate(()=>document.activeElement===document.querySelector('#close-guide'));
  check(label+': opening focuses close',await focused());
  await page.locator('.gridrail-banner').evaluate(e=>e.decode());
  check(label+': local banner loaded',await page.locator('.gridrail-banner').evaluate(e=>e.complete&&e.naturalWidth===1800&&e.naturalHeight===600));
  check(label+': banner fits dialog',await page.locator('.gridrail-banner').evaluate(e=>{const r=e.getBoundingClientRect(),p=e.closest('[role=dialog]').getBoundingClientRect();return r.width>0&&r.left>=p.left&&r.right<=p.right;}));
  check(label+': banner preserves named heading',await page.getByRole('heading',{name:'GridRail AI',exact:true}).count()===1);
  check(label+': banner is not interactive',await page.locator('.gridrail-banner').evaluate(e=>e.tabIndex===-1&&!e.closest('a')));
  check(label+': title readable',await page.locator('#gridrail-title').evaluate(e=>parseFloat(getComputedStyle(e).fontSize)>=23));
  check(label+': subtitle readable',await page.locator('.gridrail-brand-text p').evaluate(e=>parseFloat(getComputedStyle(e).fontSize)>=12&&e.textContent==='Project guide for GridGuard AI'));
  check(label+': banner aspect ratio 3 to 1',await page.locator('.gridrail-brand').evaluate(e=>{const r=e.getBoundingClientRect();return Math.abs(r.width/r.height-3)<0.02;}));
  check(label+': image has nonrepeating alternative',await page.locator('.gridrail-banner').getAttribute('alt')==='Abstract network with a highlighted screening path');

  check(label+': dialog name and modal semantics',await page.getByRole('dialog',{name:'GridRail AI',exact:true}).getAttribute('aria-modal')==='true');
  check(label+': background and launcher inert',await page.evaluate(()=>document.querySelector('main').inert&&document.querySelector('header').inert&&document.querySelector('#guide-launcher').inert));
  await page.locator('[data-size="small"]').evaluate(e=>e.focus());
  check(label+': background programmatic focus blocked',await focused());
  // Fallback containment even if a host does not honor inert.
  await page.locator('main').evaluate(e=>e.removeAttribute('inert'));
  await page.locator('[data-size="small"]').evaluate(e=>e.focus());
  check(label+': focusin guard blocks background focus',await focused());
  await page.locator('main').evaluate(e=>e.setAttribute('inert',''));
  const expected=['#close-guide','#starters li:nth-child(1) button','#starters li:nth-child(2) button','#starters li:nth-child(3) button','#starters li:nth-child(4) button','#request-invitation'];
  for(let cycle=0;cycle<2;cycle++){
   for(let i=1;i<=expected.length;i++){
    await page.keyboard.press('Tab');const selector=expected[i%expected.length];
    check(label+': forward cycle '+cycle+' position '+i,await page.locator(selector).evaluate(e=>e===document.activeElement));
    check(label+': visible focus '+cycle+' position '+i,await page.locator(selector).evaluate(e=>{const s=getComputedStyle(e);return parseFloat(s.outlineWidth)>=3&&s.outlineStyle!=='none'&&s.outlineColor!=='transparent';}));
   }
  }
  await page.keyboard.press('Shift+Tab');check(label+': reverse wraps first to last',await page.locator(expected[expected.length-1]).evaluate(e=>e===document.activeElement));
  for(let i=expected.length-2;i>=0;i--){await page.keyboard.press('Shift+Tab');check(label+': reverse order '+i,await page.locator(expected[i]).evaluate(e=>e===document.activeElement));}
  await page.locator('#request-invitation').focus();
  check(label+': invitation CTA keyboard reachable',await page.locator('#request-invitation').evaluate(e=>e===document.activeElement));
  check(label+': invitation CTA accessible label',await page.getByRole('link',{name:'Request an invitation to GridRail AI',exact:true}).count()===1);
  check(label+': exact public form destination',await page.locator('#request-invitation').getAttribute('href')==='https://docs.google.com/forms/d/e/1FAIpQLSddC199Z7tKwWrrFcPfUeZEiMqhM-7-hKzAlmLFpLpcesjSRA/viewform');
  check(label+': isolated new tab',await page.locator('#request-invitation').getAttribute('target')==='_blank'&&await page.locator('#request-invitation').getAttribute('rel')==='noopener noreferrer');
  check(label+': request does not guarantee access',(await page.locator('#invitation-status').innerText()).includes('Submitting a request does not guarantee access.'));
  const invitationUrl=await page.locator('#request-invitation').getAttribute('href');
  await context.route(invitationUrl,r=>r.fulfill({body:'<title>Intercepted public invitation form</title>',contentType:'text/html'}));
  const popupReady=page.waitForEvent('popup');await page.keyboard.press('Enter');const invitationPopup=await popupReady;await invitationPopup.waitForLoadState();
  check(label+': CTA opens approved form in a new tab',invitationPopup.url()===invitationUrl);
  check(label+': new tab has no opener',await invitationPopup.evaluate(()=>window.opener===null));
  await invitationPopup.close();

  check(label+': invitation heading visible',await page.getByRole('heading',{name:'Interested in trying GridRail AI?'}).isVisible());
  check(label+': accurate private workspace note',(await page.locator('#gridrail-panel').innerText()).includes('GridRail AI has completed core manual validation in a private ASU workspace and is not yet publicly accessible.'));
  check(label+': no obsolete availability copy',! /not live yet|coming soon|being prepared for public access/i.test(await page.locator('#gridrail-panel').innerText()));
  await page.locator('#close-guide').focus();
  // Hidden/disabled controls must not enter the trap.
  await page.locator('#starters button').nth(0).evaluate(e=>e.disabled=true);
  await page.keyboard.press('Tab');check(label+': disabled controls skipped',await page.locator('#starters button').nth(1).evaluate(e=>e===document.activeElement));
  await page.locator('#starters button').nth(0).evaluate(e=>e.disabled=false);
  const question=await page.locator('#starters button').first().innerText();await page.locator('#starters button').first().focus();await page.keyboard.press('Enter');
  await page.waitForFunction(()=>document.querySelector('#guide-status').textContent.includes('Your question has been copied'));
  check(label+': starter activation and unavailable status preserved',await page.evaluate(()=>window.__copiedQuestion)===question&&(await page.locator('#guide-status').innerText()).includes('GridRail AI is currently available by invitation'));
  check(label+': no live GPT link',await page.locator('#gpt-link').isHidden());
  await page.evaluate(()=>navigator.clipboard.writeText=async()=>{throw Error('synthetic denial');});await page.locator('#starters button').first().click();
  await page.locator('#copy-fallback').waitFor({state:'visible'});
  check(label+': clipboard denial exposes focused manual-copy control',await page.locator('#copy-fallback').evaluate(e=>e===document.activeElement)&&await page.locator('#copy-fallback').inputValue()===question);
  await page.keyboard.press('Tab');check(label+': manual-copy reaches invitation CTA',await page.locator('#request-invitation').evaluate(e=>e===document.activeElement));
  await page.keyboard.press('Tab');check(label+': dynamic manual-copy control wraps to close',await focused());
  await page.keyboard.press('Shift+Tab');await page.keyboard.press('Shift+Tab');check(label+': reverse includes visible manual-copy control',await page.locator('#copy-fallback').evaluate(e=>e===document.activeElement));
  // A configured legitimate link also joins DOM-order navigation, without contacting it.
  await page.locator('#gpt-link').evaluate(e=>{e.href='https://chatgpt.com/g/g-test-fixture';e.hidden=false;});
  await page.keyboard.press('Tab');check(label+': legitimate link joins dynamic cycle',await page.locator('#gpt-link').evaluate(e=>e===document.activeElement));
  await page.keyboard.press('Tab');check(label+': configured link reaches invitation CTA',await page.locator('#request-invitation').evaluate(e=>e===document.activeElement));await page.keyboard.press('Tab');check(label+': configured link wraps to close',await focused());
  await page.keyboard.press('Escape');
  check(label+': Escape closes dialog',await page.locator('#gridrail-panel').isHidden());
  check(label+': Escape returns focus to launcher',await launcher.evaluate(e=>e===document.activeElement));
  check(label+': background restored without clearing prior inert',await page.evaluate(()=>!document.querySelector('main').inert&&!document.querySelector('header').inert&&!document.querySelector('#guide-launcher').inert&&document.querySelector('footer').inert));
  await page.keyboard.press('Enter');await page.locator('#close-guide').click();
  check(label+': pointer close restores launcher',await page.locator('#gridrail-panel').isHidden()&&await launcher.evaluate(e=>e===document.activeElement));
  await page.keyboard.press('Enter');await page.keyboard.press('Enter');
  check(label+': keyboard close restores launcher',await page.locator('#gridrail-panel').isHidden()&&await launcher.evaluate(e=>e===document.activeElement));
  check(label+': no console or runtime errors',errors.length===0);
  await context.close();
 }
 const result={passed:checks.length,failed:0,checks,viewports:['1440x1000','768x1024','390x844'],network:'Local assets intercepted, no live GPT or deployment',clipboard:'Mocked success and denial',deployed:false};
 fs.writeFileSync(path.join(root,'audit/GRIDRAIL_FOCUS_CHECKS.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({passed:checks.length,failed:0}));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exit(1)});
