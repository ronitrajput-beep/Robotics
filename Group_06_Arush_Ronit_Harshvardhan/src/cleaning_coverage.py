"""Area-weighted projected brush-footprint proxies, not resolved bristle contacts."""
import numpy as np


class CoverageMap:
    def __init__(self, nx=120, ny=80):
        self.dx, self.dy = 6 / nx, 4 / ny
        self.x = -3 + (np.arange(nx) + .5) * self.dx
        self.y = -2 + (np.arange(ny) + .5) * self.dy
        self.X, self.Y = np.meshgrid(self.x, self.y)
        self.geometric = np.zeros((ny, nx), bool)
        self.qualified = np.zeros((ny, nx), bool)
        self.soil = np.ones((ny, nx))
        # Declared interior reporting region, not proof that every cell is reachable.
        self.interior = (abs(self.X) < 2.55) & (abs(self.Y) < 1.55)

    def update(self, center, axle, radius, halfwidth, force, speed, sweeping, dt):
        axle = np.asarray(axle, dtype=float)
        norm = np.linalg.norm(axle)
        if norm < 1e-10:
            return
        lateral = axle / norm
        forward = np.array([lateral[1], -lateral[0]])
        # Conservative bounding box plus one cell; all qualifying cells retain
        # the exact original dot-product test and update order.
        extent=np.abs(forward)*radius+np.abs(lateral)*(halfwidth*norm)
        x0=max(0,int(np.searchsorted(self.x,center[0]-extent[0]))-1)
        x1=min(len(self.x),int(np.searchsorted(self.x,center[0]+extent[0],side='right'))+1)
        y0=max(0,int(np.searchsorted(self.y,center[1]-extent[1]))-1)
        y1=min(len(self.y),int(np.searchsorted(self.y,center[1]+extent[1],side='right'))+1)
        if x0>=x1 or y0>=y1:return
        region=np.s_[y0:y1,x0:x1]
        dx, dy = self.X[region] - center[0], self.Y[region] - center[1]
        mask = ((abs(dx * forward[0] + dy * forward[1]) < radius) &
                (abs(dx * lateral[0] + dy * lateral[1]) < halfwidth * norm))
        self.geometric[region] |= mask
        if sweeping and force > .1 and abs(speed) > 1:
            self.qualified[region] |= mask
            soil=self.soil[region];soil[mask] *= np.exp(-2 * dt)

    def summary(self):
        area = self.dx * self.dy
        return {
            'grid_cell_area_m2': area,
            'panel_area_m2': 24.,
            'geometric_footprint_fraction': float(self.geometric.mean()),
            'qualified_contact_fraction': float(self.qualified.mean()),
            'half_soil_proxy_removed_fraction': float((self.soil <= .5).mean()),
            'interior_area_m2': float(self.interior.sum() * area),
            'interior_qualified_fraction': float(self.qualified[self.interior].mean()),
            'soil_removed_proxy_fraction': float(1 - self.soil.mean()),
        }

    def save(self, path):
        np.savez_compressed(path, x_m=self.x, y_m=self.y,
                            geometric=self.geometric, qualified=self.qualified,
                            soil=self.soil, interior=self.interior)
