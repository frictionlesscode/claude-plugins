#!/usr/bin/env python3
"""Grade a child's Chinese read-aloud recording against photos of the pages.

  readcheck.py prepare RUN AUDIO PAGE.jpg [PAGE.jpg ...]   setup if needed, OCR, transcribe
  readcheck.py grade RUN                                    score, mistakes, clips  (needs RUN/ref.json)
  readcheck.py build RUN SITE "Date label"                  review page             (reads RUN/gloss.json)

Models live in $READCHECK_MODELS (default ~/.cache/readcheck). All of them come from
sherpa-onnx GitHub releases, which this environment can reach (Hugging Face usually can't).
"""
import sys, os, json, subprocess, shutil, hashlib, wave, urllib.parse

MODELS = os.path.expanduser(os.environ.get("READCHECK_MODELS", "~/.cache/readcheck"))
HERE = os.path.dirname(os.path.abspath(__file__))
SR = 16000
REL = "https://github.com/k2-fsa/sherpa-onnx/releases/download"
DOWNLOADS = {  # path in MODELS -> archive or file URL
    "sherpa-onnx-paraformer-zh-2024-03-09": f"{REL}/asr-models/sherpa-onnx-paraformer-zh-2024-03-09.tar.bz2",
    "sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17": f"{REL}/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17.tar.bz2",
    "matcha-icefall-zh-baker": f"{REL}/tts-models/matcha-icefall-zh-baker.tar.bz2",
    "silero_vad.onnx": f"{REL}/asr-models/silero_vad.onnx",
    "vocos-22khz-univ.onnx": f"{REL}/vocoder-models/vocos-22khz-univ.onnx",
}
PARA = f"{MODELS}/sherpa-onnx-paraformer-zh-2024-03-09/"
SV = f"{MODELS}/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17/"
TTS = f"{MODELS}/matcha-icefall-zh-baker/"
END = set("。？！")


def is_cjk(c): return "一" <= c <= "鿿"
def jload(p): return json.load(open(p, encoding="utf-8"))
def jdump(o, p): json.dump(o, open(p, "w", encoding="utf-8"), ensure_ascii=False)
def ff(*args): subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def setup():
    try:
        import sherpa_onnx, rapidocr_onnxruntime, pypinyin, cv2, PIL  # noqa: F401
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "--break-system-packages", "-q", "sherpa-onnx",
                        "rapidocr_onnxruntime", "pypinyin", "opencv-python-headless", "pillow", "numpy"], check=True)
    os.makedirs(MODELS, exist_ok=True)
    for name, url in DOWNLOADS.items():
        dst = f"{MODELS}/{name}"
        if os.path.exists(dst): continue
        print("downloading", name, flush=True)
        if url.endswith(".tar.bz2"):
            subprocess.run(f'curl -sSL "{url}" | tar xj -C "{MODELS}"', shell=True, check=True)
        else:
            subprocess.run(["curl", "-sSL", "-o", dst, url], check=True)


# ---------------------------------------------------------------- prepare
def ocr(run, images):
    from rapidocr_onnxruntime import RapidOCR
    eng, pages = RapidOCR(), []
    for pi, f in enumerate(images):
        dst = f"{run}/page{pi+1}{os.path.splitext(f)[1].lower() or '.jpg'}"
        if os.path.abspath(f) != os.path.abspath(dst): shutil.copy(f, dst)
        res, _ = eng(dst)
        lines = sorted(({"text": t, "box": [[float(x), float(y)] for x, y in b]} for b, t, _ in res or []),
                       key=lambda l: (l["box"][0][1] + l["box"][3][1]) / 2)
        for i, l in enumerate(lines): l["id"] = f"p{pi+1}l{i+1}"
        pages.append({"image": dst, "lines": lines})
        print("==", dst); [print(l["id"], l["text"]) for l in lines]
    jdump({"pages": pages}, f"{run}/ocr.json")


