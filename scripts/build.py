import argparse,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--shared-source',type=Path);a=p.parse_args()
for name in ['styles.css','display-template.css']:
 if a.shared_source:
  source=a.shared_source/name
  assert source.is_file() and not source.is_symlink()
  shutil.copyfile(source,ROOT/'shared'/name)
 shutil.copyfile(ROOT/'shared'/name,ROOT/'site/static'/name)
print('Built two canonical shared CSS assets; data unchanged.')
