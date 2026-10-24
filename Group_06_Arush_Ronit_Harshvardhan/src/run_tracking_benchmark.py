"""Predeclared 30-second tracking comparison; NOT full cleaning evaluation."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import argparse,json,csv
from crawler_cleaning_controller import mission,ROOT

def run_one(job):
    variant,seed,folder=job
    return mission(seed,Path(folder)/f'{variant}_{seed}_real_trials.csv.gz',30,False,variant)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--runs',type=int,default=30);p.add_argument('--workers',type=int,default=4);a=p.parse_args()
    folder=ROOT/'analytics/tracking_benchmark'
    folder.mkdir(exist_ok=False)
    protocol={'scope':'30-second initial-sweep tracking only; not whole-mission efficacy','runs_per_variant':a.runs,'randomisation':'initial panel x/y independent uniform +/- .01 m','seeds':{'baseline':list(range(1000,1000+a.runs)),'proposed':list(range(2000,2000+a.runs))},'primary_metric':'path_tracking_rmse_m','test':'two-sided Welch; run is experimental unit','logging_hz':500}
    (folder/'protocol.json').write_text(json.dumps(protocol,indent=2))
    jobs=[(v,s,str(folder)) for v,seeds in protocol['seeds'].items() for s in seeds];results=[]
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        for f in as_completed([pool.submit(run_one,j) for j in jobs]):
            results.append(f.result());(folder/'results.json').write_text(json.dumps(results,indent=2))
            print(f'FINISHED {len(results)}/{len(jobs)}',flush=True)
    with (folder/'summary.csv').open('w',newline='') as out:
        w=csv.DictWriter(out,fieldnames=results[0]);w.writeheader();w.writerows(results)