def transcribe(run, audio):
    import numpy as np, sherpa_onnx as so
    wav = f"{run}/audio.wav"
    ff("-i", audio, "-ar", str(SR), "-ac", "1", wav)
    w = wave.open(wav)
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    para = so.OfflineRecognizer.from_paraformer(paraformer=PARA + "model.int8.onnx", tokens=PARA + "tokens.txt", num_threads=2)
    sv = so.OfflineRecognizer.from_sense_voice(model=SV + "model.int8.onnx", tokens=SV + "tokens.txt",
                                              language="zh", use_itn=False, num_threads=2)
    # Children read softly with long pauses: low VAD threshold, then split long regions at their quietest point.
    cfg = so.VadModelConfig(); v = cfg.silero_vad
    v.model, v.threshold, v.min_silence_duration, v.min_speech_duration, v.max_speech_duration = \
        f"{MODELS}/silero_vad.onnx", 0.15, 0.5, 0.1, 120
    cfg.sample_rate = SR
    vad = so.VoiceActivityDetector(cfg, buffer_size_in_seconds=len(a) // SR + 60)
    regions = []
    def drain():
        while not vad.empty():
            regions.append((vad.front.start, vad.front.start + len(vad.front.samples))); vad.pop()
    for i in range(0, len(a), 512): vad.accept_waveform(a[i:i + 512]); drain()
    vad.flush(); drain()
    FR = SR // 50
    def split(s, e):
        if e - s <= 18 * SR: return [(s, e)]
        n = (e - s) // FR
        rms = np.sqrt((a[s:s + n * FR].reshape(n, FR) ** 2).mean(1))
        sm = np.convolve(rms, np.ones(15) / 15, "same")
        cut = s + (n // 4 + int(np.argmin(sm[n // 4:3 * n // 4]))) * FR
        return split(s, cut) + split(cut, e)
    P, S, times = "", "", []
    for s, e in (seg for r in regions for seg in split(*r)):
        x = para.create_stream(); x.accept_waveform(SR, a[s:e]); para.decode_stream(x)
        P += "".join(c for c in x.result.text if is_cjk(c))
        y = sv.create_stream(); y.accept_waveform(SR, a[s:e]); sv.decode_stream(y)
        for tok, ts in zip(y.result.tokens, y.result.timestamps):
            for c in tok:
                if is_cjk(c): S += c; times.append(round(s / SR + ts, 2))
    jdump({"duration": round(len(a) / SR, 2), "para": P, "sv": S, "sv_times": times}, f"{run}/asr.json")
    print(f"transcribed {len(a)/SR:.0f}s: {len(P)} / {len(S)} chars")


# ---------------------------------------------------------------- grade
def char_cells(gray, quad, n):
    """Split an OCR line box into n character cells, snapping cuts to ink gaps so perspective drift doesn't accumulate."""
    import numpy as np, cv2
    q = np.array(quad, dtype=np.float32)
    H = 48; W = max(n * 8, int(np.linalg.norm(q[1] - q[0]) * H / max(np.linalg.norm(q[3] - q[0]), 1)))
    M = cv2.getPerspectiveTransform(q, np.array([[0, 0], [W, 0], [W, H], [0, H]], dtype=np.float32))
    _, bw = cv2.threshold(cv2.warpPerspective(gray, M, (W, H)), 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    ink = bw.sum(0).astype(float); ink = np.convolve(ink / (ink.max() or 1), np.ones(3) / 3, "same")
    p = W / n; win = int(0.45 * p); pen = lambda w: 0.6 * ((w - p) / p) ** 2
    cuts = [0]
    if n > 1:  # DP over cut positions: low ink at each cut, cell widths near the pitch
        cand = [range(max(1, int(k * p) - win), min(W - 1, int(k * p) + win) + 1) for k in range(1, n)]
        cost = [{x: ink[x] + pen(x) for x in cand[0]}]; back = [{}]
        for k in range(1, len(cand)):
            ck, bk = {}, {}
            for x in cand[k]:
                opts = [(c + pen(x - px), px) for px, c in cost[-1].items() if 0.55 * p <= x - px <= 1.45 * p]
                if opts: v, bk[x] = min(opts); ck[x] = v + ink[x]
            cost.append(ck); back.append(bk)
        last = {x: c + pen(W - x) for x, c in cost[-1].items()}
        if last:
            x = min(last, key=last.get); path = [x]
            for k in range(len(cand) - 1, 0, -1): x = back[k][x]; path.append(x)
            cuts += path[::-1]
        else:
            cuts += [int(k * p) for k in range(1, n)]
    cuts.append(W)
    Mi = np.linalg.inv(M)
    def pt(x, y): v = Mi @ [x, y, 1.0]; return [round(v[0] / v[2], 1), round(v[1] / v[2], 1)]
    return [[pt(cuts[i], 0), pt(cuts[i + 1], 0), pt(cuts[i + 1], H), pt(cuts[i], H)] for i in range(n)]


def align(ref, hyp):
    """Levenshtein over sets of toneless readings (so polyphones and 的/地/得 match).
    Extra speech costs less than a miss, so repeats and self-corrections aren't penalized.
    Returns per ref char: ("ok"|"sub", hyp index) or ("del", None)."""
    import numpy as np
    n, m = len(ref), len(hyp)
    D = np.zeros((n + 1, m + 1)); D[:, 0] = np.arange(n + 1); D[0, :] = np.arange(m + 1) * 0.7
    for i in range(1, n + 1):
        r, Di, Dp = ref[i - 1], D[i], D[i - 1]
        for j in range(1, m + 1):
            Di[j] = min(Dp[j - 1] + (0 if r & hyp[j - 1] else 1), Dp[j] + 1, Di[j - 1] + 0.7)
    i, j, ops = n, m, [None] * n
    while i > 0:
        if j > 0 and D[i, j] == D[i - 1, j - 1] + (0 if ref[i - 1] & hyp[j - 1] else 1):
            ops[i - 1] = ("ok" if ref[i - 1] & hyp[j - 1] else "sub", j - 1); i -= 1; j -= 1
        elif D[i, j] == D[i - 1, j] + 1: ops[i - 1] = ("del", None); i -= 1
        else: j -= 1
    return ops


def grade(run):
    import cv2
    from pypinyin import pinyin, lazy_pinyin, Style
    ocrd, ref, asr = jload(f"{run}/ocr.json"), jload(f"{run}/ref.json"), jload(f"{run}/asr.json")
    R, pages, sent_text, sent = [], [], {}, 0
    for pi, pg in enumerate(ref["pages"]):
        opg = ocrd["pages"][pi]; img = cv2.imread(opg["image"]); gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        boxes = {l["id"]: l["box"] for l in opg["lines"]}; start = len(R)
        for lid, text in pg["lines"]:
            for ch, poly in zip(text, char_cells(gray, boxes[lid], len(text))):
                sent_text[sent] = sent_text.get(sent, "") + ch
                if is_cjk(ch): R.append({"c": ch, "page": pi, "line": lid, "poly": poly, "sent": sent})
                elif ch in END: sent += 1
        sent += 1
        for r, py in zip(R[start:], pinyin("".join(r["c"] for r in R[start:]), style=Style.TONE)): r["py"] = py[0]
        pages.append({"title": pg.get("title", ""), "image": opg["image"], "start": start, "end": len(R)})

    def readings(t): return [set(r) | {c} for r, c in zip(pinyin(t, style=Style.NORMAL, heteronym=True), lazy_pinyin(t))]
    rp = readings("".join(r["c"] for r in R))
    P, S = asr["para"], asr["sv"]
    op_p, op_s = align(rp, readings(P)), align(rp, readings(S))
    t = [asr["sv_times"][o[1]] if o[1] is not None else None for o in op_s]
    known = [i for i, x in enumerate(t) if x is not None]
    for i in range(len(t)):  # interpolate times for chars SenseVoice didn't hear
        if t[i] is None and known:
            lo = max((k for k in known if k < i), default=None); hi = min((k for k in known if k > i), default=None)
            t[i] = t[hi] if lo is None else t[lo] if hi is None else t[lo] + (t[hi] - t[lo]) * (i - lo) / (hi - lo)
    for i, r in enumerate(R):
        a, b = op_p[i][0], op_s[i][0]; r["t"] = round(t[i] or 0, 2)
        # Error only when both models disagree with the page. One model hearing a different sound = "possible".
        r["state"] = ("skipped" if a == b == "del" else "misread") if a != "ok" and b != "ok" else \
                     "possible" if "sub" in (a, b) else "ok"

    def heard(lo, hi, ops, text):
        js = [ops[k][1] for k in range(lo, hi + 1) if ops[k][1] is not None]
        if not js: return ""
        prev = next((ops[k][1] for k in range(lo - 1, -1, -1) if ops[k][1] is not None), min(js) - 1)
        nxt = next((ops[k][1] for k in range(hi + 1, len(ops)) if ops[k][1] is not None), max(js) + 1)
        return text[prev + 1:nxt]

    os.makedirs(f"{run}/clips", exist_ok=True)
    items, i = [], 0
    while i < len(R):
        if R[i]["state"] == "ok": i += 1; continue
        conf = R[i]["state"] != "possible"; j = i
        while (j + 1 < len(R) and R[j + 1]["sent"] == R[i]["sent"] and R[j + 1]["state"] != "ok"
               and (R[j + 1]["state"] != "possible") == conf): j += 1
        kinds = {R[k]["state"] for k in range(i, j + 1)}
        kind = "possible" if not conf else "skipped" if kinds == {"skipped"} else "misread"
        if kind == "possible" and all(op_s[k][0] == "ok" for k in range(i, j + 1)): said = heard(i, j, op_p, P)
        else: said = heard(i, j, op_s, S) or heard(i, j, op_p, P)
        t0 = R[i - 1]["t"] if i else R[i]["t"]; t1 = R[j + 1]["t"] if j + 1 < len(R) else R[j]["t"] + 2
        s0 = max(0, t0 - 0.5); s1 = min(asr["duration"], max(t1 + 0.9, s0 + 2.5), s0 + 14)
        iid = f"e{len(items)+1:02d}"
        ff("-ss", f"{s0:.2f}", "-to", f"{s1:.2f}", "-i", f"{run}/audio.wav", "-b:a", "48k", f"{run}/clips/{iid}.mp3")
        items.append({"id": iid, "kind": kind, "page": R[i]["page"], "chars": list(range(i, j + 1)),
                      "text": "".join(R[k]["c"] for k in range(i, j + 1)), "said": said,
                      "said_py": " ".join(lazy_pinyin(said)), "sentence": sent_text[R[i]["sent"]].strip("”“ "),
                      "clip": f"clips/{iid}.mp3"})
        i = j + 1
    for pg in pages:
        rs = R[pg["start"]:pg["end"]]
        pg.update(n=len(rs), errors=sum(r["state"] in ("misread", "skipped") for r in rs),
                  seconds=round(max(r["t"] for r in rs) - min(r["t"] for r in rs), 1))
    jdump({"pages": pages, "chars": R, "items": items}, f"{run}/result.json")
    for p in pages:
        print(f"{p['title']}: {100*(p['n']-p['errors'])/p['n']:.1f}% ({p['errors']}/{p['n']} wrong, {p['seconds']}s)")
    for it in items:
        print(it["id"], it["kind"], it["text"], "->", it["said"] or "-", "|", it["sentence"])


# ---------------------------------------------------------------- build
def build(run, site, label):
    import numpy as np, sherpa_onnx as so
    from PIL import Image
    from pypinyin import pinyin, Style
    res = jload(f"{run}/result.json"); R = res["chars"]
    gloss = jload(f"{run}/gloss.json") if os.path.exists(f"{run}/gloss.json") else {}
    for d in ("clips", "tts"): os.makedirs(f"{site}/{d}", exist_ok=True)
    pages = []
    for pi, pg in enumerate(res["pages"]):
        im = Image.open(pg["image"]).convert("RGB"); sc = min(1.0, 1400 / im.width)
        im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
        im.save(f"{site}/page{pi+1}.jpg", quality=82)
        pages.append({"title": pg["title"], "image": f"page{pi+1}.jpg", "w": im.width, "h": im.height,
                      "n": pg["n"], "seconds": pg["seconds"], "scale": sc})
    tts = so.OfflineTts(so.OfflineTtsConfig(model=so.OfflineTtsModelConfig(
        matcha=so.OfflineTtsMatchaModelConfig(acoustic_model=TTS + "model-steps-3.onnx", vocoder=f"{MODELS}/vocos-22khz-univ.onnx",
                                              lexicon=TTS + "lexicon.txt", tokens=TTS + "tokens.txt", dict_dir=TTS + "dict"),
        num_threads=2), rule_fsts=f"{TTS}phone.fst,{TTS}date.fst,{TTS}number.fst"))
    def say(text):
        out = f"tts/{hashlib.md5(text.encode()).hexdigest()[:10]}.mp3"
        if not os.path.exists(f"{site}/{out}"):
            a = tts.generate(text, sid=0, speed=0.85); tmp = f"{site}/{out}.wav"
            with wave.open(tmp, "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(a.sample_rate)
                w.writeframes((np.clip(np.array(a.samples), -1, 1) * 32767).astype(np.int16).tobytes())
            ff("-i", tmp, "-b:a", "48k", f"{site}/{out}"); os.remove(tmp)
        return out
    def polys(idx, sc):  # one quad per run of consecutive chars on the same line
        runs = []
        for k in idx:
            if runs and R[k]["line"] == R[runs[-1][-1]]["line"] and k == runs[-1][-1] + 1: runs[-1].append(k)
            else: runs.append([k])
        return [[[round(x * sc, 1), round(y * sc, 1)] for x, y in (R[g[0]]["poly"][0], R[g[-1]]["poly"][1],
                 R[g[-1]]["poly"][2], R[g[0]]["poly"][3])] for g in runs]
    items = []
    for it in res["items"]:
        g = gloss.get(it["id"], {}); word = g.get("word") or it["text"]; w = "".join(c for c in word if is_cjk(c))
        sidx = [k for k, r in enumerate(R) if r["sent"] == R[it["chars"][0]]["sent"]]
        s_txt, off, py = "".join(R[k]["c"] for k in sidx), it["chars"][0] - sidx[0], None
        pos = s_txt.find(w)
        while pos != -1 and py is None:  # pinyin from sentence context when the word sits on the error
            if pos <= off < pos + len(w) or pos <= off + len(it["chars"]) - 1 < pos + len(w):
                py = " ".join(R[sidx[0] + pos + q]["py"] for q in range(len(w)))
            pos = s_txt.find(w, pos + 1)
        errs, ci, flags = set(it["chars"]), 0, []
        for ch in it["sentence"]:
            flags.append(int(is_cjk(ch) and sidx[0] + ci in errs)); ci += is_cjk(ch)
        shutil.copy(f"{run}/{it['clip']}", f"{site}/{it['clip']}")
        items.append({**{k: it[k] for k in ("id", "kind", "page", "text", "said", "said_py", "sentence", "clip")},
                      "n": len(it["chars"]), "word": word, "en": g.get("en", ""), "flags": flags,
                      "py": g.get("py") or py or " ".join(p[0] for p in pinyin(w, style=Style.TONE)),
                      "polys": polys(it["chars"], pages[it["page"]]["scale"]),
                      "tts_word": say(f"{w}，{w}。"), "tts_sent": say(it["sentence"])})
        print(it["id"], word, items[-1]["py"])
    cjk = "".join(sorted({c for c in json.dumps(items, ensure_ascii=False) + "".join(p["title"] for p in pages) if is_cjk(c)}))
    data = {"date": label, "pages": pages, "items": items, "run": hashlib.md5(json.dumps(res["items"]).encode()).hexdigest()[:8]}
    html = open(os.path.join(HERE, "..", "assets", "template.html"), encoding="utf-8").read()
    html = (html.replace("__FONT_URL__", "https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@500;700&display=swap&text="
                         + urllib.parse.quote(cjk + "田字格"))
                .replace("__TITLE__", " · ".join(p["title"] for p in pages))
                .replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")))
    open(f"{site}/index.html", "w", encoding="utf-8").write(html)
    files = sorted(os.path.relpath(os.path.join(d, f), site) for d, _, fs in os.walk(site) for f in fs if f != "index.html")
    print("PUBLISH_FILES " + json.dumps([{"path": f} for f in files]))


if __name__ == "__main__":
    cmd, args = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ("", [])
    if cmd == "prepare" and len(args) >= 3:
        os.makedirs(args[0], exist_ok=True); setup(); ocr(args[0], args[2:]); transcribe(args[0], args[1])
    elif cmd == "grade" and len(args) == 1: grade(args[0])
    elif cmd == "build" and len(args) == 3: build(*args)
    elif cmd == "setup": setup()
    else: sys.exit(__doc__)
