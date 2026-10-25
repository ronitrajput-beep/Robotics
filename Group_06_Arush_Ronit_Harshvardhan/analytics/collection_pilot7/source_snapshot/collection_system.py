"""Explicit reduced-order dust storage/service accounting and physical solid scoring."""
import numpy as np
import mujoco


class CollectionSystem:
    # Assumed dust areal loading, blower power and charge power, not calibrated hardware.
    areal_density_kg_m2=.02
    def __init__(self):
        self.bin_kg=0.;self.station_kg=0.;self.collected_kg=0.;self.blower_J=0.;self.charge_J=0.
        self.service_started=None;self.events=[];self.rows=[]
    def soil_mass(self,field):
        return sum(np.pi*p.radius**2*p.aspect*p.remaining*self.areal_density_kg_m2 for p in field.patches)
    def deposited_mass(self,field):
        return sum(np.pi*p.radius**2*p.aspect*self.areal_density_kg_m2 for p in field.patches)
    def pickup(self,before,after,dt):
        collected=max(0.,before-after);self.bin_kg+=collected;self.collected_kg+=collected;self.blower_J+=20.*dt
    def sample(self,time,state,field,dt):
        if state=='DOCK_SERVICE':
            if self.service_started is None:
                self.service_started=float(time);self.events.append({'event':'DOCK_SERVICE_START','time_s':float(time),'bin_kg':self.bin_kg})
            transfer=min(self.bin_kg,.002*dt);self.bin_kg-=transfer;self.station_kg+=transfer
            self.charge_J+=30.*dt
        soil=self.soil_mass(field);deposited=self.deposited_mass(field)
        self.rows.append([float(time),soil,self.bin_kg,self.station_kg,deposited,soil+self.bin_kg+self.station_kg-deposited,self.blower_J,self.charge_J])
    def summary(self,field):
        return {'deposited_dust_kg':self.deposited_mass(field),'remaining_on_glass_kg':self.soil_mass(field),'onboard_bin_kg':self.bin_kg,'station_waste_kg':self.station_kg,'captured_dust_kg':self.collected_kg,'mass_balance_error_kg':self.soil_mass(field)+self.bin_kg+self.station_kg-self.deposited_mass(field),'blower_energy_J':self.blower_J,'dock_charge_energy_J':self.charge_J,'events':self.events,'assumptions':'20 g/m2 initial areal soil; contact-gated exponential capture into bin; 20 W blower; dock 2 g/s emptying and 30 W charge energy. No airflow, seals, electrochemistry or connector contact solved.'}


class PhysicalSolid:
    def __init__(self):
        self.spawned=False;self.events=[];self.rows=[];self.first_touch=None;self.first_brush=None;self.off=False;self.caught=False;self.peak=0.;self.position=None;self.final_retained=False
    def update(self,m,d,o,R):
        geom=m.geom('combined_solid_geom').id;body=m.body('combined_solid').id;joint=m.joint('combined_solid_joint');q=joint.qposadr[0];v=joint.dofadr[0]
        if not self.spawned and d.time>=3:
            d.qpos[q:q+3]=o+R@np.array([-.8,-1.78,.12]);d.qpos[q+3:q+7]=[np.cos(.349066/2),np.sin(.349066/2),0,0];d.qvel[v:v+6]=0
            m.body_gravcomp[body]=0;m.geom_rgba[geom,3]=1;self.spawned=True
            self.events.append({'event':'SOLID_RELEASED','time_s':float(d.time)});mujoco.mj_forward(m,d)
        if not self.spawned:return
        p=R.T@(d.geom_xpos[geom]-o);extent=np.abs(R.T@d.geom_xmat[geom].reshape(3,3))@m.geom_size[geom]
        off=p[0]-extent[0]>3 or p[0]+extent[0]<-3 or p[1]-extent[1]>2 or p[1]+extent[1]<-2
        if off and not self.off:self.off=True;self.events.append({'event':'SOLID_OFF_GLASS','time_s':float(d.time)})
        force=0.;brush=m.geom('brush_cylinder').id;deflector=m.geom('solid_deflector').id;tray=m.geom('lower_catch_tray').id
        for i,c in enumerate(d.contact):
            pair={int(c.geom1),int(c.geom2)}
            if geom in pair and (brush in pair or deflector in pair):
                wrench=np.zeros(6);mujoco.mj_contactForce(m,d,i,wrench);force+=max(0.,wrench[0])
                if self.first_touch is None:self.first_touch=float(d.time);self.events.append({'event':'SOLID_TOOL_CONTACT','tool':m.geom(c.geom1 if c.geom1!=geom else c.geom2).name,'time_s':float(d.time)})
                if brush in pair and self.first_brush is None:self.first_brush=float(d.time);self.events.append({'event':'SOLID_BRUSH_CONTACT','time_s':float(d.time)})
            if pair=={tray,geom} and not self.caught:self.caught=True;self.events.append({'event':'SOLID_TRAY_CONTACT','time_s':float(d.time)})
        self.peak=max(self.peak,force);self.position=p.copy()
        self.final_retained=bool(self.caught and abs(p[0])+extent[0]<3.3 and -2.69<p[1]-extent[1] and p[1]+extent[1]<-1.98 and -.18<p[2]<.15)
        self.rows.append([float(d.time),*p,force,self.off,self.caught,self.final_retained])
    def summary(self):
        return {'size_m':[.07,.07,.05],'mass_kg':.12,'first_tool_contact_s':self.first_touch,'first_brush_contact_s':self.first_brush,'fully_left_glass':self.off,'contacted_catch_tray':self.caught,'retained_in_tray_at_end':self.final_retained,'peak_tool_object_force_N':self.peak,'final_panel_position_m':None if self.position is None else self.position.tolist(),'events':self.events,'scope':'Persistent rigid body after release; fixed diagonal deflector and bottom-row handling corridor, not arbitrary object-specific planning; glass scratching/damage not modelled.'}
