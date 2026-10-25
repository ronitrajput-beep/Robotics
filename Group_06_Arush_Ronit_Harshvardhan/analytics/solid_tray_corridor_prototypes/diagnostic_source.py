import sys
sys.path.insert(0,'src')
import mujoco,numpy as np
from collection_system import PhysicalSolid
for sy in (-1.65,-1.78,-1.83,-1.88):
 m=mujoco.MjModel.from_xml_path('models/collection_cleaning_crawler.xml');d=mujoco.MjData(m);mujoco.mj_forward(m,d)
 rack=m.body('pv_array_rack').id;R=d.xmat[rack].reshape(3,3).copy();o=d.xpos[rack].copy()
 d.qpos[:3]=o+R@[-1.5,-1.6,.12]
 j=m.joint('combined_solid_joint');q=j.qposadr[0];v=j.dofadr[0];g=m.geom('combined_solid_geom').id;b=m.body('combined_solid').id
 d.qpos[q:q+3]=o+R@[-.8,sy,.045];d.qpos[q+3:q+7]=[np.cos(.349066/2),np.sin(.349066/2),0,0];m.geom_rgba[g,3]=1;m.body_gravcomp[b]=0
 mujoco.mj_forward(m,d)
 solid=PhysicalSolid();solid.spawned=True
 joints=[m.joint(a+'_'+b).dofadr[0] for a in ('left','right') for b in ('front','rear')];integ=np.zeros(4);maxtilt=0;maxheight=0
 for step in range(16000):
  speed=.14 if 1<d.time<24 else 0
  for i,k in enumerate(joints):
   e=speed/.06-d.qvel[k];integ[i]=np.clip(integ[i]+e*.002,-3,3);d.ctrl[i]=np.clip(.8*e+.5*integ[i],-3,3)
  d.ctrl[4]=-15 if 1<d.time<24 else 0
  mujoco.mj_forward(m,d);solid.update(m,d,o,R)
  p=R.T@(d.xpos[m.body('crawler_chassis').id]-o);tilt=np.degrees(np.arccos(np.clip((R.T@d.xmat[m.body('crawler_chassis').id].reshape(3,3))[2,2],-1,1)))
  maxtilt=max(maxtilt,tilt);maxheight=max(maxheight,p[2]);mujoco.mj_step(m,d)
 print(sy,solid.summary(),'tilt',maxtilt,'height',maxheight,flush=True)
