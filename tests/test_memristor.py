"""Tests for memristor simulator."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import numpy as np
import pytest


def test_memristor_init():
    from memristor_sim import Memristor
    m = Memristor()
    assert m.R_on < m.R_off
    assert m.G_min < m.G < m.G_max


def test_potentiation_increases_G():
    from memristor_sim import Memristor
    m = Memristor()
    m.reset("mid")
    G0 = m.G
    m.update(5)
    assert m.G > G0


def test_depression_decreases_G():
    from memristor_sim import Memristor
    m = Memristor()
    m.reset("mid")
    G0 = m.G
    m.update(-5)
    assert m.G < G0


def test_G_bounded():
    from memristor_sim import Memristor
    m = Memristor()
    m.update(10000)
    assert m.G <= m.G_max + 1e-12
    m.update(-20000)
    assert m.G >= m.G_min - 1e-12


def test_crossbar_vmm():
    from memristor_sim import Crossbar
    N = 4
    cb = Crossbar(N, N)
    G = np.ones((N, N)) * 1e-5
    cb.program(G)
    V = np.array([0.1, 0.2, 0.3, 0.4])
    I = cb.vmm(V)
    assert np.allclose(I, G @ V)


def test_energy_per_mac_positive():
    from memristor_sim import Crossbar
    cb = Crossbar(64, 64)
    E = cb.energy_per_mac()
    assert E > 0


def test_per_mac_memristor_loses_to_adiabatic():
    """Honest result: memristor per-MAC is worse than adiabatic."""
    from memristor_sim import per_mac_comparison
    r = per_mac_comparison()
    assert r["memristor_vs_adiabatic"] > 1.0


def test_per_mac_memristor_beats_digital():
    """Memristor per-MAC is better than digital CMOS."""
    from memristor_sim import per_mac_comparison
    r = per_mac_comparison()
    assert r["memristor_vs_digital"] < 1.0
