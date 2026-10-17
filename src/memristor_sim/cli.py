"""CLI for memristor-sim."""
import argparse, sys
import numpy as np
from .device import Memristor
from .crossbar import Crossbar
from .energy_audit import per_mac_comparison, per_vmm_comparison


def main(argv=None):
    p = argparse.ArgumentParser(prog="memristor-sim",
        description="Memristor crossbar simulator")
    sub = p.add_subparsers(dest="cmd", required=True)

    pd = sub.add_parser("device", help="Single memristor")
    pd.add_argument("--pulses", type=int, nargs="+",
                    default=[-10, -5, 0, 5, 10])

    pc = sub.add_parser("crossbar", help="Crossbar VMM")
    pc.add_argument("--N", type=int, default=64)

    pa = sub.add_parser("audit", help="Energy comparison")

    args = p.parse_args(argv)

    if args.cmd == "device":
        m = Memristor()
        print(f"{m}")
        print(f"  On/off ratio: {m.R_off/m.R_on:.0f}")
        print()
        for n in args.pulses:
            m.reset("mid")
            m.update(n)
            print(f"  {n:+4d} pulses: G = {m.G*1e6:7.2f} uS")
        return 0

    if args.cmd == "crossbar":
        N = args.N
        cb = Crossbar(N, N)
        G = np.random.uniform(cb.devices[0][0].G_min,
                              cb.devices[0][0].G_max, (N, N))
        cb.program(G)
        V = np.random.uniform(0.01, 0.1, N)
        I = cb.vmm(V)
        err = np.max(np.abs(I - G @ V))
        print(f"Crossbar {N}x{N}:")
        print(f"  VMM error: {err:.2e} A")
        print(f"  Energy per MAC: {cb.energy_per_mac()*1e15:.3f} fJ")
        return 0

    if args.cmd == "audit":
        r = per_mac_comparison()
        print("PER-MAC comparison:")
        print(f"  Memristor : {r['memristor_J']*1e15:.3f} fJ")
        print(f"  Adiabatic : {r['adiabatic_J']*1e18:.2f} aJ")
        print(f"  Digital   : {r['digital_J']*1e12:.2f} pJ")
        print()
        print(f"  Memristor vs adiabatic: {r['memristor_vs_adiabatic']:.2f}x "
              "(memristor worse)")
        print(f"  Memristor vs digital  : {r['memristor_vs_digital']:.4f}x "
              "(memristor better)")
        print()
        print("PER-VMM comparison:")
        for N in (16, 64, 128, 256):
            v = per_vmm_comparison(N)
            print(f"  N={N:>4}: "
                  f"memristor {v['memristor_J']*1e12:>10.3f} pJ vs "
                  f"adiabatic {v['adiabatic_J']*1e12:>10.3f} pJ  "
                  f"({v['memristor_vs_adiabatic']:.2f}x)")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
