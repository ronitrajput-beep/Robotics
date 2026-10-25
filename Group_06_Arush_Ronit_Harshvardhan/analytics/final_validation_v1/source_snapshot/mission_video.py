"""Actual EGL-rendered mission recorder, with explicitly labelled playback rate."""
import subprocess,json
from pathlib import Path
import mujoco
from PIL import Image,ImageDraw,ImageFont


class MissionVideo:
    def __init__(self,directory):
        self.directory=Path(directory);self.renderer=None;self.encoder=None;self.log=None
        self.last_time=-1;self.frames=0;self.last_picture=None
        font=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
        self.font=ImageFont.truetype(str(font),14) if font.exists() else ImageFont.load_default()
    def capture(self,m,d,field,origin,rotation,state,coverage,target_count):
        speed=1 if d.time<8 else 8
        if d.time<self.last_time+speed/25-1e-9:return
        self.last_time=float(d.time)
        if self.renderer is None:
            self.renderer=mujoco.Renderer(m,height=480,width=640,max_geom=10000)
            self.log=(self.directory/'ffmpeg.log').open('w')
            self.encoder=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','warning','-n','-f','rawvideo','-pix_fmt','rgb24',
                '-s','640x480','-r','25','-i','-','-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p',
                '-movflags','+faststart',str(self.directory/'vision_cleaning_demo.mp4')],stdin=subprocess.PIPE,stderr=self.log)
        camera=mujoco.MjvCamera();mujoco.mjv_defaultCamera(camera)
        camera.lookat[:]=origin;camera.distance=4.0 if 2.9<d.time<5.5 else 7.6;camera.azimuth=90;camera.elevation=-65
        self.renderer.update_scene(d,camera=camera);field.append_visuals(self.renderer.scene,origin,rotation)
        picture=Image.fromarray(self.renderer.render());draw=ImageDraw.Draw(picture)
        draw.rectangle((0,0,640,66),fill=(12,18,25))
        lines=[f'Actual physics | {speed}x playback | t={d.time:.2f}s | {state}',
               f'RGB dirt targets: {target_count} | contact footprint: {coverage["qualified_contact_fraction"]:.1%}',
               'Guard-assisted | Ground-truth navigation | Visible soil-removal proxy']
        for i,line in enumerate(lines):draw.text((8,4+i*20),line,font=self.font,fill='white')
        self.encoder.stdin.write(picture.tobytes());self.frames+=1;self.last_picture=picture
    def close(self,report=None):
        if self.encoder is None:return
        if report is not None:
            picture=self.last_picture.copy();draw=ImageDraw.Draw(picture)
            draw.rectangle((0,0,640,90),fill=(12,18,25))
            lines=[f'END OF RUN: {report["status"]} (held summary)',
                   f'Contact footprint: {report["physical_mission"]["coverage_metrics_v2"]["qualified_contact_fraction"]:.1%}',
                   f'Uncleared fine-dirt patches: {report["hidden_dirt_score"]["uncleared_patches"]}',
                   'Development run; controlled dirt colours; no hardware safety claim']
            for i,line in enumerate(lines):draw.text((8,4+i*20),line,font=self.font,fill='white')
            picture.save(self.directory/'final_preview.png')
            for _ in range(50):self.encoder.stdin.write(picture.tobytes());self.frames+=1
        self.encoder.stdin.close();code=self.encoder.wait();self.renderer.close();self.log.close()
        if code:raise RuntimeError('ffmpeg encoding failed')
        (self.directory/'video_metadata.json').write_text(json.dumps({'fps':25,'frames':self.frames,'duration_s':self.frames/25,
            'playback':'First 8 simulation seconds at 1x; subsequent motion at 8x; final 2s summary held',
            'source':'Fresh actual physics with visible hybrid soil field; no robot pose replay'},indent=2)+'\n')
