"""Optional download of assignment inputs, kept out of the submission Git tree."""
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile
import io

ROOT=Path(__file__).resolve().parents[1]/'sources'
BASE='https://code.s3.yandex.net/solution-architect/'
ROOT.mkdir(exist_ok=True)
for name in ['AS-IS.puml','OrderProcessingService.java','interview-business.md','interview-support.md']:
    with urlopen(BASE+name, timeout=30) as response:
        (ROOT/name).write_bytes(response.read())
with urlopen(BASE+'interview.zip', timeout=30) as response:
    archive=ZipFile(io.BytesIO(response.read()))
    dest=(ROOT/'developer-interviews').resolve()
    dest.mkdir(exist_ok=True)
    for item in archive.infolist():
        target=(dest/item.filename).resolve()
        if not target.is_relative_to(dest): raise ValueError('Unsafe archive path')
        if not item.is_dir():
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(archive.read(item))
print('Downloaded; run tools/validate.py to compare with the recorded source hashes.')
