"""Physics-driven raster mission. Ground-truth pose feedback; roller track approximation."""
from pathlib import Path
import argparse, csv, json, hashlib, gzip
import mujoco
import numpy as np
from planning import raster, segment_reference, clearance

ROOT = Path(__file__).resolve().parents[1]

def mission(seed=0, output=None, duration=360., viewer=False, variant="proposed"):
    if variant not in ("baseline", "proposed"): raise ValueError("Unknown controller")
    rng = np.random.default_rng(seed)
    model_path = ROOT/'models/solar_cleaning_crawler.xml'
    hashes={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in {'model_sha256':model_path,'controller_sha256':Path(__file__),'planner_sha256':ROOT/'src/planning.py'}.items()}
    m = mujoco.MjModel.from_xml_path(str(model_path)); d = mujoco.MjData(m)
    mujoco.mj_forward(m,d)
    b=m.body('crawler_chassis').id; rack=m.body('pv_array_rack').id
    R=d.xmat[rack].reshape(3,3).copy(); origin=d.xpos[rack].copy()
    # Initial conditions only; never overwrite state during integration.
    d.qpos[0:3] = origin + R @ np.array([-2.20+rng.uniform(-.01,.01),1.20+rng.uniform(-.01,.01),.12])
    mujoco.mj_forward(m,d)
    joints=[m.joint(s+'_'+e).dofadr[0] for s in ('left','right') for e in ('front','rear')]
    route=raster()[1:]; index=0; integral=np.zeros(4); dt=m.opt.timestep
    initial=(R.T@(d.xpos[b]-origin))[:2].copy()
    axisx=np.linspace(-3,3,120); axisy=np.linspace(-2,2,80)
    X,Y=np.meshgrid(axisx,axisy); soil=np.ones(X.shape); visited=np.zeros(X.shape,bool)
    f=None; writer=None
    if output:
        output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
        f=gzip.open(output,'wt',newline='') if output.suffix=='.gz' else output.open('w',newline='');writer=csv.writer(f)
        writer.writerow(['time_s','state','x_m','y_m','yaw_rad','ref_x_m','ref_y_m','path_error_m','brush_rad_s','brush_contact','brush_normal_N','coverage_fraction','soil_removed_fraction','effort_Nm2_s','work_J'])
    display=None
    if viewer:
        from mujoco import viewer as mj_viewer
        display=mj_viewer.launch_passive(m,d)
    effort=work=0.; status='TIMEOUT'; errors=[]
    try:
        for step in range(int(duration/dt)):
            p=R.T@(d.xpos[b]-origin); h=R.T@d.xmat[b].reshape(3,3)[:,0]; yaw=np.arctan2(h[1],h[0])
            goal=route[index]; distance=np.linalg.norm(goal-p[:2])
            reference,cross_error=segment_reference(p[:2],initial if index==0 else route[index-1],goal)
            if variant=="baseline": reference=goal.copy()
            delta=reference-p[:2]
            angle=np.arctan2(delta[1],delta[0])
            forward_error=np.arctan2(np.sin(angle-yaw),np.cos(angle-yaw))
            segment_start=initial if index==0 else route[index-1]
            direction=1 if goal[0]>=segment_start[0] else -1
            if direction<0: angle+=np.pi
            error=np.arctan2(np.sin(angle-yaw),np.cos(angle-yaw))
            state='SETTLE' if d.time<1 else ('ALIGN' if abs(error)>.4 else 'SWEEP')
            if clearance(p)<.02 or p[2]<.04:
                status='ABORT_EDGE';break
            if d.time>=1 and distance<.10:
                index+=1
                if index==len(route):status='ROUTE_COMPLETE';break
            v=0 if state!='SWEEP' else direction*min(.18,.8*distance)*max(0,np.cos(error))
            omega=0 if state=='SETTLE' else np.clip(3*error,-1.2,1.2)
            speeds=np.array([v-.20*omega]*2+[v+.20*omega]*2)/.06
            for i,j in enumerate(joints):
                e=speeds[i]-d.qvel[j]
                integral[i]=np.clip(integral[i]+e*dt,-3,3)
                d.ctrl[i]=np.clip(.8*e+(.5*integral[i] if variant=="proposed" else 0),-3,3)
            d.ctrl[4]=15 if state=='SWEEP' else 0
            mujoco.mj_forward(m,d)
            if not np.isfinite(d.qpos).all() or any(w.number for w in d.warning):
                status='ABORT_PHYSICS';break
            brush=m.geom('brush_cylinder').id; glass=m.geom('pv_glass_surface').id
            normal_force=0.
            for contact_index,c in enumerate(d.contact):
                if {int(c.geom1),int(c.geom2)}=={brush,glass}:
                    wrench=np.zeros(6);mujoco.mj_contactForce(m,d,contact_index,wrench)
                    normal_force+=max(0.,wrench[0])
            contact=normal_force>.1
            brush_speed=abs(d.qvel[m.joint('brush_hinge').dofadr[0]])
            bp=R.T@(d.geom_xpos[brush]-origin)
            ux=np.cos(yaw)*(X-bp[0])+np.sin(yaw)*(Y-bp[1]);uy=-np.sin(yaw)*(X-bp[0])+np.cos(yaw)*(Y-bp[1])
            mask=(abs(ux)<.06)&(abs(uy)<.275)
            if contact and brush_speed>1 and state=='SWEEP':
                visited|=mask;soil[mask]*=np.exp(-2*dt) # phenomenological, uncalibrated
            effort+=float(np.sum(d.actuator_force**2))*dt
            work+=float(np.sum(np.maximum(0,d.actuator_force*d.actuator_velocity)))*dt
            errors.append(cross_error)
            if writer:writer.writerow([d.time,state,*p[:2],yaw,*reference,cross_error,d.qvel[m.joint('brush_hinge').dofadr[0]],int(contact),normal_force,visited.mean(),1-soil.mean(),effort,work])
            mujoco.mj_step(m,d)
            if display and step%16==0:
                if not display.is_running():status='USER_STOP';break
                display.sync()
        result={**hashes,'variant':variant,'planned_duration_s':duration,'seed':seed,'status':status,'time_s':float(d.time),'waypoints_reached':index,'waypoints_total':len(route),'visited_contact_fraction':float(visited.mean()),'soil_removed_proxy_fraction':float(1-soil.mean()),'path_tracking_rmse_m':float(np.sqrt(np.mean(np.square(errors)))),'effort_Nm2_s':effort,'positive_mechanical_work_J':work,'mujoco':mujoco.__version__}
        if output:output.with_suffix('.json').write_text(json.dumps(result,indent=2))
        print(json.dumps(result,indent=2));return result
    finally:
        if f:f.close()
        if display:display.close()

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--seed',type=int,default=0);a.add_argument('--duration',type=float,default=360);a.add_argument('--output');a.add_argument('--viewer',action='store_true');args=a.parse_args()
    mission(args.seed,args.output,args.duration,args.viewer)
