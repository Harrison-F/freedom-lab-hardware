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
  response=page.goto(url,wait_until='networkidle');assert response.status==200
  page.locator('.display-card').first.wait_for();page.locator('#bom-rows tr').first.wait_for()
  count=page.locator('.display-card').count();assert count>0
  columns=page.locator('.display-template').first.evaluate('(e)=>getComputedStyle(e).gridTemplateColumns.split(" ").length')
  assert columns==(4 if width==1280 else 1)
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
  page.locator('#search').fill('Waveshare');assert page.locator('.display-card:visible').count()<count
  page.locator('#reset').click();assert page.locator('.display-card:visible').count()==count
  for selector in ['#recommendation-filter','#status-filter','#category-filter','#scope-filter']:
   value=page.locator(selector+' option').nth(1).get_attribute('value');page.locator(selector).select_option(value);assert page.locator('.display-card:visible').count()>0;page.locator('#reset').click()
  page.locator('.research-evidence summary').first.click();assert page.locator('.research-evidence').first.get_attribute('open') is not None
  page.locator('.display-card').first.hover();page.mouse.move(0,0)
  for mode in ['affordability','fastest','fit']:page.locator('#cost-sort').select_option(mode)
  page.locator('#bom-rows summary').first.click();assert page.locator('#bom-rows details').first.get_attribute('open') is not None
  page.locator('#github-link').focus()
  with page.expect_popup() as pop:page.keyboard.press('Enter')
  popup=pop.value;assert popup.url.startswith('https://github.com/Harrison-F/freedom-lab-hardware');popup.close()
  page.locator('#cost-sort').scroll_into_view_if_needed();page.screenshot(path=str(output/f'{width}-comparison.png'))
  page.locator('.display-card').first.scroll_into_view_if_needed();page.screenshot(path=str(output/f'{width}-cards.png'))
  results.append({'width':width,'columns':columns,'cards':count,'url':page.url});page.close()
 browser.close()
assert not errors,errors
print(json.dumps({'passed':True,'seconds':round(time.monotonic()-start,2),'results':results,'errors':errors,'screenshots':str(output)}))
