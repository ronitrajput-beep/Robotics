"""Actual larger rigid-object sweep, with an explicit external catch tray."""
from pathlib import Path
import argparse,csv,json,xml.etree.ElementTree as ET
import mujoco,numpy as np

ROOT=Path(__file__).resolve().parents[1]


def run(directory,on_sample=None):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    root=ET.fromstring((ROOT/'models/guarded_cleaning_crawler.xml').read_text())
    angle=.349066;c,s=np.cos(angle),np.sin(angle);R=np.array([[1,0,0],[0,c,-s],[0,s,c]]);origin=np.array([0,0,1.2])
    point=origin+R@np.array([.8,0,.045])
    body=ET.SubElement(root.find('worldbody'),'body',name='solid_object',pos=' '.join(map(str,point)),euler='.349066 0 0')
    ET.SubElement(body,'freejoint',name='solid_joint')
    ET.SubElement(body,'geom',name='solid_object_geom',type='box',size='.035 .035 .025',mass='.12',
                  rgba='.42 .24 .10 1',friction='.7 .005 .001')
    ET.SubElement(root.find(".//body[@name='pv_array_rack']"),'geom',name='solid_catch_tray',type='box',
                  pos='3.3 0 -.20',size='.30 1.1 .025',rgba='.28 .34 .38 1',friction='1 .005 .001')
    ET.SubElement(root.find(".//body[@name='pv_array_rack']"),'geom',name='lower_catch_tray',type='box',
                  pos='0 -2.3 -.20',size='3.3 .30 .025',rgba='.28 .34 .38 1',friction='1 .005 .001')
    xml=ET.tostring(root,encoding='unicode');(directory/'model.xml').write_text(xml)
    m=mujoco.MjModel.from_xml_string(xml);d=mujoco.MjData(m)
    d.qpos[:3]=origin+R@np.array([.1,0,.12]);mujoco.mj_forward(m,d)
    joints=[m.joint(a+'_'+b).dofadr[0] for a in ('left','right') for b in ('front','rear')]
    integral=np.zeros(4);solid=m.geom('solid_object_geom').id;trays={m.geom('solid_catch_tray').id,m.geom('lower_catch_tray').id};brush=m.geom('brush_cylinder').id
    caught=False;off=False;first_touch=None;peak=0.;rows=[];events=[]
    for _ in range(14500):
        speed=.14 if 1<d.time<24 else 0.
        for i,j in enumerate(joints):
            error=speed/.06-d.qvel[j];integral[i]=np.clip(integral[i]+error*.002,-3,3)
            d.ctrl[i]=np.clip(.8*error+.5*integral[i],-3,3)
        d.ctrl[4]=-15 if 1<d.time<24 else 0.
        mujoco.mj_forward(m,d)
        p=R.T@(d.geom_xpos[solid]-origin);extent=np.abs(R.T@d.geom_xmat[solid].reshape(3,3))@m.geom_size[solid]
        if not off and (p[0]-extent[0]>3 or p[0]+extent[0]<-3 or p[1]-extent[1]>2 or p[1]+extent[1]<-2):off=True;events.append({'time_s':float(d.time),'event':'FULLY_OFF_GLASS'})
        force=0.
        for index,contact in enumerate(d.contact):
            pair={int(contact.geom1),int(contact.geom2)}
            if pair=={brush,solid}:
                wrench=np.zeros(6);mujoco.mj_contactForce(m,d,index,wrench);force+=max(0.,wrench[0])
                if first_touch is None:first_touch=float(d.time);events.append({'time_s':first_touch,'event':'BRUSH_CONTACT'})
            if solid in pair and any(tray in pair for tray in trays) and not caught:caught=True;events.append({'time_s':float(d.time),'event':'CAUGHT_IN_TRAY'})
        peak=max(peak,force)
        rows.append([float(d.time),*p,force,off,caught])
        if on_sample is not None:on_sample(m,d,{'position':p.copy(),'brush_force_N':force,'off_glass':off,'caught':caught})
        mujoco.mj_step(m,d)
        if not np.isfinite(d.qpos).all() or any(w.number for w in d.warning):raise RuntimeError('Invalid physics')
    with (directory/'positions.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['time_s','solid_x_m','solid_y_m','solid_z_m','brush_contact_force_N','off_glass','caught']);w.writerows(rows)
    result={'size_m':[.07,.07,.05],'mass_kg':.12,'material_assumption':'Solid wood-like block, assumed density about 490 kg/m3; no scratch/damage model',
            'first_brush_contact_s':first_touch,'fully_left_glass':off,'contacted_catch_tray':caught,'peak_brush_object_force_N':peak,
            'final_panel_position_m':p.tolist(),'events':events,'scope':'Controlled physical object-ejection test; scripted drive, not camera-selected autonomous collection'}
    (directory/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args();run(a.output_dir)
