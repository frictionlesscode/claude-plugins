---
name: writing-technical-articles
description: Long-form technical article workflow for a personal site, built on Superpowers. Interviews you about the idea, drafts sections in parallel with subagents that leave machine-findable stubs rather than inventing facts, mines your repos and notes for real specifics, batches every open question back to you in chat, then runs a single-author voice pass so parallel drafting does not read like four different writers. Use this whenever someone wants to write a blog post, technical article, engineering write-up, essay or long-form piece for their own site, says "help me write an article about", "turn this project into a post", "write this up", or wants to resume an article already in progress. Also use it for revision rounds on an existing draft. Requires the Superpowers plugin.
---

# Writing technical articles

Parallel drafting is fast and it produces prose that reads like four people
took a section each. That is the central problem this skill solves. Almost
every rule here exists to make a document written by many agents read as one
author.

The second problem is confabulation. A subagent asked to write about work it
cannot see will produce fluent, specific, wrong details: version numbers
that were never used, measurements nobody took, a config that does not
exist. On a personal engineering site that is worse than a thin article,
because readers who know the domain will catch it.

Both problems are handled the same way: agents are never allowed to fill a
gap with plausible text. They mark it and move on.

## Check the dependency first

Confirm `superpowers:brainstorming` and `superpowers:writing-plans` are
reachable. If not, stop and say this skill layers on Superpowers, with the
install:

