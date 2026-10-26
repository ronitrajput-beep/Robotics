"""Small source-only update for existing local demo installations."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
names=['crawler_cleaning_controller.py','vision_mission.py','live_mission_viewer.py','run_live.py']
target=ROOT/'submission/Group06_Live_Viewer_Update.zip'
manifest={}
with ZipFile(target,'w',ZIP_DEFLATED) as archive:
    for name in names:
        content=(ROOT/'src'/name).read_bytes();archive.writestr('src/'+name,content)
        manifest['src/'+name]=hashlib.sha256(content).hexdigest()
(ROOT/'submission/LIVE_VIEWER_UPDATE.json').write_text(json.dumps({'scope':'Source-only interactive mission update; no documents, venv, model or experiment data replaced','files':manifest},indent=2)+'\n')
print(target, target.stat().st_size,'bytes')
