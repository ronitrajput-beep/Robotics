"""Explicit physical fine-particle spawning and logged hybrid deposition."""
import numpy as np
import mujoco


class FallingDebris:
    def __init__(self,scenario='dirty'):
        self.scenario=scenario;self.spawned=False;self.deposited=set();self.events=[]
        self.positions=[(-.8,.65),(-.4,.65),(0,.65),(.4,-.45),(.8,-.45),(0,-.45)]
        if scenario=='clean':self.positions=[]
        if scenario=='subthreshold':self.positions=self.positions[:1]

    def update(self,m,d,origin,rotation,surface):
        if not self.spawned and d.time>=3:
            for i,(x,y) in enumerate(self.positions):
                body=m.body(f'falling_{i}').id;joint=m.joint(f'falling_joint_{i}');geom=m.geom(f'falling_geom_{i}').id
                q,v=joint.qposadr[0],joint.dofadr[0]
                d.qpos[q:q+3]=origin+rotation@np.array([x,y,.65]);d.qpos[q+3:q+7]=[1,0,0,0];d.qvel[v:v+6]=0
                m.body_gravcomp[body]=0;m.geom_contype[geom]=1;m.geom_conaffinity[geom]=1;m.geom_rgba[geom,3]=1
            self.spawned=True;self.events.append({'event':'PARTICLES_SPAWNED','time_s':float(d.time),'count':len(self.positions)})
            mujoco.mj_forward(m,d)
        glass=m.geom('pv_glass_surface').id
        for i in range(len(self.positions)):
            if i in self.deposited:continue
            geom=m.geom(f'falling_geom_{i}').id
            if any({int(c.geom1),int(c.geom2)}=={glass,geom} for c in d.contact):
                body=m.body(f'falling_{i}').id
                p=rotation.T@(d.xpos[body]-origin)
                surface.deposit([p[:2]])
                self.deposited.add(i)
                m.geom_contype[geom]=0;m.geom_conaffinity[geom]=0;m.geom_rgba[geom,3]=0
                m.body_gravcomp[body]=1
                dof=m.joint(f'falling_joint_{i}').dofadr[0];d.qvel[dof:dof+6]=0
                self.events.append({'event':'HYBRID_DEPOSITION','time_s':float(d.time),'id':i,'panel_xy_m':p[:2].tolist(),
                                    'assumption':'Fine rigid grain converted to visible stationary soil layer; velocity discarded, not resolved adhesion'})
