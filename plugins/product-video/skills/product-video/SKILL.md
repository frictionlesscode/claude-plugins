---
name: product-video
description: Turn an app's real screen recordings and screenshots into a short (15-30 s), high-impact launch-style product video built with Remotion and FFmpeg, in 16:9 and/or 9:16, with animated device framing, camera pushes, spotlights, speed ramps and captions. Use whenever the user wants a product video, promo video, launch video, app trailer, hero video for an article or landing page, a Play Store / App Store preview video, or a social clip of their app, or says "make a video from these recordings", even if they don't mention Remotion.
---

# Product video

Act as an elite product video director, motion designer, editor and Remotion engineer.
Turn the project's assets into a short product video that communicates **one** product story
fast and makes the product feel premium, modern and desirable: closer to an Apple / Linear
launch video than a screen-recording tutorial.

Optimize for impact, not completeness. One capability shown extremely well in 18 seconds beats
the whole app explained in 60.

## Ground rules

- Use the real product UI. Never fabricate, redraw, alter or AI-generate UI in a way that
  misrepresents the app. Freezes, speed changes, crops and overlays are fine; repainting is not.
- Captions claim only what the footage or the product's own copy supports. Store listings and
  READMEs are good sources for the hook line and for which features are real.
- Ask only what changes the work: where it will be used (article, store, social; decides the
  primary aspect ratio), voiceover or captions only, and any footage you can't find. Default
  the rest and say what you chose.

## Workflow

1. **Inspect every asset.** Recordings (ffprobe size, fps, duration; many phone recordings are
   variable frame rate), screenshots, store assets, icons, brand colours and fonts from the app
   source (theme files, font resources), and store-listing copy. Make a timestamped contact
   sheet of each recording (`fps=1,drawtext=%{pts\:hms},tile`) to learn what happens when.
   Extract full-res frames of key moments, one ffmpeg call per frame (a single call with
   several `-ss` inputs maps the first input to every output), over a 100 px grid so you can
   measure element positions as fractions of the screen.
2. **Pick the story.** What does the product do, and what is the single most compelling
   outcome the footage can show? Look beyond the recording: framed store screenshots or
   screenshot-test renders often hold the strongest hook (e.g. the live screen the app exists
   for). Prefer the highest-resolution source; crop store frames off with exact pixel bounds.
3. **Storyboard and timing plan**, briefly, before code.
4. **Build the first complete cut** (start from `assets/remotion-starter/`, see below).
5. **Render, then review frames** throughout: readability, caption placement, UI fidelity,
   awkward crops, black frames, timing, hierarchy, transition quality, smoothness, branding.
   Fix what you find and render again. Expect 2-3 passes.

## Creative approach

