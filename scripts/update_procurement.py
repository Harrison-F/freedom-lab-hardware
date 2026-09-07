import json,sys,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('checks',ROOT/'tests/test_public.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=ROOT/'site/procurement.json';data=json.loads(p.read_text());updates=json.loads(Path(sys.argv[1]).read_text())
byid={r['id']:r for r in data['builds']}
for row in updates['builds']:
 assert row['id'] in byid,'Unknown research ID';byid[row['id']]=row
candidate={**data,'builds':list(byid.values())}
for k in ['status','methodology']:
 if k in updates:candidate[k]=updates[k]
m.validate_procurement(candidate)
text=json.dumps(candidate,indent=2)+'\n';m.audit_text(text)
tmp=p.with_suffix('.tmp');tmp.write_text(text);tmp.replace(p)
print('Validated and merged',len(updates['builds']),'reviewed public rows')
