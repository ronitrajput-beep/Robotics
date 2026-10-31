import sys,unittest
from pathlib import Path
import numpy as np
import mujoco
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from cinematic_scene import RooftopScene,make_renderer,render_studio,cinematic_camera


class PresentationIsolationChecks(unittest.TestCase):
    def test_presentation_does_not_change_sensor_images_or_physics(self):
        m=mujoco.MjModel.from_xml_path(str(Path(__file__).resolve().parents[1]/'models/guarded_cleaning_crawler.xml'))
        d=mujoco.MjData(m);mujoco.mj_forward(m,d)
        qpos=d.qpos.copy();qvel=d.qvel.copy();rgba=m.geom_rgba.copy()
        config=(m.stat.extent,m.vis.global_.offwidth,m.vis.global_.offheight,m.vis.quality.shadowsize,m.vis.quality.offsamples)
        with mujoco.Renderer(m,height=240,width=320) as sensor:
            sensor.update_scene(d,camera='edge_left');before=sensor.render().copy()
            studio=make_renderer(m,width=640,height=360)
            rgb=render_studio(studio,m,d,cinematic_camera(25,d,m),RooftopScene());studio.close()
            self.assertEqual(rgb.shape,(360,640,3))
            sensor.update_scene(d,camera='edge_left');after=sensor.render()
        np.testing.assert_array_equal(before,after)
        np.testing.assert_array_equal(qpos,d.qpos);np.testing.assert_array_equal(qvel,d.qvel)
        np.testing.assert_array_equal(rgba,m.geom_rgba)
        self.assertEqual(config,(m.stat.extent,m.vis.global_.offwidth,m.vis.global_.offheight,m.vis.quality.shadowsize,m.vis.quality.offsamples))
