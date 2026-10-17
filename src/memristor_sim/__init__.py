"""Memristor crossbar simulator."""
from .device import Memristor
from .crossbar import Crossbar
from .energy_audit import (
    per_mac_comparison, per_vmm_comparison,
    E_MEMRISTOR_MAC_J, E_ADIABATIC_MAC_J, E_DIGITAL_MAC_J,
)

__version__ = "0.1.0"
__all__ = [
    "Memristor", "Crossbar",
    "per_mac_comparison", "per_vmm_comparison",
    "E_MEMRISTOR_MAC_J", "E_ADIABATIC_MAC_J", "E_DIGITAL_MAC_J",
]
