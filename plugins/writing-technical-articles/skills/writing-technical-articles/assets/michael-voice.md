# Voice spec: Michael Swanson (frictionlesscode.com)

Extracted from *AI Fitness Coaching Is a Context Problem* (Sep 2026, ~5,400
words, 22 min read), which is the reference article. Follow this shape
unless told otherwise for a specific piece.

Every rule below is quoted from that article. When a rule and an instinct
disagree, the quote wins.

---

## Article shape

The reference piece runs in this order. Reuse it unless the subject
genuinely does not fit.

1. **Title is a claim, not a topic.** "AI Fitness Coaching Is a Context
   Problem" not "Building an AI Fitness Coach with MCP". The URL slug can
   be descriptive; the title argues.
2. **Dek, two sentences.** What was built, then a reframe of what was
   actually interesting: "I built my own coach out of three MCP servers
   wired into Claude. The interesting engineering wasn't the prompt, it was
   the data."
3. **Cold open on the real problem**, in first person, concrete, no
   context-setting preamble. The reference opens on 18 months of training
   and the decision that was actually hard.
4. **Name the gap precisely.** What each part knew, and what none of them
   knew. "Neither one could see the other, which meant both were giving me
   reasonable answers to incomplete questions."
5. **Result stated up front**, flagged as such, so the reader can decide
   whether to continue: "**The result, so you know whether this was worth
   doing:**".
6. **Numbered requirements, written before building**, that later sections
   trace back to: "I wrote these down before building anything, and every
   decision later in this piece traces back to one of them."
7. **Scenes of it working**, present tense, subheaded by moment rather than
   by feature (Morning, Eating, Training). Images with italic captions.
8. **An explicit divider between story and build**, in italics: "Everything
   above is the story. Everything below is the build. If you are here for
   the systems, this is where it starts."
9. **Architecture**, components in bold with links, one paragraph each,
   saying what it is and why it exists.
10. **A conceptual model** that makes the rest legible ("Three layers, not
    one"), with the single governing rule in bold.
11. **Decisions and tradeoffs** as bold lead-ins, each a mini-essay of two
    to six sentences. This is the densest and most valuable section.
12. **Where it is still rough**, numbered, genuinely candid, including the
    things that are embarrassing.
13. **Running it yourself**, ordered so each step is useful alone and later
    ones assume earlier ones work.
14. **Retrospective**: what actually took the time, what actually mattered.
15. **A landing sentence that reframes the whole piece.** Never a summary
    paragraph. "And the thing that finally made an AI coach useful was not
    making it smarter. It was making sure that when it said 'go heavy
    today,' it knew what I did on Tuesday."

## Sentences

- Long explanatory sentences chained by "because", "so", "which meant",
  broken up by short declaratives that land a point.
- The short sentence is a deliberate instrument. Use it sparingly and only
  to land something: "The plumbing was missing, not the model." / "Five
  numbers." / "The model was the easy part." / "A local SQLite cache. A
  90-day trend question should not turn into 90 API calls."
- Mostly expanded forms: "it is", "that is", "I am", "do not", "cannot".
  Contractions appear but are the minority. This is what makes the prose
  read measured rather than chatty.
- First person singular throughout. Second person only when instructing the
  reader or generalising a lesson to them.

## Paragraphs

- Two to five sentences typically.
- One-sentence paragraphs for emphasis, roughly once per section: "This is
  the part that changed my training."
- No paragraph exists purely to transition. Each carries content.

## Signature moves

**"X rather than Y" is the primary contrast construction.** It appears
dozens of times and is the most recognisable habit in the piece: "a coach
rather than an advisor", "stored per date rather than derived", "degrade
partially than fail closed", "the fix went in the skill rather than the
code", "Multi-tenant is a different program rather than a bigger version of
this one."

**"actually" as the marker of the real thing** versus the assumed thing:
"What I actually wanted", "What it actually took to build", "What data
actually moves the needle", "the actual cause turned out to be", "a diet I
actually stuck to." Section titles use it freely.

**Zoom out to a transferable principle at the end of a section.** Never at
the end of the article, where the landing does that job instead. "If you
have ever pulled policy out of platform code so the platform stops needing
a release every time policy changes, this is the same move." / "Data that
never changes a decision is just noise with a timestamp on it."

**Real numbers everywhere, and only real ones.** 134 tests, 83 tests, 291
exercises, 8 hours 7 minutes, sleep score 90, 190.2, 574 calories against a
target of 1,288. Specificity is the credibility mechanism of the whole
piece. A number that cannot be sourced does not appear.

**Dry understatement for the uncomfortable bits.** "It has not caused a
problem yet, and 'yet' is doing some work in that sentence." / "which is
obviously not ideal." / "an honest warning that all of this is built on
APIs nobody promised me."

**Admit the fork.** Credit is explicit and unhedged: "This one is a fork,
not something I built from scratch," followed by exactly what came from
upstream and exactly what was added.

## Handling limitations

Limitations get their own section, numbered, and are stated flatly rather
than hedged inside other sentences. State the claim with confidence, then
undercut it in a separate sentence if it needs undercutting.

The reference includes limitations that are genuinely unflattering: a
plaintext password, no auth layer, no approval gate on writes, tests the
author is nervous about running, a Windows box that might not come back up.
That candour is load-bearing. Do not sand it off.

## Formatting

- H2 for major sections, H3 for scenes inside them.
- Section titles are short and often claims or questions: "Where it is
  still rough", "Three layers, not one", "What data actually moves the
  needle".
- Bold for list lead-ins and for the one governing rule in a section: "**the
  skills contain zero training philosophy.**"
- Numbered lists when order or priority is real. Bold-lead paragraphs, not
  bullets, when each item needs more than a sentence.
- Links are dense and specific: products, repos, papers, READMEs. Link the
  thing being named, at first mention.
- Images carry italic captions that add information rather than describing
  the image: "Two apps, two truths, no overlap."
- Horizontal rules between major movements.

## Banned constructions

- **Em dashes.** Use a period, a comma, or restructure. There are none in
  the reference article.
- **"It's not just X, it's Y."** Note that "X, not Y" and "X rather than Y"
  are his and are fine. The banned form is the escalating hype version.
- Opening with validation, throat-clearing, or a definition.
- "It's worth noting", "it's important to remember", "at the end of the
  day".
- Colon-then-reveal sentences used for drama.
- Scare quotes around invented labels.
- Self-promotional asides. Let the work make the argument. The reference
  never mentions the author's job title.
- A concluding paragraph that summarises what the reader just read. End on
  a landing.
- Vague quantifiers where a real number exists.

## Open question to confirm

Spelling is mixed: "generalises", "realise" and "labelled" are British,
"behavioral" is American. Ask which to standardise on rather than picking
one silently.

---

## Applying this to a shorter piece

The reference is 5,400 words. For a piece under 1,500, keep items 1 through
5, one scene, the decisions section, and the landing. Drop the story/build
divider, the conceptual-model section, and "Running it yourself". The
sentence-level rules and signature moves do not change with length.
