#!/usr/bin/env python3
"""Count the AI tells that are countable. Run before the tells pass.

Usage: python3 tells.py draft.md

Nothing here decides whether prose is good. It flags patterns worth a human
look, and gives the tells-pass agent a starting point instead of a blank
page. Thresholds are tuned against a 5,400-word reference article.
"""
import re
import sys
from collections import Counter
from statistics import mean, pstdev

VOCAB = """delve leverage leveraging robust seamless seamlessly landscape realm
underscore underscores testament crucial vital harness harnessing tapestry
myriad plethora elevate unlock empower empowering streamline foster pivotal
intricate nuanced comprehensive holistic cutting-edge game-changer paradigm
journey unpack pivotal""".split()

PHRASES = [
    "it is important to note", "it's important to note", "it is worth noting",
    "it's worth noting", "that said", "moreover", "furthermore", "ultimately",
    "in conclusion", "at its core", "in today's world", "dive into",
    "but here's the thing", "not only", "having established",
    "now that we", "with that in mind", "let's turn to", "let us turn to",
]


def strip(md):
    md = re.sub(r"<!--\s*tells:ignore\s*-->.*?<!--\s*/tells:ignore\s*-->",
                "", md, flags=re.S)
    md = re.sub(r"```.*?```", "", md, flags=re.S)
    md = re.sub(r"`[^`]*`", "", md)
    md = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", md)
    md = re.sub(r"\[\[(?:SRC|STUB):[^\]]*\]\]", "", md)
    md = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", md)
    return md


def main(path):
    raw = open(path, encoding="utf-8").read()
    body = strip(raw)
    prose = []
    for l in body.split("\n"):
        t = l.strip()
        if not t or t.startswith(("#", ">", "|", "---", "![")):
            continue
        t = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", t)   # drop list markers
        t = re.sub(r"^\*\*[^*]+\*\*\s*", "", t)       # drop bold lead-ins
        if t:
            prose.append(t)
    paras, buf = [], []
    for line in body.split("\n"):
        if line.strip():
            buf.append(line)
        elif buf:
            paras.append(" ".join(buf)); buf = []
    if buf:
        paras.append(" ".join(buf))
    paras = [p for p in paras
             if not p.lstrip().startswith(("#", "|", "---", "!["))]

    words = re.findall(r"[A-Za-z']+", body)
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", " ".join(prose))
                 if s.strip()]

    print(f"words {len(words)}   sentences {len(sentences)}   "
          f"paragraphs {len(paras)}\n")

    # hard failures
    ems = body.count("\u2014")
    print(f"[{'FAIL' if ems else 'ok  '}] em dashes: {ems}")

    stubs = len(re.findall(r"\[\[STUB:", raw))
    print(f"[{'FAIL' if stubs else 'ok  '}] unresolved stubs: {stubs}")

    # vocabulary
    low = body.lower()
    hits = Counter()
    for w in VOCAB:
        n = len(re.findall(rf"\b{re.escape(w)}\b", low))
        if n:
            hits[w] = n
    for p in PHRASES:
        n = low.count(p)
        if n:
            hits[p] = n
    flag = "FAIL" if hits else "ok  "
    print(f"[{flag}] vocabulary tells: {sum(hits.values())}"
          + (f"  {dict(hits.most_common(8))}" if hits else ""))

    # structural evenness
    plens = [len(re.findall(r"[A-Za-z']+", p)) for p in paras if p.strip()]
    if plens:
        cv = pstdev(plens) / mean(plens) if mean(plens) else 0
        print(f"[{'WARN' if cv < 0.45 else 'ok  '}] paragraph length "
              f"variation: cv={cv:.2f} (want >0.45), mean={mean(plens):.0f}w")

    secs = re.split(r"\n##+ ", raw)[1:]
    slens = [len(re.findall(r"[A-Za-z']+", strip(s))) for s in secs]
    if len(slens) > 2:
        ratio = max(slens) / max(min(slens), 1)
        print(f"[{'WARN' if ratio < 3 else 'ok  '}] section length spread: "
              f"{ratio:.1f}x (want >3x), {min(slens)}w to {max(slens)}w")

    # three-item lists
    runs, cur = [], 0
    for line in body.split("\n"):
        if re.match(r"^\s*([-*]|\d+\.)\s+\S", line):
            cur += 1
        elif cur:
            runs.append(cur); cur = 0
    if cur:
        runs.append(cur)
    threes = sum(1 for r in runs if r == 3)
    print(f"[{'WARN' if threes >= 3 else 'ok  '}] three-item lists: {threes} "
          f"of {len(runs)} lists")

    # sentence opening diversity
    openers = Counter(s.split()[0].lower() for s in sentences if s.split())
    if sentences:
        top, n = openers.most_common(1)[0]
        share = n / len(sentences)
        print(f"[{'WARN' if share > 0.10 else 'ok  '}] most common sentence "
              f"opener: '{top}' {n}x ({share:.0%}, want <10%)")

    # short-sentence instrument
    short = sum(1 for s in sentences
                if len(re.findall(r"[A-Za-z']+", s)) <= 6)
    if sentences:
        share = short / len(sentences)
        print(f"[{'WARN' if not 0.03 <= share <= 0.15 else 'ok  '}] short "
              f"sentences (<=6w): {short} ({share:.0%}, want 3-15%)")

    # reflective codas: paragraphs ending a section that generalise
    coda = re.compile(r"\b(that generalis|generalizes|the same move|"
                      r"the lesson|more broadly|beyond \w+, )", re.I)
    codas = len(coda.findall(body))
    print(f"[{'WARN' if codas > 2 else 'ok  '}] reflective codas: {codas} "
          f"(want <=2)")

    print("\nWARN is a prompt to look, not a defect. FAIL blocks publish.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "draft.md")
