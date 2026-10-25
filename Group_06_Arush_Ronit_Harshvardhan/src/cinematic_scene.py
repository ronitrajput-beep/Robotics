"""Presentation-only rooftop materials/scenery. Never enters physics or sensor RGB."""
import numpy as np
import mujoco


class RooftopScene:
    def __init__(self):
        self.rng=np.random.default_rng(42)
        self.buildings=[(x,y,float(self.rng.uniform(8,15)),float(self.rng.uniform(.6,1.5)))
                        for y in (18,25,34) for x in np.arange(-22,24,3.2)]
    def geom(self,scene,kind,size,pos,color,rotation=None,specular=.1):
        if scene.ngeom>=scene.maxgeom:raise RuntimeError('Presentation geometry capacity exceeded')
        g=scene.geoms[scene.ngeom]
        mujoco.mjv_initGeom(g,kind,np.asarray(size,float),np.asarray(pos,float),
                          np.eye(3).ravel() if rotation is None else np.asarray(rotation).ravel(),np.asarray(color,float))
        g.specular=specular;g.shininess=.6;scene.ngeom+=1
        return g
    def box(self,scene,size,pos,color,rotation=None,specular=.1):
        return self.geom(scene,mujoco.mjtGeom.mjGEOM_BOX,size,pos,color,rotation,specular)
    def beam(self,scene,a,b,radius,color):
        if scene.ngeom>=scene.maxgeom:raise RuntimeError('Presentation geometry capacity exceeded')
        g=scene.geoms[scene.ngeom]
        mujoco.mjv_initGeom(g,mujoco.mjtGeom.mjGEOM_CAPSULE,np.ones(3),np.zeros(3),np.eye(3).ravel(),np.array(color,float))
        mujoco.mjv_connector(g,mujoco.mjtGeom.mjGEOM_CAPSULE,radius,np.array(a,float),np.array(b,float));scene.ngeom+=1
    def apply(self,scene,m,d):
        rack=m.body('pv_array_rack').id;R=d.xmat[rack].reshape(3,3);o=d.xpos[rack]
        world=lambda p:o+R@np.asarray(p)
        # Surface materials affect this render only, not model arrays.
        for g in scene.geoms[:scene.ngeom]:
            if g.objtype!=mujoco.mjtObj.mjOBJ_GEOM or g.objid<0:continue
            name=m.geom(g.objid).name
            if name=='chassis_geom':g.rgba[:]=[.06,.38,.43,1];g.specular=.65;g.shininess=.8
            elif name.startswith('frame_'):g.rgba[:]=[.7,.74,.76,1];g.specular=.8;g.shininess=.8
            elif name.endswith('_roller'):g.rgba[:]=[.035,.04,.045,1];g.specular=.18
        if scene.nlight:
            light=scene.lights[0];light.type=mujoco.mjtLightType.mjLIGHT_DIRECTIONAL
            light.dir[:]=[-.35,-.25,-1];light.ambient[:]=[.28,.30,.34]
            light.diffuse[:]=[.85,.80,.69];light.specular[:]=[.6,.57,.5];light.castshadow=True
        scene.flags[mujoco.mjtRndFlag.mjRND_SHADOW]=1
        # Rooftop deck and individually coloured boards.
        self.box(scene,[120,120,.05],[0,0,-6.2],[.38,.43,.48,1])
        self.box(scene,[4.7,3.7,3.0],[0,0,-3.04],[.48,.49,.49,1])
        self.box(scene,[4.7,3.7,.08],[0,0,0],[.24,.25,.27,1])
        for i in range(47):
            shade=.02*np.sin(i*1.8)
            self.box(scene,[.095,3.65,.008],[-4.6+i*.2,0,.09],[.34+shade,.27+shade,.20+shade,1])
        # Open skyline against a layered blue sky; no external asset dependencies.
        for i in range(18):
            color=[.76-.019*i,.85-.014*i,.91-.006*i,1]
            sky=self.box(scene,[120,.2,2],[0,65,i*4],color);sky.emission=.2;sky.specular=0
        for i,(x,y,height,width) in enumerate(self.buildings):
            color=[.34+.025*(i%4),.41+.02*(i%3),.49+.02*(i%4),1]
            self.box(scene,[width,width,height/2],[x,y,-6+height/2],color)
            if y==18:
                for floor in range(1,int(height/.7),3):
                    for col in (-.5,.5):
                        self.box(scene,[.12,.012,.18],[x+col*width,y-width-.014,-5.6+floor*.7],[.67,.78,.84,1])
        sun=self.geom(scene,mujoco.mjtGeom.mjGEOM_SPHERE,[2,0,0],[-14,62,11],[1,.92,.65,1]);sun.emission=.8
        for x,y,z in [(-10,54,13),(12,56,11),(27,59,10)]:
            for shift in (-2,0,2):
                self.geom(scene,mujoco.mjtGeom.mjGEOM_ELLIPSOID,[2.6,.8,.7],[x+shift,y,z+.3*(shift==0)],[.94,.96,.99,1])
        # Balcony rails and a clear front safety screen.
        for y in (-3.45,3.45):
            self.beam(scene,[-4.5,y,1.12],[4.5,y,1.12],.025,[.12,.16,.18,1])
            for x in np.linspace(-4.5,4.5,10):
                self.beam(scene,[x,y,.1],[x,y,1.12],.018,[.16,.20,.22,1])
        for x in (-4.5,4.5):
            self.beam(scene,[x,-3.45,1.12],[x,3.45,1.12],.025,[.12,.16,.18,1])
        # Steel panel frame supports with diagonal braces.
        tops=[]
        for x in (-2.6,2.6):
            for y in (-1.65,1.65):
                top=world([x,y,-.07]);base=np.array([top[0],top[1],.12]);tops.append((base,top))
                self.beam(scene,base,top,.035,[.38,.42,.45,1])
                self.box(scene,[.12,.12,.025],base,[.26,.29,.31,1])
        for i,j in [(0,1),(2,3)]:self.beam(scene,tops[i][0],tops[j][1],.017,[.32,.36,.39,1])
        # Photovoltaic cell grid and busbars, below the unchanged dirt layer.
        for ix in range(12):
            for iy in range(8):
                x=-2.75+ix*.5;y=-1.75+iy*.5
                color=[.025+.003*(ix%3),.075+.004*(iy%3),.145+.006*((ix+iy)%3),1]
                cell=self.box(scene,[.245,.245,.00015],world([x,y,.02045]),color,R,.65)
                cell.shininess=.85
                for shift in (-.11,.11):
                    self.box(scene,[.0012,.242,.00007],world([x+shift,y,.02068]),[.39,.49,.58,1],R,.7)
        # A home marker, painted on top of the panel, not a physical obstacle.
        for cx,cy,sx,sy in [(-2.82,1.53,.012,.13),(-2.62,1.53,.012,.13),(-2.72,1.53,.11,.012)]:
            self.box(scene,[sx,sy,.0001],world([cx,cy,.021]),[.25,.8,.55,1],R)
        # Robot hardware details follow the actual rigid-body pose.
        b=m.body('crawler_chassis').id;B=d.xmat[b].reshape(3,3);p=d.xpos[b]
        robot=lambda v:p+B@np.array(v)
        self.box(scene,[.15,.16,.006],robot([0,0,.046]),[.15,.20,.22,1],B,.7)
        for x in (-.17,.17):
            for y in (-.19,.19):
                self.geom(scene,mujoco.mjtGeom.mjGEOM_CYLINDER,[.008,.003,0],robot([x,y,.048]),[.72,.75,.77,1],B,.8)
        for y in (-.20,.20):self.box(scene,[.13,.025,.018],robot([0,y,-.01]),[.12,.15,.17,1],B,.4)
        # Camera housing is aligned with the actual robot sensor camera.
        cam=m.camera('robot_camera').id;C=d.cam_xmat[cam].reshape(3,3);cp=d.cam_xpos[cam]
        self.beam(scene,robot([.12,0,.045]),cp,.012,[.3,.34,.36,1])
        self.box(scene,[.04,.03,.025],cp,[.16,.20,.22,1],C,.5)
        self.geom(scene,mujoco.mjtGeom.mjGEOM_CYLINDER,[.021,.006,0],cp-C[:,2]*.03,[.025,.045,.065,1],C,.9)
        brush=m.geom('brush_cylinder').id;Q=d.geom_xmat[brush].reshape(3,3);bp=d.geom_xpos[brush]
        for axial in np.linspace(-.38,.38,16):
            for angle in (0,np.pi/2,np.pi,3*np.pi/2):
                radial=np.array([np.cos(angle),np.sin(angle),0])
                self.beam(scene,bp+Q@(radial*.058+[0,0,axial]),bp+Q@(radial*.065+[0,0,axial]),.002,[.18,.53,.65,1])


