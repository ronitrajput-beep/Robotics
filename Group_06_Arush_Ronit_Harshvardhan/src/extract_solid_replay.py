"""Make a labelled slow-motion detail from frames of the completed real-physics video."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image


def extract(directory):
    directory=Path(directory);movie=directory/'cinematic_cleaning.mp4';output=directory/'solid_contact_slow_motion.mp4'
    if output.exists():raise FileExistsError(output)
    # Match the saved same-time frame to its encoded counterpart. Only a small
    # comparison thumbnail is decoded; no state replay or invented motion.
    ref=np.asarray(Image.open(directory/'solid_contact_closeup.png').resize((128,72)),dtype=float)
    decoder=subprocess.Popen(['ffmpeg','-v','error','-i',str(movie),'-vf','scale=128:72','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
    index=0;best=(float('inf'),0)
    while True:
        raw=decoder.stdout.read(128*72*3)
        if not raw:break
        if len(raw)!=128*72*3:raise RuntimeError('Truncated video decode')
        score=float(np.mean(abs(np.frombuffer(raw,np.uint8).reshape(72,128,3).astype(float)-ref)))
        if score<best[0]:best=(score,index)
        index+=1
    if decoder.wait():raise RuntimeError('Video decoding failed')
    fps=json.loads((directory/'cinematic_metadata.json').read_text())['fps'];start=best[1]/fps
    subprocess.run(['ffmpeg','-v','error','-n','-ss',str(start),'-t','2','-i',str(movie),
        '-vf',"setpts=4*(PTS-STARTPTS),drawbox=x=0:y=0:w=1280:h=65:color=0x0d1720:t=fill,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='0.25x REPLAY - same recorded brush contact and tray landing':x=22:y=22:fontsize=23:fontcolor=white",
        '-an','-r',str(fps),'-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(output)],check=True)
    (directory/'solid_replay_metadata.json').write_text(json.dumps({'source_video':movie.name,'matched_frame_index':best[1],'thumbnail_mean_absolute_error':best[0],'source_start_video_s':start,'source_duration_s':2,'playback':'.25x replay of already recorded physics; no new simulation'},indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);extract(p.parse_args().directory)
