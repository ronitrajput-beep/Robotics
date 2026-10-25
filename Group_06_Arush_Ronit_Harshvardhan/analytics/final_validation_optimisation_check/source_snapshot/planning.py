"""Panel-frame bidirectional raster and conservative whole-robot clearance."""
import numpy as np

FOOTPRINT_RADIUS = .45  # encloses brush: hypot(.29+.06, .275) < .45 m

def raster(layout="standard"):
    if layout not in ("standard", "expanded", "expanded_safe_return"):
        raise ValueError("Unknown raster layout")
    left, right, top = (-2.20, 2.30, 1.20) if layout == "standard" else (-2.40, 2.40, 1.35)
    points=[(left,top)]
    for i,y in enumerate(np.linspace(top,-1.20 if layout=="expanded_safe_return" else -top,8)):
        if i: points.append((points[-1][0] - np.sign(points[-1][0])*.65,float(y)))
        points.append((right if i%2==0 else (-2.30 if layout=="standard" else left),float(y)))
    points.append((0.,-1.))
    return np.array(points)

def segment_reference(position,start,end,lookahead=.30):
    delta=end-start; length=np.linalg.norm(delta)
    if length<1e-10:return end.copy(),float(np.linalg.norm(position-end))
    t=np.clip(np.dot(position-start,delta)/(length*length),0,1)
    closest=start+t*delta
    target=start+min(1,t+lookahead/length)*delta
    return target,float(np.linalg.norm(position-closest))

def clearance(position):
    return float(min(3-abs(position[0]),2-abs(position[1]))-FOOTPRINT_RADIUS)
