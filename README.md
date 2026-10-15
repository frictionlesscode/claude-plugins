# claude-plugins

Claude Code plugins from [frictionlesscode.com](https://frictionlesscode.com).
This repo is the `frictionlesscode` marketplace; each plugin lives under
`plugins/`.

One skill per plugin. `fixing-raw-bugs` and `writing-technical-articles`
layer on top of [Superpowers](https://github.com/obra/superpowers) and
refuse to run without it rather than falling back to a worse version of what
it already does. `chinese-reading-check` stands alone. Install them
separately, so taking one does not saddle you with another.

```
/plugin marketplace add frictionlesscode/claude-plugins
/plugin install fixing-raw-bugs@frictionlesscode
/plugin install writing-technical-articles@frictionlesscode
/plugin install chinese-reading-check@frictionlesscode
```

Superpowers first, if you want the first two and do not already have it:

```
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

## `fixing-raw-bugs`

An intake layer for the pile that arrives before a plan exists. Superpowers
is excellent from `here is what I want built` onward and has no opinion on
twenty unsorted field reports, some of which are feature requests and some
of which cannot be reproduced at all with the tooling you have today.

The work is in three reference files:

- **`references/triage.md`** turns a pile into an ordered list. Cheap
  read-only agents fan out one per bug and report facts only, never
  conclusions, because a model that cheap asked how hard a bug is will
  guess low and sound certain. Tiering happens centrally afterward, nothing
  is `mechanical` without a `file:line`, and unknown escalates.
- **`references/decisions.md`** separates a code problem from a product
  problem. Design questions get asked in one batch, all of them rather than
  the two or three that look important, each with concrete options and a
  real example. Chat is the default; file mode is opt-in and sticky.
- **`references/execution.md`** is the part that saves money. Batch
  composition, waves that share a surface, local concurrency limits, and the
  tier-to-model mapping.

Use `/fix-raw-bugs`, or just describe a bug backlog and it triggers on its
own. It writes `bugs/STATE.md` and resumes from whatever phase that names,
so a second run continues rather than re-triaging.

**You will probably need to build an instrument first.** Superpowers will
not attempt a fix until a failing test exists, so any bug that needs
conditions you cannot summon at a desk comes back `NO_REPRO`. That is the
tooling working correctly and it stalls the run until you can replay the
condition on demand. For me that meant device logging plus a replay path.
For you it might mean an MCP server pointed at your log aggregation, or an
export-and-replay path for one real session. Build it alone, before the
fixes.

## `writing-technical-articles`

Long-form drafting for a personal site. Parallel section agents leave
grep-findable `[[STUB:]]` markers instead of inventing details, every
technical claim carries a `[[SRC:]]` anchor, and a single-author pass runs
afterward so a document written by many agents reads as one person.

`assets/michael-voice.md` is my own voice spec. It ships as a worked example
of what one looks like, not as a style you should adopt. Build your own from
samples of your writing.

Use `/write-article`.

## `chinese-reading-check`

A child records themselves reading a few pages of a Chinese textbook
aloud. This grades the recording against photos of the pages and publishes a
review page: the score and characters per minute, the photos with each mistake
marked, and a card per mistake with the correct characters, pinyin, English,
a clip of what was read, and a model reading of the word and sentence.

Two local speech models (Paraformer and SenseVoice via
[sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx)) transcribe the
recording, and a character only counts as wrong when both disagree with the
page. Matching is on toneless pinyin, so tones are not graded. Where only one
model hears a problem the card is marked "Maybe" and the parent decides.

Everything runs through `scripts/readcheck.py` (`prepare`, `grade`,
`build`). The two steps that need judgment stay with Claude: checking the
OCR text against the photo, and writing the English and fixing pinyin.
Models download from sherpa-onnx GitHub releases on first use, about 500 MB.

Use `/check-reading`, or attach a recording and page photos and ask for the
reading to be checked.

## Verifying it works

1. Give `fixing-raw-bugs` a fresh list of 8 to 10 mixed bugs. It should stop
   after triage rather than fixing, and nothing should land in `mechanical`
   without a `file:line` in its reasoning.
2. Run it again immediately. It should resume at the next phase, not
   re-triage. Re-triaging is the main regression to watch for.
3. Give it a list where two or three bugs share one bad read path. It should
   say so and plan one task, not three.
4. Disable Superpowers and run it. It should refuse and name the install
   command rather than proceeding.
5. Give it a batch with two or three design-tier bugs. It should ask the
   questions in chat as one numbered list and wait, without creating
   `bugs/decisions.md`, unless you explicitly ask for file mode.

## Background

[AI Tools Want a Well-Formed Bug Report. I Have a Voice Memo.](https://frictionlesscode.com/writing/fixing-raw-bugs/)

## License

MIT
