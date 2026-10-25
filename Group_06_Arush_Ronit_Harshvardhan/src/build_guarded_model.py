"""Build a separate, explicitly guarded development model; preserve the base XML."""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]


def build(destination):
    tree=ET.parse(ROOT/'models/solar_cleaning_crawler.xml'); root=tree.getroot()
    ET.SubElement(root,'statistic',extent='6',center='0 0 1.2')  # visible rack bounds; inactive particles at 100 m must not clip onboard camera
    rack=root.find(".//body[@name='pv_array_rack']")
    # Original raised trim remains visual. Separate guard supplies containment.
    for geom in rack.findall('geom'):
        if geom.get('name','').startswith('frame_'):
            geom.set('contype','0');geom.set('conaffinity','0')
    for name,pos,size in [
        ('left', '-3.025 0 .25','.025 2.05 .25'),
        ('right','3.025 0 .25','.025 2.05 .25'),
        ('lower','0 -2.025 .25','3.05 .025 .25'),
        ('upper','0 2.025 .25','3.05 .025 .25')]:
        ET.SubElement(rack,'geom',name='guard_'+name,type='box',pos=pos,size=size,
                      rgba='.8 .2 .1 0',contype='2',conaffinity='0',friction='0 0 0',condim='1',priority='2')
    for geom in root.findall('.//geom'):
        if geom.get('name')=='chassis_geom' or geom.get('name','').endswith('_roller'):
            geom.set('conaffinity','3')
    root.find(".//geom[@name='chassis_geom']").set('rgba','.12 .65 .75 1')
    root.find(".//geom[@name='chassis_geom']").set('size','.22 .235 .04')
    brush=root.find(".//geom[@name='brush_cylinder']")
    brush.set('size','.06 .40')  # permanently fixed 0.8 m width; unchanged 1.2 kg budget
    brush_body=root.find(".//body[@name='rotary_brush']")
    ET.SubElement(brush_body,'geom',name='brush_stripe',type='box',size='.008 .39 .008',
                  pos='.042 0 .042',rgba='1 .9 .2 1',contype='0',conaffinity='0',mass='0')
    for name,pos in [('edge_left','-2.7 0 5'),('edge_right','2.7 0 5')]:
        # Cameras point down at the panel; overlapping cropped views are fused.
        ET.SubElement(rack,'camera',name=name,pos=pos,fovy='70')
    chassis=root.find(".//body[@name='crawler_chassis']")
    ET.SubElement(chassis,'camera',name='robot_camera',pos='.15 0 .25',
                  xyaxes='0 -1 0 .70710678 0 .70710678',fovy='75')
    world=root.find('worldbody')
    for i in range(8):
        particle=ET.SubElement(world,'body',name=f'falling_{i}',pos=f'{i} 0 100',gravcomp='1')
        ET.SubElement(particle,'freejoint',name=f'falling_joint_{i}')
        ET.SubElement(particle,'geom',name=f'falling_geom_{i}',type='sphere',size='.014',mass='.0005',
                      rgba='.4 .22 .075 0',contype='1',conaffinity='1',friction='.8 .01 .001')
    ET.indent(tree,space='  ')
    tree.write(destination,encoding='unicode')


if __name__=='__main__':
    build(ROOT/'models/guarded_cleaning_crawler.xml')
