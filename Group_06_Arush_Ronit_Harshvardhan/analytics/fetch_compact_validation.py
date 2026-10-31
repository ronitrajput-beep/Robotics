"""Fetch the six actual primary-window files for the light jury code/documents package.

Explicit invocation is required: approximately 200 MB. Existing files
are checked, never overwritten with a different dataset.
"""
from pathlib import Path
import argparse, hashlib, json, urllib.request

ROOT=Path(__file__).resolve().parents[1]


def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download',action='store_true',help='Explicitly download the full original streams')
    args=parser.parse_args()
    manifest=json.loads((ROOT/'analytics/COMPACT_DOWNLOAD_MANIFEST.json').read_text())
    print(f"{len(manifest['files'])} primary-window files; {sum(i['bytes'] for i in manifest['files'])/1024**2:.1f} MiB")
    if not args.download:return
    for index,item in enumerate(manifest['files'],1):
        path=ROOT/item['relative_path']
        if path.exists():
            if digest(path)!=item['sha256']:raise ValueError(f'Existing data differs: {path}')
            continue
        path.parent.mkdir(parents=True,exist_ok=True);temporary=path.with_name(path.name+'.download')
        if temporary.exists():raise FileExistsError(temporary)
        with urllib.request.urlopen(item['url'],timeout=120) as response, temporary.open('xb') as target:
            while chunk:=response.read(1024*1024):target.write(chunk)
        if digest(temporary)!=item['sha256']:raise ValueError(f'Download hash mismatch: {temporary}')
        temporary.rename(path)
        print(f'{index}/{len(manifest["files"])} verified: {path.name}',flush=True)


if __name__=='__main__':main()
