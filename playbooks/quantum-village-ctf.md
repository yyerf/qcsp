# Quantum Village-Style CTF Guide

## Why This Matters
The DEF CON Quantum Village/QOLOSSUS examples show a style that is broader than Quirk:
- Tiny OpenQASM circuit synthesis under weird checker constraints.
- Statevector/property validation instead of normal measured output.
- Quantum-history OSINT where the final answer format matters.
- Unicode/native-script traps, like requiring Kitaev's name in Cyrillic.

For QCSP, this is useful because the handbook includes a Classical-Quantum category and allows AI/tools. If organizers borrow this style, speed comes from quickly turning English predicates into circuits and quickly checking answer formats.

## XOR-bit-al Pattern
Challenge:
```text
Make a circuit that has output measurements only when
c[0] xor c[1] == c[2].
Do this in <=7 lines of OpenQASM.
```

The property means the nonzero output basis states must satisfy:
```text
q[2] = q[0] xor q[1]
```

Fast solve:
```bash
python3 tools/qcsp.py quantum qasm-solve 'c[0] xor c[1] == c[2] <=7 lines OpenQASM'
```

The generated solution:
```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
h q[0];
h q[1];
cx q[0],q[2];
cx q[1],q[2];
```

Why it works:
- `h q[0]` and `h q[1]` create all four possible input pairs.
- The two `cx` gates compute `q[2] = q[0] xor q[1]`.
- The only nonzero outputs are `000`, `011`, `101`, and `110`, exactly the satisfying states.
- The tool counts lines the same way the example says the checker did: semicolons.

Check a candidate:
```bash
python3 tools/qcsp.py quantum qasm-check solution.qasm --file --predicate 'c[0] xor c[1] == c[2]'
```

Simulate any small OpenQASM:
```bash
python3 tools/qcsp.py quantum qasm-sim solution.qasm --file
```

Auto-route pasted Quantum Village text:
```bash
python3 tools/qcsp.py quantum qv-solve 'paste challenge text here'
```

## QASM Checker Notes
- Default check is exact support: every nonzero state must satisfy the predicate, and every satisfying state must appear.
- Use `--subset-ok` only if the challenge wording truly allows a strict subset.
- The simulator supports a small OpenQASM 2 subset: `qreg`, `creg`, `h`, `x`, `y`, `z`, `s`, `sdg`, `t`, `tdg`, `cx`, `cz`, `ccx`, `swap`, and ignored `measure`/`barrier`.
- No Qiskit dependency is required.

## Picture Found Pattern
Challenge:
```text
Who is this?
```

Fast helper:
```bash
python3 tools/qcsp.py quantum picture-helper ./person.png
python3 tools/qcsp.py quantum person-lookup kitaev
```

For the provided example, the trap is not just identifying Alexei Kitaev. The accepted answer can require his Cyrillic full name:
```text
Алексей Юрьевич Китаев
```

Workflow:
- Reverse image search the exact crop.
- Identify the person in English.
- Check birthplace/nationality/language.
- Try full legal name, common name, and native-script name.
- Preserve Unicode exactly if the flag/answer box is case-sensitive.

## Common Quantum People To Recognize
- Alexei Kitaev: topological quantum computing, phase estimation, Kitaev model.
- Peter Shor: factoring and period finding.
- Lov Grover: search/amplitude amplification.
- David Deutsch: Deutsch and Deutsch-Jozsa algorithms.
- Charles Bennett and Gilles Brassard: BB84 quantum cryptography.
- Artur Ekert: entanglement-based QKD.
- John Preskill: NISQ and quantum information.
- Richard Feynman: quantum simulation.

## Practical Competition Use
1. If the challenge says OpenQASM, try `qv-solve` first.
2. If it contains an XOR predicate, run `qasm-solve`.
3. If they provide a candidate circuit, run `qasm-check`.
4. If it is an image/person clue, run `picture-helper`, reverse image search, then `person-lookup`.
5. If it is a Quirk link, use `quirk-solve` instead.
