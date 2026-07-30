# Photograph log

Every published photograph, what is actually in it, and where it came from.

This file is committed. The working manifest (`_incoming/manifest.csv`) is not — `_incoming/`
is gitignored, so the descriptions would be lost with it. Anything worth keeping goes here.

Written for two jobs: the `alt` text and captions on the site, and posting these one at a
time later — Instagram, or wherever. The **notes** column is the raw material for that.
Longer than a caption on purpose. Cut it down when you post, don't write it again.

Voice rule from BRAND.md still applies: short sentences, concrete nouns — chulha, paddy,
borewell. Never "authentic", never "immersive". Say what is in the frame.

## Consent

`held` means the people in the frame agreed to it being published. That is recorded per row
in the manifest and repeated here. Photographs with no identifiable person carry no consent
note. **Do not publish a new photograph of a person before this column can say `held`.**

---

## The three page images

| slug | where it's used | source | what's in it |
|---|---|---|---|
| `hero.jpg` | homepage hero, 2400px | `20250707_183555` · Sarangada · July 2025 | The market road under monsoon cloud. A man cycling away from camera, a woman under a black umbrella, mud and standing water down the left. Bikes parked outside a green-shuttered shop. Mist sitting on the hills at the end of the road. Consent: held, figures are distant and turned away. |
| `land.jpg` | "The land" page head, the land door card | `20250809_165828` · Kandhamal · August 2025 | Brown monsoon water under low hills, framed by a leaning tree. Flat light. |
| `road.jpg` | "How to reach" page head, the road door card | `20251020_114113` · Odisha · October 2025 | A paved road running straight between two sheets of water, goats crossing, big blue sky with piled cloud. |

## The gallery, in page order

| slug | caption on site | place · when | notes |
|---|---|---|---|
| `terraces` | Paddy terraced into the hillside | Kandhamal · Oct 2025 | Bright green paddy stepped up a slope, earthen bunds holding water between the steps. Banana and palm along the top edge. This is the shape of farming here — the hill decides the field, not the other way round. Video frame. |
| `street-dusk` | Power lines over the market road | Sarangada · Oct 2024 | Dusk. Power lines cross above the road, hills going blue behind. The "old and new side by side" note made literal — this is the photograph to pair with it. |
| `football-wide` | The whole village at the football ground | Sarangada · Oct 2024 | A wide panorama, 8096px original. Match in progress on red earth, spectators lining the far edge, goalpost with a yellow net at left. Two heads in the foreground, watching. Consent: held. |
| `thali` | Rice, dal and greens | Sarangada · Jan 2025 | Looking down at a meal. Rice, a dal, a dry green, a fish, a small bowl of something red. Steel and a patterned floor. Good for the "food is plain and there is a lot of it" post. |
| `mist-hills` | Mist on the Eastern Ghats | Kandhamal · Sep 2025 | Cloud sitting halfway down forested hills, everything wet and grey-green. Shot from the road. This is what the drive in looks like in monsoon. Video frame. |
| `water-tower` | The water tower at dusk | Sarangada · May 2024 | The concrete water tower against an orange evening sky, a motorcycle on the road below, shopfronts down the right. |
| `women-earth` | Sorting the harvest on bare earth | Sarangada · Jan 2025 | Four women sitting on bare packed earth outside a mud-walled house, sorting into baskets and sacks. Firewood stacked behind. Midday, hard shadows. Consent: held. The strongest photograph in the set for showing work rather than scenery. |
| `ground-red` | Red earth, before the match | Sarangada · Oct 2024 | The empty football ground, red earth in the foreground, tree line and low buildings behind. Wide, quiet. |
| `paddy-green` | Paddy after the rain | Kandhamal · Oct 2025 | Deep green paddy and scrub, hills behind under wet cloud. Video frame. |
| `fire-night` | The fire after dark | Sarangada · Jan 2025 | Four people standing around an open fire at night, one seated on a plastic stool on a phone. Firelight only. Consent: held. Use this one for a post about evenings — there is no wifi after seven and nobody minds. |
| `market-hills` | Market road, hills behind | Sarangada · Jan 2025 | The market strip — shopfronts, parked bikes, a hill rising directly behind the roofline. Two men in the foreground walking away. Consent: held. |
| `bikes-paddy` | Bikes at the edge of the paddy | Sarangada · July 2025 | Motorcycles and a bicycle parked on red mud at the edge of a bright green field, water tank behind. |
| `road-ghats` | The road climbing west | Kandhamal · Oct 2025 | An empty road curving away under a big tree, hills beyond. The last stretch in. Video frame, portrait. |
| `shop-night` | The shop stays open after dark | Sarangada · Jan 2025 | A green-painted shop lit by a single bulb, goods hung in rows, two people at the counter. Consent: held. |
| `road-sunset` | Sunset over the village road | Sarangada · Oct 2024 | Sun going down the length of the road, houses either side, wires overhead, a parked white car. |
| `pandal` | Inside the festival pandal | Sarangada · Jan 2025 | Inside a decorated pandal — pink and yellow cloth, a latticed ceiling, balloons, a seated crowd facing a stage. Consent: held. |

---

## Adding more

1. Drop originals into `_incoming/` (any subfolder). Videos into `_incoming/_videos/`.
2. `python tools/extract_video_gems.py` if there are new videos.
3. `python tools/photos.py sheet` and look at the contact sheets.
4. `python tools/photos.py manifest`, set `publish=yes`, fill in `consent`, `slug`, `caption`, `place`, `when`.
5. `python tools/photos.py build`.
6. Add a `<figure>` in `land.html` and a row in this file.

Originals never enter git. Only `assets/photos/` does.
