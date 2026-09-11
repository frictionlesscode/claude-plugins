---
name: fixing-raw-bugs
description: Intake layer above the Superpowers workflow for a pile of raw, unsorted bug reports. Triages with evidence rather than guesswork, builds missing test instrumentation before attempting fixes, asks every open design question in chat by default (file mode available), then hands cost-tiered batches to superpowers:subagent-driven-development. Use this whenever someone dumps a list of bugs, says "fix raw bugs", "triage these bugs", "here's what I found testing", "here are the bugs from the field", or asks to resume bug work already underway — even if they never say the words triage or batch. Also use it to resume: it detects which phase work is in from state files and picks up there rather than restarting. Requires the Superpowers plugin.
---

# Fixing raw bugs

A layer above Superpowers, not a replacement for it.

Superpowers starts from "here is what I want built." From that point on it
is excellent: plan construction, the implement-review-fix loop, two-stage
review, model tiering at dispatch. It has no opinion on what arrives before
that. A pile of unsorted field reports with no repro steps, no priorities,
some of which are feature requests, some of which need a product decision,
and some of which cannot be reproduced at all with the tooling that exists
today.

This skill covers exactly that gap and then hands off. Everything from a
plan file onward belongs to Superpowers. Do not reimplement it here.

## Check the dependency first

Confirm the Superpowers skills are reachable before doing anything else:
`superpowers:writing-plans`, `superpowers:subagent-driven-development` and
`superpowers:systematic-debugging`.

If they are not, stop. Say plainly that this skill is a layer on top of
Superpowers and cannot run without it, and give the install:

