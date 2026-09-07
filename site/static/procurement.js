'use strict';
(() => {
 const escape = v => String(v ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const money = v => typeof v === 'number' ? `$${v.toFixed(2)}` : 'Unknown — pending';
 const list = a => `<ul>${a.map(v=>`<li>${escape(v)}</li>`).join('')}</ul>`;
 let data;
 function render() {
  const mode=document.querySelector('#cost-sort').value;
  const rows=[...data.builds];
  const score = r => mode==='fit' ? r.fit_rank ?? Infinity : mode==='affordability' ? (r.complete && [r.wifi_total_usd,r.shipping_usd,r.tax_usd].every(v=>typeof v==='number') ? r.wifi_total_usd+r.shipping_usd+r.tax_usd : Infinity) : (r.complete && r.arrival_latest ? Date.parse(r.arrival_latest) : Infinity);
  rows.sort((a,b)=>score(a)-score(b)||(a.fit_rank??999)-(b.fit_rank??999));
  const known=rows.filter(r=>Number.isFinite(score(r)));
  document.querySelector('#ranking-note').textContent=(mode==='fit'?'Fit: e-ink + audio + physical PTT pilot suitability. ':known.length?'Only complete, documented builds are ranked; unresolved builds follow. ':'No defensible '+(mode==='fastest'?'fastest-delivery':'complete-build affordability')+' winner yet. ')+data.methodology;
  document.querySelector('#bom-rows').innerHTML=rows.map(r=>`<tr data-build-id="${escape(r.id)}"><td><strong>${escape(r.name)}</strong><small>${r.fit_rank?'Fit direction '+escape(r.fit_rank):'Unranked reference'}</small><details><summary>Purchase &amp; assembly</summary><h3>Purchase</h3>${list(r.purchase_list)}<h3>Assembly</h3>${list(r.assembly_list)}<h3>Cellular additions</h3>${list(r.cellular_additions)}${r.sources.map(s=>/^https:\/\//.test(s.url)?`<p><a href="${escape(s.url)}" target="_blank" rel="noopener noreferrer">${escape(s.label)} ↗</a></p>`:'').join('')}</details></td><td>${money(r.price_usd)}<small>${escape(r.price_status)}</small><small>Observed ${escape(r.checked_at)}</small></td><td>${money(r.wifi_total_usd)}<small>${r.complete?'Documented parts total':'Incomplete BOM qualification'}</small></td><td>${money(r.cellular_total_usd)}<small>Service + engineering separate</small></td><td>Shipping: ${money(r.shipping_usd)}<small>Tax: ${money(r.tax_usd)}</small><small>${r.arrival_latest?escape((r.arrival_earliest||'?')+' – '+r.arrival_latest):'Arrival: unknown'}</small><small>${escape(r.delivery_status)}</small></td></tr>`).join('');
 }
 fetch('procurement.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json()}).then(d=>{if(d.schema_version!==1||!Array.isArray(d.builds))throw Error('Unsupported schema');data=d;render();document.querySelector('#cost-sort').addEventListener('change',render)}).catch(e=>{document.querySelector('#ranking-note').textContent='Procurement data unavailable: '+e.message});
})();
