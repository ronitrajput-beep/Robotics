"""Bounded wheel targets and torque slew; conditional integration prevents windup."""
import numpy as np


class DriveRegulator:
    def __init__(self,dt,torque_limit=1.0,wheel_acceleration=4.,torque_rate=4.):
        self.dt=dt;self.torque_limit=torque_limit;self.wheel_acceleration=wheel_acceleration;self.torque_rate=torque_rate
        self.targets=np.zeros(4);self.integral=np.zeros(4);self.torque=np.zeros(4);self.mode=None
    def update(self,requested,actual,mode):
        if mode!=self.mode:self.integral[:]=0;self.mode=mode
        self.targets+=np.clip(np.asarray(requested)-self.targets,-self.wheel_acceleration*self.dt,self.wheel_acceleration*self.dt)
        error=self.targets-np.asarray(actual)
        proposed=np.clip(self.integral+error*self.dt,-3,3)
        unsaturated=.6*error+.2*proposed
        integrate=(abs(unsaturated)<=self.torque_limit)|(error*unsaturated<0)
        self.integral=np.where(integrate,proposed,self.integral)
        target=np.clip(.6*error+.2*self.integral,-self.torque_limit,self.torque_limit)
        self.torque+=np.clip(target-self.torque,-self.torque_rate*self.dt,self.torque_rate*self.dt)
        return self.torque.copy()
