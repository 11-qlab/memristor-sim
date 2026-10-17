# memristor-sim

Memristor crossbar simulator for analog matrix-vector multiply.

## The honest verdict

| Comparison | Memristor | Adiabatic | Digital |
|---|---|---|---|
| Per MAC | 1.5 fJ | **122 aJ** | 12 pJ |
| Per VMM (128x128) | 24.6 pJ | **2.0 pJ** | 82 uJ |

- **vs adiabatic**: memristor is 12x WORSE per MAC and per VMM
- **vs digital**: memristor is 8x better per MAC, 3300x better per VMM

Memristors do not beat adiabatic CMOS on energy. They beat
**digital** CMOS by eliminating data movement (no SRAM read,
no ALU dispatch, no writeback).

## Why memristors are built anyway

Even though they lose to adiabatic per operation, memristors win
against the technology actually deployed today (digital CMOS):

- 128x128 VMM in ONE analog step (10 ns) vs 384 ns for digital
- 24.6 pJ per VMM vs 82 uJ for digital (3300x better)
- The whole multiply happens in Ohm's law + Kirchhoff's law, in hardware

But a fully-adiabatic implementation of the same VMM would cost
only 2 pJ. The industry is comparing against digital because
adiabatic CMOS is not yet deployed.

## Physics

- Linear ion drift memristor (Strukov 2008)
- Crossbar VMM (Ohm + KCL in hardware)
- Realistic device: R_on=1k, R_off=100k, on/off=100

## Install

    pip install -e .

## CLI

    memristor-sim device                # single device
    memristor-sim crossbar --N 64       # VMM
    memristor-sim audit                 # energy comparison

## Tests

    pytest tests/ -v

## License

Apache 2.0
