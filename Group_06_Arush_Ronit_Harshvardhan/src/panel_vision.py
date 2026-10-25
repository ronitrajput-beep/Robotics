"""RGB-only controlled-scene dirt segmentation and calibrated plane projection."""
from dataclasses import dataclass
import numpy as np
from scipy import ndimage


@dataclass
class CameraCalibration:
    position: np.ndarray
    rotation: np.ndarray
    fovy_deg: float
    panel_origin: np.ndarray
    panel_rotation: np.ndarray
    glass_z: float = .02

    def project_pixel(self,u,v,width,height):
        focal=.5*height/np.tan(np.deg2rad(self.fovy_deg)/2)
        ray=self.rotation@np.array([(u-width/2)/focal,-(v-height/2)/focal,-1.])
        normal=self.panel_rotation[:,2]
        denominator=float(normal@ray)
        if abs(denominator)<1e-10:return None
        distance=float(normal@(self.panel_origin+normal*self.glass_z-self.position))/denominator
        if distance<=0:return None
        local=self.panel_rotation.T@(self.position+distance*ray-self.panel_origin)
        return local[:2] if abs(local[0])<=3 and abs(local[1])<=2 else None


def detect_dirt(rgb,calibration,min_pixels=8):
    """Prototype for brown deposition under controlled lighting, not arbitrary dirt."""
    r,g,b=rgb.astype(float).transpose(2,0,1)
    mask=(r>45)&(r<235)&(g>20)&(g<190)&(r>1.20*g)&(g>1.12*b)&(b<155)
    labels,count=ndimage.label(mask)
    detections=[]
    # Connected-component bounds avoid rescanning the entire frame per speck.
    for number,bounds in enumerate(ndimage.find_objects(labels),1):
        if bounds is None:continue
        yy,xx=np.nonzero(labels[bounds]==number)
        if len(xx)<min_pixels:continue
        y0,x0=bounds[0].start,bounds[1].start
        # Integer sums preserve the original full-frame mean exactly.
        u=float(int(xx.sum())+x0*len(xx))/len(xx)
        v=float(int(yy.sum())+y0*len(yy))/len(yy)
        point=calibration.project_pixel(u,v,rgb.shape[1],rgb.shape[0])
        if point is not None:
            detections.append({'panel_x_m':float(point[0]),'panel_y_m':float(point[1]),
                               'bbox_xyxy':[x0,y0,bounds[1].stop-1,bounds[0].stop-1],'pixels':len(xx),'confidence':min(1.,len(xx)/12.)})
    return detections,mask
