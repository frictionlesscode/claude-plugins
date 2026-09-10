# claude-plugins

Claude Code plugins from [frictionlesscode.com](https://frictionlesscode.com).
This repo is the `frictionlesscode` marketplace; each plugin lives under
`plugins/`.

## `claude-workflows`

Two Claude Code skills I use on my own projects. Both layer on top of
[Superpowers](https://github.com/obra/superpowers) and both refuse to run
without it rather than falling back to a worse version of what it already
does.

```
/plugin marketplace add frictionlesscode/claude-plugins
/plugin install claude-workflows@frictionlesscode
```

Superpowers first, if you do not already have it:

```
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

### `fixing-raw-bugs`

An intake layer for the pile that arrives before a plan exists. Superpowers
is excellent from `here is what I want built` onward and has no opinion on
twenty unsorted field reports, some of which are feature requests and some
of which cannot be reproduced at all with the tooling you have today.

The work is in three reference files:

- **`references/triage.md`** turns a pile into an ordered list. Cheap
  read-only agents fan out one per bug and report facts only, never
  conclusions, because a model that cheap asked how hard a bug is will
  guess low and sound certain. Tiering happens centrally afterward, nothing
  is `mechanical` without a `file:line`, and unknown escalates.
- **`references/decisions.md`** separates a code problem from a product
  problem. Design questions get asked in one batch, all of them rather than
  the two or three that look important, each with concrete options and a
  real example. Chat is the default; file mode is opt-in and sticky.
- **`references/execution.md`** is the part that saves money. Batch
  composition, waves that share a surface, local concurrency limits, and the
  tier-to-model mapping.

Use `/fix-raw-bugs`, or just describe a bug backlog and it triggers on its
own. It writes `bugs/STATE.md` and resumes from whatever phase that names,
so a second run continues rather than re-triaging.

**You will probably need to build an instrument first.** Superpowers will
not attempt a fix until a failing test exists, so any bug that needs
conditions you cannot summon at a desk comes back `NO_REPRO`. That is the
tooling working correctly and it stalls the run until you can replay the
condition on demand. For me that meant device logging plus a replay path.
For you it might mean an MCP server pointed at your log aggregation, or an
export-and-replay path for one real session. Build it alone, before the
fixes.

### `writing-technical-articles`

Long-form drafting for a personal site. Parallel section agents leave
grep-findable `[[STUB:]]` markers instead of inventing details, every
technical claim carries a `[[SRC:]]` anchor, and a single-author pass runs
afterward so a document written by many agents reads as one person.

`assets/michael-voice.md` is my own voice spec. It ships as a worked example
of what one looks like, not as a style you should adopt. Build your own from
samples of your writing.

Use `/write-article`.

### Verifying it works

1. Give `fixing-raw-bugs` a fresh list of 8 to 10 mixed bugs. It should stop
   after triage rather than fixing, and nothing should land in `mechanical`
   without a `file:line` in its reasoning.
2. Run it again immediately. It should resume at the next phase, not
   re-triage. Re-triaging is the main regression to watch for.
3. Give it a list where two or three bugs share one bad read path. It should
   say so and plan one task, not three.
4. Disable Superpowers and run it. It should refuse and name the install
   command rather than proceeding.
5. Give it a batch with two or three design-tier bugs. It should ask the
   questions in chat as one numbered list and wait, without creating
   `bugs/decisions.md`, unless you explicitly ask for file mode.

## Background

[AI Tools Want a Well-Formed Bug Report. I Have a Voice Memo.](https://frictionlesscode.com/writing/fixing-raw-bugs/)

## License

MIT
