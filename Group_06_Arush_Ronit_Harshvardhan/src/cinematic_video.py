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
        self.sensor_views={};self.sensor_time=0.
        self.last_time=-1;self.frames=0;self.last_picture=None;self.camera=None;self.closeup_frames=0
        self.font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
        self.small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
    def update_sensor_views(self,time,views):
        self.sensor_time=time;self.sensor_views=views

    def capture(self,m,d,field,origin,rotation,state,coverage,target_count):
        brush=rotation.T@(d.geom_xpos[m.geom('brush_cylinder').id]-origin)
        near_dirt=any(p.remaining>=.1 and np.linalg.norm(brush[:2]-[p.x,p.y])<.55 for p in field.patches)
        collection=getattr(self,'collection_status',None)
        solid=collection['solid'] if collection else None
        solid_active=solid is not None and solid['first_tool_contact_s'] is not None and not solid['contacted_catch_tray']
        closeup=d.time>=8 and (near_dirt or 22<d.time%80<26)
        catch_time=next((e['time_s'] for e in solid['events'] if e['event']=='SOLID_TRAY_CONTACT'),-100.) if solid else -100.
        catch_window=0<=d.time-catch_time<3
        speed=1 if catch_window or d.time<8 or closeup or solid_active or state=="DOCK_SERVICE" else 8
        if d.time<self.last_time+speed/25-1e-9:return
        self.last_time=float(d.time)
        if self.renderer is None:
            self.renderer=make_renderer(m,width=960,height=540)
            self.log=(self.directory/'cinematic_ffmpeg.log').open('w')
            self.encoder=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','warning','-n','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720',
                '-r','25','-i','-','-an','-c:v','libx264','-preset','fast','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart',
                str(self.directory/'cinematic_cleaning.mp4')],stdin=subprocess.PIPE,stderr=self.log)
        desired=cinematic_camera(float(d.time),d,m)
        self.environment.collection_status=collection
        if closeup:
            desired.lookat[:]=.5*(d.xpos[m.body('crawler_chassis').id]+d.geom_xpos[m.geom('brush_cylinder').id])
            desired.distance=1.65;desired.elevation=-29;desired.azimuth=115
        if collection is not None:
            if d.time<2.8 or state=='DOCK_SERVICE':
                desired.lookat[:]=origin+rotation@np.array([-3.7,1.5,.13]);desired.distance=2.3;desired.elevation=-36;desired.azimuth=130
            elif d.time<8:
                desired.lookat[:]=origin+rotation@np.array([-.4,0,0]);desired.distance=8.6;desired.elevation=-53
            elif solid_active:
                sp=origin+rotation@np.asarray(solid['final_panel_position_m'])
                desired.lookat[:]=.5*(sp+d.geom_xpos[m.geom('brush_cylinder').id]);desired.distance=4.8;desired.elevation=-50;desired.azimuth=100
        if collection is not None and solid['contacted_catch_tray']:
            catch_time=next(e['time_s'] for e in solid['events'] if e['event']=='SOLID_TRAY_CONTACT')
            if 0<=d.time-catch_time<3:
                desired.lookat[:]=origin+rotation@np.asarray(solid['final_panel_position_m']);desired.distance=1.7;desired.elevation=-40;desired.azimuth=100
                speed=1
        if self.camera is None:self.camera=desired
        else:
            for name in ('distance','azimuth','elevation'):setattr(self.camera,name,.84*getattr(self.camera,name)+.16*getattr(desired,name))
            self.camera.lookat[:]=.84*self.camera.lookat+.16*desired.lookat
        picture=Image.fromarray(render_studio(self.renderer,m,d,self.camera,self.environment,field))
        detail=None
        if solid_active or catch_window:
            # A labelled second presentation view, rendered from the same physical state.
            inspect=mujoco.MjvCamera();mujoco.mjv_defaultCamera(inspect)
            inspect.lookat[:]=origin+rotation@np.asarray(solid['final_panel_position_m']);inspect.distance=1.15;inspect.elevation=-40;inspect.azimuth=115
            detail=Image.fromarray(render_studio(self.renderer,m,d,inspect,self.environment,field)).resize((300,169),Image.Resampling.LANCZOS)
        base=Image.new('RGB',(1280,720),(13,23,32))
        base.paste(picture.resize((960,540),Image.Resampling.LANCZOS),(4,104))
        picture=base;draw=ImageDraw.Draw(picture)
        if detail is not None:
            picture.paste(detail,(16,133));draw.rectangle((16,110,316,133),fill=(13,23,32))
            draw.text((22,113),'Same-time solid / guide close-up',font=self.small,fill=(225,215,170))
        draw.line((978,66,978,694),fill=(70,100,110),width=2)
        for i,name in enumerate(('edge_left','edge_right','robot_camera')):
            top=70+i*208
            draw.text((994,top),f'{dict(edge_left="Panel left",edge_right="Panel right",robot_camera="Onboard")[name]} RGB  t={self.sensor_time:.1f}s',font=self.small,fill=(185,225,230))
            if name in self.sensor_views:
                view=self.sensor_views[name];image=Image.fromarray(view['rgb']).resize((250,187),Image.Resampling.LANCZOS)
                boxes=ImageDraw.Draw(image)
                for detection in view['detections']:
                    if detection['confidence']<.8:continue
                    x0,y0,x1,y1=detection['bbox_xyxy']
                    sx=250/view['rgb'].shape[1];sy=187/view['rgb'].shape[0]
                    boxes.rectangle((x0*sx,y0*sy,x1*sx,y1*sy),outline=(70,255,120),width=2)
                picture.paste(image,(994,top+18))
        if collection is not None:
            draw.rectangle((12,610,958,657),fill=(13,23,32))
            draw.text((22,615),f'Dust bin {collection["bin_g"]:.2f} g  >  station {collection["station_g"]:.2f} g  |  Dock charge {collection["charge_J"]:.0f} J (model)',font=self.small,fill=(225,215,170))
            phase='solid release scheduled at t=3 s' if not solid['spawned'] else 'solid retained in tray' if solid['retained_in_tray_at_end'] else 'solid contacting tray' if solid['contacted_catch_tray'] else 'physical solid on panel'
            draw.text((22,638),f'Brush > intake > bin | {phase} | fixed mounts and permanent lower catch tray',font=self.small,fill=(164,195,207))
        draw.text((22,664),'Raw camera inputs at 2 Hz; green boxes are RGB dirt detections',font=self.small,fill=(164,195,207))
        draw.rectangle((0,0,1280,65),fill=(13,23,32))
        tilt=float(np.rad2deg(np.arccos(np.clip((rotation.T@d.xmat[m.body('crawler_chassis').id].reshape(3,3))[2,2],-1,1))))
        draw.text((22,80),f'Chassis tilt: {tilt:.2f} degrees',font=self.small,fill=(164,195,207))
        title='SOLID GUIDED TO CATCH TRAY' if solid_active else 'DOCK: EMPTYING BIN + CHARGING (MODEL)' if state=='DOCK_SERVICE' else 'RETURNING HOME' if state=='RETURN_HOME' else 'VISION-REQUESTED BOTTOM EDGE CLEAN' if state=='EDGE_CLEAN_BOTTOM' else 'INSPECTION / BRUSH CONTACT' if closeup else ('MONITORING' if state=='HOME_MONITOR' else 'AUTONOMOUS SOLAR CLEANING')
        draw.text((22,10),title,font=self.font,fill=(224,239,240))
        draw.text((22,38),f'Simulation {d.time:6.2f}s   |   {state}   |   {speed}x playback   |   RGB targets {target_count}   |   Contact footprint {coverage["qualified_contact_fraction"]:.1%}',font=self.small,fill=(164,195,207))
        draw.rectangle((0,694,1280,720),fill=(13,23,32))
        draw.text((22,699),'Guard-assisted physics / ground-truth navigation / modelled fine-dust capture; no resolved suction airflow' if collection else 'MuJoCo physical motion / guard-assisted / ground-truth navigation / contact-driven soil proxy',font=self.small,fill=(164,195,207))
        if self.frames==0:picture.save(self.directory/'cinematic_preview.png')
        if solid_active and not (self.directory/'solid_contact_closeup.png').exists():picture.save(self.directory/'solid_contact_closeup.png')
        if catch_window and not (self.directory/'solid_in_tray.png').exists():picture.save(self.directory/'solid_in_tray.png')
        if state=='DOCK_SERVICE' and not (self.directory/'dock_service.png').exists():picture.save(self.directory/'dock_service.png')
        if closeup and self.closeup_frames==40:picture.save(self.directory/'brush_closeup.png')
        if closeup:self.closeup_frames+=1
        self.encoder.stdin.write(picture.tobytes());self.frames+=1;self.last_picture=picture
    def close(self,report=None):
        if self.encoder is None:return
        if report:
            picture=self.last_picture.copy();draw=ImageDraw.Draw(picture)
            draw.rectangle((300,250,980,425),fill=(13,23,32))
            lines=[report['status'],f"Measured contact footprint: {report['physical_mission']['coverage_metrics_v2']['qualified_contact_fraction']:.1%}",
                   f"Uncleared deposited patches: {report['hidden_dirt_score']['uncleared_patches']}",f"Maximum chassis tilt: {report['physical_mission']['maximum_chassis_tilt_deg']:.2f} degrees"]
            for i,line in enumerate(lines):draw.text((330,275+i*32),line,font=self.font,fill=(224,239,240))
            picture.save(self.directory/'cinematic_final.png')
            for _ in range(75):self.encoder.stdin.write(picture.tobytes());self.frames+=1
        self.encoder.stdin.close();code=self.encoder.wait();self.renderer.close();self.log.close()
        if code:raise RuntimeError('Cinematic ffmpeg encoding failed')
        (self.directory/'cinematic_metadata.json').write_text(json.dumps({'frames':self.frames,'fps':25,'duration_s':self.frames/25,
            'resolution':[1280,720],'encoding_crf':23,'playback':'1x during initial deposition and brush inspection shots; otherwise 8x; final 3s held outcome',
            'sensor_views':'Three actual RGB detector inputs, timestamped at 2 Hz, with detected image bounding boxes','closeup_frames':self.closeup_frames,'scene':'Procedural rooftop, deck, supports, skyline, sky and robot visual details; presentation only'},indent=2)+'\n')
