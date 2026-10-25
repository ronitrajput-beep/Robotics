"""Paired contact diagnosis on the same route; fixed start time is test-only."""
from pathlib import Path
import argparse,json
from crawler_cleaning_controller import mission,ROOT


def run(directory,model):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    clock=[0.]
    def observe(m,d,state,coverage):clock[0]=float(d.time)
    result=mission(duration=500,guarded=True,guarded_model_path=model,output=directory/'telemetry.csv.gz',
                   should_move=lambda:clock[0]>=4.,on_sample=observe)
    (directory/'result.json').write_text(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--model',type=Path,required=True);a=p.parse_args();run(a.output_dir,a.model)
