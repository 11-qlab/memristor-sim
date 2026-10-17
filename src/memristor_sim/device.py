"""Memristor device models.

Two standard models:

1. Linear ion drift (Strukov 2008):
     R(w) = R_on * w / D + R_off * (1 - w / D)
     dw/dt = mu_v * R_on / D^2 * i(t)

2. Behavioral model with nonlinear conductance update (used in
   neuromorphic hardware):
     G_new = G_old + dG (for potentiation)
     G_new = G_old - dG (for depression)
   with non-linear dG formulas from the literature.

Typical device parameters (HfO2, TaOx, or WO3 resistive switching):
     R_on  ~ 1-10 kOhm (LRS, low resistance state)
     R_off ~ 100 kOhm - 10 MOhm (HRS, high resistance state)
     On/off ratio ~ 10-1000
"""
from __future__ import annotations
import numpy as np


class Memristor:
    """A single memristive device (resistive switching)."""

    def __init__(self,
                 R_on=1e3,
                 R_off=1e5,
                 mu_v=1e-14,
                 D=10e-9,
                 G_min=None,
                 G_max=None):
        self.R_on = R_on
        self.R_off = R_off
        self.mu_v = mu_v
        self.D = D

        # Conductance bounds (S)
        self.G_max = 1.0 / R_on if G_max is None else G_max
        self.G_min = 1.0 / R_off if G_min is None else G_min

        # Initial state: at midpoint
        self.G = 0.5 * (self.G_min + self.G_max)

    @property
    def R(self):
        return 1.0 / self.G

    def update(self, pulses, dG_max=None):
        """Apply `pulses` programming pulses (positive = potentiate)."""
        if dG_max is None:
            dG_max = 0.1 * (self.G_max - self.G_min)

        for _ in range(abs(pulses)):
            if pulses > 0:
                # Potentiation: exponential approach to G_max
                dG = dG_max * (1 - (self.G - self.G_min) / (self.G_max - self.G_min))
                self.G = min(self.G + dG, self.G_max)
            else:
                dG = dG_max * ((self.G - self.G_min) / (self.G_max - self.G_min))
                self.G = max(self.G - dG, self.G_min)

    def reset(self, to="mid"):
        if to == "mid":
            self.G = 0.5 * (self.G_min + self.G_max)
        elif to == "on":
            self.G = self.G_max
        elif to == "off":
            self.G = self.G_min

    def __repr__(self):
        return (f"Memristor(R_on={self.R_on/1e3:.1f}k, "
                f"R_off={self.R_off/1e3:.0f}k, G={self.G*1e6:.1f}uS)")


if __name__ == "__main__":
    print("=== Single memristor ===\n")

    m = Memristor()
    print(f"  {m}")
    print(f"  R_on = {m.R_on/1e3:.1f} kOhm")
    print(f"  R_off = {m.R_off/1e3:.0f} kOhm")
    print(f"  On/off ratio = {m.R_off/m.R_on:.0f}")
    print(f"  G_max = {m.G_max*1e6:.1f} uS")
    print(f"  G_min = {m.G_min*1e6:.2f} uS")
    print()

    print("Conductance after N pulses (starting at mid):")
    for N in (-10, -5, -1, 0, 1, 5, 10):
        m.reset("mid")
        m.update(N)
        print(f"  {N:+3d} pulses: G = {m.G*1e6:6.2f} uS")
