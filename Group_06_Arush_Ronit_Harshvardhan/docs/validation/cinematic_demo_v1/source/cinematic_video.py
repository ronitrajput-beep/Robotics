"""720p rooftop presentation; validated sensor images and physics are untouched."""
from pathlib import Path
import json,subprocess
import numpy as np
import mujoco
from PIL import Image,ImageDraw,ImageFont
from cinematic_scene import RooftopScene,cinematic_camera,make_renderer,render_studio


class CinematicVideo:
    def __init__(self,directory):
        self.directory=Path(directory);self.renderer=None;self.encoder=None;self.environment=RooftopScene()
        self.last_time=-1;self.frames=0;self.last_picture=None;self.camera=None;self.closeup_frames=0
        self.font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
        self.small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
    def capture(self,m,d,field,origin,rotation,state,coverage,target_count):
        brush=rotation.T@(d.geom_xpos[m.geom('brush_cylinder').id]-origin)
        near_dirt=any(p.remaining>=.1 and np.linalg.norm(brush[:2]-[p.x,p.y])<.55 for p in field.patches)
        closeup=d.time>=8 and (near_dirt or 22<d.time%80<26)
        speed=1 if d.time<8 or closeup else 8
        if d.time<self.last_time+speed/25-1e-9:return
        self.last_time=float(d.time)
        if self.renderer is None:
            self.renderer=make_renderer(m)
            self.log=(self.directory/'cinematic_ffmpeg.log').open('w')
            self.encoder=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','warning','-n','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720',
                '-r','25','-i','-','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',
                str(self.directory/'cinematic_cleaning.mp4')],stdin=subprocess.PIPE,stderr=self.log)
        desired=cinematic_camera(float(d.time),d,m)
        if closeup:
            desired.lookat[:]=.5*(d.xpos[m.body('crawler_chassis').id]+d.geom_xpos[m.geom('brush_cylinder').id])
            desired.distance=1.65;desired.elevation=-29;desired.azimuth=115
        if self.camera is None:self.camera=desired
        else:
            for name in ('distance','azimuth','elevation'):setattr(self.camera,name,.84*getattr(self.camera,name)+.16*getattr(desired,name))
            self.camera.lookat[:]=.84*self.camera.lookat+.16*desired.lookat
        picture=Image.fromarray(render_studio(self.renderer,m,d,self.camera,self.environment,field))
        draw=ImageDraw.Draw(picture)
        draw.rectangle((0,0,1280,65),fill=(13,23,32))
        title='INSPECTION / BRUSH CONTACT' if closeup else ('MONITORING' if state=='HOME_MONITOR' else 'AUTONOMOUS SOLAR CLEANING')
        draw.text((22,10),title,font=self.font,fill=(224,239,240))
        draw.text((22,38),f'Simulation {d.time:6.2f}s   |   {state}   |   {speed}x playback   |   RGB targets {target_count}   |   Contact footprint {coverage["qualified_contact_fraction"]:.1%}',font=self.small,fill=(164,195,207))
        draw.rectangle((0,694,1280,720),fill=(13,23,32))
        draw.text((22,699),'MuJoCo physical motion  /  guard-assisted  /  ground-truth navigation  /  contact-driven soil proxy',font=self.small,fill=(164,195,207))
        if self.frames==0:picture.save(self.directory/'cinematic_preview.png')
        if closeup and self.closeup_frames==40:picture.save(self.directory/'brush_closeup.png')
        if closeup:self.closeup_frames+=1
        self.encoder.stdin.write(picture.tobytes());self.frames+=1;self.last_picture=picture
    def close(self,report=None):
        if self.encoder is None:return
        if report:
            picture=self.last_picture.copy();draw=ImageDraw.Draw(picture)
            draw.rectangle((300,250,980,425),fill=(13,23,32))
            lines=[report['status'],f"Measured contact footprint: {report['physical_mission']['coverage_metrics_v2']['qualified_contact_fraction']:.1%}",
                   f"Uncleared deposited patches: {report['hidden_dirt_score']['uncleared_patches']}",'Held outcome card / controlled development scenario']
            for i,line in enumerate(lines):draw.text((330,275+i*32),line,font=self.font,fill=(224,239,240))
            picture.save(self.directory/'cinematic_final.png')
            for _ in range(75):self.encoder.stdin.write(picture.tobytes());self.frames+=1
        self.encoder.stdin.close();code=self.encoder.wait();self.renderer.close();self.log.close()
        if code:raise RuntimeError('Cinematic ffmpeg encoding failed')
        (self.directory/'cinematic_metadata.json').write_text(json.dumps({'frames':self.frames,'fps':25,'duration_s':self.frames/25,
            'resolution':[1280,720],'playback':'1x during initial deposition and brush inspection shots; otherwise 8x; final 3s held outcome',
            'closeup_frames':self.closeup_frames,'scene':'Procedural rooftop, deck, supports, skyline, sky and robot visual details; presentation only'},indent=2)+'\n')
