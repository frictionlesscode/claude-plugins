# Decisions reference

## Two modes, one default

Design questions arrive in a clump after triage and after any instrument
re-triage. They need to reach the user in a batch, not one interruption per
bug, but *where* they land is a separate choice from *that* they're batched.

**Chat is the default and needs no announcement.** Ask the whole batch of
open questions as one numbered list, right in the conversation, and wait
for the reply there. Most runs are a single sitting: the user is present,
the questions are fresh, and a reply typed back into chat is faster than
opening a file, editing it, and saying "done."

**File mode exists for the case chat doesn't fit:** a long backlog the user
wants to answer over several days, asynchronously, without holding the
session open. Use it only when the user asks for it, or when
`bugs/STATE.md` already says `decision_mode: file` from earlier in the same
run. Don't offer the choice by default and don't ask which the user prefers
unless they bring it up; silently defaulting to chat is the point.

Once a run is in file mode, stay in file mode for the rest of that run's
decisions. Switching mid-run means some answers live in chat history and
some live in a file, and nothing after Phase 3 knows to check both.

## Format, either mode

Same content either way, just a different destination.

```markdown
### D1: <the question in one sentence>

Resolves bugs: 4, 7, 10

**Option A — <name>**
What it means. What it costs. What it makes harder later.
Example: <concrete instance of this option, see below for when>

**Option B — <name>**
...

**Recommendation:** A, because <reason>.
```

Merge questions that share an underlying decision. If three bugs all hinge
on the same definition, that is one question resolving three bugs, not
three questions.

### When to add an example

Add a concrete example per option when the option names alone could map to
more than one real result — the usual case for copy, formatting, unit
display, or anything a user will actually see or hear. "Show elapsed time
as a countdown" is not decidable from the name; "Option A: countdown —
`3:59 remaining`" is. Pick the example from the bug's own data or repro
where you have it (an actual value, an actual string, an actual screen)
rather than inventing a generic placeholder — a real number from the report
is more informative than "e.g. some value" and costs nothing extra to
include.

Skip the example when the option name already is the decision: a binary
toggle, an on/off default, a numeric threshold with no formatting question
attached, a choice between two named library behaviours the user already
knows. "Option A: retry once, Option B: retry three times" needs no
example; adding one there is filler that makes a fast question slower to
read. The test is whether a reasonable person could pick correctly from the
option name and one line of cost/benefit alone — if so, no example; if two
people could read the same option name and picture different results, add
one.

This applies per-option within a question, not per-question: a single
`D`-block can have an example on the option where it disambiguates
something and no example on the option where the name is already the full
answer.

**Chat mode:** present the numbered list of `D`-blocks as your message and
stop; do not create a file. Include every `D`-block from this phase in that
one message, however many there are: 3 or 30, the list is not summarized,
sampled, or trimmed to "the important ones" for length. A large list is
better organized with sub-headings by theme (e.g. "Unit display", "Error
copy") than shortened. When the user answers, write each answer back into
`bugs/triage.md` next to the bugs it resolves (`decision_answer:`), so the
resolution is durable without a standalone decisions file.

**File mode:** write the blocks into `bugs/decisions.md`, each with a
trailing empty `**Answer:**` field, and stop. That empty field is the gate:
a question with an empty answer is unresolved, anything else counts as
answered. The user edits the file inline, asynchronously; you re-read it on
the next run to see what's been filled in.

## Questions that need their strings written out

When a decision determines what a user sees or hears, the decision is not
finished until the literal strings exist. Not a description of the string:
the string. This holds in both modes; a string agreed verbally in chat is
just as final as one written into a file, so get it typed out completely
before treating the question as resolved.

For anything with modes, units, or locales, write the full matrix. Every
combination of mode and unit gets a row. Gaps in that matrix are what
produce `MISSING_STRING` stops later, and they are cheap to fill now and
expensive to discover mid-batch.

Include a do-not-say list where the original bug was bad phrasing. Naming
the specific failure ("no vague quantifiers") is more useful to a worker
than a general instruction to write clearly.

Every string that expresses a comparison must name its own frame of
reference. "Behind" is ambiguous across an interval, a session, and a
target; a user cannot tell which one they are hearing, and neither can a
worker implementing it.

## Gate semantics

An unanswered question blocks only the tasks that depend on it, regardless
of mode.

At planning time, for each candidate task, check whether it references an
unanswered decision. If it does, exclude that task and name it in the
excluded list. If it does not, plan it.

Never stall a whole batch on one open question. The mechanical bugs that
have nothing to do with it can ship today.

Tell the user explicitly which tasks were excluded and which decision would
unblock them. That converts "the batch is small" into "answering D2
unblocks four more tasks," which is actionable.

## When to actually brainstorm

Write the options first. Reach for `superpowers:brainstorming` only when the
option list turns out to be wrong or incomplete, not to generate it.

Generating options is cheap and mechanical; judging between them is the
part that needs the user. Spending an interactive session producing a list
you could have written spends their attention on the wrong half. This is
true in either decision mode: brainstorm decides what the options are,
chat-vs-file only decides how the user picks among them.
