# QCSP CTF War Room Toolkit

Offline-first toolkit for the QCSP/ISC2 Quantum + Cybersecurity Hackathon 2026.

## Fast Start
- Dashboard: open `warroom/index.html` in a browser and paste challenges into the Live Challenge Solver.
- CLI selftest: `python3 tools/qcsp.py selftest`
- Smart solve router: `python3 tools/qcsp.py solve 'paste challenge text here'`
- New notes folder: `python3 tools/qcsp.py challenge-new crypto warmup-rsa --points 100 --owner you`
- Artifact triage: `python3 tools/qcsp.py file-triage ./artifact.bin --out triage.md`
- Flag check: `python3 tools/qcsp.py flag-check 'isc2_qcsp{test}'`
- Safe web scan: `python3 tools/qcsp.py web scan 'https://challenge-url/' --yes-in-scope --out web-scan.md`

## Vercel Deployment
This repository is ready to deploy as a static Vercel project.

Recommended Vercel settings:
- Framework Preset: `Other`
- Root Directory: repository root
- Build Command: leave empty
- Output Directory: leave empty
- Install Command: leave empty

The root URL redirects to `/warroom/`. The browser dashboard remains client-side only: tracker state, timer state, CTFd URL, and notes entered in the UI are stored in each teammate's browser `localStorage`, not in a shared database. The Python CLI tools still run locally from the cloned repo.

The deployment intentionally excludes local scratch files, generated Python caches, and the local `Quirk/` source checkout. The dashboard links to the public Quirk simulator instead.

## Where To Run Commands
From the project root:
```bash
cd /home/yyerf/h4x/qcsp
python3 tools/qcsp.py selftest
```

From inside the tools folder:
```bash
cd /home/yyerf/h4x/qcsp/tools
python3 qcsp.py selftest
```

Do not combine top-level commands like `python3 qcsp.py links selftest`. Use separate commands, or shell-chain them:
```bash
python3 qcsp.py links && python3 qcsp.py selftest && python3 qcsp.py promptvault
```

## Event Defaults
- CTF format: Jeopardy-style CTF on CTFd.
- Duration: 3 hours.
- Start: June 27, 2026, 1:30 PM Asia/Manila.
- Flag format: `isc2_qcsp{<flag>}`.
- Categories: OSINT, DFIR, Cryptography, Classical-Quantum, Prompt Vault.
- AI: allowed for challenge solving, not for attacking infrastructure or automated abuse.

## Useful Commands
```bash
python3 tools/qcsp.py links
python3 tools/qcsp.py solve 'paste full challenge text, URLs, counts, or hints here'
python3 tools/qcsp.py wordlist 'paste challenge text here' --format-flags
python3 tools/qcsp.py promptvault
python3 tools/qcsp.py crypto auto 'UVNTUHt0ZXN0fQ=='
python3 tools/qcsp.py crypto rot 'uryyb'
python3 tools/qcsp.py crypto xor --hex 2b2e2e --key key
python3 tools/qcsp.py quantum quirk bell --open
python3 tools/qcsp.py quantum counts '{"00": 12, "10": 381, "11": 9}' --mode bv
python3 tools/qcsp.py quantum dj 0011
python3 tools/qcsp.py quantum bb84 --alice-bases +x++x --bob-bases ++x+x --bob-bits 10110
python3 tools/qcsp.py quantum prob --amps '1/sqrt(2),0,0,1/sqrt(2)'
python3 tools/qcsp.py quantum quirk-patterns
python3 tools/qcsp.py quantum quirk-solve 'paste the full Quirk challenge text or URL here'
python3 tools/qcsp.py quantum quirk-analyze 'https://algassert.com/quirk#circuit=...'
python3 tools/qcsp.py quantum quirk-sim '{"cols":[["H",1],["•","X"]]}'
python3 tools/qcsp.py quantum qasm-solve 'c[0] xor c[1] == c[2] <=7 lines OpenQASM'
python3 tools/qcsp.py quantum person-lookup kitaev
python3 tools/qcsp.py web crawl 'https://challenge-url/' --yes-in-scope --max-pages 30 --depth 2 --delay 0.5 --well-known --out crawl.md
python3 tools/qcsp.py web endpoints './app.js' --file --base-url 'https://challenge-url/'
```

## Event-Day Guide
1. Open `warroom/index.html`.
2. Click `Start Now` when the CTF begins, or use `Event Time` if the schedule is exact.
3. Put the official CTFd URL into the dashboard after the briefing.
4. Assign roles quickly: one submitter, one Prompt Vault/AI person, one web/OSINT person, one DFIR person, one crypto/quantum person.
5. Paste every new challenge statement into the Live Challenge Solver before assigning deep work.
6. Solve Prompt Vault first if it appears easy, because the handbook hints it may be one-shotted by AI.
7. For every challenge, create notes:
```bash
python3 tools/qcsp.py challenge-new "Web Recon" "challenge-name" --points 100 --owner yourname
```
8. Before submitting, validate the flag in the dashboard or CLI:
```bash
python3 tools/qcsp.py flag-check 'isc2_qcsp{candidate}'
```

