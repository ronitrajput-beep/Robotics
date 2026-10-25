"""Cross-slope transits avoid abrupt turns into the steepest uphill direction."""
import numpy as np


def cross_slope_transit(start,end,max_grade=.30):
    current=np.asarray(start,dtype=float).copy();end=np.asarray(end,dtype=float)
    points=[]
    for _ in range(24):
        delta=end-current
        if abs(delta[1])<.02 or abs(delta[1])<=max_grade*abs(delta[0]):
            points.append(tuple(end));return points
        x=1.2 if current[0]<=0 else -1.2
        y=current[1]+np.sign(delta[1])*min(.35,abs(delta[1])/2)
        current=np.array([x,y]);points.append(tuple(current))
    raise ValueError('Could not construct bounded cross-slope transit')
