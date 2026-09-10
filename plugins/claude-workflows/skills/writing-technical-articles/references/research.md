# Research reference

## The conventions

Two markers carry the whole anti-confabulation discipline. Both are
grep-findable on purpose.

### Stubs

```
[[STUB: what is missing | Q: the question for the author | TRY: where to look]]
```

Written whenever an agent does not know something. It writes the marker and
keeps going; it never fills the gap with plausible text.

The `Q:` field is required. A stub without a question is a note to nobody,
and the review loop enumerates stubs by their questions. Write the question
as the author would need to hear it, not as a placeholder.

The `TRY:` field is optional and often the most useful part. "TRY: the
migration commit around March" turns a question into something an agent can
resolve next round without bothering the author at all.

Examples:

```
[[STUB: the actual p99 before the change | Q: do you have the dashboard
number, or should we cut the specific figure? | TRY: grafana export in
notes/, or the incident doc]]

[[STUB: why Room over SQLDelight | Q: was this a considered decision or
inherited? | TRY: ADR directory, or the commit that added the dependency]]
```

### Source anchors

```
[[SRC: app/src/main/PaceCalculator.kt:112]]
[[SRC: commit a1b2c3d]]
[[SRC: https://example.com/doc]]
[[SRC: evidence/ruckpace-repo.md#gps-pipeline]]
```

Every specific technical claim carries one: numbers, versions, file names,
API behaviour, configuration, timings, error text.

**The rule that matters:** a claim with no anchor and no evidence backing it
becomes a `[[STUB:]]` instead. Not a hedge, not a softened version of the
claim. A stub. This is the equivalent of a failing test before a fix: it
gives "grounded" a mechanical definition instead of a vibe, and it is what
lets a cheap model draft safely.

Anchors are stripped at publish. They exist for the author's verification
pass, not the reader.

## Mining repos

Dispatch read-only subagents, one per repo, on a cheap model, in parallel.
Where the harness has a built-in read-only exploration agent, use it; it is
already denied write access, which is what you want.

Brief them to extract, into `evidence/<source>.md`:

- The actual shape of the thing being written about: real paths, real type
  and function names, real structure.
- Configuration and versions as they actually appear in the files.
- Commits and PRs that mark the decisions the article discusses, with
  hashes and dates. Commit messages and PR descriptions are frequently the
  best prose source available, because the author wrote them at the time
  with the context fresh.
- Real error messages, log lines, test names.
- Numbers only where the repo genuinely contains them. An agent that infers
  a benchmark is worse than one that records a gap.

They do not write prose and do not draw conclusions. They retrieve.

Everything they could not find goes in a `## Gaps` section at the bottom of
the evidence file. Those gaps become stubs during drafting, which is exactly
where they should surface.

## Mining prior conversations and notes

What is possible depends on the harness, and it is worth being straight
about which one you are in rather than implying access you do not have.

**With past-conversation search available** (the chat surfaces), search on
distinctive content nouns from the article topic: the project name, the
technology, the specific problem. Extract the author's own words in
particular. How they explained something in conversation is usually closer
to their voice than anything an agent will generate, and reusable directly.

**Without it** (Claude Code), this means files: exported conversations, a
notes directory, prior drafts, talk slides, long PR descriptions, the
repo's own docs. Ask the author to point at a directory and mine it the same
way as a repo.

Either way, distinguish carefully in the evidence file between something the
author asserted and something an assistant suggested to them. A past
suggestion that was never acted on, quoted in an article as a decision, is a
factual error with the author's name on it.

## Evidence file format

```markdown
# Evidence: <source name>
Gathered: <date> | Source: <path or url>

## <topic matching an outline section>
- <specific fact> [[SRC: anchor]]
- <specific fact> [[SRC: anchor]]

## Quotable
Verbatim commit messages, comments, or the author's own phrasing that
could be used directly or adapted.

## Gaps
- <what was looked for and not found, and where else it might live>
```

Organise by outline section where possible. A drafting agent receives only
the evidence its brief allows, so evidence organised by topic is far more
usable than a flat dump.

## What a drafting agent may assume

Nothing not in its evidence files, its brief, or the voice spec.

General technical knowledge is fine: how a protocol works, what a pattern
is called, why an approach is common. What is never fine is a specific
claim about *this* author's *this* project that is not in evidence.

The line is: writing "adaptive icons crop to a centre region" needs no
anchor. Writing "we set the safe zone to 29dp" needs one, or it is a stub.
