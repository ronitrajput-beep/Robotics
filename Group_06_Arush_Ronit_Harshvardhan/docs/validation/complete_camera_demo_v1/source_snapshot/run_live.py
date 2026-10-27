"""Run the actual autonomous combined mission in an interactive MuJoCo window.

Mac: MUJOCO_GL=cgl mjpython src/run_live.py
Linux desktop: MUJOCO_GL=glfw python src/run_live.py
"""
import os,sys
os.environ.setdefault('MUJOCO_GL','cgl' if sys.platform=='darwin' else 'glfw')
import argparse
from datetime import datetime
from pathlib import Path
from vision_mission import run,ROOT


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--duration',type=float,default=1000.)
    parser.add_argument('--speed',type=float,default=1.,help='Wall-clock playback target; 1=real time, 2=twice as fast. Physics timestep is unchanged.')
    parser.add_argument('--scenario',choices=['combined','clean','subthreshold'],default='combined')
    args=parser.parse_args()
    if not 0<args.speed<=20:parser.error('--speed must be greater than zero and at most 20')
    directory=args.output_dir or ROOT/'analytics'/('live_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    print('Starting actual camera/controller mission. Logs:',directory,flush=True)
    run(directory,scenario=args.scenario,duration=args.duration,save_images=False,live_viewer=True,viewer_speed=args.speed)


if __name__=='__main__':main()