```
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

Do not fall back to hand-rolling plans and dispatch. A silent fallback
produces a worse version of the thing the user already installed, and they
will not know it happened.

## Always start by locating the work

Read `bugs/STATE.md` if it exists. It names the current phase, and the
`decision_mode` in effect for this run (see Phase 3). Resume there.

Do not restart from intake, do not re-triage bugs already triaged, do not
rebuild plans that already exist. Re-doing a finished phase costs real money
and silently discards decisions the user already made.

If `bugs/STATE.md` is absent, infer the phase from which of
`bugs/raw-list.md`, `bugs/triage.md`, `bugs/decisions.md` and `plans/` are
present, write `bugs/STATE.md`, and continue. If none exist, this is a fresh
intake: go to Phase 0.

Announce which phase you are entering, in one line, before working. The user
needs to know whether this run gathers evidence or changes code, because
those cost very different amounts.

## The phases

| Phase | Owner | Produces | Ends when |
|---|---|---|---|
| 0 Intake | this skill | `bugs/raw-list.md` | Every report is a numbered item |
| 1 Triage | this skill | `bugs/triage.md` | Every bug has an evidence-backed tier |
| 2 Instrument | handoff | a merged instrument plan | Blocked bugs became testable |
| 3 Decide | this skill | answers recorded (chat or file) | Every open question is answered |
| 4 Execute | handoff | merged fixes | A batch merged; loop for the next |
| 5 Close | this skill | updated `bugs/triage.md` | Nothing is unaccounted for |

Phases 2 and 4 are Superpowers runs. This skill decides *what* goes into
them and *at which tier*. Superpowers decides how it gets built.

Update `bugs/STATE.md` at every boundary. Commit the artifact.

---

## Phase 0: intake

Turn whatever the user gave you into `bugs/raw-list.md`: one numbered
section per bug, their own words preserved for intent, plus any priority
they stated ("this is the biggest one") marked verbatim.

Preserve their emphasis. Stated priority is real information about what to
sequence first, and it is routinely lost when a list gets reformatted.

Split a report into two bugs when it contains two independent failures. A
wrong value and a badly worded message that displays it are separate: one is
a logic defect, the other is a copy decision, they have different tiers and
different fixes. Filing them as one means a worker fixes half and reports
success.

Watch for items that are not bugs. Feature requests and missing tooling
often arrive mixed into a bug list. Keep them, label them, because they
frequently turn out to be prerequisites rather than nice-to-haves.

## Phase 1: triage

Read `references/triage.md` for the schema, the tier rules and the evidence
dispatch pattern. The short version:

Dispatch cheap read-only subagents in parallel to gather evidence. Evidence
is: does a deterministic repro exist, what reproduces it, which files are
implicated, is there test coverage. **Evidence gathering returns facts, not
conclusions.** You do the tiering yourself, centrally, after evidence
returns. That split is what keeps the cost down without letting a cheap
model decide what is hard.

Tiers are `mechanical`, `standard`, `investigate`, `design`, and the rule
that matters most is: **if you cannot cite a file:line, it is not
mechanical.** Between two tiers, take the higher one. Unknown escalates.
Never guess downward to reduce the user's review load — a mistiered bug
costs far more than an over-tiered one.

Look for shared root causes before filing bugs independently. Several
symptoms often trace to one bad read path. Ask explicitly: do these go
through one place, and is that place wrong? A shared cause is one task, not
five, and finding it changes the whole plan.

`investigate`-tier bugs do not get root-caused inline here. Hand each to
`superpowers:systematic-debugging`, one subagent per bug, with a strict
brief: investigate and report a cause, do not fix. Fold findings back into
`bugs/triage.md` and re-tier. A bug with a located cause is usually
`standard` or `mechanical`; one that resists investigation is usually
blocked on an instrument, not on effort.

## Phase 2: instrument

This phase is the one people skip, and skipping it is what produces a batch
that reports fixing nothing.

After triage, ask: **which bugs cannot be reproduced on demand, and why?**

Some bugs need conditions you cannot summon: sensor noise, a specific
device, a network state, a timing race, a third-party response, a
particular data shape in production. Superpowers enforces a failing test
before implementation, so a worker facing one of these will correctly
refuse and report `NO_REPRO`. That is the tooling working. The missing
piece is infrastructure, not effort.

When that is true, build the instrument first, alone:

- **Capture** real-world state when the condition does occur.
- **Replay** that capture deterministically, headlessly, with no device and
  no waiting.
- A checked-in fixture format with a schema version.

Capture alone is not enough. A log you can read tells you what happened
once. A log you can replay turns an unreproducible bug into a permanent
test. Those two look identical until you try to write the test, so if an
instrument plan already exists, audit it against that distinction before
executing.

Hand the instrument to `superpowers:writing-plans` as its own plan with
nothing else in it, then execute it alone. It is the measuring device, not a
fix; batched with fixes, the fixes get written blind.

**Then re-triage.** Easy to forget and where most of the value lands. Bugs
tiered `investigate` only because no fixture existed usually become
`standard` once one does. Genuinely environment-dependent bugs stay blocked
and go in a separate later plan with an explicit precondition naming the
capture they need. Do not assume the original triage still holds: it was
made without the instrument.

## Phase 3: decide

Read `references/decisions.md` for the two modes, the question format, and
gate semantics. The short version:

**Default is chat.** Ask each design question directly in this
conversation, batched as one numbered list per stop rather than one
interruption per bug. For each question give a one-sentence framing, two or
three concrete options with tradeoffs, and your recommendation. Add a
concrete example (an actual string, an actual number, an actual screen) to
an option only where the option name doesn't already make the result
obvious — see `references/decisions.md` for the line between the two. A
yes/no toggle doesn't need one; a copy or formatting choice usually does.
Merge bugs that share an underlying decision into one question. Then stop
and wait for
the user's reply in chat before planning any task that depends on it. Once
answered, record each resolved question and its answer in `bugs/triage.md`
against the bugs it resolves, so the decision persists past this session
even though it was never written to a standalone file.

**Ask every open question, not a sample of them.** Before stopping, count
the `design`-tier and merged-question entries in `bugs/triage.md` and
confirm the numbered list you're about to send has exactly that many items
(after merging). A batch of 20 bugs needing 14 distinct decisions gets a
list of 14, not "the main ones" or "a few examples." There is no soft cap
on question count in chat mode: a long numbered list the user answers once
is strictly better than a short one that silently defers questions to a
later message, because deferred-and-unstated is indistinguishable from
forgotten. If the list is genuinely long, group by shared theme within the
same message rather than dropping items — headings inside the one message
are fine, splitting across multiple stops is not.

**File mode is opt-in.** Use it only if the user asks for it for this run
(e.g. "put the decisions in a file", "batch these into a file this time")
or `bugs/STATE.md` already records `decision_mode: file` from an earlier
turn in this same bug-fixing run. In file mode, write `bugs/decisions.md`
in the format the reference describes, then stop; the user answers inline,
asynchronously, at their own pace. Once a run is in file mode, stay in it:
set `decision_mode: file` in `bugs/STATE.md` so a later resume doesn't
silently switch back to asking in chat mid-run. Don't ask which mode to use
unprompted; chat is the default and needs no announcement, file mode only
happens on request.

Do not run `superpowers:brainstorming` once per design-tier bug in either
mode. That is one context switch per bug, and most of those questions are
the same question wearing different clothes. Reach for
`superpowers:brainstorming` only when the option list turns out to be wrong or
incomplete, not to generate it.

Two gate rules, same in both modes:

- An unanswered question blocks **only its dependent tasks**, never the
  whole batch. Exclude those, name them, carry on.
- Any user-facing string must be settled, verbatim, before its task is
  planned — recorded in chat and copied into the plan, or in
  `bugs/decisions.md` in file mode.

## Phase 4: execute

Read `references/execution.md`. It covers only what Superpowers does not:
which bugs enter a batch, how big a batch is, how many of a batch's tasks
run concurrently on your local toolchain, what tier each task gets, and the
three extra worker rules this workflow needs.

Dispatch waves within a batch back to back automatically; a clean wave
rolls straight into the next without asking. Only stop mid-batch when a
wave trips one of the stop conditions in the reference (too few tasks,
repeated `MISSING_STRING`/`NO_REPRO`/`MISTIERED`, or a failure that
survives isolated retry). Otherwise keep going until the batch is done.

Everything else is `superpowers:writing-plans` then
`superpowers:subagent-driven-development`, unmodified. Their dispatch
templates already require a model per worker, their reviewers already take a
diff range, their fix loop already bounds itself and escalates. Do not
restate any of that in the plan.

## Phase 5: close

Reconcile every bug in `bugs/raw-list.md` into exactly one state: merged,
deferred to a named batch, blocked on a named instrument or decision, or
closed as not-a-bug with a reason. Report counts and what the next batch
would hold.

Fold `bugs/found-during-fix.md` back into `bugs/raw-list.md` as new numbered
items so adjacent problems go through the same pipeline rather than
accumulating in a side file nobody reads.

## Failure modes

**"Nothing was fixed."** Three causes, check in order: a planning phase ran
but no execution phase; the batch was empty because everything was gated; or
workers hit `NO_REPRO` across the board. The third means Phase 2 was
skipped.

**A batch under four tasks.** Something is gating harder than expected. Say
what, rather than executing a trivial batch.

**Re-triaging on resume.** Expensive, and it discards the user's decisions.
Read the state file first, always.

**Asking design questions one at a time instead of batching.** Defeats the
point even in chat mode. Gather every open question for the current phase
before stopping, ask them together as one numbered list, and only then wait.

**Asking only some of the open questions.** Just as bad as asking one at a
time, and easier to do by accident: it looks like helpful brevity in the
moment and costs a second round-trip once the user notices bugs 9 through
20 never got a question. Cross-check the numbered list against every
`design`-tier bug in `bugs/triage.md` before sending it. A count mismatch
means questions were dropped, not that the list is appropriately concise.
