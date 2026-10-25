import sys,tempfile
sys.path.insert(0,'src')
from pathlib import Path
from unittest.mock import patch
import numpy as np,mujoco
import crawler_cleaning_controller as control
from build_collection_model import build
# A diagnostic copy disables cleaning motor throughout this return transit only.
source=Path('src/crawler_cleaning_controller.py').read_text();source=source.replace("d.ctrl[4]=(-15 if route_profile=='external_dock' and not returning and index==sweep_goal_count(route_profile)-1 and retries==0 else 15) if state in ('SWEEP','EDGE_CLEAN_BOTTOM') else 0",'d.ctrl[4]=0')
namespace={'__file__':str(Path('src/crawler_cleaning_controller.py').resolve()),'__name__':'dock_diagnostic'};exec(compile(source,'dock_diagnostic','exec'),namespace)
namespace['edge_raster']=lambda p:np.array([[-1.8,1.35],[-2.72,1.53],[-3.65,1.53]])
for friction in (1.2,.4,.25):
 with tempfile.TemporaryDirectory() as directory:
  p=Path(directory)/'model.xml';build(p);text=p.read_text().replace('friction="1.2 .005 .001"','friction="'+str(friction)+' .005 .001"',1);p.write_text(text)
  result=namespace['mission'](duration=35,guarded=True,route_profile='external_dock',guarded_model_path=p)
  print('DIAGNOSTIC',friction,result['status'],result['maximum_chassis_tilt_deg'],result['maximum_chassis_height_m'],flush=True)