Rhythm to aim for (don't force it if the assets suggest better):

| Time | Beat |
|---|---|
| 0-2 s | Hook: outcome or visual surprise |
| 2-6 s | Establish the product and problem |
| 6-12 s | Rapid interaction showing the core feature |
| 12-17 s | Payoff / result |
| 17-22 s | One or two rapid supporting capabilities |
| last 2-3 s | Brand / logo + concise CTA |

- Start with the outcome, not the mechanics. Show only the screens the story needs; cut hard.
- Speed up scrolling, typing, loading, menus and navigation (about 1.5x-6x). Hold important
  results about 0.75-1.5 s.
- Scenes mostly 1-3 s. Motion transitions about 180-400 ms on springs or natural easing,
  never linear. Keep something moving without being frantic.
- **Zoom only where the UI is too small to read** (typically the payoff number or a dense
  stat). Everywhere else direct attention with other tools so the camera isn't doing the same
  thing every scene: spotlights (dim the screen, ring the element), 3D tilt entrances and
  drifts, speed ramps, freeze frames, crossfades with a slight settle, tap indicators where a
  tap matters. Avoid gimmicky or excessive transitions.
- **Push the device, not the pixels.** When you do zoom, scale the whole phone and let it
  overflow the canvas. Zooming inside the screen crops edge-to-edge rows (mobile UIs are full
  width) and upscales low-res footage. Keep one device on screen for the whole video and swap
  only its screen content, so the eye never has to find it again.
- Reframe per aspect ratio rather than cropping one layout: 16:9 puts captions left and the
  phone right; 9:16 puts captions on top and the phone below, and the phone should only grow
  downward when pushed so it never slides under the captions.

## Copy

Very little text; the video must work muted. Captions about 3-8 words, stating benefits or
results, not actions ("0:28 ahead. Goal made.", not "Tap Finish"). Highlight the key number
or benefit in the accent colour. Set line breaks by hand so nothing is orphaned. No filler
("revolutionary", "game-changing", "next-generation").

## Audio

Skip audio entirely if the video will autoplay muted (article heroes, most web embeds) and
say so. Otherwise:
- Write an extremely concise voiceover only if it helps; it complements the screen rather
  than narrating it. Generate it with OpenAI TTS if credentials are available.
- Add understated sound design: tap, soft impact, whoosh, success.
- Duck any music under narration.

## Implementation (Remotion + FFmpeg)

`assets/remotion-starter/` is a working project from a shipped video (RuckPace). Copy it
into the target repo (e.g. `video/`), `npm install`, then edit:

- `src/brand.ts`: the reusable config: brand colours (take them from the app theme), fonts
  (load the app's own font files from `public/fonts`), device style, caption style,
  transition and motion defaults. Replace the RuckPace values.
- `src/components.tsx`: `Background`, `Device`, `RemappedVideo`, `Still`, `cameraAt`
  (push and 3D tilt), `Highlight` (spotlight), `ScreenIn` (crossfade + settle), `Caption`
  (`*accent*` words, `\n` line breaks, staggered spring-in), `EndCard`. These are generic.
- `src/Promo.tsx`: the storyboard as data (`SCENES`): per scene, frames, screen, camera
  shots, spotlights (rect as screen fractions) and captions. A new video is mostly a new
  array.
- `src/Root.tsx`: Landscape 1920x1080 and Portrait 1080x1920 compositions of the same
  component.

Notes that cost time once:
- Transcode recordings to constant 30 fps first (`-vf fps=30 -c:v libx264 -crf 16 -g 15`),
  cropped to even dimensions, audio stripped.
- `RemappedVideo` takes `[outputFrame, sourceSeconds]` keys and renders through
  `<Freeze>` + `<OffthreadVideo>`: flat segments are freeze frames, steep ones are speed
  ramps. Exact in renders; scrubbing in Studio can be choppy.
- Check where a screen actually appears in the source: starting a scene a few tenths of a
  second early flashes the previous screen.
- Rendering over an MP4 that a media player has open fails on Windows (EPERM on rename).
  Render to a new name instead.
- Files written by Python in text mode on Windows get CRLF line endings; strip `\r` before
  tsc. Set tsconfig `target` to ES2023 or later for `findLastIndex` / `.at()`.
- Review renders with contact sheets:
  `ffmpeg -i out.mp4 -vf "select='eq(n\,30)+eq(n\,90)+...',scale=640:-2,tile=4x3" -frames:v 1 -fps_mode vfr sheet.png`.
- `npm run render` renders both aspect ratios at `--crf 18`.

## Deliverables

1. Final MP4(s): 16:9 and/or 9:16 as the use case needs.
2. Remotion source, committed (keep `node_modules/` and `out/` ignored).
3. A short storyboard/timeline: each scene and its duration (the project README is a good home).
4. Any generated voiceover/audio assets.
5. A brief description of the creative choices.
6. The reusable config file (`src/brand.ts`): brand colours, fonts, device style, caption
   style, transition style, animation defaults.

When the video is for a web article, also export a poster JPG from a frame where the hook
caption and UI are fully on screen, and embed it the way the site already embeds hero video
(autoplay muted loop playsinline, with an aria-label describing the tour).
