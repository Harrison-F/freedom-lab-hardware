import json,sys,time,tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
url=sys.argv[1] if len(sys.argv)>1 else 'https://hardware.freedomlab.nyc/'
start=time.monotonic();errors=[];results=[];output=Path(tempfile.mkdtemp(prefix='hardware-qa-'))
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True)
 for width in [1280,390]:
  page=browser.new_page(viewport={'width':width,'height':900})
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('console',lambda e:errors.append(e.text) if e.type=='error' else None)
  page.set_default_timeout(8000)
  response=page.goto(url,wait_until='domcontentloaded',timeout=20000);assert response.status==200
  page.locator('#collections .display-card').first.wait_for();page.locator('#bom-rows .procurement-card').first.wait_for()
  count=page.locator('#collections .display-card').count();assert count==42
  assert page.locator('#collections .display-card img').count()==40
  page.locator('#collections .display-card img').evaluate_all('(imgs)=>Promise.all(imgs.map(i=>{i.loading="eager";return i.decode()}))')
  assert page.locator('#bom-rows .procurement-card').count()==13
  assert page.locator('#bom-rows img').count()==12
  for image in page.locator('#bom-rows img').all():
   identity=image.locator('xpath=ancestor::article[@data-build-id]').get_attribute('data-build-id')
   assert image.get_attribute('src')==page.locator('#collections [data-id="'+identity+'"] img').get_attribute('src')
  page.locator('#bom-rows img').evaluate_all('(imgs)=>Promise.all(imgs.map(i=>i.decode()))')
  assert page.locator('#bom-rows').evaluate('(e)=>getComputedStyle(e).gridTemplateColumns.split(" ").length')==(4 if width==1280 else 1)
  page.locator('#bom-rows').evaluate('(e)=>e.scrollIntoView({block:"start"})')
  page.screenshot(path=str(output/f'{width}-initial-image-comparison.png'))
  columns=page.locator('.display-template').first.evaluate('(e)=>getComputedStyle(e).gridTemplateColumns.split(" ").length')
  assert columns==(4 if width==1280 else 1)
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
  page.locator('#search').fill('Waveshare');assert page.locator('#collections .display-card:visible').count()<count
  page.locator('#reset').click();assert page.locator('#collections .display-card:visible').count()==count
  for selector in ['#recommendation-filter','#status-filter','#category-filter','#scope-filter']:
   value=page.locator(selector+' option').nth(1).get_attribute('value');page.locator(selector).select_option(value);assert page.locator('#collections .display-card:visible').count()>0;page.locator('#reset').click()
  page.locator('#collections .research-evidence summary').first.click();assert page.locator('#collections .research-evidence').first.get_attribute('open') is not None
  page.locator('#collections .display-card').first.hover();page.mouse.move(0,0)
  assert page.locator('#bom-rows .procurement-card:visible').count()==13
  for mode in ['known','affordability','fastest','fit']:
   page.locator('#cost-sort').select_option(mode)
   if mode in ['affordability','fastest']:assert 'No defensible' in page.locator('#ranking-note').inner_text()
   if mode=='known':assert 'NOT an affordability ranking' in page.locator('#ranking-note').inner_text()
  assert '$29.89 known parts' in page.locator('[data-build-id="ALT01"]').inner_text()
  assert '$44.40 known parts + quoted freight only' in page.locator('[data-build-id="KIT01"]').inner_text()
  row=page.locator('[data-build-id="ALT02"]');row.locator('summary').last.click()
  assert '$64.99' in row.inner_text() and '2026-09-28' in row.inner_text()
  row.locator('.offer').filter(has_text='$64.99').last.evaluate('(e)=>e.scrollIntoView({block:"start"})')
  page.screenshot(path=str(output/f'{width}-shipping-offer.png'))
  row.locator('summary').last.click()
  row=page.locator('[data-build-id="ALT01"]');row.locator('summary').last.click()
  assert 'Prime conditional' in row.inner_text() and 'battery inclusion unverified' in row.inner_text()
  row.locator('.offer').filter(has_text='1.54 fast board near-match').last.evaluate('(e)=>e.scrollIntoView({block:"start"})')
  page.screenshot(path=str(output/f'{width}-near-match.png'))
  row.locator('summary').last.click()
  page.locator('#bom-rows summary').first.click();assert page.locator('#bom-rows details').first.get_attribute('open') is not None
  assert 'Adafruit 4474' in page.locator('[data-build-id="ALT01"]').inner_text()
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
  page.locator('#github-link').focus()
  with page.expect_popup() as pop:page.keyboard.press('Enter')
  popup=pop.value;assert popup.url.startswith('https://github.com/Harrison-F/freedom-lab-hardware');popup.close()
  page.locator('#bom-rows').evaluate('(e)=>e.scrollIntoView({block:"start"})');page.screenshot(path=str(output/f'{width}-comparison.png'))
  page.locator('#collections .research-evidence summary').first.click()
  page.locator('#collections .display-card').first.evaluate('(e)=>e.scrollIntoView({block:"start"})')
  page.locator('#collections .display-card img').first.evaluate('(e)=>e.decode()')
  page.screenshot(path=str(output/f'{width}-cards.png'))
  results.append({'width':width,'columns':columns,'cards':count,'url':page.url});page.close()
 browser.close()
assert not errors,errors
print(json.dumps({'passed':True,'seconds':round(time.monotonic()-start,2),'results':results,'errors':errors,'screenshots':str(output)}))
