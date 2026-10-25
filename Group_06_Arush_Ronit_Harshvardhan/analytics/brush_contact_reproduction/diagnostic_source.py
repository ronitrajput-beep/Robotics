import mujoco,numpy as np
z=np.load('analytics/collection_contact_trace/lift_state.npz');inputs=[]
m0=mujoco.MjModel.from_xml_path('analytics/collection_contact_trace/model.xml');temp=mujoco.MjData(m0)
for state in z['states']:
 mujoco.mj_setState(m0,temp,state,mujoco.mjtState.mjSTATE_INTEGRATION);inputs.append(temp.ctrl.copy())
for tc in (.005,.01,.02,.04):
 m=mujoco.MjModel.from_xml_path('analytics/collection_contact_trace/model.xml');d=mujoco.MjData(m)
 for name in ('geom_contype','geom_conaffinity','geom_rgba','body_gravcomp'):getattr(m,name)[:]=z[name]
 brush=m.geom('brush_cylinder').id
 if tc!=.005:
  m.geom_solref[brush]=[tc,1];m.geom_priority[brush]=2;m.geom_friction[brush]=[.4,.005,.0001]
 mujoco.mj_setState(m,d,z['states'][0],mujoco.mjtState.mjSTATE_INTEGRATION);mujoco.mj_forward(m,d)
 rack=m.body('pv_array_rack').id;R=d.xmat[rack].reshape(3,3).copy();o=d.xpos[rack].copy();b=m.body('crawler_chassis').id
 maxh=0.;maxtilt=0.;peak=0.
 for i in range(375):
  d.ctrl[:]=inputs[min(i,len(inputs)-1)];mujoco.mj_forward(m,d)
  for j,c in enumerate(d.contact):
   if brush in (c.geom1,c.geom2):
    force=np.zeros(6);mujoco.mj_contactForce(m,d,j,force);peak=max(peak,force[0])
  maxh=max(maxh,(R.T@(d.xpos[b]-o))[2]);maxtilt=max(maxtilt,np.degrees(np.arccos(np.clip((R.T@d.xmat[b].reshape(3,3))[2,2],-1,1))))
  mujoco.mj_step(m,d)
 print(tc,'height',maxh,'tilt',maxtilt,'peak_brush_contact_N',peak,flush=True)
