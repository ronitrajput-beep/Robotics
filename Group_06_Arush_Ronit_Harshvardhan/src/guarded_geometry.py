"""Guarded-route geometry. Body reach, support and cleaning are separate metrics."""
import numpy as np


def edge_raster():
    points=[(-2.72,1.70)]
    for i,y in enumerate(np.linspace(1.70,-1.70,9)):
        if i:points.append((points[-1][0]-np.sign(points[-1][0])*.65,float(y)))
        points.append((2.72 if i%2==0 else -2.72,float(y)))
    points.append((0.,-1.))
    return np.array(points)


def body_edge_gaps(position,rotation,halfsize=(.22,.18,.04)):
    # Axis-aligned panel bounds of the actual oriented chassis box.
    extent=np.abs(rotation)@np.asarray(halfsize)
    x,y=position[:2];ex,ey=extent[:2]
    return np.array([3+x-ex,3-x-ex,2+y-ey,2-y-ey])
