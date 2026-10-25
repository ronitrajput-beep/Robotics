"""Make a compact review bundle; bulk raw telemetry stays in the sharing repo."""
from pathlib import Path
from zipfile import ZipFile, ZIP_STORED, ZIP_DEFLATED
from datetime import datetime,timezone
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
def package():
    audit=json.loads((ROOT/'submission/deliverable_checks.json').read_text());files=set()
    def add(pattern):files.update(p for p in ROOT.glob(pattern) if p.is_file())
    for pattern in ['requirements.txt','src/*.py','models/*.xml','tests/*.py','tests/fixtures/*.json','analytics/final_business_model.py','analytics/final_business_inputs.json','analytics/analyse_final_validation.py','analytics/analyse_tracking_benchmark.py','submission/*.py','submission/*.md','submission/*.json','submission/*.txt','submission/templates/*.docx','submission/source_audit/*','submission/figures/*.png']:
        add(pattern)
    files.discard(ROOT/'submission/BUNDLE_MANIFEST.json')
    # The full repository retains legacy scaffold tests. The compact bundle
    # carries the focused current-system tests and all of their small fixtures.
    for name in ['test_figures.py','test_geometry_economics.py']:files.discard(ROOT/'tests'/name)
    add('tests/fixtures/*.png')
    for fixture in json.loads((ROOT/'tests/fixtures/rgb_components_before_optimisation.json').read_text()):add(fixture['image'])
    for name in ['model.xml','lift_state.npz']:add('analytics/collection_contact_trace/'+name)
    for filename in ['MDRIIA_Group_06_Technical_Dossier.docx','MDRIIA_Group_06_Technical_Dossier.pdf','COLLECTION_AND_EXTERNAL_DOCK.md','PANEL_CAMERA_RIGS.md','RUN_AND_DEMO.md','AI_AUDIT.md']:
        add('docs/'+filename)
    for filename in ['cinematic_cleaning.mp4','solid_contact_slow_motion.mp4','README.md','result.json','independent_collection_checks.json','headless_recording_comparison.json','video_decode_check.json','collection_evidence.pdf','collection_evidence.png','solid_contact_closeup.png','solid_in_tray.png','brush_closeup.png','dock_empty_bin.png','dock_service.png']:
        add('docs/validation/collection_demo_v6/'+filename)
    for filename in ['panel_camera_tour.mp4','README.md','video_decode_check.json']:add('docs/validation/panel_camera_rig_v4/'+filename)
    for filename in ['protocol.json','statistics.json','summary.csv']:add('analytics/tracking_benchmark/'+filename)
    for filename in ['result.json','independent_collection_checks.json']:add('analytics/collection_pilot8/'+filename)
    business='business_nominal_draft_v1' if audit['preliminary'] else 'final_business_v1'
    add('analytics/'+business+'/*')
    if not audit['preliminary']:
        for filename in ['protocol.json','statistics.json','summary.csv','batch_complete.json','trace_audit.json']:add('analytics/final_validation_v1/'+filename)
        add('analytics/final_validation_v1/figures/*');add('analytics/final_validation_v1/models/*')
    else:add('analytics/final_validation_v1/protocol.json')
    # The manifest is made from exactly the bytes written, including any status snapshot.
    target=ROOT/'submission/Group06_Submission_Bundle.zip';temporary=target.with_suffix('.zip.part');manifest=[]
    with ZipFile(temporary,'w',compression=ZIP_DEFLATED,compresslevel=5) as archive:
        for path in sorted(files):
            content=path.read_bytes();relative=str(path.relative_to(ROOT))
            archive.writestr(ROOT.name+'/'+relative,content,compress_type=ZIP_STORED if path.suffix in ('.mp4','.docx','.pdf','.png') else ZIP_DEFLATED)
            manifest.append({'path':relative,'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()})
        record={'created_utc':datetime.now(timezone.utc).isoformat(),'status':'PRELIMINARY REVIEW COPY: final validation pending' if audit['preliminary'] else 'TECHNICAL REVIEW COPY: unsigned personal fields and team submission actions remain','bulk_raw_data':'Full real 500 Hz trial logs are retained separately in the personal Robotics repository; see submission/REPRODUCE.md. Archive is not a substitute for raw data.','files':manifest}
        archive.writestr(ROOT.name+'/submission/BUNDLE_MANIFEST.json',json.dumps(record,indent=2)+'\n')
    with ZipFile(temporary) as archive:assert archive.testzip() is None
    assert temporary.stat().st_size<95*1024**2,'Keep the compact download below GitHub single-file limit'
    temporary.replace(target)
    (ROOT/'submission/BUNDLE_MANIFEST.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'bundle':str(target),'bytes':target.stat().st_size,'files':len(manifest),'preliminary':audit['preliminary']},indent=2));return target

if __name__=='__main__':package()
