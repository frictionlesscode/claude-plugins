---
name: codex-graphic
description: Use when an article, README, landing page or social post needs a graphic (illustration, hero image, concept art, chart, diagram, social card) and the user wants OpenAI to make it, mentions Codex, gpt-image or ChatGPT images, or says OpenAI is better at graphics, while Claude keeps the brief and the final check.
---

# Codex graphic

Claude directs, Codex draws. Claude owns the brief, the facts and the final check. Codex
(OpenAI's CLI, signed in with a ChatGPT plan, so no API key and no per-image bill) makes the
image. Nothing Codex returns ships until Claude has looked at it.

## Pick the route first

| The graphic | Route |
|---|---|
| Illustration, hero, concept art, social background: no text a reader has to trust | **Image.** Codex generates a PNG. |
| Chart, diagram, org chart, anything with numbers, labels, code or UI | **HTML.** Codex designs one self-contained HTML page; Claude renders it to PNG. Image models misspell words and drift numbers. |
| The product's own screens | Neither. Use real screenshots; never generate UI. |

Both: pass `-i` reference images (the old version, the site's style, a sketch).

## Preflight

- `codex login status` says "Logged in using ChatGPT". If not, ask the user to run `! codex login`.
- `codex features list | grep image_generation` shows `true` (image route only).

## The brief

Write `brief.md` in a fresh scratch folder. Its parts, in order:

1. **Job:** where it appears and what a reader gets in one glance.
2. **Text:** every word, verbatim, then "No other text." (Image route: ideally none.)
3. **Facts:** every number with its source, then "Do not invent data."
4. **Format:** pixel size, file name. HTML route: one `graphic.html`, inline CSS, no scripts or network requests, root element sized exactly to the render size.
5. **Style:** palette as hex, font, background, how busy (prefer one idea, lots of space).
6. **Avoid:** what this graphic must not show (logos, people, fake UI, clutter).

## Run

```bash
W="<scratch>/codex-graphic-<name>"; mkdir -p "$W"; cd "$W"
codex exec -m <model> --skip-git-repo-check -s workspace-write -C "$W" \
  -i ref.png -o last.txt "$(cat brief.md)" < /dev/null > run.log 2>&1
grep -m1 "session id:" run.log
```

- `< /dev/null` is required: without it `exec` waits on stdin.
- A run takes 1-5 minutes. Give the shell call a 10-minute timeout.
- **Model:** if `run.log` says `model_not_found` or "not supported when using Codex with a ChatGPT
  account", run `codex debug models`, pick a slug whose `"visibility"` is `"list"`, and pass it
  with `-m`. Don't edit the user's `~/.codex/config.toml`.
- Raw generations also land in `~/.codex/generated_images/<session>/`.

HTML route, render it yourself (any Chromium):

```bash
chrome --headless=new --hide-scrollbars --force-device-scale-factor=2 \
  --window-size=<w>,<h> --screenshot=graphic.png "file:///$W/graphic.html"
```

## Review every round

Open the PNG and check it against the brief:

- Every word present, spelled right, nothing extra.
- Every number matches its source.
- Nothing implies a feature, product, person or brand that isn't real.
- Readable at the size it displays (a phone is about 360 px wide).
- Right size and aspect.

Send fixes to the same session, naming each problem exactly ("the label reads 81%, it must read 87%"):

```bash
rm -f last.txt
codex exec resume <session-id> -m <model> --skip-git-repo-check -o last.txt "<fixes>" \n  < /dev/null >> run.log 2>&1 || tail -5 run.log
```

`resume` needs `--skip-git-repo-check` too (it has no `-C`), and a failed run leaves the old
`last.txt` behind, so delete it first and check the exit code.

Three rounds, then change approach: if a raster's text is still wrong, ask Codex for the art
with no text and set the text in HTML on top.

## Deliver

Copy the final file into the site's image folder, write alt text that says what it shows
(numbers included), and show the user. Keep `brief.md` and any `graphic.html` with the
site's other visual sources so the graphic can be regenerated.

## Common mistakes

| Mistake | Fix |
|---|---|
| Charts through image generation | HTML route. |
| Brief says "a chart of the bill" | Give exact text and numbers. |
| Shipping without opening the image | Review every round. |
| Hanging `codex exec` | Add `< /dev/null`. |
| Trusting `last.txt` after a failed `resume` | Delete it first; check the exit code. |
| Editing the user's Codex config to fix the model | Pass `-m`. |