The toolkit does not submit flags. Submit manually in CTFd.

## Smart Solve Router
Use this first when a challenge opens and you have text, a Quirk URL, measurement counts, encoded strings, or mixed hints:
```bash
python3 tools/qcsp.py solve 'paste the full challenge text here'
python3 tools/qcsp.py solve challenge.txt --file
```

The report gives:
- Direct `isc2_qcsp{...}` candidates.
- Category signals for Prompt Vault, OSINT, Web, DFIR, Crypto, and Classical-Quantum.
- A top Recommended Lead with a short evidence trail.
- Structured findings with score, confidence, source, and display priority.
- Ranked high-confidence decode attempts for Base64/Base32/hex/binary/URL/HTML/Morse/JWT/ROT13/Caesar/ROT47.
- Low-confidence Caesar/ROT noise collapsed by default.
- Quantum quick reads for BV, Deutsch-Jozsa, Grover, BB84, Simon/generic counts.
- QASM/circuit pattern analysis for Bell state, X gate, H superposition, and measurement-only circuits.
- Event-derived wordlist seeds from QCSP, DurianPy, SpinQ Gemini Mini, Ateneo, Davao, and date clues.
- Exact next commands to run.

For suspicious encoded strings only:
```bash
python3 tools/qcsp.py crypto auto 'paste suspicious string here'
```

For password/key guesses or flag-shaped candidates:
```bash
python3 tools/qcsp.py wordlist 'paste challenge text here'
python3 tools/qcsp.py wordlist 'paste challenge text here' --format-flags
```

Browser solver acceptance tests:
```bash
node --check warroom/app.js
node warroom/solver-tests.js
```

## Web Recon
The `web` commands are read-only helpers for authorized challenge URLs:
- `web scan` fetches the target page plus harmless well-known files like `robots.txt`, `sitemap.xml`, and `security.txt`.
- `web crawl` follows same-origin links at a low rate and extracts forms, scripts, comments, possible flags, endpoints, and suspicious strings.
- `web endpoints` extracts URLs, routes, flags, and token-looking strings from copied HTML/JS/text without making network requests.

The crawler does not submit forms, fuzz parameters, brute-force directories, run exploits, or attack CTFd infrastructure.

### Web Recon Workflow
Use this only on challenge URLs that are explicitly in scope.

Browser-first:
- Paste the challenge URL into `Scoped Web Recon` in `warroom/index.html`.
- Check the in-scope confirmation box.
- Keep defaults conservative: max 12 pages, depth 1, 750 ms delay.
- If browser CORS blocks the fetch, click `Copy CLI Fallback` or paste copied HTML/JS into `Analyze Pasted HTML/JS`.

Start with a passive scan:
```bash
python3 tools/qcsp.py web scan 'https://challenge-url/' --yes-in-scope --out web-scan.md
```

If the site has multiple pages, run a low-rate crawl:
```bash
python3 tools/qcsp.py web crawl 'https://challenge-url/' \
  --yes-in-scope \
  --max-pages 30 \
  --depth 2 \
  --delay 0.5 \
  --well-known \
  --out crawl.md
```

If you download or copy JavaScript, extract endpoints without making requests:
```bash
python3 tools/qcsp.py web endpoints './app.js' --file --base-url 'https://challenge-url/'
```

Read the report in this order:
- `Flags`: try these only if the evidence makes sense.
- `Interesting strings`: tokens, debug values, secrets, or flag-like values.
- `Forms`: useful login/search/upload actions to inspect manually in the browser.
- `Pages`: status codes, titles, errors, comments, and discovered routes.
- `JavaScript endpoints`: hidden API paths and client-side routes.
- `External links`: only follow if the challenge clearly scopes them.

Good web challenge checklist:
```bash
python3 tools/qcsp.py web scan 'https://challenge-url/' --yes-in-scope --out web-scan.md
rg -n "flag|isc2_qcsp|admin|debug|token|secret|password|todo|hint" web-scan.md
python3 tools/qcsp.py web crawl 'https://challenge-url/' --yes-in-scope --max-pages 30 --depth 2 --delay 0.5 --well-known --out crawl.md
rg -n "flag|isc2_qcsp|admin|debug|token|secret|password|todo|hint" crawl.md
```

Safety line: do not run broad scanners like `nmap`, `nikto`, `sqlmap`, high-rate fuzzers, or directory brute-forcers against CTFd or any target unless the challenge explicitly authorizes that exact activity.

## Category Guides
### Prompt Vault
```bash
python3 tools/qcsp.py promptvault
```
- Paste only the challenge text and relevant outputs into AI.
- Ask for hidden instructions, delimiter tricks, encoded strings, output-format traps, and exact candidate flags.
- Use `flag-check` before submitting.

