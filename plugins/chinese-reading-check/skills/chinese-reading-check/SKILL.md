---
name: chinese-reading-check
description: Grades a child's recorded Chinese read-aloud against photos of the textbook pages and publishes a review page with the score, highlighted mistakes, a clip of each mistake, pinyin, English and a model reading. Use when given a recording (m4a/mp3/wav) plus page photos and asked to check, grade or score the reading.
---

# Chinese reading check

Inputs: one recording of a child reading simplified Chinese aloud, and a photo of each page in reading order.
Output: a published artifact with overall and per-page accuracy, chars/min, the photos with mistakes marked
(tap to hear), and a card per mistake with the correct 汉字, pinyin, English, the sentence, what was heard,
the clip, a model reading and a "Count it" toggle for the parent.

All the mechanics are in `scripts/readcheck.py` next to this file. If it isn't there (an account copy of the
skill), `git clone --depth 1 https://github.com/frictionlesscode/claude-plugins /tmp/fc-plugins` and use
`/tmp/fc-plugins/plugins/chinese-reading-check/skills/chinese-reading-check/scripts/readcheck.py`.

## Steps

1. `python3 readcheck.py prepare run <audio> <page1.jpg> [<page2.jpg> ...]`
   Installs and downloads models on first use (a few minutes), copies the photos to `run/`, OCRs them
   (prints numbered lines) and transcribes with two speech models. Never modify the uploads.
2. Write `run/ref.json` from the printed lines, checking each against the photo yourself:
   `{"pages":[{"title":"数星星的孩子","lines":[["p1l2","夏天的晚上，有一个孩子坐在"], ...]}]}`
   - Body text only, in reading order. Leave out the title (unless the recording reads it), pinyin
     annotation lines (`ge`, `shao`), headers, footers and the 新字新词 box.
   - Fix OCR errors against the photo, keeping the character count (seen: 毕昇→毕异, 蹲→跨).
3. `python3 readcheck.py grade run` prints page scores and every item:
   `eNN kind text -> heard | sentence`. Don't hand-edit results. The parent's toggles handle disputes.
4. Write `run/gloss.json`, one entry per item: `{"e01": {"word": "指着", "en": "pointing at"}}`.
   - `word`: the word or phrase in the sentence that contains the error (盘 → 转盘; a skipped clause → the clause).
   - `en`: short English a child can follow.
   - `py`: add it whenever the auto pinyin is wrong. Usual misses: verb 数 is shǔ, neutral tones
     (星星 xīng xing, 爷爷 yé ye), 得/地 particles are de, 一 sandhi (一个 yí ge).
5. `python3 readcheck.py build run site "<recording date> · <what it was>"`, then check every card's pinyin
   in its output. Publish with the Artifact tool: `file_path` site/index.html, `root` site, `files` = the
   list printed after `PUBLISH_FILES`, `icon` "book".

Reply with the overall and per-page score and chars/min, the 3 to 6 words to practice (repeat misses and
the page's new words), and one line that tones aren't graded and "Maybe" items need a listen.

## How grading works (for questions)
- Two models (Paraformer, SenseVoice) transcribe. Alignment is on toneless pinyin, so homophones count
  as correct. Tones are not graded.
- An error needs both models to disagree with the page: misread if either heard something else, skipped if
  neither heard anything. One model disagreeing makes a "Maybe", not counted.
- Repeats and self-corrections aren't penalized. Score = (chars − errors) / chars, CJK characters only.
- Clips come from SenseVoice timestamps, padded about half a second each side. The model reading is a
  standard Mandarin TTS voice; words are said twice because single words came out unclear.
