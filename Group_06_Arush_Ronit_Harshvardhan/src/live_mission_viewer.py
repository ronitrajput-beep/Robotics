"""Interactive presentation of the actual mission; never commands the robot."""
import time
import numpy as np
from cinematic_scene import RooftopScene


class LiveMissionViewer:
    def __init__(self,model,data,field,speed=1.,launcher=None):
        if not np.isfinite(speed) or speed<=0:raise ValueError('Viewer speed must be positive')
        if launcher is None:
            from mujoco import viewer
            launcher=viewer.launch_passive
        self.model=model;self.data=data;self.field=field;self.speed=speed
        self.environment=RooftopScene();self.paused=False;self.last_state=None;self.next_message=0.
        self.handle=launcher(model,data,key_callback=self.key_callback,show_left_ui=False,show_right_ui=False)
        self.wall_start=time.monotonic();self.sim_start=float(data.time)
        with self.handle.lock():
            self.handle.cam.lookat[:]=[-.55,0,1.2]
            self.handle.cam.distance=8.;self.handle.cam.azimuth=110.;self.handle.cam.elevation=-40.
        print('LIVE MISSION: waiting for camera-detected dirt. P pauses/resumes; mouse rotates/zooms; close window to stop.',flush=True)

    def key_callback(self,key):
        if key in (ord('P'),ord('p')):self.paused=not self.paused

    def update(self,state,target_count,collection=None,solid=None):
        if collection is not None:
            self.environment.collection_status={'bin_g':collection.bin_kg*1000,'station_g':collection.station_kg*1000,'charge_J':collection.charge_J,'state':state}
        if state!=self.last_state or self.data.time>=self.next_message:
            print(f't={self.data.time:.1f}s | {state} | RGB dirt targets={target_count}',flush=True)
            self.last_state=state;self.next_message=float(self.data.time)+15.

    def is_running(self):return self.handle.is_running()

    def sync(self):
        if not self.is_running():return
        # The native viewer copies user_scn during sync. Only these extra
        # presentation geometries are edited; model and integration state stay intact.
        with self.handle.lock():
            scene=self.handle.user_scn;scene.ngeom=0
            self.environment.apply(scene,self.model,self.data)
            rack=self.model.body('pv_array_rack').id
            self.field.append_visuals(scene,self.data.xpos[rack],self.data.xmat[rack].reshape(3,3))
        self.handle.sync()
        if self.paused:
            before=time.monotonic()
            while self.paused and self.is_running():
                self.handle.sync();time.sleep(.02)
            self.wall_start+=time.monotonic()-before
        remaining=(float(self.data.time)-self.sim_start)/self.speed-(time.monotonic()-self.wall_start)
        while remaining>0 and self.is_running():
            time.sleep(min(remaining,.02))
            remaining=(float(self.data.time)-self.sim_start)/self.speed-(time.monotonic()-self.wall_start)

    def close(self):self.handle.close()
