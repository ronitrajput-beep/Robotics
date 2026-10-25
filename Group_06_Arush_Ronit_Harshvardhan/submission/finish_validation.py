"""Wait for the frozen batch, preserve completed data, then build review files.

This never signs or submits to the faculty repo/Teams/LinkedIn. --publish only
uses the already-authorised personal sharing remote on the existing branch.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess,sys,time,traceback

ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent
BATCH=ROOT/'analytics/final_validation_v1';STATUS=ROOT/'submission/STATUS.json'
SIM='/workspace/venvs/group06/bin/python';DOC=sys.executable
ENV={**os.environ,'MUJOCO_GL':'egl','LP_NUM_THREADS':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','XDG_CACHE_HOME':'/workspace/.cache','MPLCONFIGDIR':'/workspace/.cache/group06-matplotlib'}

def update(phase,**extras):
    value={'updated_utc':datetime.now(timezone.utc).isoformat(),'phase':phase,'batch':'analytics/final_validation_v1','technical_files':'docs/MDRIIA_Group_06_Technical_Dossier.docx and .pdf','human_actions':'Member authorship/learning/declarations, actual peer reviews, team video/LinkedIn, signatures and faculty/Teams submission remain required.',**extras}
    temporary=STATUS.with_suffix('.json.part');temporary.write_text(json.dumps(value,indent=2)+'\n');temporary.replace(STATUS);print(json.dumps(value),flush=True)

def command(argv,cwd=ROOT):
    print('RUN',argv,flush=True);return subprocess.run(argv,cwd=cwd,env=ENV,check=True,text=True)

def git(*args):return subprocess.check_output(['git',*args],cwd=REPO,text=True).strip()

def commit_paths(paths,message,publish):
    if not publish:return
    if git('branch','--show-current')!='feat/e052-waterless-rotary-bru':raise RuntimeError('Unexpected branch; refusing automatic Git mutation')
    if git('diff','--cached','--name-only'):raise RuntimeError('Existing staged work needs review; refusing to include it')
    paths=[str(p.relative_to(REPO)) for p in paths if p.exists()]
    if not paths:return
    command(['git','add','--',*paths],REPO)
    if git('diff','--cached','--name-only'):
        command(['git','commit','-m',message],REPO)
    command(['git','push','origin','HEAD'],REPO)

def completed():
    result=[];path=BATCH/'completed_trials.jsonl'
    if path.exists():
        for line in path.read_text().splitlines():
            try:result.append(json.loads(line))
            except json.JSONDecodeError:pass # a single in-flight final line
    return result

def run(publish=False,batch_pid=None):
    marker=ROOT/'submission/published_trials.json';pushed=set(json.loads(marker.read_text()) if marker.exists() else [])
    started=time.monotonic();last_update=0.
    while True:
        rows=completed();done=(BATCH/'batch_complete.json').exists()
        waiting=[r for r in rows if f"{r['tilt_deg']:g}/{r['variant']}_{r['seed']}" not in pushed]
        if time.monotonic()-last_update>=60 or done:
            update('final-validation-running' if not done else 'final-validation-finished-analysis-pending',completed=len(rows),planned=180,statuses={s:sum(r['status']==s for r in rows) for s in sorted({r['status'] for r in rows})},review_files_are_preliminary=not (ROOT/'analytics/final_business_v1/results.json').exists())
            last_update=time.monotonic()
        if publish and (len(waiting)>=10 or done and waiting):
            # trial_summary is written after the CSV and per-run log close.
            chosen=waiting[:10];paths=[]
            for row in chosen:
                key=f"{row['tilt_deg']:g}/{row['variant']}_{row['seed']}"
                paths += [BATCH/f"tilt_{row['tilt_deg']:g}"/f"{row['variant']}_{row['seed']}",BATCH/'logs'/f"tilt_{row['tilt_deg']:g}_{row['variant']}_{row['seed']}.log"]
                pushed.add(key)
            marker.write_text(json.dumps(sorted(pushed),indent=2)+'\n')
            paths += [BATCH/'protocol.json',BATCH/'models',BATCH/'source_snapshot',marker,STATUS]
            commit_paths(paths,f'Preserve {len(pushed)} completed frozen full-mission trials',publish)
        if done:
            if waiting and publish:continue
            break
        if batch_pid is not None:
            try:os.kill(batch_pid,0)
            except ProcessLookupError:raise RuntimeError('Batch process stopped before batch_complete.json; partial runs preserved')
        if time.monotonic()-started>20*3600:raise RuntimeError('20-hour batch monitor limit reached; inspect before the submission deadline')
        time.sleep(20)
    if not (BATCH/'statistics.json').exists():command([SIM,'analytics/analyse_final_validation.py',str(BATCH)])
    if not (ROOT/'analytics/final_business_v1/results.json').exists():command([SIM,'analytics/final_business_model.py','--validation-dir',str(BATCH),'--output-dir','analytics/final_business_v1'])
    update('building-final-technical-review-files',completed=len(rows),planned=180)
    field_audit=json.loads((ROOT/'submission/dossier_field_audit.json').read_text())
    existing=ROOT/'docs/MDRIIA_Group_06_Technical_Dossier.docx'
    if hashlib.sha256(existing.read_bytes()).hexdigest()!=field_audit['dossier_sha256']:
        raise RuntimeError('Dossier was edited after the generated review copy; preserving member edits. Merge completed statistics/business results into that copy before rebuilding.')
    command([DOC,'submission/build_dossier.py'])
    command(['soffice','-env:UserInstallation=file:///tmp/group06_lo_final_submission','--headless','--convert-to','pdf','--outdir','docs','docs/MDRIIA_Group_06_Technical_Dossier.docx'])
    command([DOC,'submission/check_deliverables.py'])
    update('technical-review-files-ready-human-actions-remain',completed=len(rows),planned=180,review_files_are_preliminary=False)
    command([DOC,'submission/package_submission.py'])
    (ROOT/'docs/CONTINUE_HERE.md').open('a').write('\n\n## Frozen final validation and technical review bundle completed\n\nAll 180 frozen attempts are retained in analytics/final_validation_v1. Read statistics.json and trace_audit.json for actual outcomes; no success count is assumed here. Business outputs are analytics/final_business_v1, calibrated to all 30 nominal proposed attempts including failures. The original Word form, matching PDF and compact ZIP have been rebuilt and checked; submission/STATUS.json and deliverable_checks.json record status. Yellow personal controls, signatures, real peer reviews and final team video/LinkedIn remain human actions. Nothing has been signed or submitted to the faculty repository or Teams.\n')
    paths=[BATCH,ROOT/'analytics/final_business_v1',ROOT/'docs/MDRIIA_Group_06_Technical_Dossier.docx',ROOT/'docs/MDRIIA_Group_06_Technical_Dossier.pdf',ROOT/'docs/CONTINUE_HERE.md',ROOT/'submission']
    commit_paths(paths,'Complete frozen evaluation, business analysis and technical review bundle',publish)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');p.add_argument('--batch-pid',type=int);a=p.parse_args()
    try:run(a.publish,a.batch_pid)
    except Exception as error:
        traceback.print_exc();update('needs-attention',error=repr(error),review_files_are_preliminary=not (ROOT/'analytics/final_business_v1/results.json').exists());raise
