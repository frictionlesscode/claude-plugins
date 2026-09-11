# Voice reference

## Why this file exists

A subagent told to "match the author's voice" will produce competent generic
prose, because it has nothing to match against. Voice has to be written down
as rules a stranger could follow, with examples, or parallel drafting will
average everything toward the same neutral register.

Store the spec at user scope (`~/.claude/voice/<author>-voice.md`) so it is
built once and reused across articles. Refine it when a published piece
teaches you something, not every run.

A spec for this author already exists at `assets/michael-voice.md` in this
skill, derived from a published article. Use it. The instructions below are
for building one for a different author, or for refreshing this one after
several more pieces are published.

## Building the spec

Gather samples: published posts, README prose they wrote, long PR
descriptions, internal write-ups. Five or six pieces is plenty. Prefer
things they wrote alone and were happy with.

Then extract **measurable and quotable** properties, never adjectives:

- **Sentence length.** Rough average and how much it varies. Do they mix a
  three-word sentence into a run of long ones?
- **Paragraph length.** Sentences per paragraph, and whether one-line
  paragraphs appear for emphasis.
- **Openings.** Do they open with the problem, a scene, a claim, a number?
  Quote two real openings.
- **Person and stance.** First person singular? Plural? Do they address the
  reader as "you"?
- **Structure.** Headers or continuous prose? Lists only for genuine lists,
  or freely?
- **Technical density.** Do they show code, or describe it? How much do they
  assume?
- **Hedging.** How do they handle uncertainty, and how often?
- **Endings.** Do they conclude, trail off, or land on a practical next
  step?
- **Banned constructions.** Specific patterns to never emit.
- **Signature moves.** The two or three things that make it recognisably
  them. Quote each.

Every entry gets a real quoted example from a sample. The example is what
makes the rule usable; the rule alone is not enough.

## Default banned constructions

Seed every spec with these unless samples show otherwise, then add
author-specific ones:

- Em dashes. Use a period, a comma, or restructure.
- "It's not just X, it's Y" and bare "not X but Y".
- Opening with validation or throat-clearing.
- Colon-then-reveal sentences used for drama.
- Scare quotes around invented labels.
- Stock hedges: "it's worth noting", "it's important to remember".
- Self-promotional asides. Let the work make the argument.
- Concluding paragraphs that summarise what the reader just read.

Add anything the author has told you directly. A stated preference outranks
anything inferred from samples.

## Structural preferences worth capturing

Some authors have a shape they reach for. If samples show one, write it
down, because a section agent will otherwise default to a generic shape.

A common one for engineering write-ups: state the problem first, then what
was done about it, then close on the result. If that is the author's habit,
say so explicitly, because it governs section-level structure and not just
sentences.

## The unify pass

One agent. The whole document. The most capable model available. Never
parallel, under any circumstances: running voice-fixing in parallel
recreates the inconsistency it exists to remove, and does it more subtly
because each agent will have smoothed toward a different centre.

**What it does:**

- Smooths transitions across section boundaries so each section leads into
  the next.
- Removes constructions repeated across sections. Four agents will
  independently reach for the same framing, and the repetition is invisible
  to each of them and glaring to a reader.
- Enforces the voice spec throughout.
- Fixes rhythm: breaks up runs of same-length sentences, varies paragraph
  openings, kills accidental alliteration and unintended echoes.
- Checks that terminology is consistent. Parallel agents will name the same
  thing three ways.
- Verifies the piece answers the question its opening sets up.

**What it must not do:**

- Change any fact, number, name or claim.
- Alter anything carrying a `[[SRC:]]` anchor. If a sourced sentence reads
  badly, flag it rather than rewriting it.
- Restructure sections or move content between them. That is an outline
  decision and belongs to the author.
- Resolve a `[[STUB:]]`. Stubs are questions for the author, and an agent
  answering one is exactly the invention this workflow prevents.
- Add new material.

**Report format.** Return a short list of what changed and why, grouped by
kind: transitions smoothed, repetitions removed, voice violations fixed,
terminology unified. The author needs to be able to object to a change
without re-reading the whole piece.

## Revision briefs

When relaunching a section agent, the brief must carry:

1. The section's current full text.
2. The **verbatim** last paragraph of the preceding section and first
   paragraph of the following one. Not a summary. The agent needs to hear
   the actual prose it is joining.
3. The voice spec.
4. The specific change requested, in the author's own words where possible.
5. The boundary rule: edit only this section, do not touch the neighbours
   even to fix an obvious seam.

Point 2 is what stops each revision drifting further from the whole. Point 5
is what stops two agents fighting over the same paragraph.

Seams left by point 5 are fixed by the unify pass, which is the only thing
allowed to see the whole document at once.
