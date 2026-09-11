# Tells reference

Voice consistency and factual grounding are handled elsewhere. This file is
about a different failure: prose that is consistent, accurate, and still
obviously machine-assembled.

The tells below are ranked by how loudly they give the game away.

---

## 1. Structural evenness

The loudest tell, and the one this workflow actively causes if unmanaged.
Parallel agents hitting per-section word targets produce sections of similar
length, paragraphs of similar length, and lists of similar size. Human
writing is lumpy because attention is uneven.

Measure it in the reference article: the tradeoffs section runs from a
two-sentence item to a six-sentence one, and the rough-edges list has items
of wildly different weight sitting next to each other.

**Rules:**

- Section briefs carry a target that reflects **how much the author cares**,
  not an even division of the word budget. At least one section should be
  three or more times another. Say why in the brief: "this is the heart of
  the piece, go long" or "this is a hinge, keep it to four sentences."
- Vary paragraph length deliberately within a section. A run of five
  same-length paragraphs reads as generated regardless of content.
- Lists should not all have three items. Three-item lists are the single
  most overused shape in machine prose. If a list naturally has three, ask
  whether one is padding.
- One section should go noticeably deeper than the rest. Depth asymmetry is
  what signals a human who found something genuinely interesting.

## 2. The reflective coda

Ending a section by zooming out to a general lesson is a real move in the
reference article. It appears **twice in 5,400 words**.

Applied per-section by parallel agents it becomes the defining sound of
machine writing: every subsection closing with a tidy takeaway.

**Rule: at most two per article, never in adjacent sections.** Assign them
in the outline, to specific named sections. Every other section ends on
whatever it was saying, or on a concrete detail, or mid-thought.

## 3. Uniform confidence

Machine prose applies the same certainty to everything. Human writers are
more sure about what they know well and audibly less sure elsewhere, and
the variation tracks something real.

Look for: does anything in the draft sound less certain than the rest? If
every claim lands with identical weight, the piece is flat.

## 4. Absence of cost

The reference article admits a plaintext password, no auth layer, no
approval gate on writes, a test suite the author is nervous about running,
and a Windows box that might not come back up. That candour is not decorum,
it is the strongest evidence a human wrote it, because an agent has no
access to what embarrassed anybody.

If a draft contains no admission that costs the author something, the
interview failed. Go back and ask.

## 5. Announced transitions

"Now that we have covered X, let us turn to Y." "With that in mind." "Having
established the architecture." Machine prose signposts because each agent
knows it sits in a sequence and reaches for a handle.

The reference article transitions by content, not by announcement. The one
explicit signpost in the whole piece is the italic story/build divider, and
it is doing real work for a reader who wants to skip.

**Rule: at most one announced transition per article, and only if a reader
genuinely needs to navigate.**

## 6. Vocabulary tells

Machine-frequent words that rarely appear in the reference article. Treat
each as a flag to justify, not an absolute ban, but the default is cut.

<!-- tells:ignore -->
delve, leverage (as a verb), robust, seamless, landscape, realm,
underscore, testament, crucial, vital, harness (as a verb), navigate (as a
metaphor), tapestry, myriad, plethora, elevate, unlock, empower, streamline,
foster, pivotal, intricate, nuanced, comprehensive, holistic, cutting-edge,
game-changer, paradigm, ecosystem (outside its literal software sense),
journey (as a metaphor), dive into, unpack, at its core, in today's world,
it is important to note, it is worth noting, that said, moreover,
furthermore, ultimately, in conclusion

Also flag: "not only... but also", "isn't just... it's", any sentence
beginning "But here's the thing", and rhetorical questions used as section
openers.
<!-- /tells:ignore -->

## 7. Rhythmic sameness

- **Sentence openings.** If most sentences in a section open with the
  subject, or many paragraphs open with "The", the rhythm is mechanical.
- **Tricolon addiction.** Three balanced clauses in a row, repeatedly. One
  is fine and often good. Four in an article is a pattern.
- **Balanced pairs everywhere.** "Fast and reliable", "simple and powerful".
  Machine prose reaches for the pair reflexively.

## 8. Completeness over interest

Agents write what is true and complete. Humans write what is interesting and
leave gaps, drop asides, and mention things once without resolving them.

The reference article has "Sometimes your architecture is decided by someone
else's notification model" sitting at the end of a tradeoff and going
nowhere. That kind of loose end is a strong human signal, and no agent
generates one unprompted because it reads as incomplete.

**Rule:** do not resolve every thread. If the author said something vivid in
the interview that does not fit a section's argument, it can still earn a
sentence.

---

## The tells pass

Run this as a **separate pass after the voice unify pass**, not folded into
it. They have different jobs: unify makes it sound like one person, tells
makes that person sound human. Combining them means one gets shortchanged.

One agent, whole document, most capable model, same as unify.

Give it this file and the draft. It reports findings by category and
proposes specific edits. It may not change facts, restructure, or touch
anything carrying a `[[SRC:]]` anchor.

Run `scripts/tells.py` first and hand its output to the agent as a starting
point. The script catches what is countable; the agent catches what is not.

## What the author should write

Two parts of any article carry disproportionate voice and are the most
read: **the opening hundred words and the closing two sentences.**

Offer to have the author write or dictate both, even roughly, and have the
agents match inward from there. A rough human opening beats a polished
generated one, and it anchors the voice of everything that follows.

If the author declines, generate them last, after the body exists, so they
are written against real material rather than against an outline.
