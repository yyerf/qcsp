#!/usr/bin/env python3
"""
QCSP / CTF jumpstart assistant.

Scope:
- Works on user-provided text, files, folders, or URLs.
- Automates common CTF triage and small quantum-computing challenge checks.
- Uses Python standard library only.

This is intended for authorized CTF/hackathon use. It does not brute-force
remote targets, exploit services, or bypass contest infrastructure.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import collections
import hashlib
import html
import json
import math
import os
import pathlib
import re
import shlex
import string
import subprocess
import sys
import textwrap
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Iterable


FLAG_PATTERNS = [
    re.compile(rb"(?:QCSP|QCS|DURIANPY|PYTHONPH|QUANTUMPH|CTF|FLAG)\{[^{}\r\n]{1,120}\}", re.I),
    re.compile(rb"flag\s*[:=]\s*['\"]?([A-Za-z0-9_\-{}@!#$%^&*+=:;,.?/]{4,160})", re.I),
]

PRINTABLE = set(bytes(string.printable, "ascii"))
COMMON_MAGIC = {
    b"\x89PNG\r\n\x1a\n": "PNG image",
    b"\xff\xd8\xff": "JPEG image",
    b"GIF87a": "GIF image",
    b"GIF89a": "GIF image",
    b"%PDF": "PDF document",
    b"PK\x03\x04": "ZIP / Office / JAR archive",
    b"7z\xbc\xaf\x27\x1c": "7z archive",
    b"\x1f\x8b\x08": "gzip archive",
    b"BZh": "bzip2 archive",
    b"Rar!\x1a\x07": "RAR archive",
    b"\x7fELF": "ELF binary",
    b"MZ": "Windows PE executable",
    b"ID3": "MP3 audio",
    b"OggS": "Ogg media",
}


def print_section(title: str) -> None:
    print(f"\n== {title} ==")


def safe_decode(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


def read_target(target: str, max_bytes: int = 4_000_000) -> bytes:
    if target == "-":
        return sys.stdin.buffer.read(max_bytes)
    if looks_like_url(target):
        return fetch_url(target, max_bytes=max_bytes).body
    return pathlib.Path(target).read_bytes()[:max_bytes]


def looks_like_url(value: str) -> bool:
    parsed = urllib.parse.urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


@dataclass
class FetchResult:
    url: str
    status: int
    headers: dict[str, str]
    body: bytes


def fetch_url(url: str, max_bytes: int = 1_000_000, timeout: int = 12) -> FetchResult:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "qcsp-jumpstart/1.0 authorized-ctf-helper",
            "Accept": "text/html,application/json,text/plain,*/*",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read(max_bytes)
        return FetchResult(
            url=resp.geturl(),
            status=getattr(resp, "status", 0),
            headers=dict(resp.headers.items()),
            body=body,
        )


def extract_flags(data: bytes) -> list[str]:
    hits: list[str] = []
    for pattern in FLAG_PATTERNS:
        for match in pattern.finditer(data):
            value = match.group(1) if match.lastindex else match.group(0)
            decoded = safe_decode(value).strip("'\" ")
            if decoded not in hits:
                hits.append(decoded)
    return hits


def extract_strings(data: bytes, min_len: int = 5) -> list[str]:
    out: list[str] = []
    cur = bytearray()
    for byte in data:
        if byte in PRINTABLE and byte not in b"\r\n\t\x0b\x0c":
            cur.append(byte)
        else:
            if len(cur) >= min_len:
                out.append(safe_decode(bytes(cur)))
            cur.clear()
    if len(cur) >= min_len:
        out.append(safe_decode(bytes(cur)))
    return out


def file_magic(data: bytes) -> list[str]:
    hits = []
    for magic, label in COMMON_MAGIC.items():
        if data.startswith(magic):
            hits.append(label)
    if not hits:
        hits.append("unknown / raw data")
    return hits


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = collections.Counter(data)
    total = len(data)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def find_embedded_magic(data: bytes) -> list[tuple[int, str]]:
    hits: list[tuple[int, str]] = []
    for magic, label in COMMON_MAGIC.items():
        start = 1
        while True:
            idx = data.find(magic, start)
            if idx == -1:
                break
            hits.append((idx, label))
            start = idx + 1
    return sorted(set(hits))


def decode_candidates(text: str) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    cleaned = text.strip()
    compact = re.sub(r"\s+", "", cleaned)

    def add(label: str, value: bytes | str) -> None:
        if isinstance(value, bytes):
            value = safe_decode(value)
        value = value.strip()
        if value and is_interesting(value):
            pair = (label, value)
            if pair not in candidates:
                candidates.append(pair)

    if "%" in cleaned:
        add("url-decode", urllib.parse.unquote(cleaned))
    if "&" in cleaned or "&amp;" in cleaned:
        add("html-unescape", html.unescape(cleaned))

    for label, decoder in [
        ("base64", lambda s: base64.b64decode(pad_base(s), validate=False)),
        ("base32", lambda s: base64.b32decode(pad_base(s).upper(), casefold=True)),
        ("base16/hex", lambda s: bytes.fromhex(s)),
    ]:
        if possible_encoded(compact, label):
            try:
                add(label, decoder(compact))
            except Exception:
                pass

    if re.fullmatch(r"[01]{8,}", compact) and len(compact) % 8 == 0:
        try:
            add("binary-ascii", bytes(int(compact[i : i + 8], 2) for i in range(0, len(compact), 8)))
        except Exception:
            pass

    morse = try_morse(cleaned)
    if morse:
        add("morse", morse)

    for shift in range(1, 26):
        decoded = caesar(cleaned, shift)
        if score_text(decoded) >= 8:
            add(f"caesar-{shift}", decoded)

    rot47 = "".join(chr(33 + ((ord(ch) + 14) % 94)) if 33 <= ord(ch) <= 126 else ch for ch in cleaned)
    if score_text(rot47) >= 8:
        add("rot47", rot47)

    jwt = decode_jwt(cleaned)
    if jwt:
        add("jwt-header.payload", jwt)

    return candidates


def pad_base(value: str) -> str:
    return value + ("=" * ((4 - len(value) % 4) % 4))


def possible_encoded(value: str, label: str) -> bool:
    if label == "base64":
        return len(value) >= 8 and re.fullmatch(r"[A-Za-z0-9+/=_-]+", value) is not None
    if label == "base32":
        return len(value) >= 8 and re.fullmatch(r"[A-Z2-7=]+", value.upper()) is not None
    if label == "base16/hex":
        return len(value) >= 4 and len(value) % 2 == 0 and re.fullmatch(r"[0-9a-fA-F]+", value) is not None
    return False


def is_interesting(value: str) -> bool:
    if any(pattern.search(value.encode(errors="ignore")) for pattern in FLAG_PATTERNS):
        return True
    printable_ratio = sum(ch in string.printable for ch in value) / max(len(value), 1)
    if printable_ratio < 0.9:
        return False
    lowered = value.lower()
    words = ["flag", "qcsp", "quantum", "secret", "key", "password", "ctf", "gemini", "spinq"]
    return any(word in lowered for word in words) or score_text(value) >= 9


def score_text(value: str) -> int:
    lowered = value.lower()
    score = 0
    for word in ["the", "and", "flag", "key", "secret", "quantum", "spinq", "gemini", "qcsp", "ctf"]:
        if word in lowered:
            score += 3
    score += sum(ch == " " for ch in value[:120])
    score += sum(ch in "{}_-" for ch in value[:120])
    return score


MORSE = {
    ".-": "A",
    "-...": "B",
    "-.-.": "C",
    "-..": "D",
    ".": "E",
    "..-.": "F",
    "--.": "G",
    "....": "H",
    "..": "I",
    ".---": "J",
    "-.-": "K",
    ".-..": "L",
    "--": "M",
    "-.": "N",
    "---": "O",
    ".--.": "P",
    "--.-": "Q",
    ".-.": "R",
    "...": "S",
    "-": "T",
    "..-": "U",
    "...-": "V",
    ".--": "W",
    "-..-": "X",
    "-.--": "Y",
    "--..": "Z",
    "-----": "0",
    ".----": "1",
    "..---": "2",
    "...--": "3",
    "....-": "4",
    ".....": "5",
    "-....": "6",
    "--...": "7",
    "---..": "8",
    "----.": "9",
}


def try_morse(value: str) -> str | None:
    if not re.fullmatch(r"[.\-/\s]+", value.strip()):
        return None
    words = []
    for word in re.split(r"\s*/\s*|\s{3,}", value.strip()):
        letters = []
        for token in word.split():
            if token not in MORSE:
                return None
            letters.append(MORSE[token])
        words.append("".join(letters))
    return " ".join(words)


def caesar(value: str, shift: int) -> str:
    out = []
    for ch in value:
        if "a" <= ch <= "z":
            out.append(chr((ord(ch) - 97 + shift) % 26 + 97))
        elif "A" <= ch <= "Z":
            out.append(chr((ord(ch) - 65 + shift) % 26 + 65))
        else:
            out.append(ch)
    return "".join(out)


def decode_jwt(value: str) -> str | None:
    parts = value.split(".")
    if len(parts) < 2:
        return None
    decoded = []
    for part in parts[:2]:
        try:
            decoded.append(json.dumps(json.loads(base64.urlsafe_b64decode(pad_base(part))), indent=2))
        except Exception:
            return None
    return "\n".join(decoded)


def cmd_analyze(args: argparse.Namespace) -> int:
    data = read_target(args.target, max_bytes=args.max_bytes)
    print_section("basic")
    print(f"bytes: {len(data)}")
    print(f"magic: {', '.join(file_magic(data))}")
    print(f"sha256: {hashlib.sha256(data).hexdigest()}")
    print(f"entropy: {entropy(data):.3f} bits/byte")

    flags = extract_flags(data)
    print_section("flag-like hits")
    if flags:
        for hit in flags:
            print(hit)
    else:
        print("none found")

    embedded = find_embedded_magic(data)
    print_section("embedded file signatures")
    if embedded:
        for offset, label in embedded[:30]:
            print(f"offset {offset}: {label}")
    else:
        print("none found")

    strings = extract_strings(data, min_len=args.min_string)
    interesting = [s for s in strings if is_interesting(s)]
    print_section("interesting strings")
    if interesting:
        for item in interesting[:60]:
            print(item[:240])
    else:
        print("none found")

    text = safe_decode(data)
    candidates = decode_candidates(text)
    print_section("decode candidates")
    if candidates:
        for label, value in candidates[:40]:
            print(f"[{label}] {value[:500]}")
    else:
        print("none found")

    print_section("next moves")
    for hint in triage_hints(data, strings):
        print(f"- {hint}")
    return 0


def triage_hints(data: bytes, strings: list[str]) -> list[str]:
    hints = []
    ent = entropy(data)
    lower_strings = "\n".join(strings[:500]).lower()

    if ent > 7.4:
        hints.append("High entropy: likely compressed/encrypted/random. Try archive tools, known passwords, or challenge text as key material.")
    if any(label for _, label in find_embedded_magic(data)):
        hints.append("Embedded file signature found. Carve from the offset with dd or inspect with binwalk if available.")
    if b"PK\x03\x04" in data:
        hints.append("ZIP-like content. Check for Office metadata, hidden files, comments, or password protection.")
    if "exif" in lower_strings or data.startswith((b"\xff\xd8\xff", b"\x89PNG")):
        hints.append("Image file. Inspect metadata, trailing bytes, least significant bits, and possible QR content.")
    if "spinq" in lower_strings or "gemini" in lower_strings:
        hints.append("SpinQ/Gemini clue. Expect 2-qubit tasks, measurement counts, or named algorithms from the pubmat.")
    if "deutsch" in lower_strings or "jozsa" in lower_strings:
        hints.append("Deutsch-Jozsa clue. Classify oracle output as constant or balanced.")
    if "bernstein" in lower_strings or "vazirani" in lower_strings:
        hints.append("Bernstein-Vazirani clue. The dominant measured bitstring is usually the hidden string.")
    if "grover" in lower_strings:
        hints.append("Grover clue. Sort measurement counts; the dominant state is usually the marked item.")
    if "bb84" in lower_strings or "basis" in lower_strings:
        hints.append("Quantum key distribution clue. Keep only positions where Alice and Bob bases match.")
    if not hints:
        hints.append("Try decode mode on suspicious strings, then inspect file metadata or challenge-specific text.")
    return hints


def cmd_decode(args: argparse.Namespace) -> int:
    text = args.text if args.text is not None else safe_decode(read_target(args.target, max_bytes=args.max_bytes))
    print_section("direct flag-like hits")
    for hit in extract_flags(text.encode()):
        print(hit)
    print_section("decode candidates")
    candidates = decode_candidates(text)
    if not candidates:
        print("none found")
    for label, value in candidates:
        print(f"[{label}]\n{value}\n")
    return 0


def cmd_url(args: argparse.Namespace) -> int:
    result = fetch_url(args.url, max_bytes=args.max_bytes)
    print_section("response")
    print(f"url: {result.url}")
    print(f"status: {result.status}")
    for key in ["server", "content-type", "x-powered-by", "location", "set-cookie"]:
        for header, value in result.headers.items():
            if header.lower() == key:
                print(f"{header}: {value}")

    text = safe_decode(result.body)
    print_section("comments")
    comments = re.findall(r"<!--(.*?)-->", text, flags=re.S)
    if comments:
        for comment in comments[:25]:
            print(comment.strip()[:500])
    else:
        print("none found")

    print_section("links and script sources")
    links = sorted(set(re.findall(r"""(?:href|src)=["']([^"']+)["']""", text, flags=re.I)))
    if links:
        for link in links[:80]:
            print(urllib.parse.urljoin(result.url, link))
    else:
        print("none found")

    print_section("flag-like hits")
    flags = extract_flags(result.body)
    if flags:
        for hit in flags:
            print(hit)
    else:
        print("none found")
    return 0


def cmd_quantum(args: argparse.Namespace) -> int:
    if args.quantum_cmd == "counts":
        counts = parse_counts(args.counts)
        print_section("measurement counts")
        total = sum(counts.values())
        for state, count in sorted(counts.items(), key=lambda item: item[1], reverse=True):
            prob = count / total if total else 0
            print(f"{state}: {count} ({prob:.2%})")
        if counts:
            state, count = max(counts.items(), key=lambda item: item[1])
            print_section("likely answer")
            print(f"dominant state: {state}")
            print(f"as binary: {state.replace('|', '').replace('>', '')}")
            try:
                print(f"as integer: {int(state.replace('|', '').replace('>', ''), 2)}")
            except ValueError:
                pass
        return 0

    if args.quantum_cmd == "bv":
        counts = parse_counts(args.counts)
        state = majority_state(counts)
        print_section("Bernstein-Vazirani")
        print(f"likely hidden string: {state}")
        print("reason: BV returns the hidden bitstring as the dominant measurement result.")
        return 0

    if args.quantum_cmd == "grover":
        counts = parse_counts(args.counts)
        print_section("Grover")
        if not counts:
            print("no counts parsed")
            return 1
        total = sum(counts.values())
        for state, count in sorted(counts.items(), key=lambda item: item[1], reverse=True):
            print(f"{state}: {count} ({count / total:.2%})")
        print(f"likely marked item: {majority_state(counts)}")
        return 0

    if args.quantum_cmd == "dj":
        bits = re.sub(r"[^01]", "", args.outputs)
        print_section("Deutsch-Jozsa")
        if not bits:
            print("no 0/1 outputs parsed")
            return 1
        unique = set(bits)
        if len(unique) == 1:
            print("constant")
        elif bits.count("0") == bits.count("1"):
            print("balanced")
        else:
            print("neither exactly constant nor balanced; re-check oracle table or noise.")
        print(f"outputs: {bits}")
        return 0

    if args.quantum_cmd == "bb84":
        key_bits, kept = bb84_key(args.alice_bases, args.bob_bases, args.bob_bits)
        print_section("BB84 sifted key")
        print(f"matching positions: {','.join(map(str, kept)) if kept else 'none'}")
        print(f"key bits: {key_bits}")
        if key_bits and len(key_bits) % 8 == 0:
            try:
                msg = bytes(int(key_bits[i : i + 8], 2) for i in range(0, len(key_bits), 8))
                print(f"ascii: {safe_decode(msg)}")
            except Exception:
                pass
        return 0

    return 1


def parse_counts(value: str) -> dict[str, int]:
    value = value.strip()
    if not value:
        return {}
    try:
        raw = json.loads(value)
        return {normalize_state(str(k)): int(v) for k, v in raw.items()}
    except Exception:
        pass

    counts: dict[str, int] = {}
    for state, count in re.findall(r"([|]?[01]{1,16}>?)\s*[:=]\s*(\d+)", value):
        counts[normalize_state(state)] = int(count)
    if counts:
        return counts

    for state in re.findall(r"[01]{1,16}", value):
        counts[normalize_state(state)] = counts.get(normalize_state(state), 0) + 1
    return counts


def normalize_state(state: str) -> str:
    return state.replace("|", "").replace(">", "").strip()


def majority_state(counts: dict[str, int]) -> str:
    if not counts:
        return ""
    return max(counts.items(), key=lambda item: item[1])[0]


def bb84_key(alice_bases: str, bob_bases: str, bob_bits: str) -> tuple[str, list[int]]:
    ab = normalize_bases(alice_bases)
    bb = normalize_bases(bob_bases)
    bits = re.sub(r"[^01]", "", bob_bits)
    n = min(len(ab), len(bb), len(bits))
    key = []
    kept = []
    for idx in range(n):
        if ab[idx] == bb[idx]:
            key.append(bits[idx])
            kept.append(idx)
    return "".join(key), kept


def normalize_bases(value: str) -> str:
    out = []
    for ch in value:
        if ch in "+Zz0":
            out.append("Z")
        elif ch in "xX*1":
            out.append("X")
    return "".join(out)


def cmd_hashid(args: argparse.Namespace) -> int:
    value = args.value.strip()
    length = len(value)
    hex_only = re.fullmatch(r"[0-9a-fA-F]+", value) is not None
    print_section("hash guess")
    guesses = []
    if hex_only:
        guesses.extend(
            {
                32: ["MD5", "NTLM"],
                40: ["SHA1", "RIPEMD160"],
                56: ["SHA224"],
                64: ["SHA256", "SHA3-256", "BLAKE2s"],
                96: ["SHA384"],
                128: ["SHA512", "SHA3-512", "BLAKE2b"],
            }.get(length, [])
        )
    if re.fullmatch(r"\$2[aby]\$\d{2}\$.{53}", value):
        guesses.append("bcrypt")
    if re.fullmatch(r"\$argon2(?:id|i|d)\$.+", value):
        guesses.append("argon2")
    if value.startswith("$6$"):
        guesses.append("sha512crypt")
    if value.startswith("$5$"):
        guesses.append("sha256crypt")
    if not guesses:
        guesses.append("unknown")
    print(f"length: {length}")
    print(f"hex-only: {hex_only}")
    print("possible: " + ", ".join(guesses))
    return 0


def cmd_toolcheck(args: argparse.Namespace) -> int:
    tools = ["file", "strings", "exiftool", "binwalk", "zbarimg", "steghide", "foremost", "tshark", "john", "hashcat", "qiskit"]
    print_section("local helper availability")
    for tool in tools:
        found = shutil_which(tool)
        print(f"{tool}: {found or 'not found'}")
    return 0


def shutil_which(cmd: str) -> str | None:
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        path = os.path.join(directory, cmd)
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return None


def cmd_pubmat(args: argparse.Namespace) -> int:
    text = args.text
    print_section("pubmat-derived likely challenge map")
    print("strong signals:")
    print("- 2-qubit real hardware: expect small state-space tasks, noisy counts, and basis/measurement questions.")
    print("- Named algorithms: Deutsch-Jozsa, Grover, and Bernstein-Vazirani are explicitly advertised.")
    print("- Desktop/room-temperature wording: possible hardware-identification or physics trivia flags.")
    print("- Cybersecurity hackathon pairing: likely hybrid crypto, stego, web, OSINT, and quantum-themed crypto puzzles.")
    print("- Venue/date/sponsor terms: possible password/key material includes Ateneo, Davao, DurianPy, QCSP, SpinQ, GeminiMini, June272026.")
    if text:
        flags = extract_flags(text.encode())
        print_section("direct flag-like hits")
        print("\n".join(flags) if flags else "none found")
        print_section("decode candidates from supplied text")
        candidates = decode_candidates(text)
        print("\n".join(f"[{label}] {value}" for label, value in candidates) if candidates else "none found")
    print_section("priority prep")
    print("- Practice converting measurement counts into the most likely bitstring.")
    print("- Memorize BB84 sifting: keep only positions where bases match.")
    print("- For Deutsch-Jozsa, all outputs equal means constant; equal zero/one split means balanced.")
    print("- For Bernstein-Vazirani, the measured string reveals the hidden string.")
    print("- For Grover, the highest-count result is the marked item, with noise tolerated.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="QCSP/CTF jumpstart assistant for authorized challenge triage.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            examples:
              python3 qcsp_jumpstart.py pubmat
              python3 qcsp_jumpstart.py analyze challenge.png
              python3 qcsp_jumpstart.py decode --text "UVNTUHt0ZXN0fQ=="
              python3 qcsp_jumpstart.py quantum bv --counts '{"00": 12, "10": 381, "11": 9}'
              python3 qcsp_jumpstart.py quantum dj --outputs 0011
              python3 qcsp_jumpstart.py quantum bb84 --alice-bases +x++x --bob-bases ++x+x --bob-bits 10110
            """
        ),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    analyze = sub.add_parser("analyze", help="triage a file, URL, or stdin")
    analyze.add_argument("target", help="path, URL, or - for stdin")
    analyze.add_argument("--max-bytes", type=int, default=4_000_000)
    analyze.add_argument("--min-string", type=int, default=5)
    analyze.set_defaults(func=cmd_analyze)

    decode = sub.add_parser("decode", help="try common CTF decoders")
    decode.add_argument("target", nargs="?", default="-", help="path, URL, or - for stdin")
    decode.add_argument("--text", help="literal text to decode")
    decode.add_argument("--max-bytes", type=int, default=1_000_000)
    decode.set_defaults(func=cmd_decode)

    url = sub.add_parser("url", help="passively inspect one authorized URL")
    url.add_argument("url")
    url.add_argument("--max-bytes", type=int, default=1_000_000)
    url.set_defaults(func=cmd_url)

    hashid = sub.add_parser("hashid", help="guess hash type from format")
    hashid.add_argument("value")
    hashid.set_defaults(func=cmd_hashid)

    pubmat = sub.add_parser("pubmat", help="print likely challenge map from the supplied event pubmats")
    pubmat.add_argument("--text", default="")
    pubmat.set_defaults(func=cmd_pubmat)

    toolcheck = sub.add_parser("toolcheck", help="show optional local CTF tool availability")
    toolcheck.set_defaults(func=cmd_toolcheck)

    quantum = sub.add_parser("quantum", help="small quantum challenge helpers")
    qsub = quantum.add_subparsers(dest="quantum_cmd", required=True)

    counts = qsub.add_parser("counts", help="summarize measurement counts")
    counts.add_argument("--counts", required=True, help='JSON dict or text like "00:10 11:50"')
    counts.set_defaults(func=cmd_quantum)

    bv = qsub.add_parser("bv", help="solve Bernstein-Vazirani result from counts")
    bv.add_argument("--counts", required=True)
    bv.set_defaults(func=cmd_quantum)

    grover = qsub.add_parser("grover", help="infer Grover marked state from counts")
    grover.add_argument("--counts", required=True)
    grover.set_defaults(func=cmd_quantum)

    dj = qsub.add_parser("dj", help="classify Deutsch-Jozsa oracle outputs")
    dj.add_argument("--outputs", required=True, help="oracle outputs such as 0000 or 0011")
    dj.set_defaults(func=cmd_quantum)

    bb84 = qsub.add_parser("bb84", help="sift BB84 key bits")
    bb84.add_argument("--alice-bases", required=True, help="bases using +/x or Z/X")
    bb84.add_argument("--bob-bases", required=True, help="bases using +/x or Z/X")
    bb84.add_argument("--bob-bits", required=True, help="Bob measured bits")
    bb84.set_defaults(func=cmd_quantum)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
