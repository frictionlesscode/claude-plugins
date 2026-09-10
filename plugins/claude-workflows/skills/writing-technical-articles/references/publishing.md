# Publishing reference

Only reachable when the author says they are happy. Do not offer it as a way
to end a round.

## Preflight, both targets

Refuse to publish and list what is wrong if any of these fail:

1. **No unresolved stubs.** `grep -c '\[\[STUB:' draft.md` returns 0.
   Publishing with a stub means shipping a visible placeholder, so this is a
   hard stop rather than a warning.
2. **Anchors verified, then stripped.** Before removing `[[SRC:]]` markers,
   the author should have had a chance to spot-check them. Offer a
   verification listing: every anchored claim with its source, so they can
   scan it once. Then strip all anchors from the published copy and keep
   the anchored version at `draft.md` as the working source.
3. **Unify pass run over the whole document**, not just the sections touched
   in the last round.
4. **Links resolve.** Check external URLs still respond.
5. **Code blocks are tagged** with a language and, where they came from a
   repo, actually match what is there.

## Site configuration

On first run, ask once and cache to `~/.claude/voice/site-config.md`:

- GitHub owner and repository for the site.
- Generator: Jekyll, Hugo, Astro, or plain HTML. This determines the post
  path and front matter shape, and guessing it wrong produces a PR that
  silently does not build.
- Post directory, working it out from the repo rather than assuming.
  Jekyll uses `_posts/YYYY-MM-DD-slug.md`, Hugo `content/posts/slug.md`,
  Astro `src/content/blog/slug.md`.
- Which front matter fields the existing posts carry. Copy the shape from a
  real recent post in the repo instead of writing a generic block: sites
  accumulate custom fields, and a post missing one may not render.
- Default branch, and whether the site builds from it or from a build
  branch.

Reading an existing post is worth more than any of these questions. Do that
first and ask only about what it does not answer.

## Artifact target

For reading and sharing without touching the repo. Render the stripped
markdown to a self-contained HTML artifact with reasonable typography:
constrained measure, readable line height, syntax-highlighted code blocks.

Use this when the author wants to read it as a reader would, or send it to
someone for comment. It is the right default for a first look, since the
repo target implies a commit.

## GitHub Pages target

Generate the file at the correct path with front matter matching existing
posts, then:

- **Open a PR. Do not push to the default branch.** A personal site is
  still a live site, and a preview build is the last real check.
- Report the branch and PR URL.
- Say what the built URL will be once merged, derived from the site's
  permalink pattern rather than guessed.

If the repo has a local preview command in its README or package.json, offer
to run it and report the local URL so the author can see it rendered before
merging.

Images and assets: if the article references any, place them where the
generator expects and use the path form the existing posts use. Relative
paths that work locally and break on the built site are a common failure,
and copying an existing post's convention avoids it.

## After publishing

Update `STATE.md` to record where it went and the PR or artifact reference.

Ask whether anything learned in this article should be folded back into the
voice spec. A finished piece the author is happy with is the best available
evidence of how they actually write, and the spec improves fastest right
after a successful one.
