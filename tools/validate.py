"""Artifact integrity checks; does not simulate production or approve the design."""
from pathlib import Path
from urllib.parse import unquote
import hashlib, json, re, sys
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8')

ROOT=Path(__file__).resolve().parents[1]
required=['Task1/requirements.md','Task1/stakeholders.md','Task1/interview-scenarios.md','Task1/interview-analysis.md',
 'Task2/architecture-canvas.md','Task2/as-is-analysis.md','Task2/as-is.drawio','Task2/as-is.svg','Task2/as-is.png',
 'Task3/transformation.md','Task3/to-be.drawio','Task3/to-be.svg','Task3/to-be.png',
 'Task4/migration-roadmap.md','Task4/cutover-plan.md','README.md','REQUIREMENTS_MATRIX.md','sources/README.md','sources/sha256.json']
errors=[]
for name in required:
    p=ROOT/name
    if not p.exists() or not p.stat().st_size: errors.append('Missing/empty: '+name)
mds=list(ROOT.glob('*.md'))+list(ROOT.glob('Task*/*.md'))+list(ROOT.glob('sources/*.md'))
links=0
for p in mds:
    content=p.read_text(encoding='utf-8')
    if re.search(r'\b(TODO|TBD|FIXME)\b',content): errors.append('Unresolved placeholder: '+str(p.relative_to(ROOT)))
    for target in re.findall(r'\]\(([^)]+)\)',content):
        if target.startswith(('http://','https://','#','mailto:')): continue
        path=unquote(target.split('#')[0])
        if path and not (p.parent/path).is_file(): errors.append(f'Broken link: {p.relative_to(ROOT)} → {path}')
        links+=1
for p in ROOT.glob('Task*/*.drawio'):
    tree=ET.parse(p); cells=tree.findall('.//mxCell'); ids=[c.get('id') for c in cells]
    if len(ids)!=len(set(ids)): errors.append('Duplicate mxCell id: '+p.name)
    for c in cells:
        if c.get('edge')=='1':
            for attr in ('source','target'):
                if c.get(attr) not in ids: errors.append('Missing edge endpoint: '+p.name)
            if not c.get('value'): errors.append('Unlabelled edge: '+p.name)
    if len([c for c in cells if c.get('edge')=='1'])<8: errors.append('Incomplete diagram: '+p.name)
for p in ROOT.glob('Task*/*.svg'): ET.parse(p)
hashes=json.loads((ROOT/'sources/sha256.json').read_text(encoding='utf-8'))
for name,expected in hashes.items():
    if hashlib.sha256((ROOT/'sources'/name).read_bytes()).hexdigest()!=expected: errors.append('Source checksum mismatch: '+name)
matrix=(ROOT/'REQUIREMENTS_MATRIX.md').read_text(encoding='utf-8')
expected_ids=[f'T1-{i:02}' for i in range(1,12)]+[f'T2-{i:02}' for i in range(1,5)]+[f'T3-{i:02}' for i in range(1,6)]+[f'T4-{i:02}' for i in range(1,4)]+[f'S-{i:02}' for i in range(1,5)]
for key in expected_ids:
    if not re.search(r'\| '+key+r' \|',matrix): errors.append('Missing coverage row: '+key)
if errors:
    print('\n'.join(errors)); raise SystemExit(1)
print(f'PASS: {len(required)} required artifacts; {links} local links; 2 drawio + 2 SVG parsed; {len(hashes)} source hashes; {len(expected_ids)} coverage rows.')
print('Production tests, stakeholder approval, numeric SLOs and deployment are not asserted by this check.')
