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
  for k in ['price_usd','wifi_total_usd','cellular_total_usd','shipping_usd','tax_usd']:
   v=r[k];assert v is None or (type(v) in (int,float) and math.isfinite(v) and v>=0)
  for k in ['purchase_list','assembly_list','cellular_additions','sources']:assert isinstance(r[k],list) and r[k]
  assert isinstance(r['complete'],bool)
  if r['complete']:assert r['wifi_total_usd'] is not None
  for k in ['arrival_earliest','arrival_latest']:
   assert r[k] is None or re.fullmatch(r'\d{4}-\d{2}-\d{2}',r[k])
  if r['arrival_latest']:assert r['delivery_status']
  for s in r['sources']:assert s['url'].startswith('https://')
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
 validate_procurement(json.loads((ROOT/'site/procurement.json').read_text()))
 for name in ['styles.css','display-template.css']:assert (ROOT/'shared'/name).read_bytes()==(ROOT/'site/static'/name).read_bytes()
 assert 'repeat(4, minmax(0, 1fr))' in (ROOT/'shared/display-template.css').read_text()
 print(json.dumps({'passed':True,'allowlisted_files':len(allowed),'research_items':len(d['items']),'schema':'valid','shared_css':'byte-identical'}))
if __name__=='__main__':main()
