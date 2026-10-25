import sys,collections,json
sys.path.insert(0,'src')
from pathlib import Path
import numpy as np,mujoco
import vision_mission as vm
original=vm.mission
buffer=collections.deque(maxlen=100);saved=False
output=Path('analytics/collection_contact_trace')
def traced_mission(*args,**kwargs):
 cb=kwargs['on_sample']
 def sample(m,d,state,coverage):
  global saved
  cb(m,d,state,coverage)
  rack=m.body('pv_array_rack').id;R=d.xmat[rack].reshape(3,3);o=d.xpos[rack];p=R.T@(d.xpos[m.body('crawler_chassis').id]-o)
  if d.time>400:
   size=mujoco.mj_stateSize(m,mujoco.mjtState.mjSTATE_INTEGRATION);snapshot=np.empty(size);mujoco.mj_getState(m,d,snapshot,mujoco.mjtState.mjSTATE_INTEGRATION)
   buffer.append(snapshot)
   if p[2]>.121 and abs(p[0])<2 and abs(p[1])<1.6 and not saved:
    contacts=[]
    for i,c in enumerate(d.contact):
     force=np.zeros(6);mujoco.mj_contactForce(m,d,i,force)
     contacts.append({'names':[m.geom(c.geom1).name,m.geom(c.geom2).name],'pos':c.pos.tolist(),'distance':float(c.dist),'force':force.tolist()})
    print('LIFT_TRACE',d.time,p.tolist(),contacts,flush=True)
    np.savez_compressed(output/'lift_state.npz',states=np.array(buffer),geom_contype=m.geom_contype,geom_conaffinity=m.geom_conaffinity,geom_rgba=m.geom_rgba,body_gravcomp=m.body_gravcomp)
    (output/'contact_trace.json').write_text(json.dumps({'time_s':float(d.time),'panel_position':p.tolist(),'contacts':contacts,'ctrl':d.ctrl.tolist()},indent=2)+'\n');saved=True
 kwargs['on_sample']=sample
 return original(*args,**kwargs)
vm.mission=traced_mission
vm.run(output,'combined',1000)
