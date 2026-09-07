'use strict';
// Public read-only research collection; no backend or write APIs.
const $ = s => document.querySelector(s);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const safeURL = value => { try { const u = new URL(value); return u.protocol === 'https:' ? u.href : ''; } catch { return ''; } };
const filters = ['recommendation', 'status', 'category', 'scope'];
let collection;
function card(item) {
  const image = item.image && /^\.\.\/static\/voice-device-media\/[a-z0-9-]+\.webp$/.test(item.image.path) ? item.image : null;
  const media = image ? `<img class="portrait" src="${esc(image.path)}" alt="${esc(image.alt)}" loading="lazy">` : '<div class="image-unavailable">No verified source image</div>';
  const links = item.sources.map(s => safeURL(s.url) ? `<a class="secondary-button" href="${esc(safeURL(s.url))}" target="_blank" rel="noopener noreferrer">${esc(s.label)} ↗</a>` : '').join('');
  return `<article class="display-card" data-id="${esc(item.id)}">
    <div class="portrait-wrap">${media}${item.rank ? `<span class="priority">Direction ${esc(item.rank)}</span>` : ''}</div>
    <div class="card-body">
      <div class="card-head"><div class="identity"><h2>${esc(item.name)}</h2></div></div>
      <p class="bio">${esc(item.summary)}</p>
      <div class="meta"><span class="chip">${esc(item.recommendation)}</span><span class="chip">${esc(item.status)}</span><span class="chip">${esc(item.scope)}</span></div>
      <details class="research-evidence"><summary>Evidence &amp; gaps<span class="sr-only"> — ${esc(item.name)}</span></summary>
        <ul>${item.evidence.map(e => `<li>${esc(e)}</li>`).join('')}</ul>
        <div class="fit"><h3>Still needed</h3><p>${esc(item.gaps)}</p></div>
        <p class="image-source">${esc(item.id)} · ${esc(item.category)} · ${esc(item.scope)}</p>
        ${image ? `<p class="image-source">${esc(image.kind)} · <a href="${esc(safeURL(image.source_url))}" target="_blank" rel="noopener noreferrer">Exact image source ↗</a></p>` : ''}
      </details>
      <div class="card-foot"><div class="card-links">${links}</div></div>
    </div></article>`;
}
function render() {
  const q = $('#search').value.trim().toLocaleLowerCase();
  const selected = collection.items.filter(item => filters.every(f => !$('#'+f+'-filter').value || item[f] === $('#'+f+'-filter').value) && [item.name,item.summary,item.gaps,...item.evidence,item.id].join(' ').toLocaleLowerCase().includes(q));
  const groups = [['Recommended pilot directions', i => i.rank != null], ['Public hardware & software references', i => i.rank == null]];
  if (!$('#collections').children.length) {
    $('#collections').innerHTML = groups.map(([title, predicate]) => {
      const entries = collection.items.filter(predicate);
      return entries.length ? `<section class="research-collection"><h2 class="collection-heading">${esc(title)}</h2><div class="display-template" aria-label="${esc(title)}">${entries.map(card).join('')}</div></section>` : '';
    }).join('');
  }
  const visibleIDs = new Set(selected.map(i => i.id));
  for (const el of document.querySelectorAll('.display-card')) el.hidden = !visibleIDs.has(el.dataset.id);
  for (const group of document.querySelectorAll('.research-collection')) group.hidden = !group.querySelector('.display-card:not([hidden])');
  $('#count').textContent = `${selected.length} of ${collection.items.length} research items · reviewed ${collection.updated_at}`;
  $('#empty').hidden = selected.length !== 0;
}
async function load() {
  try {
    const response = await fetch('data.json', {cache:'no-store'});
    if (!response.ok || !response.headers.get('content-type')?.includes('application/json')) throw new Error(`Research data unavailable (HTTP ${response.status}).`);
    collection = await response.json();
    if (collection.schema_version !== 1 || !Array.isArray(collection.items)) throw new Error('Research data format is unsupported.');
    collection.items.sort((a,b) => (a.rank ?? 100) - (b.rank ?? 100) || a.id.localeCompare(b.id));
    $('#recommendation-headline').textContent = collection.headline;
    $('#recommendation-summary').textContent = collection.recommendation_summary;
    $('#notice').textContent = collection.notice;
    $('#coverage').textContent = collection.coverage.statement;
    for (const f of filters) {
      for (const value of [...new Set(collection.items.map(i=>i[f]))].sort()) { const o = document.createElement('option'); o.value = value; o.textContent = value; $('#'+f+'-filter').append(o); }
      $('#'+f+'-filter').addEventListener('change', render);
    }
    $('#search').addEventListener('input', render);
    $('#reset').addEventListener('click', () => { $('#search').value = ''; for (const f of filters) $('#'+f+'-filter').value = ''; render(); });
    render();
  } catch (error) { $('#notice').textContent = 'Evidence could not be loaded.'; $('#count').textContent = ''; $('#error').textContent = error.message; $('#error').hidden = false; }
}
load();
