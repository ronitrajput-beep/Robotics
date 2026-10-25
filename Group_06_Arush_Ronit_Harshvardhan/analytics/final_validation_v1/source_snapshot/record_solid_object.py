"""Close-up recording of the separate scripted solid-object physics test."""
import os
os.environ.setdefault('MUJOCO_GL','egl')
from pathlib import Path
import argparse,json,subprocess
import mujoco,numpy as np
from PIL import Image,ImageDraw,ImageFont
from solid_object_demo import run
from cinematic_scene import RooftopScene,make_renderer,render_studio


def record(directory):
    directory=Path(directory);renderer=None;encoder=None;log=None;next_frame=0.;frames=0;peak=0.;last_picture=None;camera=None
    environment=RooftopScene();font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
    def capture(m,d,info):
        nonlocal renderer,encoder,log,next_frame,frames,peak,last_picture,camera
        peak=max(peak,info['brush_force_N'])
        if d.time+1e-9<next_frame:return
        next_frame+=.04
        if renderer is None:
            renderer=make_renderer(m);log=(directory/'ffmpeg.log').open('w')
            encoder=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','warning','-n','-f','rawvideo','-pix_fmt','rgb24',
                '-s','1280x720','-r','25','-i','-','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p',
                '-movflags','+faststart',str(directory/'solid_object_demo.mp4')],stdin=subprocess.PIPE,stderr=log)
        solid=d.geom_xpos[m.geom('solid_object_geom').id];robot=d.xpos[m.body('crawler_chassis').id]
        desired=mujoco.MjvCamera();mujoco.mjv_defaultCamera(desired)
        desired.lookat[:]=.6*solid+.4*robot
        desired.distance=1.8 if d.time>1 else 3.1;desired.azimuth=108;desired.elevation=-32 if not info['off_glass'] else -42
        if info['caught']:desired.lookat[:]=solid;desired.distance=2.8
        if camera is None:camera=desired
        else:
            camera.lookat[:]=.86*camera.lookat+.14*desired.lookat
            for key in ('distance','azimuth','elevation'):setattr(camera,key,.86*getattr(camera,key)+.14*getattr(desired,key))
        picture=Image.fromarray(render_studio(renderer,m,d,camera,environment));draw=ImageDraw.Draw(picture)
        draw.rectangle((0,0,1280,92),fill=(13,23,32))
        state='IN CATCH TRAY' if info['caught'] else ('OFF GLASS' if info['off_glass'] else 'BRUSH / OBJECT CONTACT' if info['brush_force_N']>0 else 'APPROACH / PHYSICAL MOTION')
        lines=[f'SOLID OBJECT CONTACT TEST  |  {state}  |  {d.time:.2f}s  |  1x playback',
               f'Rigid block 70 x 70 x 50 mm / 120 g    Peak brush-object force: {peak:.1f} N',
               'Scripted test / real contact and gravity / object never deleted / glass damage not modelled']
        for i,line in enumerate(lines):draw.text((18,8+i*27),line,font=font,fill=(224,239,240))
        if frames==0:picture.save(directory/'preview.png')
        encoder.stdin.write(picture.tobytes());frames+=1;last_picture=picture
    try:
        result=run(directory,capture)
        picture=last_picture.copy();draw=ImageDraw.Draw(picture)
        draw.rectangle((270,280,1010,405),fill=(13,23,32))
        draw.text((300,300),f"Off glass: {result['fully_left_glass']}   |   Caught: {result['contacted_catch_tray']}",font=font,fill='white')
        draw.text((300,340),'Measured high contact load: handling safety remains unvalidated',font=font,fill='white')
        picture.save(directory/'final_preview.png')
        for _ in range(50):encoder.stdin.write(picture.tobytes());frames+=1
    finally:
        if encoder is not None:
            encoder.stdin.close();code=encoder.wait();renderer.close();log.close()
            if code:raise RuntimeError('Solid-object video encoding failed')
    (directory/'video_metadata.json').write_text(json.dumps({'fps':25,'frames':frames,'duration_s':frames/25,
        'playback':'29 seconds of physical stepping at 1x, final 2s held summary','resolution':[1280,720]},indent=2)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args();record(a.output_dir)