```
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

Be honest about the division: Superpowers owns the Socratic interview and
brief construction. The drafting loop, voice enforcement and publishing are
this skill's own, because Superpowers targets code and this is prose.

## Always start by locating the work

Read `article/<slug>/STATE.md` if it exists and resume from the phase and
round it names. Do not restart the interview, do not re-draft sections
already approved, do not re-ask questions already answered in
`qa-log.md`. Re-asking is the fastest way to make this feel worse than
writing it yourself.

If several articles are in flight, list them and ask which.

## The phases

| Phase | Produces | Ends when |
|---|---|---|
| 0 Seed | `STATE.md`, `sources.md` | The idea and its sources are named |
| 1 Voice | `voice-spec.md` | A spec is loaded or built |
| 2 Shape | `outline.md` | You approve the outline and briefs |
| 3 Research | `evidence/` | Each section has real specifics or a gap list |
| 4 Draft | `draft.md` | Every section is written or stubbed |
| 5 Round | `qa-log.md`, revised `draft.md` | You have no more changes |
| 6 Unify | `draft.md` | One author, clean seams |
| 6b Tells | `draft.md` | It reads as unassisted |
| 7 Publish | artifact or a PR | It is where you can read it |

Phases 5 and 6 loop. Update `STATE.md` at every boundary.

---

## Phase 0: seed

Capture the idea in a few sentences and, critically, **what sources exist**.
Write `sources.md`:

- Repos to mine, by path. These are the difference between a real article
  and a generic one.
- Notes, exports, previous drafts, talk slides.
- Prior conversations. If the harness has past-conversation search, use it.
  In Claude Code it does not, so this means files on disk: exported chats, a
  notes directory, commit messages, PR descriptions. Say which you have
  rather than pretending to reach a history you cannot read.

Ask what the piece is *for* and who reads it. An article defending a
decision, teaching a technique, and recounting an incident have different
shapes, and the interview questions change accordingly.

## Phase 1: voice

Read `references/voice.md`.

A spec built from the author's published work ships with this skill at
`assets/michael-voice.md`. Copy it to `~/.claude/voice/michael-voice.md` on
first run if it is not already there, load it, and skip the rest of this
phase. It encodes the reference article's shape as well as its sentence-level
voice, so it governs section structure too, not just prose.

For a different author, or when the author says this piece should not follow
the reference shape, build a spec from samples of their existing writing. A voice spec is
concrete rules with quoted examples, never adjectives. "Conversational" is
useless to a subagent. "Opens with the problem, never with context-setting"
and "average sentence 14 words, paragraphs 2 to 4 sentences" are usable.

Every section agent gets this file. It is the only thing standing between
parallel drafting and a stitched-together document.

## Phase 2: shape

Hand the interview to `superpowers:brainstorming`. That is what it is for: a
Socratic session that refines a vague idea into something specific enough to
build from.

Push it toward article-specific territory: what the reader believes now and
should believe after, the one claim the piece defends, what gets cut, where
the piece could be wrong, what the reader gets in the first hundred words
that makes them continue.

**Then ask the questions no agent can answer for you.** This is where the
strongest anti-generic material comes from. It is content rather than style,
so no later pass can add it:

- What went wrong, and what did you do about it?
- What is still embarrassing about this? What would you not accept at work?
- What did you believe going in that turned out to be false?
- What took far longer than it should have?
- What did you get from someone else, and who?
- What are you still nervous about?

The reference article's most human moments are all answers to these. An
article with no admission that costs the author something reads as generated
however well the prose is polished.

Ask a lot here and few questions later. Questions during the interview are
cheap; questions after 3000 words are expensive because the answers
invalidate text that already exists.

Then produce `outline.md` with a **brief per section**, using
`superpowers:writing-plans`. Each brief carries: the section's job in one
sentence, what the reader knows entering and leaving it, which evidence
files it may draw on, a target length, and what it must not cover because a
neighbouring section owns it.

**Make the lengths deliberately uneven.** Target length reflects how much
the author cares, never an even division of the budget. At least one section
should run three or more times another, and the brief says why: "this is the
heart of the piece, go long" or "this is a hinge, four sentences." Even
sections are the loudest tell in a finished article, and per-section targets
are what cause them.

**Assign the reflective codas in the outline.** At most two sections in the
article end by zooming out to a general lesson, never two adjacent. Name
which. Every other brief says explicitly: end on the concrete, do not
generalise. Left unassigned, every parallel agent writes one and the piece
acquires a tidy takeaway per subsection, which is the defining sound of
machine prose.

Decide now who writes the opening hundred words and the closing two
sentences. Those carry the most voice and are the most read. Offer to have
the author write or dictate both, even roughly, so agents match inward from
real anchors. If they decline, generate them last, against the finished body
rather than the outline.

Get explicit approval on the outline before drafting. Restructuring after
drafting throws away words.

## Phase 3: research

Read `references/research.md`.

Dispatch read-only subagents on a cheap model, one per repo or source, in
parallel. They extract specifics into `evidence/<source>.md`: real file
paths, real commits, real config, real numbers, real error messages, with
enough context that a drafting agent can use them without guessing.

Evidence agents do not write prose and do not draw conclusions. They
retrieve. Anything they cannot find is recorded as a gap, and gaps become
stubs later rather than becoming invention.

## Phase 4: draft

Dispatch one section agent per section, in parallel, on a mid-tier model.
Each receives: its brief, `voice-spec.md`, the evidence files its brief
allows, and the boundary rule.

Two conventions make the whole loop work. Both are described fully in
`references/research.md`; the short version:

- `[[STUB: what's missing | Q: the question for the author | TRY: where to look]]`
  Anything the agent does not know. It writes the stub and continues rather
  than inventing. Stubs are grep-findable, so the review loop can enumerate
  them.
- `[[SRC: path:line]]`, `[[SRC: commit abc1234]]`, `[[SRC: url]]`
  Every specific technical claim carries an anchor. A claim with no anchor
  and no evidence backing becomes a stub instead. Anchors are stripped at
  publish.

**The boundary rule:** edit only your own section. Do not touch neighbouring
sections even to fix an obvious seam. Seams are Phase 6's job, and agents
editing each other's text in parallel is how a document loses its thread.

Assemble into `draft.md`, then run Phase 6 once so the first thing the
author reads is coherent rather than obviously assembled.

## Phase 5: round

Enumerate every stub. Group them: same underlying question, one ask.

Then ask in chat, not in a file. This is the one place a file would be
wrong: the author wants to talk through an article, and their answers here
are often themselves the material. Use multiple-choice where the options are
genuinely enumerable, prose questions where they are not.

Read out the questions in a batch, work through their answers, and record
every answer in `qa-log.md`. That log is what makes the next session
resumable and stops the same question being asked twice.

Then relaunch only the affected section agents. Each revision brief carries:
the section's current text, the verbatim boundary paragraphs of both
neighbours, `voice-spec.md`, the specific change, and the boundary rule
again.

Give the author the whole draft to read each round, not a diff. Prose is
judged whole.

Bound this loop the way a fix loop is bounded. If a section has been revised
three times and is still wrong, it is an outline problem: take it back to
Phase 2 for that section rather than grinding.

## Phase 6: unify

Read `references/voice.md` for what this pass may and may not change.

**One agent. The whole document. Never parallel.** This is the single most
important constraint in the skill. Parallel voice-fixing recreates the exact
problem it exists to solve.

Give it the most capable model available. It smooths transitions, removes
repeated constructions across section boundaries, enforces the voice spec,
and makes the whole thing sound like one person wrote it in one sitting.

It may not change facts, structure, or anything anchored by a `[[SRC:]]`. It
reports what it changed so the author can object.

After targeted revisions, running it over the touched sections plus their
neighbours' boundaries is proportionate. Before publish, run it over the
whole document.

## Phase 6b: tells

Read `references/tells.md`.

A **separate pass**, after unify, never folded into it. They have different
jobs: unify makes the document sound like one person, tells makes that
person sound human. Combined, one gets shortchanged, and it is always this
one.

Run `scripts/tells.py draft.md` first. It counts what is countable: em
dashes, vocabulary tells, paragraph-length variation, section-length spread,
three-item lists, sentence-opener concentration, reflective codas. Hand its
output to the agent as a starting point rather than a verdict.

Then one agent, whole document, most capable model. It reports findings by
category and proposes edits. It may not change facts, restructure, or touch
anything anchored by `[[SRC:]]`.

The script's FAIL lines block publish. Its WARN lines are prompts to look,
not defects: a genuine three-item list is a three-item list.

## Phase 7: publish

Read `references/publishing.md`.

Only offer this when the author says they are happy. Ask which target:

- **Artifact** for reading and sharing a link, no repo involved.
- **GitHub Pages** for the real thing. Strip anchors, resolve remaining
  stubs or refuse to publish, generate front matter, put it at the path the
  site generator expects, and open a PR rather than pushing to the default
  branch.

Never publish with unresolved stubs. List them and stop.

## Failure modes

**It reads like four writers.** Phase 6 was skipped, run parallel, or given
a weak model. It is one agent, whole document, best model.

**Confident wrong details.** A section agent had no evidence and no stub
discipline. Check that its brief actually pointed at evidence files.

**Question fatigue.** Too many questions arriving too late. Front-load
Phase 2 and group stubs by underlying question before asking.

**Endless rounds.** Three revisions on one section means the outline is
wrong, not the prose.

**Reads competent and generated.** Usually structural rather than
sentence-level: even section lengths, a reflective coda on every subsection,
and no admission that costs the author anything. The first two are outline
failures, the third is an interview failure. None are fixable by rewriting
sentences, which is why the tells pass runs against `references/tells.md`
rather than against instinct.
