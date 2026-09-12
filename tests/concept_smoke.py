"""Reusable desktop/mobile smoke for six concept renders and adjacent catalog."""
import sys,pathlib,json,zipfile,io,time,os
from playwright.sync_api import sync_playwright
url=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:9798/'
out=pathlib.Path(os.environ.get('CONCEPT_QA_DIR','/tmp/voice-concept-qa'));out.mkdir(parents=True,exist_ok=True)
started=time.monotonic();results=[]
with sync_playwright() as p:
 browser=p.chromium.launch()
 for label,width,height in [('desktop',1440,1000),('mobile',390,844)]:
  context=browser.new_context(viewport={'width':width,'height':height},accept_downloads=True);page=context.new_page();errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
  page.goto(url,wait_until='networkidle',timeout=45000)
  assert page.locator('.concept-device').count()==3 and page.locator('.concept-render').count()==6
  images=page.locator('.concept-render img')
  for i in range(6):
   image=images.nth(i);image.scroll_into_view_if_needed();image.evaluate('(im)=>im.decode()')
   assert image.evaluate('(im)=>im.naturalWidth===1200 && im.naturalHeight===1200')
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  pairs=page.locator('.concept-pair figure');a=pairs.nth(0).bounding_box();b=pairs.nth(1).bounding_box()
  assert (abs(a['y']-b['y'])<2 and b['x']>a['x']) if width>600 else (b['y']>=a['y']+a['height'] and abs(a['x']-b['x'])<2)
  page.locator('.concept-render').first.hover();page.locator('.concept-render').first.focus()
  with page.expect_popup() as popup:page.keyboard.press('Enter')
  large=popup.value;large.wait_for_load_state();assert 'compact154-finished.webp' in large.url
  assert large.locator('img').evaluate('(im)=>im.naturalWidth')==1200;large.close()
  with page.expect_download() as dl:page.get_by_role('link',name='Editable Blender files + script').click()
  download=dl.value;assert download.failure() is None
  raw=pathlib.Path(download.path()).read_bytes()
  with zipfile.ZipFile(io.BytesIO(raw)) as archive:
   assert len([n for n in archive.namelist() if n.endswith('.blend')])==6
   assert 'render_devices.py' in archive.namelist() and archive.testzip() is None
  page.get_by_role('link',name='Device catalog ↓',exact=True).click();assert page.url.endswith('#collections')
  assert page.locator('.hardware-row').count()==36
  page.locator('#search').fill('Waveshare');assert 0<page.locator('.hardware-row:visible').count()<36
  page.locator('#search').fill('');assert page.locator('.hardware-row:visible').count()==36
  page.locator('#concept-renders').scroll_into_view_if_needed()
  page.locator('#concept-renders').screenshot(path=str(out/(label+'-gallery.png')))
  page.locator('#concept-compact154').screenshot(path=str(out/(label+'-first-concept.png')))
  assert not errors,errors
  results.append({'viewport':label,'width':width,'render_images':6,'devices':3,'catalog_items':36,'download_bytes':len(raw),'console_errors':errors,'overflow':False})
  context.close()
 browser.close()
report={'passed':True,'url':url,'elapsed_seconds':round(time.monotonic()-started,2),'results':results}
(out/'results.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
