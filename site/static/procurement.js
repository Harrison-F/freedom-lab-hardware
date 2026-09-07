'use strict';
(() => {
 const escape = v => String(v ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const money = v => typeof v === 'number' ? `$${v.toFixed(2)}` : 'Unknown';
 const list = a => `<ul>${a.map(v=>`<li>${escape(v)}</li>`).join('')}</ul>`;
 const link = (url,label) => /^https:\/\//.test(url||'') ? `<a href="${escape(url)}" target="_blank" rel="noopener noreferrer">${escape(label)} ↗</a>` : escape(label);
 const dates = r => r.arrival_latest ? `${r.arrival_earliest||'?'} – ${r.arrival_latest}` : 'No dated arrival';
 const bom = parts => `<ul class="bom-parts">${parts.map(p=>`<li><strong>${link(p.source_url,p.name)}</strong><small>${escape(p.role)} · Qty ${escape(p.quantity)} · ${p.role==='not required'?'Not required for streaming pilot':p.unit_price_usd===0?'Included / no extra charge':money(p.unit_price_usd)+' each'}</small><small>${escape(p.status.replaceAll('_',' '))} · Shipment: ${escape(p.shipment_group||'unresolved / not applicable')}</small>${escape(p.note)}</li>`).join('')}</ul>`;
 const offers = rows => rows.map(o=>`<article class="offer"><strong>${link(o.source_url,o.name)}</strong><p>Item ${money(o.price_usd)} + shipping ${money(o.shipping_usd)}; package + freight: ${money(o.item_plus_shipping_usd)}, before tax. <strong>Not a complete delivered build.</strong></p><p>${escape(dates(o))} · ${escape(o.match)} · ${escape(o.status)}</p><p>${escape(o.note)}</p></article>`).join('');
 let data,items;
 function card(r) {
  const item=items.get(r.id),image=item?.image;
  const media=image && /^\.\.\/static\/voice-device-media\/[a-z0-9-]+\.webp$/.test(image.path) ? `<img class="portrait" src="${escape(image.path)}" alt="${escape(image.alt)}" loading="eager">` : '<div class="image-unavailable">No verified source image</div>';
  const primaryOffer=r.offers.find(o=>o.match!=='optional separate hotspot');
  const freight=r.shipments.find(s=>typeof s.shipping_usd==='number');
  return `<article class="display-card procurement-card" data-build-id="${escape(r.id)}">
   <div class="portrait-wrap">${media}${r.fit_rank?`<span class="priority">Direction ${escape(r.fit_rank)}</span>`:''}</div>
   <div class="card-body"><div class="card-head"><div class="identity"><h3>${escape(item?.name||r.name)}</h3></div></div>
   <p class="procurement-price">${r.known_parts_subtotal_usd===null?'Known subtotal unavailable':money(r.known_parts_subtotal_usd)+' known parts'}</p>
   <p class="procurement-caption">${escape(r.build_status)}</p>
   <p class="procurement-caption">Board / bundle ${money(r.price_usd)} · ${escape(r.price_status)}. Observed ${escape(r.checked_at)}.</p>
   <div class="procurement-delivery"><strong>${r.known_parts_plus_quoted_shipping_usd===null?'Delivery not fully quoted':money(r.known_parts_plus_quoted_shipping_usd)+' known parts + quoted freight only'}</strong>
    <small>${freight?escape(freight.seller)+': '+money(freight.shipping_usd)+' quoted freight; other shipments / tax extra.':'Required shipment rates unresolved; not free.'}</small>
    ${primaryOffer?`<p>${link(primaryOffer.source_url,primaryOffer.name)}: ${money(primaryOffer.item_plus_shipping_usd??primaryOffer.price_usd)} · ${escape(dates(primaryOffer))}<small>${escape(primaryOffer.match)}; package only, not all-parts readiness.</small></p>`:''}
    <small>Complete Wi-Fi ${money(r.wifi_total_usd)} · delivered ${money(r.delivered_total_usd)} · all-parts arrival unknown.</small>
   </div>
   <details class="research-evidence"><summary>Purchase &amp; assembly</summary><h4>Exact parts &amp; package contents</h4><p>${escape(r.name)}</p>${list(r.purchase_list)}${bom(r.bom)}<h4>Assembly &amp; firmware gaps</h4>${list(r.assembly_list)}
    ${r.alternatives.map(a=>`<h4>${escape(a.name)}</h4><p>${money(a.known_parts_subtotal_usd)} known parts; ${money(a.known_parts_plus_quoted_shipping_usd)} including quoted freight only. Not complete.</p><p>${escape(a.note)}</p>${bom(a.bom)}`).join('')}
    <h4>Cellular additions</h4><p>Complete cellular hardware: ${money(r.cellular_total_usd)}; service and engineering separate.</p>${list(r.cellular_additions)}<h4>Sources</h4>${r.sources.map(s=>`<p>${link(s.url,s.label)}</p>`).join('')}${image?`<p class="image-source">${link(image.source_url,'Exact image source')}</p>`:''}
   </details>
   <details class="procurement-offers"><summary>Package offers &amp; freight</summary><p>${escape(r.delivery_status)}</p><p>ALL shipments: ${money(r.shipping_usd)} · Tax ${money(r.tax_usd)}. All-parts arrival: ${escape(dates(r))}.</p>
    ${r.shipments.map(s=>`<article class="shipment"><strong>${link(s.source_url,s.seller)} · ${money(s.shipping_usd)}</strong><p>${escape(s.status)} · ${escape(s.scope)}</p><p>${escape(s.note)}</p><p>${escape(dates(s))}; this shipment only.</p></article>`).join('')}${offers(r.offers)}
   </details></div></article>`;
 }
 function render() {
  const mode=document.querySelector('#cost-sort').value,rows=[...data.builds];
  const score=r=>mode==='fit'?r.fit_rank??Infinity:mode==='known'?r.known_parts_subtotal_usd??Infinity:mode==='affordability'?(r.complete&&[r.wifi_total_usd,r.shipping_usd,r.tax_usd].every(v=>typeof v==='number')?r.wifi_total_usd+r.shipping_usd+r.tax_usd:Infinity):(r.complete&&r.arrival_latest?Date.parse(r.arrival_latest):Infinity);
  rows.sort((a,b)=>score(a)-score(b)||(a.fit_rank??999)-(b.fit_rank??999));
  const known=rows.filter(r=>Number.isFinite(score(r)));
  document.querySelector('#ranking-note').textContent=mode==='fit'?'E-ink + audio + physical PTT pilot fit. Known parts are not complete delivered totals.':mode==='known'?'Known priced lines only; may omit required parts or include unavailable references. NOT an affordability ranking.':known.length?'Only complete documented builds ranked; unresolved builds follow.':'No defensible '+(mode==='fastest'?'fastest-delivery':'complete-build affordability')+' winner yet.';
  document.querySelector('#bom-rows').innerHTML=rows.map(card).join('');
  document.querySelector('#comparison-methodology').textContent=data.methodology;
 }
 Promise.all(['procurement.json','data.json'].map(url=>fetch(url,{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json()}))).then(([d,c])=>{if(d.schema_version!==1||!Array.isArray(d.builds)||!Array.isArray(c.items))throw Error('Unsupported schema');data=d;items=new Map(c.items.map(i=>[i.id,i]));render();document.querySelector('#cost-sort').addEventListener('change',render)}).catch(e=>{document.querySelector('#ranking-note').textContent='Procurement data unavailable: '+e.message});
})();
