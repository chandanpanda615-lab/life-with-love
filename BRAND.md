# Maati Katha — brand notes

This documents what the site already does. It is a reference for keeping new pages
consistent, not a rebrand. Everything here is defined once in the `:root` block of
`index.html` — change it there, not in individual rules.

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

All three display faces are embedded as base64 woff2 in the `<style>` block, so the
page has no network font dependency. **Nothing else may be added to that stack
without embedding it** — `'Inter'` was named there for a while without ever being
embedded, and every line of body text silently fell back to `system-ui`.

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

**Image paths belong in `site.css`, not in inline styles.** A `url()` inside a CSS
custom property resolves relative to the stylesheet that parsed it, so a path written
in the HTML as `url('assets/land.jpg')` is fetched as `assets/assets/land.jpg`. The
`--page-bg` / `--head-bg` / `--card-bg` values are therefore declared in `site.css`
where the bare filename is correct.

## Photographs

`assets/hero.jpg`, `land.jpg` and `road.jpg` are stand-ins cropped out of 6-up phone
collages in `maati-katha-research/assets/`, so they are 466–1145px wide and go soft on
a large display. Each is a **single swap point** — drop a real full-resolution
photograph at the same path and the page updates with no markup or CSS change.

The gallery on `land.html` keeps its six `<figure>` cards with the `<img>` commented
out; uncomment one and the dashed placeholder disappears by itself. Its captions are
placeholders for narration that has not been written yet.

## Voice

Set by the manifesto line on the homepage: **"No fake experiences. Just life as it is."**

- Say what is true now, including that the pilot is not open. The status band exists
  for exactly this.
- Short sentences. Concrete nouns — chulha, paddy, borewell — not "authentic" or
  "immersive".
- Never publish a route, a photograph, or a host detail before it is verified on the
  ground and consented to. This is a content rule, not a style one.
