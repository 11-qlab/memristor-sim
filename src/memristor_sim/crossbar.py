"""Memristor crossbar array for vector-matrix multiplication.

Physical operation:
  - Apply input voltages V_j on rows
  - Each memristor at (i, j) has conductance G_ij
  - Current on column i: I_i = sum_j G_ij * V_j
  - This IS a matrix-vector product (VMM), performed in the analog
    domain, in one clock cycle.

No ADC is needed for intermediate results.  ADC is only required
at the output to read the currents.

Energy per MAC in the crossbar:
  E_MAC ~ (V^2 * G) * t_pulse / N_rows
       ~ 5 fJ / N_rows  (published values)

At N=128 crossbar, per-MAC energy ~ 40 aJ.
This is where memristors beat CMOS: parallelism.
"""
from __future__ import annotations
import numpy as np
from .device import Memristor


class Crossbar:
    """N x M memristor crossbar for analog VMM."""

    def __init__(self, n_rows, n_cols, R_on=1e3, R_off=1e5):
        self.N = n_rows
        self.M = n_cols
        self.devices = [[Memristor(R_on=R_on, R_off=R_off)
                         for _ in range(n_cols)]
                        for _ in range(n_rows)]

    def program(self, G_matrix):
        """Set conductances to a target matrix (for simulation)."""
        G_matrix = np.asarray(G_matrix)
        assert G_matrix.shape == (self.N, self.M)
        for i in range(self.N):
            for j in range(self.M):
                self.devices[i][j].G = G_matrix[i, j]

    def read_conductances(self):
        """Return current conductance matrix."""
        return np.array([[self.devices[i][j].G for j in range(self.M)]
                         for i in range(self.N)])

    def vmm(self, voltages):
        """Vector-matrix multiply: I = G @ V.

        voltages: array of length M (one per column)
        Returns: array of length N (current per row)
        """
        V = np.asarray(voltages)
        assert len(V) == self.M
        G = self.read_conductances()
        # I_i = sum_j G_ij V_j
        return G @ V

    def energy_per_mac(self, V=0.1, t_pulse=10e-9):
        """Energy per MAC in one crossbar operation.

        E_MAC = V^2 * G_avg * t_pulse / N_rows
        The V^2 G t_pulse factor is the per-device energy,
        divided by N_rows because all rows operate in parallel.
        """
        G_avg = self.read_conductances().mean()
        E_device = V ** 2 * G_avg * t_pulse
        return E_device / self.N


if __name__ == "__main__":
    print("=== Memristor crossbar VMM ===\n")

    for N in (16, 64, 128, 256):
        cb = Crossbar(N, N)
        # Program with a random conductance matrix
        G = np.random.uniform(cb.devices[0][0].G_min,
                              cb.devices[0][0].G_max, (N, N))
        cb.program(G)

        V = np.random.uniform(0.01, 0.1, N)
        I = cb.vmm(V)

        # Verify against numpy
        I_ref = G @ V
        err = np.max(np.abs(I - I_ref))

        print(f"N = {N}:")
        print(f"  VMM error: {err:.3e} A")
        print(f"  Energy per MAC: {cb.energy_per_mac()*1e15:.3f} fJ")
        print()
