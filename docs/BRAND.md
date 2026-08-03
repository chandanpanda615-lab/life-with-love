# Maati Katha — brand notes

This documents what the site already does. It is a reference for keeping new pages
consistent, not a rebrand. Everything here is defined once in the `:root` block of
`assets/site.css` — change it there, not in individual rules.

## Name

**Maati Katha.** *Maati* is soil, and also the place you are from. *Katha* is story.
The homepage explains this in the first note, so the name never needs a tagline
next to it.

Written as two words, both capitalised. Not "MaatiKatha", not all-caps in body text.

## Mark

A doorway standing on the ground, with the sun rising on its threshold.

- `assets/logo-mark.svg` — 24 viewBox, the drawing of record
- `assets/favicon.svg` — 32 viewBox, laterite tile, for browser tabs
- `assets/favicon-32.png`, `assets/apple-touch-icon.png` (180×180) — raster fallbacks
- The nav copy is inlined in `index.html` so its strokes inherit `currentColor` and
  flip with the theme. Keep the two `.frame` paths and the one `.sun` path in sync
  with `logo-mark.svg`.

Rules:

- **Clear space** — one jamb-width (about 1/5 of the mark) on all four sides.
- **Minimum size** — 20px on screen. Below that the arch fills in; use the favicon
  tile instead, which is drawn heavier for exactly this reason.
- **Do not** recolour the sun, stretch the mark, add a stroke to the sun, or place the
  open-stroke version on a busy photograph. Over imagery, use the laterite tile.

## Lockup

Mark + "Maati Katha" set in Cormorant Garamond 600, centred on the mark's optical
middle, gap `0.7rem`. That is `.brand-mark` in `index.html`. Below 560px the wordmark
is dropped and the mark stands alone.

## Colour

| Token | Value | Use |
|---|---|---|
| `--laterite` | `#8B3A1F` | accent in light theme, favicon tile, soil |
| `--turmeric` | `#C8842B` | accent in dark theme, the sun, primary button |
| `--sal` | `#2D3B26` | deep green, sparingly |
| `--ash` | `#E8E1D4` | text on dark, the status band surface in light theme |
| `--indigo` | `#1F2A3A` | `theme-color`, nav ground |
| `--band-bg` | `--ash` / `#241C15` | status band surface, flips with theme |

`--accent` is laterite in light and turmeric in dark — always use `--accent` rather
than naming a colour directly, so both themes stay correct.

The page declares `color-scheme: light dark`. Without it Chrome force-darkens the
page and strips the nav and hero gradients. Do not remove it.

## Type

| Token | Face | Use |
|---|---|---|
| `--font-display` | Cormorant Garamond 500/600 + italic | wordmark, headings, ledger figures |
| `--font-accent` | Caveat | eyebrows only |
| `--font-body` | `system-ui` stack | everything else |

The display faces live in `assets/fonts/` as real woff2 files, loaded by the
`@font-face` blocks at the top of `site.css` with `font-display: swap`. They were
base64-inlined until they were measured: at 192 KB they were 82% of a
render-blocking stylesheet, so nothing painted until every font byte arrived, and
`swap` could never fire because the bytes were inside the CSS itself. Splitting
them cut `site.css` from 234 KB to 42 KB. **Do not inline them again.**

**Nothing may be added to the stack without shipping the file** — `'Inter'` was
named there for a while with no font behind it, and every line of body text
silently fell back to `system-ui`.

Scale: `--text-sm` through `--text-hero`, all in the `:root` block. `--measure: 60ch`
caps line length; the hero lede is tighter at `46ch`.

## Structure

Three pages, deliberately. The site does not scroll through the whole project — the
homepage offers doors and you click into them.

| Page | Holds |
|---|---|
| `index.html` | hero, status band, the two door cards, manifesto — about 3 screens |
| `land.html` | the notes, the plain description of the land, the photographs |
| `visit.html` | how to reach, writing, the pilot enquiry |

All three share `assets/site.css`. Keep it that way: the CSS carries four embedded
base64 fonts, so inlining it per page would triple ~217 KB.

Each page sets its own backdrop with a body class (`bg-hero`, `bg-land`, `bg-road`).
There is no drawn canvas any more — every page sits on a real, darkened photograph.

**Image paths belong in `site.css`, not in inline styles, and not inside a custom
property.** A `url()` written in an ordinary declaration resolves against the
stylesheet, so the bare filename is correct in `site.css`. A `url()` carried inside a
*custom property* does not: Chrome resolves it against the document, so the old
`--page-bg: url('road.jpg')` was fetched from the site root and 404'd on every page —
which is why the backdrops rendered as flat dark panels with no photograph in them.

The page photographs are therefore attached with plain `background-image` rules on
`body.bg-*::before`, `.head-*` and `.card-*` at the foot of `site.css`. Only `--scrim`
stays a custom property, because a gradient has no URL to resolve.

## Photographs

`assets/hero.jpg` (2400px), `land.jpg` and `road.jpg` are real photographs, built by
`tools/photos.py` from originals in the gitignored `_incoming/`. Each is a **single
swap point** — drop a new file at the same path and the page updates with no markup
or CSS change.

Nothing is upscaled. An earlier pass ran Real-ESRGAN 4× over compressed 1080p video
frames; it invented detail that was never in the footage and the results looked fake.
Video frames are published at native resolution or not at all.

The gallery on `land.html` is a hand-curated mosaic. Cards take `--feature` (4×2),
`--tall` (2×2, for portraits) or `--wide` (4×1, for panoramas); no modifier gives an
ordinary 2×1 cell. Every published photograph, its source and a longer description are
logged in `PHOTOS.md` — the working manifest lives in `_incoming/` and is not committed.

## Voice

Set by the manifesto line on the homepage: **"No fake experiences. Just life as it is."**

- Say what is true now, including that the pilot is not open. The status band exists
  for exactly this.
- Short sentences. Concrete nouns — chulha, paddy, borewell — not "authentic" or
  "immersive".
- Never publish a route, a photograph, or a host detail before it is verified on the
  ground and consented to. This is a content rule, not a style one.
