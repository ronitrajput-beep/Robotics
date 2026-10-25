"""Independent physical crumb ejection pilot: a real rigid body and catch tray."""
from pathlib import Path
import csv,json,xml.etree.ElementTree as ET
import mujoco,numpy as np

ROOT=Path(__file__).resolve().parents[1]


def run(directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    root=ET.fromstring((ROOT/'models/guarded_cleaning_crawler.xml').read_text())
    # Use the panel transform to place a real free crumb on its surface.
    angle=.349066;c,s=np.cos(angle),np.sin(angle)
    R=np.array([[1,0,0],[0,c,-s],[0,s,c]]);origin=np.array([0,0,1.2])
    point=origin+R@np.array([2.68,0,.034])
    body=ET.SubElement(root.find('worldbody'),'body',name='physical_crumb',pos=' '.join(map(str,point)),euler='.349066 0 0')
    ET.SubElement(body,'freejoint',name='crumb_joint')
    ET.SubElement(body,'geom',name='crumb',type='box',size='.018 .025 .014',mass='.004',rgba='.4 .22 .075 1',friction='.8 .005 .001')
    ET.SubElement(root.find(".//body[@name='pv_array_rack']"),'geom',name='catch_tray',type='box',
                  pos='3.28 0 -.20',size='.28 .7 .025',rgba='.25 .3 .35 1',friction='1 .005 .001')
    xml=ET.tostring(root,encoding='unicode');(directory/'model.xml').write_text(xml)
    m=mujoco.MjModel.from_xml_string(xml);d=mujoco.MjData(m)
    d.qpos[:3]=origin+R@np.array([2.05,0,.12]);mujoco.mj_forward(m,d)
    joints=[m.joint(a+'_'+b).dofadr[0] for a in ('left','right') for b in ('front','rear')]
    integral=np.zeros(4);crumb=m.geom('crumb').id;tray=m.geom('catch_tray').id
    offglass=False;caught=False;rows=[];peak_force=0.
    for _ in range(4000):
        v=.14 if 1<d.time<6 else 0.
        for i,j in enumerate(joints):
            error=v/.06-d.qvel[j];integral[i]=np.clip(integral[i]+error*.002,-3,3)
            d.ctrl[i]=np.clip(.8*error+.5*integral[i],-3,3)
        d.ctrl[4]=-15 if 1<d.time<6 else 0.
        mujoco.mj_forward(m,d)
        p=R.T@(d.geom_xpos[crumb]-origin)
        extent=np.abs(R.T@d.geom_xmat[crumb].reshape(3,3))@m.geom_size[crumb]
        offglass=offglass or p[0]-extent[0]>3
        for index,contact in enumerate(d.contact):
            if crumb in (contact.geom1,contact.geom2):
                force=np.zeros(6);mujoco.mj_contactForce(m,d,index,force);peak_force=max(peak_force,float(force[0]))
                if {int(contact.geom1),int(contact.geom2)}=={crumb,tray}:caught=True
        rows.append([float(d.time),*p,*d.qpos[:3]])
        mujoco.mj_step(m,d)
        if not np.isfinite(d.qpos).all() or any(w.number for w in d.warning):raise RuntimeError('Invalid physics')
    with (directory/'positions.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['time_s','crumb_panel_x','crumb_panel_y','crumb_panel_z','robot_world_x','robot_world_y','robot_world_z']);writer.writerows(rows)
    result={'fully_left_glass':bool(offglass),'contacted_catch_tray':bool(caught),'peak_crumb_contact_force_N':peak_force,
            'final_crumb_panel_position_m':p.tolist(),'mechanism':'Physical brush contact with reverse brush rotation; crumb remains a rigid body throughout',
            'scope':'One controlled near-edge ejection pilot, not integrated collection of arbitrary central crumbs'}
    (directory/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));return result


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args();run(a.output_dir)
