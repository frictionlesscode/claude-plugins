# Execution reference

This covers only the decisions Superpowers does not make for you. Plan
format, dispatch, review, and the fix loop belong to
`superpowers:writing-plans` and `superpowers:subagent-driven-development`.
Do not restate their rules in a plan preamble: duplicated rules drift out of
sync when the plugin updates, and the plugin's copy is the one that runs.

## What Superpowers already handles

Assume these and do not re-specify them:

- Plan file structure and task decomposition.
- The implement, review, fix loop with two-stage review.
- Per-worker model on every dispatch. Its templates mark `model` as
  required and warn that an omitted model silently inherits the session's
  most expensive one.
- Diff ranges to reviewers, so they read a scoped diff instead of crawling
  the repo.
- Bounded fix rounds, escalation to a stronger model on later rounds, and
  one fix subagent for the final whole-branch review rather than one per
  finding.
- Failing test before implementation.

Your job is to decide what goes in, at what tier, and to add three rules
Superpowers has no way to know about.

## Batch selection

A bug enters a batch plan only if all hold:

- tier is `mechanical` or `standard`
- `blocked_on` is NONE
- it references no unanswered decision — check `bugs/triage.md`'s
  `decision_answer` field in chat mode, or `bugs/decisions.md`'s `Answer:`
  field in file mode

Cap the batch around 10-12 tasks. Hold the rest and say which.

Batches exist for reasons beyond cost. One stuck task in a long serialized
run blocks everything behind it. And each merged batch teaches you something
that should change the tiering of the next one, which cannot happen if
everything is planned at once.

Group so no two tasks in a batch touch the same file **or the same shared
resource** — a localization/strings file, a DI registration module, a
shared test fixture, a build config file. "No file overlap" alone misses
these: two tasks can pass a file-level check and still collide by both
editing the strings table or both registering into the same container.
State each task's file set *and* any shared resource it touches so the
constraint is checkable rather than asserted.

Bugs sharing a root cause become one task. Fix the shared path once, then
assert corrected behaviour at each call site.

## Concurrency within a batch

Batch size and how many of those tasks run *at the same time* are separate
knobs. A 10-12 task batch dispatched all at once on a shared local
toolchain — one emulator or simulator, one build cache, one Gradle or
MSBuild daemon — produces contention, not parallelism: workers stall on
each other's build locks, steal each other's ports, and a flaky failure
caused by contention gets treated as a real fix-loop failure. That's wasted
review-fix cycles that have nothing to do with the code being wrong.

Default wave size is **2 concurrent workers** when the project builds and
tests locally with a single shared toolchain (a mobile app with one
emulator/simulator, a monorepo with one shared dev server, anything where
two builds fighting for the same lock is plausible). Raise it only when the
project's build/test setup is confirmed isolated per-worker — containerized
or otherwise sandboxed builds, no shared emulator or daemon — in which case
size the wave to that isolation, not to the batch cap.

Waves within a batch run automatically, one after the next, without
stopping for confirmation between them. A wave completing cleanly is not a
decision point: dispatch the next wave immediately. Only stop mid-batch for
one of the Stop conditions below — a wave finishing does not itself need
sign-off, only a wave that trips one of those conditions does. The batch
cap (10-12) still bounds total tasks; the wave size only bounds how many of
that batch's tasks are in flight on the local toolchain simultaneously.

If a task's fix-loop failure looks environment-shaped rather than
code-shaped — a build timeout, a port conflict, a flaky failure that passes
on retry with no code change — do not count it toward the `MISTIERED` or
stop-condition thresholds below on the first occurrence. Retry it alone,
outside the wave. Only escalate if it fails again in isolation, since that
rules out contention as the cause.

## Tier to model

Superpowers requires a model per dispatch and gives per-role guidance. You
supply the mapping for these tasks:

| Task tier | Implementer |
|---|---|
| mechanical | cheapest capable |
| standard | mid |

Reviewers follow the Superpowers roles as written: spec compliance is a
mechanical diff-scoped comparison and takes the cheapest capable model, code
quality needs judgment and takes mid, the final whole-branch review takes
the most capable.

Write the tier into the task itself so dispatch does not re-derive it from
prose.

## Three extra worker rules

Add only these to the plan preamble. They are workflow-specific and
Superpowers cannot infer them.

- **Strings.** Any user-facing string comes from the resolved decision
  (chat answer copied into the plan, or `bugs/decisions.md` verbatim in
  file mode). If the string you need was never settled, stop and report
  `MISSING_STRING`. Do not invent phrasing. Without this, a worker writes
  plausible copy and the decision the user made is quietly overwritten.
- **Frozen tier.** If the task is harder than tiered, stop and report
  `MISTIERED`. Do not escalate your own model. Self-escalation is how a
  cheap batch silently becomes an expensive one.
- **Scope.** Fix exactly this bug. Adjacent problems go to
  `bugs/found-during-fix.md`, unfixed. They re-enter through triage next
  round rather than expanding the current task.

`NO_REPRO` needs no restating: Superpowers already requires a failing test
first, so a worker will stop on its own. What matters is what *you* do with
it. A `NO_REPRO` is a signal back to Phase 2, not a task to retry.

## Stop conditions

Stop and report rather than proceeding when:

- The batch would hold fewer than four tasks. Something is gating harder
  than expected and the user should know what.
- Multiple workers return `MISSING_STRING`. The decision wasn't actually
  settled, in either mode. That is a short follow-up, not a re-plan.
- Multiple workers return `NO_REPRO`. Phase 2 was skipped or the instrument
  is insufficient.
- Multiple workers return `MISTIERED`. The triage was optimistic; re-triage
  the affected bugs before continuing.
- A task fails a second time in isolated retry after an environment-shaped
  failure (see above). At that point it's a real failure, not contention,
  and belongs in front of the user like any other.

None of these fire just because a wave finished; they fire on what a wave's
results actually show. A clean wave always rolls straight into the next
one. Each stop condition is cheap to fix at the point of detection and
expensive to discover after a merge.

## After the batch

Reconcile every bug in `bugs/raw-list.md` into exactly one state: merged,
deferred to a named batch, blocked on a named instrument or decision, or
closed as not-a-bug with a reason. Report counts.

Fold `bugs/found-during-fix.md` into `bugs/raw-list.md` as new numbered
items so they go through the same pipeline next time.
