# Event-Day Operating Plan

## Roles
- Captain / Submitter: owns CTFd submissions, scoreboard checks, final calls, and tie-breaker mode.
- Prompt Vault / AI: clears Prompt Vault first, drafts category-specific prompts, and summarizes challenge text for solvers.
- OSINT: runs searches, validates sources, captures links and screenshots, and avoids unsupported guesses.
- DFIR: triages artifacts, PCAPs, logs, metadata, strings, timestamps, and hash evidence.
- Crypto / Quantum: handles encodings, ciphers, RSA checks, Quirk circuits, basis changes, and probability reasoning.

## First 15 Minutes
- Minute 0-2: log in, confirm team name, confirm flag format, open War Room and Quirk.
- Minute 2-5: captain scans all challenge titles, points, categories, and visible files.
- Minute 5-8: assign each easy/low-point challenge to one owner; Prompt Vault starts immediately.
- Minute 8-12: everyone solves one quick target; log every candidate flag before submitting.
- Minute 12-15: submit verified easy flags, then reassign blocked people to highest-value active leads.

## 3-Hour Rhythm
- Every 20 minutes: captain checks score, solved count, and team blockers.
- Every 40 minutes: drop cold leads unless they are near a flag or high value.
- Final 30 minutes: no deep rabbit holes; prioritize near-solved tasks and low-risk submissions.
- Final 10 minutes: only submit flags that pass format validation and have an evidence trail.

## Evidence Discipline
- Record challenge name, category, points, owner, commands, links, and why the final flag is trusted.
- Keep original artifacts unchanged; work in per-challenge scratch folders.
- Use AI for reasoning and summarization, but keep the final action inside the challenge scope.
