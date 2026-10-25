"""Guarded-route geometry. Body reach, support and cleaning are separate metrics."""
import numpy as np
from transit_planning import cross_slope_transit


def edge_raster(profile="standard"):
    if profile not in ("standard","inward_turns","external_dock"):raise ValueError("Unknown guarded route profile")
    if profile=="external_dock":
        base=edge_raster("inward_turns")
        sweep=base[1:1+sweep_goal_count("inward_turns")]
        points=[(-3.65,1.53),*map(tuple,sweep)]
        points.extend(home_transit(points[-1],points[0]))
        return np.asarray(points)
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
    return 25 if profile in ('external_dock','inward_turns') else 17


def home_transit(start,home):
    if home[0]<-3.:
        return cross_slope_transit(start,(-2.72,1.53))+[tuple(home)]
    return cross_slope_transit(start,home)


def supported_position(position,external_dock=False):
    x,y,z=position
    panel=abs(x)<=3.1 and abs(y)<=2.1
    dock=external_dock and -4.4<=x<=-2.9 and 1.0<=y<=2.1
    return bool(z>=.04 and (panel or dock))
