'use strict';
const byId=id=>document.getElementById(id);
const state={size:'review',budget:.2,data:null};
function safeGptUrl(value){try{const u=new URL(value);return u.protocol==='https:'&&u.hostname==='chatgpt.com'&&/^\/g\/g-[A-Za-z0-9-]+(?:\/[A-Za-z0-9-]+)?\/?$/.test(u.pathname)&&!u.port&&!u.username&&!u.password&&!u.search&&!u.hash?u.href:null;}catch{return null;}}
const fmt=value=>new Intl.NumberFormat('en-US').format(value);
function render(){
 const d=state.data[state.size];byId('run-note').textContent=d.note;
 const rows=d.screening;const risk=rows.filter(r=>r.score==='risk_score');const baseline=rows.filter(r=>r.score==='Pre_Outage_Line_Loading');
 const available=risk.map(r=>r.budget);
 if(!available.includes(state.budget))state.budget=available[available.length-1];
 byId('chart-title').textContent=available.length===1?'Fresh cloud: measured 20% review budget':'Violation capture by review budget';
 byId('local-comparisons').hidden=state.size!=='review';
 byId('model-title').textContent=state.size==='review'?'GBT versus strongest tested simple baseline':'Model comparison';
 byId('model-context').textContent=state.size==='review'?'Comparisons stay within the selected evidence source. The local audit compares GBT with the strongest tested simple baseline on the same validation rows.':'Model metrics shown here belong only to the selected evidence source.';
 const x=v=>60+v*2600;const y=v=>228-v*190;
 let svg=`<title id="chart-description">${available.length===1?'Only the 20% budget is available for this fresh run.':'Validation capture at 1%, 5%, 10%, 20% review budgets.'} Orange: GBT, slate: loading baseline. Dashed ceiling applies to the local audit.</title>`;
 for(const tick of [0,.25,.5,.75,1])svg+=`<line class="grid" x1="60" x2="610" y1="${y(tick)}" y2="${y(tick)}"/><text x="43" y="${y(tick)+4}" text-anchor="end">${tick*100}%</text>`;
 for(const b of [.01,.05,.1,.2])svg+=`<text x="${x(b)}" y="255" text-anchor="middle">${b*100}%</text>`;
 for(const [series,color] of [[baseline,'var(--slate)'],[risk,'var(--accent)']]){
  svg+=`<polyline points="${series.map(r=>`${x(r.budget)},${y(r.capture_rate)}`).join(' ')}" fill="none" stroke="${color}" stroke-width="3"/>`;
  for(const r of series)svg+=`<circle cx="${x(r.budget)}" cy="${y(r.capture_rate)}" r="${r.budget===state.budget?6:4}" fill="${color}"/>`;
 }
 if(state.size==='review'){
  svg+=`<polyline points="${risk.map(r=>`${x(r.budget)},${y(r.best_possible_realized)}`).join(' ')}" fill="none" stroke="var(--muted)" stroke-dasharray="5 5" stroke-width="2"/>`;
 }
 byId('ceiling-legend').hidden=state.size!=='review';
 byId('capture-chart').innerHTML=svg;
 if(state.size==='review')byId('comparison-rows').innerHTML=d.comparisons.filter((r,i)=>[0,1,2,3,4,6].includes(i)).map(r=>`<tr><th scope="row">${r.metric}</th><td>${r.unit==='PR-AUC'?r.baseline.toFixed(4):(r.baseline*100).toFixed(2)+'%'}</td><td>${r.unit==='PR-AUC'?r.GBT.toFixed(4):(r.GBT*100).toFixed(2)+'%'}</td><td>${r.absolute_gain>0?'+':''}${r.unit==='PR-AUC'?r.absolute_gain.toFixed(4):(r.absolute_gain*100).toFixed(2)+' pp'}</td></tr>`).join('');
 const chosen=risk.find(r=>r.budget===state.budget),base=baseline.find(r=>r.budget===state.budget);
 byId('capture-summary').innerHTML=`<p><strong>${(chosen.capture_rate*100).toFixed(2)}%</strong>modeled violations captured</p><p><strong>+${((chosen.capture_rate-base.capture_rate)*100).toFixed(2)} pp</strong>capture over loading at this budget</p><p class="comparison">${fmt(chosen.violations_captured)} captured · ${fmt(chosen.violations_missed)} missed · ${fmt(chosen.number_screened)} cases reviewed. Loading baseline: ${(base.capture_rate*100).toFixed(2)}% captured at the same budget.</p>`;
 if(state.size==='review'){
  const u=d.uncertainty.percentile_95_intervals['gap_capture_'+Math.round(state.budget*100)];
  if(u)byId('capture-summary').innerHTML+=`<p class="comparison">95% paired scenario-bootstrap interval for gain: +${(u.lower*100).toFixed(2)} to +${(u.upper*100).toFixed(2)} percentage points.</p>`;
 }
 const names={loading:'Loading baseline',lr:'Logistic Regression',rf:'Random Forest',gbt:'Gradient-Boosted Trees'};
 byId('model-bars').innerHTML=Object.entries(d.metrics).map(([name,m])=>`<div class="model-row"><div class="model-label"><span>${names[name]}</span><strong>${m.PR_AUC.toFixed(4)}</strong></div><div class="bar-track"><div class="bar ${name==='gbt'?'best':''}" style="width:${m.PR_AUC*100}%"></div></div></div>`).join('');
 for(const b of document.querySelectorAll('[data-size]'))b.setAttribute('aria-pressed',String(b.dataset.size===state.size));
 for(const b of document.querySelectorAll('[data-budget]')){b.disabled=!available.includes(Number(b.dataset.budget));b.title=b.disabled?'Not supplied for this experiment':'';b.setAttribute('aria-pressed',String(Number(b.dataset.budget)===state.budget));}
}
async function init(){
 const [data,starters,config]=await Promise.all([fetch('data.json').then(r=>{if(!r.ok)throw Error('Results unavailable');return r.json();}),fetch('starters.json').then(r=>r.json()),fetch('config.json').then(r=>r.ok?r.json():{}).catch(()=>({}))]);
 state.data=data;render();
 document.querySelectorAll('[data-size]').forEach(b=>b.addEventListener('click',()=>{state.size=b.dataset.size;render();}));
 document.querySelectorAll('[data-budget]').forEach(b=>b.addEventListener('click',()=>{state.budget=Number(b.dataset.budget);render();}));
 const url=safeGptUrl(config.GRIDRAIL_GPT_URL);const link=byId('gpt-link');
 byId('guide-status').textContent=url?'Choose a starter to copy it and open GridRail AI in a new tab. Paste the question there.':'GridRail AI is currently available by invitation and is not yet publicly accessible.';
 if(url){link.href=url;link.hidden=false;}
 for(const question of starters.slice(0,4)){
  const li=document.createElement('li'),button=document.createElement('button');button.type='button';button.textContent=question;button.setAttribute('aria-label',(url?'Copy question and open GridRail AI in a new tab: ':'Copy question: ')+question);
  button.addEventListener('click',async()=>{
   const status=byId('guide-status'),field=byId('copy-fallback');
   field.hidden=true;field.value='';
   // Request the clipboard and activate the safe anchor during the user gesture.
   // Opening before awaiting the clipboard avoids losing popup user activation.
   let copy;
   try{copy=Promise.resolve(navigator.clipboard.writeText(question));}catch(error){copy=Promise.reject(error);}
   if(url)link.click();
   status.classList.add('is-notice');
   try{
    await copy;
    status.textContent=url?'Opening GridRail AI. Your starter question has been copied.':'GridRail AI is currently available by invitation and is not yet publicly accessible. Your question has been copied. Request an invitation to try the assistant.';
   }catch{
    field.value=question;field.hidden=false;field.focus();field.select();
    status.textContent=url?'GridRail AI was requested in a new tab. Automatic copying was unavailable. Copy the selected question manually and paste it into GridRail AI.':'GridRail AI is currently available by invitation and is not yet publicly accessible. Automatic copying was unavailable. Copy the selected question manually, or request an invitation.';
   }
   // Persistent inline feedback; never time out or move keyboard focus on success.
   status.scrollIntoView({block:'nearest',behavior:'auto'});
  });li.append(button);byId('starters').append(li);
 }
}
const PUBLIC_INVITATION_URL = 'https://docs.google.com/forms/d/e/1FAIpQLSddC199Z7tKwWrrFcPfUeZEiMqhM-7-hKzAlmLFpLpcesjSRA/viewform';
byId('request-invitation').href=PUBLIC_INVITATION_URL;
const panel=byId('gridrail-panel'),launcher=byId('guide-launcher');
let guideOpener=null;
const previousInert=new Map();
function guideControls(){
 return [...panel.querySelectorAll('button,a[href],input,select,textarea,[tabindex]')]
  .filter(el=>!el.disabled&&el.tabIndex>=0&&!el.closest('[inert]')&&el.getClientRects().length>0&&getComputedStyle(el).visibility!=='hidden');
}
function isolateGuide(){
 // Inert siblings at every ancestor level, never the dialog's ancestors.
 for(let branch=panel;branch.parentElement;branch=branch.parentElement){
  for(const sibling of branch.parentElement.children){
   if(sibling!==branch&&!previousInert.has(sibling)){
    previousInert.set(sibling,sibling.hasAttribute('inert'));
    sibling.setAttribute('inert','');
   }
  }
  if(branch.parentElement===document.body)break;
 }
}
function restoreBackground(){
 for(const [el,wasInert] of previousInert){if(!wasInert)el.removeAttribute('inert');}
 previousInert.clear();
}
function toggleGuide(open,opener=launcher){
 if(open){
  if(!panel.hidden)return;
  guideOpener=opener;
  panel.hidden=false;
  launcher.setAttribute('aria-expanded','true');
  document.body.classList.add('assistant-open');
  isolateGuide();
  byId('close-guide').focus({preventScroll:true});
 }else{
  if(panel.hidden)return;
  panel.hidden=true;
  launcher.setAttribute('aria-expanded','false');
  document.body.classList.remove('assistant-open');
  restoreBackground();
  const target=guideOpener?.isConnected?guideOpener:launcher;
  guideOpener=null;
  target.focus({preventScroll:true});
 }
}
launcher.addEventListener('click',e=>toggleGuide(true,e.currentTarget));
byId('close-guide').addEventListener('click',()=>toggleGuide(false));
document.addEventListener('keydown',e=>{
 if(panel.hidden)return;
 if(e.key==='Escape'){e.preventDefault();toggleGuide(false);return;}
 if(e.key==='Tab'){
  const controls=guideControls();
  e.preventDefault();
  if(!controls.length){byId('close-guide').focus();return;}
  const index=controls.indexOf(document.activeElement);
  const next=index<0?(e.shiftKey?controls.length-1:0):(index+(e.shiftKey?-1:1)+controls.length)%controls.length;
  controls[next].focus();
 }
});
// Also contain attempted programmatic focus when inert is unavailable.
document.addEventListener('focusin',e=>{if(!panel.hidden&&!panel.contains(e.target))byId('close-guide').focus();});
init().catch(()=>{byId('run-note').textContent='Published result summaries are unavailable. Please consult the project documentation.';byId('guide-status').textContent='GridRail AI is currently available by invitation and is not yet publicly accessible.';});
