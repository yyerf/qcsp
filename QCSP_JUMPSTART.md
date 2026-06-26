# QCSP jumpstart analysis

This is preparation material for authorized CTF/hackathon work only. It should help you move fast on challenge inputs, but it cannot guarantee flags or replace reasoning during the competition.

## Pubmat signals

- Hardware: SpinQ Gemini Mini, a 2-qubit desktop quantum computer.
- Algorithms explicitly named: Deutsch-Jozsa, Grover, Bernstein-Vazirani.
- Likely quantum task style: small circuits, measurement counts, noisy dominant states, basis selection, and simple oracle classification.
- Likely cybersecurity pairing: steganography, OSINT from public event terms, web/source inspection, crypto encodings, QR/images, archive/password clues.
- Likely clue words for passwords or keys: `QCSP`, `DurianPy`, `Davao`, `Ateneo`, `Finster`, `SpinQ`, `Gemini`, `GeminiMini`, `QuantumPH`, `June272026`, `06272026`.

## Fast quantum rules

- Deutsch-Jozsa: if all oracle outputs are the same, answer `constant`; if half are `0` and half are `1`, answer `balanced`.
- Bernstein-Vazirani: the dominant measured bitstring is usually the hidden string.
- Grover: the highest-count measured state is usually the marked item.
- BB84: keep only bit positions where Alice and Bob used the same basis.
- Noisy hardware: do not expect perfect counts; sort by probability and justify the dominant result.

## Tool usage

Browser-first workflow: open `warroom/index.html` in a browser, then paste each challenge into the dashboard's Live Challenge Solver. It runs local category routing, structured finding scoring, high-confidence decoders, quantum count interpretation, QASM pattern checks, Quirk URL parsing, wordlist hints, and flag-format checks without command-line usage.

The solver now prioritizes a top Recommended Lead, keeps evidence visible for strong candidates, and collapses low-confidence Caesar/ROT noise by default.

Terminal fallback:
```bash
python3 tools/qcsp.py solve 'paste challenge text, URLs, counts, or hints here'
python3 tools/qcsp.py file-triage challenge.png --out triage.md
python3 tools/qcsp.py crypto auto "UVNTUHt0ZXN0fQ=="
python3 tools/qcsp.py crypto hashes 5d41402abc4b2a76b9719d911017c592
python3 tools/qcsp.py web scan https://example.com/challenge --yes-in-scope --out web-scan.md
python3 tools/qcsp.py quantum counts '{"00": 12, "10": 381, "11": 9}' --mode bv
python3 tools/qcsp.py quantum counts '{"00": 4, "01": 8, "10": 122, "11": 7}' --mode grover
python3 tools/qcsp.py quantum dj 0011
python3 tools/qcsp.py quantum bb84 --alice-bases +x++x --bob-bases ++x+x --bob-bits 10110
```

Manual solver tests:
```bash
node --check warroom/app.js
node warroom/solver-tests.js
```

## Competition workflow

- Start with the browser Live Challenge Solver on every challenge statement.
- Start with `file-triage` on every provided file.
- If you see readable encoded text, use `crypto auto`.
- If the challenge provides measurement counts, use `quantum counts`.
- If an image is involved, inspect metadata, strings, trailing bytes, QR content, and embedded files.
- If a website is involved, use the dashboard's Scoped Web Recon only on challenge-provided URLs and inspect comments, linked scripts, headers, forms, and flag-like text.
- If browser CORS blocks direct recon, use `Copy CLI Fallback` or paste copied page source/JavaScript into `Analyze Pasted HTML/JS`.
- Track every candidate flag with source evidence so the team does not repeatedly try the same wrong answer.
