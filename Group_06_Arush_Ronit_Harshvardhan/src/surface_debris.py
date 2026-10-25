"""Visible surface-layer removal proxy. Physical crumbs are handled separately."""
from dataclasses import dataclass
import numpy as np
import mujoco


@dataclass
class DustPatch:
    x: float
    y: float
    radius: float=.055
    remaining: float=1.
    aspect: float=1.
    angle: float=0.
    shade: float=1.
    initial_mass_kg: float | None=None


class SurfaceDebris:
    def __init__(self):
        self.patches=[]

    def deposit(self,positions):
        self.patches.extend(DustPatch(float(x),float(y)) for x,y in positions)

    def deposit_scattered(self,position,rng):
        for _ in range(4):
            x=float(np.clip(position[0]+rng.uniform(-.14,.14),-2.95,2.95))
            y=float(np.clip(position[1]+rng.uniform(-.12,.12),-1.91,1.91))
            self.patches.append(DustPatch(x,y,float(rng.uniform(.035,.070)),1.,
                float(rng.uniform(.6,1.35)),float(rng.uniform(0,2*np.pi)),float(rng.uniform(.8,1.15))))

    def clean(self,center,axle,radius,halfwidth,normal_force,brush_speed,dt):
        norm=np.linalg.norm(axle[:2])
        if normal_force<=.1 or abs(brush_speed)<=1 or norm<1e-8:return
        lateral=axle[:2]/norm;forward=np.array([lateral[1],-lateral[0]])
        for patch in self.patches:
            offset=np.array([patch.x,patch.y])-center[:2]
            # Require the patch centre to be under the tool and near the local surface.
            # Aggregate load + geometric gap is still an explicitly uncalibrated proxy.
            local_height=center[2]+float(offset@lateral)*float(axle[2])/norm
            if abs(offset@forward)<radius and abs(offset@lateral)<halfwidth*norm and local_height-radius<=.024:
                patch.remaining*=np.exp(-5.*dt)

    def append_visuals(self,scene,origin,rotation):
        for patch in self.patches:
            if patch.remaining<.1:continue
            if scene.ngeom>=scene.maxgeom:raise RuntimeError('Scene geometry capacity exceeded')
            color=np.array([.40*patch.shade,.22*patch.shade,.075*patch.shade,1.])
            c,s=np.cos(patch.angle),np.sin(patch.angle)
            patch_rotation=rotation@np.array([[c,-s,0],[s,c,0],[0,0,1]])
            # Radius shrinks with remaining area so the RGB verifier sees residuals.
            uniform=patch.aspect==1. and patch.angle==0.
            visible_radius=patch.radius*np.sqrt(patch.remaining)
            if not uniform:visible_radius=max(.040,visible_radius)  # retain observable residual until the declared clean threshold
            kind=mujoco.mjtGeom.mjGEOM_CYLINDER if uniform else mujoco.mjtGeom.mjGEOM_ELLIPSOID
            size=np.array([patch.radius*np.sqrt(patch.remaining),.001,0.]) if uniform else np.array([visible_radius,visible_radius*patch.aspect,.001])
            mujoco.mjv_initGeom(scene.geoms[scene.ngeom],kind,size,
                origin+rotation@np.array([patch.x,patch.y,.022]),patch_rotation.ravel(),color)
            scene.ngeom+=1

    def summary(self):
        return {'patches':len(self.patches),'uncleared_patches':int(sum(p.remaining>=.1 for p in self.patches)),
                'residual_patches':[{'x_m':p.x,'y_m':p.y,'remaining':float(p.remaining)} for p in self.patches if p.remaining>=.1],
                'mean_residual':float(np.mean([p.remaining for p in self.patches])) if self.patches else 0.}
