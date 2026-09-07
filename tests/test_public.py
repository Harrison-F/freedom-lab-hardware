import json,re,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def audit_text(text):
 patterns=[r'/Users/[^\s"<>]+',r'(?i)bookmark',r'(?i)purchased inventory',r'(?i)existing M5',r'(?i)observed-sync',r'(?i)archive_posts',r'(?i)user-approved',r'(?i)explicitly supplied',r'gh[pousr]_[A-Za-z0-9]{20,}',r'sk-[A-Za-z0-9]{24,}',r'-----BEGIN .*PRIVATE KEY',r'(?i)(password|token|secret)\s*[:=]\s*["\'][^"\']{8,}']
 for pattern in patterns: assert not re.search(pattern,text),f'Privacy check failed: {pattern}'
def validate_procurement(d):
 assert d['schema_version']==1 and d['destination_zip']=='10014' and d['quantity']==1 and d['currency']=='USD'
 ids=set()
 for r in d['builds']:
  assert r['id'] not in ids;ids.add(r['id'])
  for k in ['price_usd','wifi_total_usd','cellular_total_usd','shipping_usd','tax_usd','known_parts_subtotal_usd','known_shipping_usd','known_parts_plus_quoted_shipping_usd','delivered_total_usd']:
   v=r[k];assert v is None or (type(v) in (int,float) and math.isfinite(v) and v>=0)
  for k in ['purchase_list','assembly_list','cellular_additions','sources']:assert isinstance(r[k],list) and r[k]
  assert isinstance(r['complete'],bool)
  if r['complete']:assert r['wifi_total_usd'] is not None
  for k in ['arrival_earliest','arrival_latest']:
   assert r[k] is None or re.fullmatch(r'\d{4}-\d{2}-\d{2}',r[k])
  if r['arrival_latest']:assert r['delivery_status']
  for s in r['sources']:assert s['url'].startswith('https://')
  assert r['build_status'] and r['bom'] and r['shipments']
  def valid_money(v):return v is None or (type(v) in (int,float) and math.isfinite(v) and v>=0)
  for p in r['bom']+[p for a in r['alternatives'] for p in a['bom']]:
   assert p['quantity']>=1 and valid_money(p['unit_price_usd']) and p['role']
   assert p['source_url'] is None or p['source_url'].startswith('https://')
   if p['unit_price_usd'] is not None:assert p['source_url'] or p['unit_price_usd']==0
  if r['known_parts_subtotal_usd'] is not None:
   assert round(sum(p['quantity']*(p['unit_price_usd'] or 0) for p in r['bom']),2)==r['known_parts_subtotal_usd']
  for s in r['shipments']:
   assert valid_money(s['shipping_usd']) and s['status'] and s['scope'] and s['note'] and s['source_url'].startswith('https://')
  for o in r['offers']:
   assert all(valid_money(o[k]) for k in ['price_usd','shipping_usd','item_plus_shipping_usd'])
   assert o['source_url'].startswith('https://') and o['match'] and o['status']
   if o['item_plus_shipping_usd'] is not None:assert round(o['price_usd']+o['shipping_usd'],2)==o['item_plus_shipping_usd']
  if r['known_parts_plus_quoted_shipping_usd'] is not None:
   assert round(r['known_parts_subtotal_usd']+r['known_shipping_usd'],2)==r['known_parts_plus_quoted_shipping_usd']
  if r['delivered_total_usd'] is not None:
   assert r['complete'] and all(r[k] is not None for k in ['wifi_total_usd','shipping_usd','tax_usd'])
   assert round(r['wifi_total_usd']+r['shipping_usd']+r['tax_usd'],2)==r['delivered_total_usd']
def main():
 allowed=json.loads((ROOT/'publish-allowlist.json').read_text())
 actual=sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts)
 assert actual==allowed,'Exact publish allowlist mismatch'
 for relative in allowed:
  p=ROOT/relative;assert not p.is_symlink()
  if p.suffix!='.webp' and relative!='tests/test_public.py':audit_text(p.read_text())
 d=json.loads((ROOT/'site/data.json').read_text());assert len({i['id'] for i in d['items']})==len(d['items'])
 for i in d['items']:
  for s in i['sources']:assert s['url'].startswith('https://')
  if i['image']:assert (ROOT/'site'/i['image']['path'].replace('../','',1)).is_file()
 procurement=json.loads((ROOT/'site/procurement.json').read_text());validate_procurement(procurement)
 rows={r['id']:r for r in procurement['builds']};assert len(rows)==13
 assert len(d['items'])==42 and sum(bool(i['image']) for i in d['items'])==40
 assert rows['ALT01']['known_parts_subtotal_usd']==29.89 and not rows['ALT01']['complete']
 assert rows['KIT01']['known_parts_plus_quoted_shipping_usd']==44.4
 assert rows['BM12']['alternatives'][0]['known_parts_subtotal_usd']==74.35
 assert rows['BM32']['known_parts_subtotal_usd']==127.88
 assert any(o['item_plus_shipping_usd']==64.99 and o['arrival_latest']=='2026-09-28' for o in rows['ALT02']['offers'])
 assert any(o['arrival_latest']=='2026-09-09' and 'near-match' in o['match'] for o in rows['ALT01']['offers'])
 assert all(r['arrival_latest'] is None and r['delivered_total_usd'] is None for r in rows.values())
 html=(ROOT/'site/index.html').read_text()
 assert 'id="bom-rows" class="display-template"' in html and '<table' not in html
 assert "items.get(r.id)" in (ROOT/'site/static/procurement.js').read_text()
 assert "querySelectorAll('#collections .display-card')" in (ROOT/'site/static/voice-device.js').read_text()
 for name in ['styles.css','display-template.css']:assert (ROOT/'shared'/name).read_bytes()==(ROOT/'site/static'/name).read_bytes()
 assert 'repeat(4, minmax(0, 1fr))' in (ROOT/'shared/display-template.css').read_text()
 print(json.dumps({'passed':True,'allowlisted_files':len(allowed),'research_items':len(d['items']),'schema':'valid','shared_css':'byte-identical'}))
if __name__=='__main__':main()
