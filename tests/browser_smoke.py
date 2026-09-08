import json,sys,time,tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
url=sys.argv[1] if len(sys.argv)>1 else 'https://hardware.freedomlab.nyc/'
start=time.monotonic();errors=[];results=[];output=Path(tempfile.mkdtemp(prefix='hardware-rows-qa-'))
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True)
 for width in [1280,390]:
  page=browser.new_page(viewport={'width':width,'height':1000})
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('console',lambda e:errors.append(e.text) if e.type=='error' else None)
  page.set_default_timeout(10000)
  response=page.goto(url,wait_until='domcontentloaded',timeout=30000);assert response.status==200
  page.locator('.hardware-row').first.wait_for()
  assert page.locator('.hardware-row').count()==36
  assert page.locator('[data-build-id]').count()==13
  assert page.locator('.hardware-identity .device-specs').count()==36
  assert page.locator('.device-specs > .source-links a').count()==32
  assert page.locator('[data-id="BM02"] .device-specs').inner_text().startswith('No public device specs found')
  assert 'Not a device' in page.locator('[data-id="BM18"] .device-specs').inner_text()
  assert 'project license missing' in page.locator('[data-id="ALT01"] .source-license').inner_text()
  spec=page.locator('[data-id="ALT01"] .device-specs > .source-links a').first
  assert spec.get_attribute('href')=='https://docs.waveshare.com/ESP32-S3-ePaper-1.54'
  spec.hover();page.mouse.move(0,0);spec.focus()
  with page.expect_popup() as pop:page.keyboard.press('Enter')
  popup=pop.value;popup.wait_for_load_state('domcontentloaded');assert popup.url.startswith('https://docs.waveshare.com/ESP32-S3-ePaper-1.54');popup.close()
  scope=page.locator('[data-id="ALT01"] .device-specs > details')
  scope.locator('summary').click();assert 'exact non-touch V2 schematic applicability is not confirmed' in scope.inner_text();scope.locator('summary').click()
  assert page.locator('.source-license').count()==36
  for id,expected in [('ALT01','nested codec/library terms'),('BM01','Apache-2.0'),('BM30','collection is subject to GPL3'),('ALT02','Espressif-only'),('BM32','GPL-2.0-only')]:
   license=page.locator(f'[data-id="{id}"] .source-license details')
   license.locator('summary').click();assert expected in license.inner_text()
   assert license.locator('a').count()>0
   if id=='BM01':
    license.evaluate('(e)=>e.scrollIntoView({block:"start"})');page.screenshot(path=str(output/f'{width}-license-expanded.png'))
   license.locator('summary').click()
  assert page.locator('.hardware-row img').count()==34
  page.locator('.hardware-row img').evaluate_all('(imgs)=>Promise.all(imgs.map(i=>{i.loading="eager";return i.decode()}))')
  assert page.locator('#bom-rows').count()==0
  groups=page.locator('.research-collection').evaluate_all('(els)=>els.map(e=>({name:e.dataset.category,count:e.querySelectorAll(".hardware-row").length,label:Number(e.querySelector(".group-count").textContent)}))')
  assert [g['count'] for g in groups]==[5,3,4,24]
  assert all(g['count']==g['label'] for g in groups)
  checks=page.locator('.hardware-row').evaluate_all('''els=>els.map(e=>{const a=e.getBoundingClientRect(),b=e.querySelector('.hardware-identity').getBoundingClientRect(),c=e.querySelector('.hardware-components').getBoundingClientRect(),p=e.parentElement.getBoundingClientRect();return {full:Math.abs(a.width-p.width)<2,left:b.right<c.left,above:b.bottom<=c.top,labels:e.querySelectorAll('dt').length,values:[...e.querySelectorAll('dd')].map(d=>d.textContent)}})''')
  for geom in checks:
   assert geom['labels']==6 and len(geom['values'])==6
   assert all(s.startswith(('Included','Documented add-on','Engineering plan','Unsupported','Reference only','Hardware test required')) for s in geom['values'])
   assert geom['full'] and geom['left' if width==1280 else 'above'],geom
  # Every verified required accessory source is exposed in the main right-hand list.
  parity=page.evaluate('''async()=>{const d=await (await fetch('procurement.json')).json();return d.builds.every(r=>r.bom.slice(1).filter(p=>p.role==='purchase'&&p.source_url).every(p=>[...document.querySelector(`[data-id="${r.id}"] .required-parts`).querySelectorAll('a')].some(a=>a.href===new URL(p.source_url).href))) }''')
  assert parity
  assert page.evaluate('innerWidth')==width
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  page.screenshot(path=str(output/f'{width}-top.png'))
  row=page.locator('[data-id="ALT01"]')
  assert 'Add a standalone cellular hotspot' in row.locator('.feature-list').inner_text()
  assert '$169.99 device-only' in row.locator('.feature-list').inner_text()
  assert 'Separate device, not built-in LTE' in row.locator('.feature-list').inner_text()
  hotspot=row.locator('.feature-list a[href="https://www.gl-inet.com/products/gl-e750/"]')
  assert hotspot.is_visible()
  with page.expect_popup() as pop:hotspot.click()
  popup=pop.value;popup.wait_for_load_state('domcontentloaded');assert popup.url.startswith('https://www.gl-inet.com/products/gl-e750/');popup.close()
  row.locator('.feature-list > div').nth(3).evaluate('(e)=>e.scrollIntoView({block:"start"})');page.screenshot(path=str(output/f'{width}-cellular.png'))
  row.locator('.feature-review summary').click();assert 'Unsupported means' in row.locator('.feature-review').inner_text();row.locator('.feature-review summary').click()
  assert '1500 mAh' in page.locator('[data-id="BM06"] .feature-list').inner_text()
  assert 'Reference only' in page.locator('[data-id="BM02"] .feature-list').inner_text()
  assert '$29.89 known parts' in row.inner_text()
  assert row.locator('.required-parts a[href="https://www.adafruit.com/product/4474"]').is_visible()
  assert row.locator('.required-parts a[href="https://www.adafruit.com/product/1994"]').is_visible()
  row.scroll_into_view_if_needed();row.evaluate('(e)=>e.scrollIntoView({block:"start"})')
  page.screenshot(path=str(output/f'{width}-first-row.png'))
  row.locator('.addons summary').click();assert row.locator('.addons a[href="https://www.amazon.com/dp/B0CJF7KQ3Q"]').is_visible()
  row.locator('.addons').evaluate('(e)=>e.scrollIntoView({block:"start"})');page.screenshot(path=str(output/f'{width}-addons.png'))
  row.locator('.addons summary').click()
  row.locator('.procurement-offers summary').click()
  assert 'Prime conditional' in row.inner_text() and 'battery inclusion unverified' in row.inner_text()
  row.locator('.procurement-offers summary').click()
  row=page.locator('[data-id="ALT02"]');row.locator('.procurement-offers summary').click()
  assert '$64.99' in row.inner_text() and '2026-09-28' in row.inner_text()
  row.locator('.offer').filter(has_text='$64.99').last.evaluate('(e)=>e.scrollIntoView({block:"start"})')
  page.screenshot(path=str(output/f'{width}-shipping.png'))
  page.locator('#search').fill('Waveshare');assert 0<page.locator('.hardware-row').count()<36
  page.locator('#reset').click();assert page.locator('.hardware-row').count()==36
  for selector in ['#recommendation-filter','#status-filter','#category-filter','#scope-filter']:
   page.locator(selector).select_option(page.locator(selector+' option').nth(1).get_attribute('value'))
   assert 0<page.locator('.hardware-row').count()<36;page.locator('#reset').click()
  for mode in ['known','affordability','fastest','fit']:
   page.locator('#cost-sort').select_option(mode)
   if mode in ['affordability','fastest']:assert 'No defensible' in page.locator('#ranking-note').inner_text()
   if mode=='known':assert 'NOT an affordability ranking' in page.locator('#ranking-note').inner_text()
   assert page.locator('.research-collection').count()==4
  row=page.locator('[data-id="BM12"]');row.locator('.addons summary').click()
  assert 'replaces Voice Base' in row.inner_text()
  assert row.locator('.addons a').count()==2
  row.locator('.addons').evaluate('(e)=>e.scrollIntoView({block:"start"})');page.screenshot(path=str(output/f'{width}-headphones.png'))
  row=page.locator('[data-id="KIT01"]');assert '$44.40 with quoted freight only' in row.inner_text()
  row.locator('.addons summary').click();assert row.locator('.addons a').count()==3
  page.locator('.research-evidence summary').first.click();assert page.locator('.research-evidence').first.get_attribute('open') is not None
  page.locator('.hardware-row').first.hover();page.mouse.move(0,0)
  page.locator('#github-link').focus()
  with page.expect_popup() as pop:page.keyboard.press('Enter')
  popup=pop.value;assert popup.url.startswith('https://github.com/Harrison-F/freedom-lab-hardware');popup.close()
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  results.append({'width':width,'rows':36,'images':34,'groups':groups,'url':page.url});page.close()
 browser.close()
assert not errors,errors
print(json.dumps({'passed':True,'seconds':round(time.monotonic()-start,2),'results':results,'errors':errors,'screenshots':str(output)}))
