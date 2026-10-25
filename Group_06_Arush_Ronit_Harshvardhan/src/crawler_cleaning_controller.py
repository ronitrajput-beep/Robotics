"""Physics-driven raster mission. Ground-truth pose feedback; roller track approximation."""
from pathlib import Path
import argparse, csv, json, hashlib, gzip
import mujoco
import numpy as np
from planning import raster, segment_reference, clearance
from safety import StopSupervisor
from cleaning_coverage import CoverageMap
from guarded_geometry import edge_raster, body_edge_gaps

ROOT = Path(__file__).resolve().parents[1]

def mission(seed=0, output=None, duration=360., viewer=False, variant="proposed", fault=None, fault_time=3., layout="standard", on_sample=None, guarded=False, should_move=None, revisit_targets=None, guarded_model_path=None, route_profile="standard", edge_service_targets=None):
    if fault not in (None,"pose_dropout","brush_jam","traction_loss"): raise ValueError("Unknown fault")
    if not np.isfinite(duration) or duration<=0: raise ValueError("Duration must be positive")
    if variant not in ("baseline", "proposed"): raise ValueError("Unknown controller")
    planned_route=edge_raster(route_profile) if guarded else raster(layout)
    rng = np.random.default_rng(seed)
    model_path = ROOT/('models/guarded_cleaning_crawler.xml' if guarded else 'models/solar_cleaning_crawler.xml')
    hashes={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in {'model_sha256':model_path,'controller_sha256':Path(__file__),'planner_sha256':ROOT/'src/planning.py','safety_sha256':ROOT/'src/safety.py','coverage_sha256':ROOT/'src/cleaning_coverage.py','guarded_geometry_sha256':ROOT/'src/guarded_geometry.py'}.items()}
    if guarded_model_path is not None:
        model_path=Path(guarded_model_path);hashes['model_sha256']=hashlib.sha256(model_path.read_bytes()).hexdigest()
    m = mujoco.MjModel.from_xml_path(str(model_path)); d = mujoco.MjData(m)
    mujoco.mj_forward(m,d)
    b=m.body('crawler_chassis').id; rack=m.body('pv_array_rack').id
    R=d.xmat[rack].reshape(3,3).copy(); origin=d.xpos[rack].copy()
    # Initial conditions only; never overwrite state during integration.
    d.qpos[0:3] = origin + R @ np.array([planned_route[0,0]+rng.uniform(-.01,.01),planned_route[0,1]+rng.uniform(-.01,.01),.12])
    mujoco.mj_forward(m,d)
    joints=[m.joint(s+'_'+e).dofadr[0] for s in ('left','right') for e in ('front','rear')]
    route=planned_route[1:]; index=0; integral=np.zeros(4); dt=m.opt.timestep
    initial=(R.T@(d.xpos[b]-origin))[:2].copy()
    axisx=np.linspace(-3,3,120); axisy=np.linspace(-2,2,80)
    X,Y=np.meshgrid(axisx,axisy); soil=np.ones(X.shape); visited=np.zeros(X.shape,bool)
    coverage_map=CoverageMap()
    f=None; writer=None
    if output:
        output=Path(output)
        if output.exists() or output.with_suffix('.json').exists() or output.with_suffix('.coverage.npz').exists(): raise FileExistsError(output)
        output.parent.mkdir(parents=True,exist_ok=True)
        f=gzip.open(output,'wt',newline='') if output.suffix=='.gz' else output.open('w',newline='');writer=csv.writer(f)
        writer.writerow(['time_s','state','x_m','y_m','yaw_rad','ref_x_m','ref_y_m','path_error_m','brush_rad_s','brush_contact','brush_normal_N','coverage_fraction','soil_removed_fraction','effort_Nm2_s','work_J','speed_mps','clearance_m','stop_reason','angular_speed_rad_s','brush_x_m','brush_y_m','brush_axle_x','brush_axle_y','chassis_height_m','chassis_tilt_deg','guard_normal_N'])
    display=None
    if viewer:
        from mujoco import viewer as mj_viewer
        display=mj_viewer.launch_passive(m,d)
    effort=work=0.; status='TIMEOUT'; errors=[]
    retries=0
    edge_handled=False;edge_phase=False
    max_height=0.;max_tilt=0.
    minimum_gaps=np.full(4,np.inf); guard_impulse=0.; peak_guard_force=0.
    supervisor=StopSupervisor(); events=[]; injected=False; stall_since=None; docking=False
    brush_dof=m.joint('brush_hinge').dofadr[0]
    try:
        for step in range(int(duration/dt)):
            p=R.T@(d.xpos[b]-origin); h=R.T@d.xmat[b].reshape(3,3)[:,0]; yaw=np.arctan2(h[1],h[0])
            if fault and not injected and d.time>=fault_time:
                injected=True;events.append({'time_s':float(d.time),'event':'INJECT_'+fault})
                if fault=='brush_jam': m.dof_damping[brush_dof]=20.
                if fault=='traction_loss': m.geom_friction[:,0]=.05
            tilt=float(np.rad2deg(np.arccos(np.clip((R.T@d.xmat[b].reshape(3,3))[2,2],-1,1))))
            max_height=max(max_height,float(p[2]));max_tilt=max(max_tilt,tilt)
            speed=float(np.linalg.norm((R.T@d.qvel[:3])[:2]))
            gaps=body_edge_gaps(p,R.T@d.xmat[b].reshape(3,3),m.geom_size[m.geom('chassis_geom').id]);minimum_gaps=np.minimum(minimum_gaps,gaps)
            stopping=supervisor.update(d.time,speed,(np.inf if guarded else clearance(p)),not(injected and fault=='pose_dropout'),stall_since is not None and d.time-stall_since>.5, float(np.linalg.norm(d.qvel[3:6])),abs(d.qvel[brush_dof]))
            if stopping and not any(e['event']=='BRAKING' for e in events):
                events.append({'time_s':float(d.time),'event':'BRAKING','reason':supervisor.reason});integral[:]=0
            if stopping=='STOPPED' and docking and revisit_targets is not None and retries<2:
                targets=revisit_targets()
                if targets:
                    home=planned_route[0].copy();new_goals=[]
                    for tx,ty in targets:
                        if tx< -2.48:
                            events.append({'time_s':float(d.time),'event':'UNREACHABLE_VISION_TARGET','target':[tx,ty],
                                           'reason':'Fixed forward brush cannot reach left strip with current heading policy'})
                            continue
                        safe_y=float(np.clip(ty,-1.62,1.62))
                        new_goals.extend([(max(-2.72,tx-.7),safe_y),(min(2.76,tx+.2),safe_y)])
                    if new_goals:
                        new_goals.append(home)
                        route=np.asarray(new_goals);initial=p[:2].copy();index=0
                        docking=False;supervisor=StopSupervisor();integral[:]=0;stall_since=None;retries+=1
                        events.append({'time_s':float(d.time),'event':'VISION_REVISIT','targets':targets})
                        continue
            if stopping in ('STOPPED','ABORT_UNSTOPPED'):
                status=('DOCKED' if np.linalg.norm(route[-1]-p[:2])<=.12 else 'ABORT_DOCK_POSITION') if stopping=='STOPPED' and docking else stopping
                events.append({'time_s':float(d.time),'event':status});break
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
            if should_move is not None and not should_move():state='HOME_MONITOR'
            if (not guarded and clearance(p)<0) or p[2]<.04 or abs(p[0])>3.1 or abs(p[1])>2.1:
                status='ABORT_EDGE';break
            if not stopping and not docking and state!='HOME_MONITOR' and d.time>=1 and distance<(.08 if guarded else .10):
                index+=1
                if guarded and route_profile=="inward_turns" and not edge_handled and index==len(planned_route)-4:
                    edge_handled=True
                    tasks=edge_service_targets() if edge_service_targets is not None else []
                    bottom=[(tx,ty) for tx,ty in tasks if ty< -1.65 and -1.6<tx<1.6]
                    if bottom:
                        new_goals=[]
                        for tx,ty in sorted(bottom):
                            new_goals.extend([(tx-1.,-1.40),(tx+.25,-1.74),(tx+1.,-1.40)])
                        new_goals.extend([(0.,-1.1),(0.,1.0),planned_route[0]])
                        route=np.asarray(new_goals);initial=p[:2].copy();index=0;edge_phase=True
                        events.append({'time_s':float(d.time),'event':'VISION_EDGE_SERVICE','edge':'bottom','targets':bottom})
                        continue
                if index==len(route):
                    index-=1;docking=True;supervisor.reason='DOCK';supervisor.triggered_at=d.time
                    stopping='BRAKING';integral[:]=0
                    events.append({'time_s':float(d.time),'event':'DOCKING'})
            if edge_phase and state=='SWEEP' and p[1]<-1.4:state='EDGE_CLEAN_BOTTOM'
            v=0 if state not in ('SWEEP','EDGE_CLEAN_BOTTOM') else direction*min(.12 if retries>0 or edge_phase else .18,.8*distance)*max(0,np.cos(error))
            omega=0 if state in ('SETTLE','HOME_MONITOR') else np.clip(3*error,-1.2,1.2)
            if stopping: state='DOCKING' if docking else 'BRAKING';v=omega=0.
            speeds=np.array([v-.20*omega]*2+[v+.20*omega]*2)/.06
            for i,j in enumerate(joints):
                e=speeds[i]-d.qvel[j]
                integral[i]=np.clip(integral[i]+e*dt,-3,3)
                d.ctrl[i]=np.clip(.8*e+(.5*integral[i] if variant=="proposed" else 0),-3,3)
            d.ctrl[4]=15 if state in ('SWEEP','EDGE_CLEAN_BOTTOM') else 0
            mujoco.mj_forward(m,d)
            if not np.isfinite(d.qpos).all() or any(w.number for w in d.warning):
                status='ABORT_PHYSICS';break
            brush=m.geom('brush_cylinder').id; glass=m.geom('pv_glass_surface').id
            normal_force=0.; guard_force=0.
            for contact_index,c in enumerate(d.contact):
                names=[m.geom(int(g)).name for g in (c.geom1,c.geom2)]
                if any(name.startswith('guard_') for name in names):
                    wrench=np.zeros(6);mujoco.mj_contactForce(m,d,contact_index,wrench)
                    guard_force+=max(0.,wrench[0])
                if {int(c.geom1),int(c.geom2)}=={brush,glass}:
                    wrench=np.zeros(6);mujoco.mj_contactForce(m,d,contact_index,wrench)
                    normal_force+=max(0.,wrench[0])
            guard_impulse+=guard_force*dt;peak_guard_force=max(peak_guard_force,guard_force)
            contact=normal_force>.1
            brush_speed=abs(d.qvel[m.joint('brush_hinge').dofadr[0]])
            if state in ('SWEEP','EDGE_CLEAN_BOTTOM') and brush_speed<1:
                if stall_since is None:stall_since=d.time
            else:stall_since=None
            bp=R.T@(d.geom_xpos[brush]-origin)
            axle=(R.T@d.geom_xmat[brush].reshape(3,3)[:,2])[:2]
            coverage_map.update(bp[:2],axle,*m.geom_size[brush,:2],normal_force,brush_speed,state in ('SWEEP','EDGE_CLEAN_BOTTOM'),dt)
            ux=np.cos(yaw)*(X-bp[0])+np.sin(yaw)*(Y-bp[1]);uy=-np.sin(yaw)*(X-bp[0])+np.cos(yaw)*(Y-bp[1])
            mask=(abs(ux)<.06)&(abs(uy)<.275)
            if contact and brush_speed>1 and state in ('SWEEP','EDGE_CLEAN_BOTTOM'):
                visited|=mask;soil[mask]*=np.exp(-2*dt) # phenomenological, uncalibrated
            effort+=float(np.sum(d.actuator_force**2))*dt
            work+=float(np.sum(np.maximum(0,d.actuator_force*d.actuator_velocity)))*dt
            errors.append(cross_error)
            if writer:writer.writerow([d.time,state,*p[:2],yaw,*reference,cross_error,d.qvel[m.joint('brush_hinge').dofadr[0]],int(contact),normal_force,visited.mean(),1-soil.mean(),effort,work,speed,clearance(p),supervisor.reason or '',float(np.linalg.norm(d.qvel[3:6])),*bp[:2],*axle,float(p[2]),tilt,guard_force])
            if on_sample is not None:
                on_sample(m,d,state,coverage_map)
            mujoco.mj_step(m,d)
            if display and step%16==0:
                if not display.is_running():status='USER_STOP';break
                display.sync()
        result={**hashes,'maximum_chassis_height_m':max_height,'maximum_chassis_tilt_deg':max_tilt,'vision_revisit_cycles':retries,'guarded':guarded,'minimum_chassis_edge_gaps_m':minimum_gaps.tolist(),'guard_normal_impulse_Ns':guard_impulse,'peak_guard_normal_force_N':peak_guard_force,'route_profile':route_profile,'layout':('edge_raster' if guarded else layout),'coverage_metrics_v2':coverage_map.summary(),'fault':fault,'fault_time_s':fault_time if fault else None,'events':events,'stop_reason':supervisor.reason,'terminal_angular_speed_rad_s':float(np.linalg.norm(d.qvel[3:6])),'terminal_brush_speed_rad_s':float(abs(d.qvel[brush_dof])),'dock_error_m':float(np.linalg.norm(route[-1]-(R.T@(d.xpos[b]-origin))[:2])),'terminal_speed_mps':float(np.linalg.norm((R.T@d.qvel[:3])[:2])),'variant':variant,'planned_duration_s':duration,'seed':seed,'status':status,'time_s':float(d.time),'waypoints_reached':index+int(docking),'waypoints_total':len(route),'visited_contact_fraction':float(visited.mean()),'soil_removed_proxy_fraction':float(1-soil.mean()),'path_tracking_rmse_m':float(np.sqrt(np.mean(np.square(errors)))),'effort_Nm2_s':effort,'positive_mechanical_work_J':work,'mujoco':mujoco.__version__}
        if output:
            coverage_map.save(output.with_suffix('.coverage.npz'))
            output.with_suffix('.json').write_text(json.dumps(result,indent=2))
        print(json.dumps(result,indent=2));return result
    finally:
        if f:f.close()
        if display:display.close()

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--guarded',action='store_true');a.add_argument('--layout',choices=['standard','expanded','expanded_safe_return'],default='standard');a.add_argument('--seed',type=int,default=0);a.add_argument('--duration',type=float,default=360);a.add_argument('--output');a.add_argument('--viewer',action='store_true');a.add_argument('--fault',choices=['pose_dropout','brush_jam','traction_loss']);a.add_argument('--fault-time',type=float,default=3.);args=a.parse_args()
    mission(args.seed,args.output,args.duration,args.viewer,fault=args.fault,fault_time=args.fault_time,layout=args.layout,guarded=args.guarded)
