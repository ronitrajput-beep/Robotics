"""Guarded-route geometry. Body reach, support and cleaning are separate metrics."""
import numpy as np
from transit_planning import cross_slope_transit


def edge_raster(profile="standard"):
    if profile not in ("standard","inward_turns"):raise ValueError("Unknown guarded route profile")
    if profile=="inward_turns":
        points=[(-2.72,1.53)]
        for i,y in enumerate(np.linspace(1.60,-1.60,9)):
            if i:
                edge=points[-1][0];previous_y=points[-1][1]
                points.extend([(edge-np.sign(edge)*.70,previous_y),(edge-np.sign(edge)*1.70,float(y))])
            points.append((2.72 if i%2==0 else -2.72,float(y)))
        points.extend(cross_slope_transit(points[-1],points[0]))
        return np.array(points)
    points=[(-2.72,1.70)]
    for i,y in enumerate(np.linspace(1.77,-1.77,9)):
        if i:points.append((points[-1][0]-np.sign(points[-1][0])*.65,float(y)))
        points.append((2.78 if i%2==0 else -2.78,float(y)))
    points.extend([(0.,-1.2),(0.,1.1),points[0]])
    return np.array(points)


def body_edge_gaps(position,rotation,halfsize=(.22,.18,.04)):
    # Axis-aligned panel bounds of the actual oriented chassis box.
    extent=np.abs(rotation)@np.asarray(halfsize)
    x,y=position[:2];ex,ey=extent[:2]
    return np.array([3+x-ex,3-x-ex,2+y-ey,2-y-ey])


def sweep_goal_count(profile):
    # Nine rows: one first endpoint + eight pairs of connector points/endpoints.
    return 25 if profile=='inward_turns' else 17
