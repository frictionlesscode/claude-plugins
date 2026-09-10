---
description: Triage, decide, instrument and fix a backlog of raw bug reports in cost-tiered Superpowers batches. Asks open design questions in chat by default; resumes from wherever the work stopped.
---

Use the `fixing-raw-bugs` skill.

This skill is a layer on top of Superpowers. Confirm the Superpowers skills
are reachable first. If they are not, stop and tell me rather than
hand-rolling plans and dispatch.

Read `bugs/STATE.md` and resume from the phase it names, including whatever
`decision_mode` it recorded. If it does not exist, infer the phase from
which of `bugs/raw-list.md`, `bugs/triage.md`, `bugs/decisions.md` and
`plans/` are present, write `bugs/STATE.md`, and continue from there.

Before doing any work, tell me in one line which phase you are entering and
why. I need to know whether this run gathers evidence or changes code.

$ARGUMENTS

If arguments are present, treat them as one of: the raw bug list to intake,
an instruction about scope (a specific batch or bug id), or a request to
use file mode for decisions this run ("put decisions in a file",
"batch these into a file"). Absent an explicit request for file mode,
ask any open design questions directly here in chat, batched as one
numbered list, rather than writing `bugs/decisions.md`. If arguments are
otherwise absent, continue the existing work.

Stop at the end of the phase. Do not roll into the next one without telling
me what it would cost.
