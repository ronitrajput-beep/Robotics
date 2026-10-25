"""Collection prototype: flush external dock, fixed tool mounts and permanent tray."""
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from build_guarded_model import build as guarded_build,ROOT


def build(destination):
    destination=Path(destination)
    guarded_build(destination)
    tree=ET.parse(destination);root=tree.getroot();rack=root.find(".//body[@name='pv_array_rack']")
    # A coplanar, physically supported side extension. Glass and dock top are z=.02.
    ET.SubElement(rack,'geom',name='dock_platform',type='box',pos='-3.65 1.50 0',size='.65 .50 .02',rgba='.27 .32 .36 1',friction='1.2 .005 .001')
    left=rack.find("geom[@name='guard_left']");left.set('pos','-3.025 -.50 .25');left.set('size','.025 1.50 .25')
    for name,pos,size in [('dock_outer','-4.325 1.50 .25','.025 .55 .25'),('dock_lower','-3.65 .975 .25','.65 .025 .25'),('dock_upper','-3.65 2.025 .25','.65 .025 .25')]:
        ET.SubElement(rack,'geom',name='guard_'+name,type='box',pos=pos,size=size,rgba='.8 .2 .1 0',contype='2',conaffinity='0',friction='0 0 0',condim='1',priority='2')
    # Remove the visual raised trim across the aperture too.
    trim=rack.find("geom[@name='frame_left']");trim.set('pos','-3.025 -.50 .035');trim.set('size','.025 1.50 .035')
    def fixture(name,pos,size,color):
        return ET.SubElement(rack,'geom',name=name,type='box',pos=pos,size=size,rgba=color,contype='0',conaffinity='0')
    fixture('dock_service_cabinet','-4.12 1.55 .22','.12 .33 .20','.72 .76 .78 1')
    fixture('dock_waste_drawer','-4.105 1.55 .14','.14 .22 .09','.12 .18 .21 1')
    fixture('dock_charge_contact','-3.91 1.68 .12','.015 .07 .025','1 .8 .18 1')
    fixture('dock_emptying_port','-3.91 1.43 .12','.015 .06 .04','.04 .07 .09 1')
    # Tray is a permanent physical receiver below the lower edge, with retaining lips.
    for name,pos,size in [('lower_catch_tray','0 -2.33 -.13','3.25 .33 .025'),('tray_outer_lip','0 -2.655 -.045','3.25 .025 .11'),('tray_left_lip','-3.25 -2.33 -.045','.025 .33 .11'),('tray_right_lip','3.25 -2.33 -.045','.025 .33 .11')]:
        ET.SubElement(rack,'geom',name=name,type='box',pos=pos,size=size,rgba='.45 .51 .54 1',friction='1.2 .005 .001')
    chassis=root.find(".//body[@name='crawler_chassis']")
    # Fixed support/shroud/bin shapes share the existing chassis mass budget.
    # They are noncolliding structural representations, not newly validated members.
    for side in (-1,1):
        ET.SubElement(chassis,'geom',name=f'brush_support_{side}',type='capsule',fromto=f'.10 {side*.415} .005 .29 {side*.415} -.04',size='.016',mass='0',rgba='.65 .69 .71 1',contype='0',conaffinity='0')
        ET.SubElement(chassis,'geom',name=f'brush_cross_mount_{side}',type='capsule',fromto=f'.10 {side*.20} .005 .10 {side*.415} .005',size='.016',mass='0',rgba='.65 .69 .71 1',contype='0',conaffinity='0')
    for name,pos,size,color in [('intake_slot','.235 0 -.062','.025 .34 .012','.025 .035 .045 1'),('dust_bin','-.07 0 .079','.115 .145 .035','.23 .34 .38 1'),('bin_lid','-.07 0 .117','.12 .15 .005','.68 .73 .75 1'),('vacuum_motor','-.06 0 .157','.065 .07 .03','.12 .19 .22 1')]:
        ET.SubElement(chassis,'geom',name=name,type='box',pos=pos,size=size,mass='0',rgba=color,contype='0',conaffinity='0')
    for name,a,b in [('intake_duct',' .235 .10 -.04',' .16 .10 .08'),('bin_duct','.16 .10 .08','-.01 .10 .08')]:
        ET.SubElement(chassis,'geom',name=name,type='capsule',fromto=a+' '+b,size='.025',mass='0',rgba='.10 .13 .15 1',contype='0',conaffinity='0')
    body=ET.SubElement(root.find('worldbody'),'body',name='combined_solid',pos='0 0 100',gravcomp='1')
    ET.SubElement(body,'freejoint',name='combined_solid_joint')
    ET.SubElement(body,'geom',name='combined_solid_geom',type='box',size='.035 .035 .025',mass='.12',rgba='.42 .24 .10 0',friction='.7 .005 .001',contype='1',conaffinity='1')
    ET.indent(tree,space='  ');tree.write(destination,encoding='unicode')

if __name__=='__main__':build(ROOT/'models/collection_cleaning_crawler.xml')