### OSINT
- Search exact strings first.
- Preserve source URLs and screenshots.
- Use artifact triage for images or PDFs:
```bash
python3 tools/qcsp.py file-triage ./artifact.jpg --out image-triage.md
```

### DFIR
Start with safe local triage:
```bash
python3 tools/qcsp.py file-triage ./artifact.bin --out triage.md
```
Then inspect the report for file type, hashes, strings, first bytes, PDF text, PCAP metadata, or optional `exiftool`/`binwalk` output.

For PCAPs:
```bash
capinfos capture.pcapng
tcpdump -nn -r capture.pcapng -c 25
wireshark capture.pcapng
```

### Cryptography
Try encodings before deeper crypto:
```bash
python3 tools/qcsp.py crypto b64-decode '...'
python3 tools/qcsp.py crypto b32-decode '...'
python3 tools/qcsp.py crypto hex-decode '68656c6c6f'
python3 tools/qcsp.py crypto rot 'uryyb'
```

For XOR:
```bash
python3 tools/qcsp.py crypto xor --hex 2b2e2e --key key
python3 tools/qcsp.py crypto freq ciphertext.txt --file
```

For RSA checks:
```bash
python3 tools/qcsp.py crypto rsa-check --n 0x... --e 65537 --c 0x...
python3 tools/qcsp.py crypto rsa-check --p 0x... --q 0x... --e 65537 --c 0x...
```

### Classical-Quantum
Quantum Village/QOLOSSUS-style OpenQASM:
```bash
python3 tools/qcsp.py quantum qv-solve 'paste the challenge text here'
python3 tools/qcsp.py quantum qasm-solve 'c[0] xor c[1] == c[2] <=7 lines OpenQASM'
python3 tools/qcsp.py quantum qasm-check solution.qasm --file --predicate 'c[0] xor c[1] == c[2]'
python3 tools/qcsp.py quantum qasm-sim solution.qasm --file
```

Picture/person challenges:
```bash
python3 tools/qcsp.py quantum picture-helper ./person.png
python3 tools/qcsp.py quantum person-lookup kitaev
```

Open reference circuits in Quirk:
```bash
python3 tools/qcsp.py quantum quirk list
python3 tools/qcsp.py quantum quirk bell --open
python3 tools/qcsp.py quantum cheatsheet
```

Analyze Quirk challenge links or JSON:
```bash
python3 tools/qcsp.py quantum quirk-patterns
python3 tools/qcsp.py quantum quirk-solve 'paste the full challenge text, Quirk URL, or exported JSON here'
python3 tools/qcsp.py quantum quirk-analyze 'https://algassert.com/quirk#circuit=...'
python3 tools/qcsp.py quantum quirk-analyze circuit.json --file
python3 tools/qcsp.py quantum quirk-url circuit.json --file --open
```

Paste a full problem from stdin:
```bash
python3 tools/qcsp.py quantum quirk-solve
```
Then paste the problem text, press `Ctrl-D`, and read the solve report.

Save a problem to a file:
```bash
python3 tools/qcsp.py quantum quirk-solve problem.txt --file
```

Simulate small common-gate circuits:
```bash
python3 tools/qcsp.py quantum quirk-sim '{"cols":[["H",1],["•","X"]]}'
```

Interpret noisy measurement counts:
```bash
python3 tools/qcsp.py quantum counts '{"00": 12, "10": 381, "11": 9}' --mode bv
python3 tools/qcsp.py quantum counts '{"00": 4, "01": 8, "10": 122, "11": 7}' --mode grover
```

Fast textbook checks:
```bash
python3 tools/qcsp.py quantum dj 0011
python3 tools/qcsp.py quantum bb84 --alice-bases +x++x --bob-bases ++x+x --bob-bits 10110
```

Check amplitudes and probabilities:
```bash
python3 tools/qcsp.py quantum prob --amps '1/sqrt(2),0,0,1/sqrt(2)'
```

Remember: in Quirk arithmetic, the least-significant qubit is at the top.

Full Quirk guide: `playbooks/quirk-ctf.md`.
Quantum Village-style guide: `playbooks/quantum-village-ctf.md`.

## CTFd Read-Only Setup
After the briefing:
```bash
export QCSP_CTFD_URL='https://ctfd.example'
export QCSP_CTFD_TOKEN='optional-user-token'
python3 tools/qcsp.py ctfd challenges
python3 tools/qcsp.py ctfd scoreboard --count 20
```

The toolkit does not auto-submit flags.

## Emergency 10-Minute Mode
- One person reads the challenge out loud.
- One person solves.
- One person verifies the candidate flag and evidence.
- One person keeps Quirk/browser/AI/tools ready.
- Submit only evidence-backed flags.
