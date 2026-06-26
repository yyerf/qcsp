# Quirk CTF Guide

## Why Quirk Matters For QCSP
The handbook explicitly says some challenges may redirect participants to Quirk. That makes Quirk part of the Classical-Quantum challenge surface, not just a study resource.

Quirk is relevant because it is:
- A fast visual simulator for small quantum circuits.
- Linkable: circuits are stored in the URL fragment as `#circuit=...`.
- Exportable: it can copy Circuit JSON and Simulation Data JSON.
- CTF-friendly: a challenge can hide useful data in circuit JSON, custom gates, oracle labels, measurement branches, or probability displays.

## What To Inspect First
If a challenge gives a Quirk link:
```bash
python3 tools/qcsp.py quantum quirk-analyze 'https://algassert.com/quirk#circuit=...'
```

For the fastest "paste and solve" path:
```bash
python3 tools/qcsp.py quantum quirk-solve 'paste the full challenge text, Quirk URL, or exported JSON here'
```

Or paste through stdin:
```bash
python3 tools/qcsp.py quantum quirk-solve
```
Paste the problem, press `Ctrl-D`, then read the report.

If a challenge gives raw JSON:
```bash
python3 tools/qcsp.py quantum quirk-analyze '{"cols":[["H"],["X"]]}'
```

If a challenge gives a JSON file:
```bash
python3 tools/qcsp.py quantum quirk-analyze circuit.json --file
```

Then open or rebuild the link:
```bash
python3 tools/qcsp.py quantum quirk-url circuit.json --file --open
```

## CTF Puzzle Patterns
- URL fragment puzzle: decode `#circuit=` and inspect `cols`, `gates`, and `init`.
- Custom gate puzzle: inspect the `gates` array. Custom gates use IDs like `~abcd` and can contain a `matrix` or nested `circuit`.
- Display puzzle: `Chance`, `Amps`, `Density`, and `Bloch` gates reveal probabilities, amplitudes, density matrices, or single-qubit state.
- Oracle puzzle: custom gates named `Oracle` or control-heavy columns may mark a hidden basis state.
- Grover puzzle: repeated oracle/diffusion structure means the answer may be the most likely basis state after amplification.
- QFT/period puzzle: `QFT`, `QFT†`, modular multiplication, and `modR` gates suggest period finding.
- Phase puzzle: phase may be invisible until converted with `H` gates before measurement.
- Measurement branch puzzle: `Measure`, post-selection, or controlled displays can mean the answer depends on a branch.
- Endianness trap: Quirk arithmetic uses the top wire as the low bit.

## Basic Simulation
For small circuits with common gates:
```bash
python3 tools/qcsp.py quantum quirk-sim '{"cols":[["H",1],["•","X"]]}'
```

This helper supports common H/X/Y/Z power gates, Z-basis controls, Swap pairs, and initial states. It intentionally warns on unsupported custom/arithmetic/QFT gates instead of guessing. Use Quirk's own Simulation Data JSON for full-fidelity output.

## Quirk-Solve Report Guide
`quirk-solve` tries to do the boring work automatically:
- Extracts Quirk URLs from pasted challenge text.
- Extracts raw Circuit JSON and Simulation Data JSON.
- Detects direct flag-like strings.
- Classifies custom gates, displays, QFT, arithmetic, measurement, controls, and likely puzzle style.
- Simulates simple common-gate circuits locally.
- Reads Quirk-exported `output_amplitudes` and display probabilities.
- Prints candidate states as bitstring, decimal, low-to-high order, and probability.

Trust levels:
- Highest: candidate comes from Quirk Simulation Data JSON exported by Quirk itself.
- High: candidate comes from local basic simulation with no warnings.
- Medium: candidate comes from pattern analysis or custom-gate names.
- Low: circuit contains unsupported QFT/arithmetic/custom gates and no Simulation Data JSON was pasted yet.

If the report says to paste Simulation Data JSON:
1. Open the generated Quirk URL.
2. Click `Export`.
3. Copy `Simulation Data JSON`.
4. Run `python3 tools/qcsp.py quantum quirk-solve`.
5. Paste the JSON and press `Ctrl-D`.

## Manual Quirk Workflow
1. Open the Quirk link.
2. Click `Export`.
3. Copy `Circuit JSON`.
4. Run `quirk-analyze` locally.
5. Add `Chance` or `Amps` displays at the output area.
6. Export `Simulation Data JSON`.
7. Look for the highest-probability basis state, detector result, or conditional display data.

## Source-Code Clues
From the local `Quirk` source:
- `src/ui/url.js` loads circuits from `#circuit=...`.
- `src/ui/exports.js` exports Circuit JSON and Simulation Data JSON.
- `src/circuit/Serializer.js` shows the JSON structure: `cols`, optional `gates`, optional `init`.
- `src/ui/menu.js` contains examples for Grover, Shor period finding, CHSH, teleportation, superdense coding, QFT, reversible addition, and magic-state distillation.
- `src/gates/AllGates.js` lists the serializer-known gate families.

## Commands To Remember
```bash
python3 tools/qcsp.py quantum quirk-patterns
python3 tools/qcsp.py quantum quirk-solve 'https://algassert.com/quirk#circuit=...'
python3 tools/qcsp.py quantum quirk list
python3 tools/qcsp.py quantum quirk-analyze 'https://algassert.com/quirk#circuit=...'
python3 tools/qcsp.py quantum quirk-sim circuit.json --file
python3 tools/qcsp.py quantum quirk-url circuit.json --file --open
```
