"""Deterministic Phase 1 dynamics checks; no mission-state teleportation."""
from pathlib import Path
import json
import mujoco
import numpy as np

MODEL = Path(__file__).resolve().parents[1] / 'models/solar_cleaning_crawler.xml'

def run():
    results = {}
    for case, targets in {'stationary': (0,0), 'forward': (3,3), 'reverse': (-3,-3), 'turn': (-3,3)}.items():
        m = mujoco.MjModel.from_xml_path(str(MODEL)); d = mujoco.MjData(m)
        mujoco.mj_forward(m,d)
        chassis = m.body('crawler_chassis').id
        rack = m.body('pv_array_rack').id
        rotation = d.xmat[rack].reshape(3,3).copy()
        joints = [m.joint(s+'_'+e).dofadr[0] for s in ('left','right') for e in ('front','rear')]
        start = None
        for step in range(3500):
            target = (0,0) if step < 500 else targets
            for i,j in enumerate(joints):
                d.ctrl[i] = np.clip(.6*(target[i//2]-d.qvel[j]),-3,3)
            d.ctrl[4] = 0
            mujoco.mj_step(m,d)
            assert np.isfinite(d.qpos).all() and np.isfinite(d.qvel).all()
            assert not any(w.number for w in d.warning), 'MuJoCo warning'
            assert np.max(np.abs(d.actuator_force[:4])) <= 3.000001
            if step == 499:
                start = d.xpos[chassis].copy()
                initial_heading = rotation.T @ d.xmat[chassis].reshape(3,3)[:,0]
        displacement = rotation.T @ (d.xpos[chassis]-start)
        heading = rotation.T @ d.xmat[chassis].reshape(3,3)[:,0]
        yaw = np.arctan2(heading[1],heading[0])-np.arctan2(initial_heading[1],initial_heading[0])
        results[case] = {'panel_displacement_m':displacement.tolist(),'yaw_change_rad':float(yaw)}
        if case == 'stationary': assert np.linalg.norm(displacement)<.1, results[case]
        if case == 'forward': assert displacement[0]>.3, results[case]
        if case == 'reverse': assert displacement[0]<-.3, results[case]
        if case == 'turn': assert abs(yaw)>.3, results[case]
    m = mujoco.MjModel.from_xml_path(str(MODEL)); d = mujoco.MjData(m)
    mujoco.mj_forward(m,d)
    b = m.body('crawler_chassis').id
    assert abs(m.body_subtreemass[b]-8.5)<1e-10
    com = d.xmat[b].reshape(3,3).T @ (d.subtree_com[b]-d.xpos[b])
    assert np.allclose(com,[.04094117647,0,-.01505882353],atol=1e-8)
    assert np.allclose(m.jnt_axis[m.joint('brush_hinge').id],[0,1,0])
    for _ in range(1500):
        d.ctrl[4] = 94.2478
        mujoco.mj_step(m,d)
        assert np.isfinite(d.qpos).all()
        assert abs(d.actuator_force[4])<=1.000001
        assert not any(w.number for w in d.warning)
    speed = float(d.qvel[m.joint('brush_hinge').dofadr[0]])
    assert speed > 1, 'Brush failed to rotate'
    results['model'] = {'robot_mass_kg':float(m.body_subtreemass[b]),
                        'com_in_chassis_m':com.tolist(),
                        'loaded_brush_speed_rad_s':speed}
    print(json.dumps(results,indent=2))

if __name__ == '__main__': run()