def cinematic_camera(time,d,m):
    """Continuous overview/inspection shots; never controls a sensor camera."""
    camera=mujoco.MjvCamera();mujoco.mjv_defaultCamera(camera)
    rack=m.body('pv_array_rack').id;origin=d.xpos[rack]
    robot=d.xpos[m.body('crawler_chassis').id]
    if time<2.8:
        camera.lookat[:]=origin+[0,0,-.15];camera.distance=9.8;camera.azimuth=110-7*time;camera.elevation=-16
    elif time<6:
        camera.lookat[:]=origin+[0,0,.25];camera.distance=3.6;camera.azimuth=90;camera.elevation=-55
    else:
        phase=time%80
        if 22<phase<34:
            camera.lookat[:]=robot+[.16,0,-.015];camera.distance=1.55;camera.azimuth=115;camera.elevation=-28
        else:
            camera.lookat[:]=origin;camera.distance=8.;camera.azimuth=85+12*np.sin(time/70);camera.elevation=-52
    return camera


def make_renderer(m,width=1280,height=720):
    saved=(m.vis.global_.offwidth,m.vis.global_.offheight,m.vis.quality.shadowsize,m.vis.quality.offsamples)
    try:
        m.vis.global_.offwidth=width;m.vis.global_.offheight=height;m.vis.quality.shadowsize=2048;m.vis.quality.offsamples=2
        return mujoco.Renderer(m,height=height,width=width,max_geom=10000)
    finally:
        m.vis.global_.offwidth,m.vis.global_.offheight,m.vis.quality.shadowsize,m.vis.quality.offsamples=saved


def render_studio(renderer,m,d,camera,environment,field=None):
    # Model statistics only determine render clipping/shadow scale; restore them
    # before the next sensor render or physics step.
    extent=m.stat.extent
    try:
        m.stat.extent=10
        renderer.update_scene(d,camera=camera);environment.apply(renderer.scene,m,d)
        if field is not None:
            rack=m.body('pv_array_rack').id
            field.append_visuals(renderer.scene,d.xpos[rack],d.xmat[rack].reshape(3,3))
        return renderer.render()
    finally:m.stat.extent=extent
