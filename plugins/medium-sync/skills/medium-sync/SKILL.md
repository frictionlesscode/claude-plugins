---
name: medium-sync
description: Copy new or updated articles from your own site (read from its RSS feed) to Medium as drafts, with your site as the canonical URL. Use when the user says "sync to medium", "post to medium", "cross-post", or "/medium-sync".
---

# Medium sync

Medium has no usable API for this. Drive it through Claude in Chrome, in the
user's own logged-in Chrome. Load the Chrome browser skill first.

**Never click Publish or "Save and publish".** Leave everything as a draft;
the user publishes.

## 0. First run: configure

The check script keeps its state outside the plugin, in `~/.medium-sync/`:

- `config.json`: `{"feed": "https://example.com/rss.xml"}`, the user's own
  site feed. If it is missing, ask the user for their feed URL and write it.
- `published.json`: which site URLs have been synced, to which Medium story,
  with a hash of the article body. The script writes it; never hand-edit it.

## 1. Find work

```
python "${CLAUDE_PLUGIN_ROOT}/skills/medium-sync/check.py"
```

Prints `new` and `changed` posts. Show the list to the user and confirm
which to do. Do at most about three imports per session (Medium rate-limits).

## 2. New post

1. Open `https://medium.com/p/import`, paste the post URL, click Import.
2. In the draft, verify:
   - **Canonical link:** ⋯ menu → More settings → Advanced Settings (collapsed, expand it) → "Customize Canonical Link" shows the post URL. Import sets it automatically; if not, set it. Use screenshots there; JS reads of that page get blocked.
   - **Code blocks:** compare `<pre>`/`<img>`/`<table>` counts in the source `<article>` with the draft. Import drops `<pre>` code blocks: re-add each by putting the caret at the end of the preceding paragraph, Return, type ``` then the code (shift+Return between lines).
   - **Site chrome:** import often pulls in the site's logo image or a section label under the title. Delete them (click the figure, Delete). If the article has a lead GIF or image, that goes there instead.
   - **Images:** the file must be live on the user's site (GitHub raw and jsDelivr URLs fail). Put the caret in an empty paragraph and dispatch a synthetic `paste` ClipboardEvent whose DataTransfer has `text/html` = `<img src="LIVE_URL" alt="...">`; Medium re-hosts it (GIFs stay animated). Then Backspace the leftover empty paragraph above the figure.
   - **Video:** a `<video>` (mp4) never imports; Medium only takes GIFs. Make one: `ffmpeg -i X.mp4 -vf "fps=15,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle" -loop 0 OUT.gif` (keep it under 10 MB) into a scratch directory. To upload a local file with no live URL: in an empty paragraph open the "+" menu, patch `HTMLInputElement.prototype.click` to stash file inputs instead of opening the picker, click the image button, find the file input and upload to it, then restore the original click. Set alt text from the video's `aria-label`.
   - **Tables** are dropped (Medium has none). Screenshot the live table (for example with Python Playwright: `page.locator("article table").first`, `device_scale_factor=2`, light scheme), upload it at the table's spot the same way as a GIF, and put the table's content in the alt text.
   - **Structure:** compare block order with the site. Import often leaves empty `<li>`s (blank numbers), empty H3s or blockquotes, and paragraphs out of order. Fix with real keystrokes, bottom-up: place the caret via a JS selection on the block, then send Backspace / ctrl+x / ctrl+v. An empty `<li>` takes two Backspaces (the first turns it into a `<p>`, the second joins the lists back up). To move a block: select it all, ctrl+x, Backspace, caret at the start of the block it should precede, Return, select the new empty block, ctrl+v.
   - **Subtitle:** make the article's description a subtitle: triple-click it, click the small "T" in the toolbar (ctrl+alt+2 types a literal "2"). The lead image goes after the subtitle.
3. Import already appends "Originally published at <site> on <date>." Don't add another footer.
4. Note the draft URL, then record it:
   `python "${CLAUDE_PLUGIN_ROOT}/skills/medium-sync/check.py" --record POST_URL MEDIUM_URL`
5. Story settings (`https://medium.com/p/ID/settings`); verify each by reloading the page:
   - **Reader Interests (5 topics):** click into the box by coordinates (clicking its ref doesn't focus it), type a topic, wait 2 s, zoom on the dropdown, press Return for the top suggestion. Map each feed tag to the closest real Medium topic, favoring ones with real readership (the dropdown shows counts). Watch for false friends: "Skills" means soft skills, so use "Claude Skills"; "Agents" becomes "AI Agent". Tell the user which topics you chose.
   - **SEO title:** the article title (Medium appends " | Medium").
   - **SEO description:** the post's description from the feed (import fills it from the first paragraph). Don't use ctrl+a in these fields: it can type a literal "a". Clear them with a triple-click, then check the saved value for stray characters.
6. Tell the user the draft URL and the topics you chose.

## 3. Changed post

Fetch the live article and the Medium story, diff the text, and show the user
the changed passages. Then by size:

- **Trivial** (typos, wording): suggest skipping; the canonical link sends search traffic to the site anyway. If skipped, still `--record` so it stops showing.
- **A few passages:** open the story's edit page, replace just those passages, and leave the unpublished changes for the user to "Save and publish".
- **Major rewrite:** import the URL again as a temporary draft, copy its body into the original story (which keeps its URL, claps and comments), keep the footer line, then tell the user to delete the temporary draft.

After the user confirms they saved it, run `--record` again to store the new hash.
