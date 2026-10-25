import sys,time
sys.path.insert(0,'src')
import mujoco,numpy as np
for noslip in (0,3,10):
 m=mujoco.MjModel.from_xml_path('models/collection_cleaning_crawler.xml');m.opt.noslip_iterations=noslip;d=mujoco.MjData(m);mujoco.mj_forward(m,d)
 rack=m.body('pv_array_rack').id;R=d.xmat[rack].reshape(3,3).copy();o=d.xpos[rack].copy();d.qpos[:3]=o+R@[-3.65,1.53,.12]
 j=m.joint('combined_solid_joint');q=j.qposadr[0];g=m.geom('combined_solid_geom').id;b=m.body('combined_solid').id
 d.qpos[q:q+3]=o+R@[-.8,-1.78,.12];d.qpos[q+3:q+7]=[np.cos(.349066/2),np.sin(.349066/2),0,0];m.geom_rgba[g,3]=1;m.body_gravcomp[b]=0;mujoco.mj_forward(m,d)
 mujoco.mj_step(m,d,200000)
 print(noslip,(R.T@(d.geom_xpos[g]-o)).tolist(),flush=True)
