"""Latched supervisor; braking envelope is an assumption, verified per scenario."""
from dataclasses import dataclass

@dataclass
class StopSupervisor:
    reason: str | None = None
    triggered_at: float | None = None
    quiet_since: float | None = None
    assumed_deceleration: float = .30
    latency: float = .05

    def margin(self, speed):
        return .02 + speed*self.latency + speed*speed/(2*self.assumed_deceleration)

    def update(self, time, speed, clearance, pose_valid=True, brush_stalled=False):
        if self.reason is None:
            reason = ('POSE_DROPOUT' if not pose_valid else
                      'BRUSH_STALL' if brush_stalled else
                      'EDGE_MARGIN' if clearance < self.margin(speed) else None)
            if reason:
                self.reason=reason;self.triggered_at=time
        if self.reason is None:return None
        if speed < .02:
            if self.quiet_since is None:self.quiet_since=time
        else:self.quiet_since=None
        if self.quiet_since is not None and time-self.quiet_since>=.5:return 'STOPPED'
        if time-self.triggered_at>=3:return 'ABORT_UNSTOPPED'
        return 'BRAKING'
