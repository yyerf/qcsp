# Category Triage Checklist

## Prompt Vault
- Paste only the challenge text and relevant outputs into AI.
- Ask for direct solution reasoning, possible hidden instructions, encodings, and exact flag candidates.
- Try the simplest one-shot path first; do not spend the first 20 minutes polishing prompts.

## OSINT
- Identify exact entities, handles, domains, coordinates, timestamps, images, and quoted phrases.
- Search unique strings first, then reverse image or metadata if relevant.
- Save source URLs and note which detail supports the flag.

## Web Recon
- Use only on authorized challenge URLs, not the CTFd platform or third-party sites unless the challenge explicitly scopes them.
- Start with `python3 tools/qcsp.py web scan 'https://challenge-url/' --yes-in-scope --out web-scan.md`.
- For multi-page apps, run a low-rate crawl: `python3 tools/qcsp.py web crawl 'https://challenge-url/' --yes-in-scope --max-pages 30 --depth 2 --delay 0.5 --well-known --out crawl.md`.
- Review forms, comments, JavaScript endpoints, robots/sitemap hints, redirects, headers, candidate flags, and token-looking strings.
- Do not submit forms, brute-force directories, fuzz parameters, or scan infrastructure unless the challenge explicitly authorizes it.

## DFIR
- Start with `file`, hashes, strings, metadata, and timestamps.
- For PCAPs: run `capinfos`, protocol hierarchy in Wireshark, DNS/HTTP/TLS conversations, exported objects.
- For logs: sort by time, isolate rare events, correlate usernames/IPs/processes, then extract IOCs.
- For memory/disk images: preserve originals and work from copies or read-only paths.

## Cryptography
- Check encodings before ciphers: hex, Base64, Base32, URL, binary, Morse-like separators.
- Try ROT/Caesar, XOR single-byte/repeating-key, Vigenere hints, frequency, and crib dragging.
- For RSA: inspect `n`, `e`, `c`, repeated primes, tiny exponents, shared modulus, factorable `n`, and bad padding clues.

## Classical-Quantum
- Draw the circuit before calculating.
- Track basis changes: H swaps X/Z basis, S/T add phase, CNOT copies classical bits but entangles superpositions.
- Use Quirk for quick checks: Bell state, measurement probabilities, phase kickback, Grover diffusion, and QFT patterns.
- Remember Quirk orders arithmetic qubits least-significant at the top.
