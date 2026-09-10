# Triage reference

## Evidence dispatch

Dispatch one read-only subagent per bug on the cheapest available model, in
parallel, in batches of 6-8. Give them a strict brief:

> Gather evidence only. Do not fix anything, do not edit any source file,
> do not draw conclusions about difficulty or priority. Report:
> does a deterministic repro exist; what exact steps or command reproduces
> it; which files are implicated with file:line where you can; does test
> coverage exist for that area; is the logic behind a unit-testable seam or
> tangled into UI, a service, or a framework callback.

Read-only exploration agents are the right tool here. Where the harness has
a built-in one it is usually already denied write access, which is what you
want: an evidence agent that starts fixing things is a cost leak and it
corrupts the triage.

The seam question drives cost more than bug complexity does. A trivial bug
behind a slow integration test is more expensive than a subtle one behind a
pure function.

## Schema

One block per bug in `bugs/triage.md`:

```
id / title
repro: deterministic | flaky | none
repro_steps:
suspected_site: <file:line>, or NONE
blast_radius: single-file | module | cross-cutting
coverage: yes | partial | none
testable_seam: yes | no
blocked_on: <instrument name>, <decision id>, or NONE
tier: mechanical | standard | investigate | design
why: one line citing the evidence above
open_question: required unless tier is mechanical
shared_cause_with: <bug ids>, or NONE
decision_answer: filled in once Phase 3 resolves this bug's question,
  whichever mode it was answered in
```

`why` must cite evidence, not impression. "Looks simple" is not a reason.
"Deterministic repro, single call site at Foo.kt:112, covered by existing
unit test" is.

## Tier rules

Apply literally. The point of literal rules is that they survive being
applied by a different model in a different session.

**mechanical** — all of:
- deterministic repro, and
- `suspected_site` names an actual file:line, and
- blast radius is single-file or module, and
- no API, schema, persisted-data or public-contract change.

**standard** — deterministic repro, but the fix spans a module, adds a
setting, touches persistence or migration, or needs a test written from
scratch.

**investigate** — no deterministic repro, or a repro exists but evidence
gathering could not localize a cause.

**design** — the fix needs a product decision, or two or more defensible
fixes exist with materially different tradeoffs.

Tie-breaks:
- Cannot cite a file:line → not mechanical.
- Between two tiers → take the higher one.
- Unknown → escalate.
- Never guess downward to reduce review load.

The asymmetry is deliberate. An over-tiered bug costs one model tier more
than it needed. A mistiered bug costs a full implement-review-fix loop, a
`MISTIERED` report, a re-plan, and the user's trust in the tiering.

## Investigate tier hands off

Do not root-cause `investigate`-tier bugs inline. Hand each to
`superpowers:systematic-debugging`, one subagent per bug on a capable model,
with a strict brief: investigate and report a cause, do not fix.

Fold the findings back into `bugs/triage.md` and re-tier. A bug with a
located cause is usually `standard` or `mechanical`; one that resists
investigation is usually blocked on an instrument, not on effort.

## Shared root causes

Before filing bugs independently, ask whether several symptoms trace to one
place. Look especially at bugs that touch the same preference, setting,
conversion, formatter or read path.

State the answer explicitly, with file:line, and set `shared_cause_with` on
every affected bug. Then in planning, fix the shared path once and let the
per-bug tasks assert corrected behaviour at each call site.

Five independent tickets for one bad read path is five times the review,
five chances to diverge, and four redundant fixes.

## Not-a-bug outcomes

Some reports are two correct behaviours being compared. Two different
numbers computed by two different valid definitions is a specification gap,
not a defect: tier it `design` and take it to Phase 3.

Say so plainly when it happens. Filing a definition gap as a bug produces a
worker that "fixes" one number to match the other and makes the product
worse.

## Re-triage after instrumentation

When Phase 2 merges an instrument, revisit every bug whose `testable_seam`
was `no` or whose `blocked_on` named that instrument.

Ask one question per bug: with the fixture and replay harness that now
exist, can a worker write a failing test for this without the original
environment?

- Yes → clear `blocked_on`, re-tier on the normal rules.
- No, because it needs conditions that cannot be authored honestly → it
  stays blocked, and it goes in a separate plan with an explicit
  precondition naming the capture it needs.

Do not hand-author a fixture that fakes the exact condition under
investigation. A fixture invented to match a theory will confirm that
theory and prove nothing.
