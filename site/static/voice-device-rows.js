'use strict';
// One catalog, joined by stable ID. Route-only presentation; source evidence stays verbatim.
const $ = s => document.querySelector(s);
const esc = v => String(v ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const safeURL = v => {try {const u=new URL(v);return u.protocol==='https:'?u.href:'';}catch{return '';}};
const link = (u,t) => safeURL(u)?`<a href="${esc(safeURL(u))}" target="_blank" rel="noopener noreferrer">${esc(t)} ↗</a>`:esc(t);
const money = v => typeof v==='number'?`$${v.toFixed(2)}`:'';
const list = a => `<ul>${(a||[]).map(t=>`<li>${esc(t)}</li>`).join('')}</ul>`;
const groups = ['E-ink voice devices','Other compact voice devices','Build-it-yourself options','Design references—not complete builds'];
const groupIDs = [['ALT01','ALT02','BM07','DONOR02','BM35'],['KIT01','BM01','BM12'],['DONOR01','BM32','BM06','BM34']];
const groupOf = i => {const n=groupIDs.findIndex(ids=>ids.includes(i.id));return groups[n<0?3:n];};
const filters=['recommendation','status','category','scope'];
let collection,procurement,builds;
// Explicit package evidence, never inferred from a chip's capabilities.
// Six positions: mic, speech, headphones, cellular, battery, enclosure.
const included = {
 ALT01:['Included — onboard microphone','Included — speaker',null,null,'Included — selected battery variant','Included per vendor description — verify housing on receipt'],
 ALT02:['Included — onboard microphone','Included — supplied speaker; attach its connector',null,null,'Included — vendor battery',null],
 KIT01:['Included — onboard microphone','Included — speaker',null,null,'Included — 250 mAh battery','Included — device case'],
 BM01:['Included — onboard microphone','Included — speaker',null,null,'Included — select battery SKU 29957','Included — black case'],
 BM12:['Included — K147 Voice Base microphone','Included — K147 Voice Base speaker',null,null,null,'Included — controller and Voice Base cases'],
 BM07:['Included — microphone','Not yet solved — buzzer cannot speak',null,null,'Included — 750 mAh battery','Included — magnetic case'],
 DONOR02:['Included — microphone','Not yet solved — buzzer cannot speak',null,null,'Included — 1150 mAh battery','Included — case'],
 BM35:['Included — microphone',null,null,null,'Included — battery','Included — case'],
 BM34:[null,null,null,null,'Included — 1800 mAh battery',null],
 BM04:['Included per device documentation — dual microphones','Included per device documentation — speaker',null,null,null,null]
};
function features(i,r) {
 const names=['Microphone','Speech output','Headphone jack','Cellular','Battery','Enclosure'];
 const state=[...(included[i.id]||[])];
 const add=(n,p,note='')=>{if(p)state[n]=`Add ${link(p.source_url,p.name)}${note?' — '+esc(note):''}`;};
 if(i.id==='BM32'){add(0,r.bom[1],'includes microphones');add(1,r.bom[1],'includes speaker');add(4,r.bom[2],'separate battery board');}
 if(i.id==='BM12'){
  add(2,r.alternatives[1].bom.find(p=>p.name.includes('A166')),'replaces Voice Base, not stackable; headset still unselected');
  add(4,r.alternatives[0].bom.find(p=>p.name.includes('power bank')),'optional external power bank; USB-powered without it');
 }
 return `<dl class="feature-list">${names.map((n,k)=>`<div><dt>${n}${k===2||k===3?' <small>optional upgrade</small>':''}</dt><dd>${state[k]?.startsWith('Add ')?state[k]:esc(state[k]||(k===3?'Not yet solved — no built-in cellular verified':k===2?'Not yet solved — no verified headphone jack':'Not yet solved — exact compatible part unselected'))}</dd></div>`).join('')}</dl>`;
}
function part(p,technical=false){
 const unresolved=p.role.includes('unresolved')||p.status.includes('reference_only')||p.status.includes('unverified_variant');
 const label=unresolved?'Not yet solved':p.role.startsWith('included')?'Included':p.role==='not required'?'Not required':'Add';
 return `<li><strong>${label}</strong> — ${link(p.source_url,p.name)}${money(p.unit_price_usd)&&p.unit_price_usd!==0?` · ${money(p.unit_price_usd)}${p.quantity>1?' each × '+p.quantity:''}`:''}${technical?`<small>${esc(p.status.replaceAll('_',' '))} · ${esc(p.role)}</small><p>${esc(p.note)}</p>`:p.status.includes('out_of_stock')?' <small>Out of stock at review</small>':''}</li>`;
}
function alternatives(r){
 return `<details class="addons"><summary>Optional headphones &amp; cellular / battery upgrades</summary><p>Not needed for a Wi-Fi speaker build. These are engineering options, not plug-and-play upgrades.</p>${r.alternatives.map(a=>`<h4>${esc(a.name)}</h4><p>${esc(a.note)}</p><ul class="parts">${a.bom.filter(p=>!r.bom.some(b=>b.name===p.name)).map(p=>part(p,true)).join('')}</ul>`).join('')}${list(r.cellular_additions)}${r.offers.filter(o=>o.match==='optional separate hotspot').map(o=>`<p>${link(o.source_url,o.name)} · ${money(o.price_usd)}. Separate device; SIM/service and setup extra.</p>`).join('')}</details>`;
}
function shipping(r){return `<details class="procurement-offers"><summary>Package offers &amp; shipping evidence</summary><p>Quotes are for individual packages, not arrival of every required part. Checked ${esc(r.checked_at)} · ZIP 10014 · quantity 1 · USD.</p>${r.shipments.map(s=>`<article class="shipment"><h4>${link(s.source_url,s.seller)}${money(s.shipping_usd)?' · '+money(s.shipping_usd)+' shipping':''}</h4><p>${esc(s.status)} · ${esc(s.scope)}</p><p>${esc(s.note)}</p></article>`).join('')}${r.offers.map(o=>`<article class="offer"><h4>${link(o.source_url,o.name)}</h4><p>${money(o.price_usd)}${money(o.shipping_usd)?' + '+money(o.shipping_usd)+' shipping':''}${money(o.item_plus_shipping_usd)?' = '+money(o.item_plus_shipping_usd)+' package + freight':''}; before tax.</p><p>${esc(o.arrival_earliest)}${o.arrival_latest!==o.arrival_earliest?' – '+esc(o.arrival_latest):''} · ${esc(o.match)} · ${esc(o.status)}</p><p>${esc(o.note)}</p></article>`).join('')}</details>`;}
const plainSummary={
 ALT01:'Small e-ink screen with microphone, speaker and battery. The most promising first Wi-Fi voice pilot; select the non-touch V2 battery bundle.',
 ALT02:'Larger e-ink screen with microphone, supplied speaker and battery. Connect the speaker and build a protective case; the board is not a finished handheld.',
 KIT01:'Small color-screen device with microphone, speaker, battery and case. A compact Wi-Fi pilot, not e-ink.',
 BM01:'Color touch-screen device with microphone, speaker and case. Choose battery-included SKU 29957 and match the software to the board revision.',
 BM12:'Tiny color-screen audio kit with microphone and speaker. Runs on USB power; a portable battery and headphones are separate options.',
 BM07:'E-ink device that can hear you, but cannot speak back: its buzzer is not a speech speaker. Voice-output hardware still needs to be designed.',
 DONOR02:'E-ink device with microphone, battery and case. It can capture speech but only has a buzzer for output; spoken replies still need hardware.',
 BM35:'E-ink handheld with microphone, battery and case. Spoken replies and headphones still need a verified hardware solution.',
 DONOR01:'A weather-display project to redesign, not a voice kit. Microphone, speaker, button, power and case compatibility are not yet solved.',
 BM32:'Build a handheld from a Raspberry Pi, an audio/display board and a separate battery board. A useful voice-software starting point; the Pi was out of stock and the fitted case is unresolved.',
 BM06:'An e-ink bike-computer project to adapt. Its music buttons control a phone; they do not prove this board can speak.',
 BM34:'An e-ink display and battery donor. No onboard microphone is documented; a complete voice hardware design is still needed.'
};
function deliveryPreview(r){const o=r.offers.find(o=>o.match!=='optional separate hotspot');return o?`<p class="delivery-preview">Package-only offer: ${link(o.source_url,o.name)} · ${money(o.item_plus_shipping_usd??o.price_usd)}${typeof o.item_plus_shipping_usd==='number'?' with quoted freight':' before shipping'} · ${esc(o.arrival_earliest)}${o.arrival_latest!==o.arrival_earliest?' – '+esc(o.arrival_latest):''}. ${esc(o.match)}. Before tax; conditions below, not all-parts arrival.</p>`:'';}
function card(i){
 const r=builds.get(i.id),reference=groupOf(i)===groups[3];
 const image=i.image&&/^\.\.\/static\/voice-device-media\/[a-z0-9-]+\.webp$/.test(i.image.path)?i.image:null;
 const primary=r?.bom[0],purchase=primary&&!primary.role.includes('unresolved')&&!primary.status.includes('reference_only');
 const extras=r?r.bom.slice(1).filter(p=>p.role.includes('purchase')):[];
 return `<article class="hardware-row${reference?' reference-row':''}" data-id="${esc(i.id)}" ${r?`data-build-id="${esc(i.id)}"`:''}>
 <div class="hardware-identity"><div class="hardware-image">${image?`<img src="${esc(image.path)}" alt="${esc(image.alt)}" loading="lazy">`:'<p class="image-unavailable">No verified source image</p>'}</div><h3>${esc(i.name)}</h3>${primary?`<p class="main-purchase">${link(primary.source_url,purchase?'Buy '+primary.name:'Source / variant to verify')}${money(r.price_usd)?' · '+money(r.price_usd):''}</p>`:`<p>${link(i.sources[0]?.url,'Project source')}</p>`}${primary?.status.includes('out_of_stock')?'<p>Out of stock at review</p>':''}${reference?'<p class="subtle">Design reference, not a complete build</p>':''}</div>
 <div class="hardware-components"><p class="row-summary">${esc(plainSummary[i.id]||i.summary)}</p>${features(i,r)}
 ${r?`<section class="required-parts"><h4>What else to buy for Wi-Fi + spoken replies</h4><ul class="parts">${extras.map(p=>part(p)).join('')}</ul>${!extras.length?'<p>No complete additional-parts list verified.</p>':''}</section><p class="software-needed">Needs programming to talk to Hermes. Assembly and testing still required.</p><p class="cost-line">${money(r.known_parts_subtotal_usd)?money(r.known_parts_subtotal_usd)+' known parts':'Parts subtotal not established'}${money(r.known_parts_plus_quoted_shipping_usd)?' · '+money(r.known_parts_plus_quoted_shipping_usd)+' with quoted freight only':''}. <span>Not a complete delivered total; tax, missing parts and unquoted shipping extra.</span></p>${deliveryPreview(r)}${alternatives(r)}${shipping(r)}`:'<p class="software-needed">Not yet solved — no verified complete voice-device shopping list or Hermes setup.</p>'}
 <details class="research-evidence"><summary>Technical evidence &amp; unresolved work</summary><p>${esc(i.id)} · ${esc(i.status)} · ${esc(i.scope)}</p><p>Original desk-review summary (later exact-package evidence below takes precedence): ${esc(i.summary)}</p>${list(i.evidence)}<h4>Still needed</h4><p>${esc(i.gaps)}</p>${r?`<h4>Exact package &amp; parts evidence</h4><p>${esc(r.name)} · ${esc(r.price_status)} · ${esc(r.build_status)}</p>${list(r.purchase_list)}<ul class="parts">${r.bom.map(p=>part(p,true)).join('')}</ul><h4>Assembly &amp; firmware evidence</h4>${list(r.assembly_list)}`:''}<div class="source-links">${i.sources.map(s=>link(s.url,s.label)).join(' · ')}</div>${r?`<div class="source-links">${r.sources.map(s=>link(s.url,s.label)).join(' · ')}</div>`:''}${image?`<p>${esc(image.kind)} · ${link(image.source_url,'Exact image source')}</p>`:''}</details></div></article>`;
}
function render(){
 const q=$('#search').value.trim().toLowerCase(),mode=$('#cost-sort').value;
 const selected=collection.items.filter(i=>filters.every(f=>!$('#'+f+'-filter').value||(f==='category'?groupOf(i):i[f])===$('#'+f+'-filter').value)&&JSON.stringify([i,builds.get(i.id)]).toLowerCase().includes(q));
 const score=i=>mode==='known'?builds.get(i.id)?.known_parts_subtotal_usd??Infinity:i.rank??builds.get(i.id)?.fit_rank??100;
 selected.sort((a,b)=>score(a)-score(b)||a.id.localeCompare(b.id));
 $('#collections').innerHTML=groups.map(title=>{const items=selected.filter(i=>groupOf(i)===title);return items.length?`<section class="research-collection" data-category="${esc(title)}"><h2 class="collection-heading">${esc(title)} <span class="group-count">${items.length}</span></h2>${title===groups[0]?'<p class="group-note">E-paper devices with a documented microphone. Some still need hardware for spoken replies.</p>':title===groups[2]?'<p class="group-note">Separate boards or display donors: wiring, power, case and voice integration need work.</p>':title===groups[3]?'<p class="group-note">Interaction, display, robotics and software inspiration—not additional ready-to-buy voice builds.</p>':''}<div class="hardware-rows">${items.map(card).join('')}</div></section>`:'';}).join('');
 $('#count').textContent=`${selected.length} of ${collection.items.length} items · one catalog · reviewed ${collection.updated_at}`;
 $('#ranking-note').textContent=mode==='known'?'Known priced lines within each category; NOT an affordability ranking. Missing parts are not zero.':mode==='fit'?'Pilot fit within each category. No complete operational build has been verified.':'No defensible '+(mode==='fastest'?'fastest-delivery':'complete-build affordability')+' winner yet. Showing pilot fit within categories.';
 $('#empty').hidden=selected.length!==0;
}
async function load(){try{
 [collection,procurement]=await Promise.all(['data.json','procurement.json'].map(async url=>{const r=await fetch(url,{cache:'no-store'});if(!r.ok||!r.headers.get('content-type')?.includes('application/json'))throw Error('Data unavailable (HTTP '+r.status+').');return r.json();}));
 if(collection.schema_version!==1||procurement.schema_version!==1)throw Error('Unsupported data format');
 builds=new Map(procurement.builds.map(r=>[r.id,r]));
 $('#notice').textContent=collection.notice;$('#coverage').textContent=collection.coverage.statement;
 $('#comparison-methodology').textContent=procurement.methodology;
 for(const f of filters){for(const v of f==='category'?groups:[...new Set(collection.items.map(i=>i[f]))].sort()){const o=document.createElement('option');o.value=v;o.textContent=v;$('#'+f+'-filter').append(o);}$('#'+f+'-filter').addEventListener('change',render);}
 $('#search').addEventListener('input',render);$('#cost-sort').addEventListener('change',render);
 $('#reset').addEventListener('click',()=>{$('#search').value='';for(const f of filters)$('#'+f+'-filter').value='';$('#cost-sort').value='fit';render();});render();
 }catch(e){$('#error').textContent=e.message;$('#error').hidden=false;$('#count').textContent='';}}
load();
