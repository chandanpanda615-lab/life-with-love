#!/usr/bin/env python3
"""Photo intake for Maati Katha. Standard library + Pillow, nothing else.

Drop originals in _incoming/ (gitignored), then:

    python tools/photos.py sheet    # contact sheets, so the whole set can be looked at
    python tools/photos.py manifest # write/refresh _incoming/manifest.csv
    python tools/photos.py build    # web-sized, EXIF-stripped copies -> assets/photos/
    python tools/photos.py render   # manifest -> the galleries in the pages, and PHOTOS.md

Originals never enter git. Only what build/ produces is committed — plus manifest.csv,
which is the one file carrying every caption and consent record.
"""
import csv, html, os, re, sys, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_incoming"
SHEETS = SRC / "_sheets"
OUT = ROOT / "assets" / "photos"
MANIFEST = SRC / "manifest.csv"

PHOTO_EXT = {".jpg", ".jpeg", ".png", ".heic", ".webp"}
VIDEO_EXT = {".mp4", ".mov", ".avi", ".wmv", ".mkv", ".3gp"}

COLS, ROWS, THUMB = 5, 4, 380          # 20 per sheet
WEB_MAX = 1600                          # longest edge of a published photo
HERO_MAX = 2400                         # the one photo marked hero=yes goes bigger
WEB_QUALITY = 82

FIELDS = ["file", "publish", "consent", "people", "slug", "caption", "alt", "place", "when",
          "group", "span", "cover", "hero", "tags", "notes"]

# Section order on photographs.html. A group named in the manifest but missing here
# lands in "rest" at the end, so a typo loses the section heading, never the photo.
# A row with a BLANK group is a page image (hero.jpg, land.jpg, road.jpg) — published,
# but it belongs to a backdrop, not to the gallery, so it is skipped entirely.
GROUPS = [
    ("land",     "The land",      "Soil, hills, water, and what the monsoon does to all three."),
    ("village",  "The village",   "The ground, the road, the evenings. Where the day ends up."),
    ("work",     "Work",          "Paddy, harvest, firewood. What the day is actually spent on."),
    ("school",   "The school",    "The blackboard, the mid-day meal, and the break in between."),
    ("festival", "Festival",      "The pandal, the flag, the days the village stops."),
    ("food",     "Food",          "Rice, dal, greens, and a chulha that is lit before you wake."),
    ("jungle",   "Jungle & jharana", "The forest behind the village, and the streams inside it."),
    ("market",   "The market",    "The road, the shopfronts, and the haat when it comes."),
    ("rest",     "Everything else", "Photographs that do not sit in one of the sets above."),
]

MARK_START = "<!-- GALLERY:START"
MARK_END = "<!-- GALLERY:END -->"


def scan():
    """Every file under _incoming/, split into photos and videos. Sorted, so the
    index printed on a contact sheet is stable between runs."""
    photos, videos = [], []
    for p in sorted(SRC.rglob("*")):
        if not p.is_file() or SHEETS in p.parents:
            continue
        ext = p.suffix.lower()
        if ext in PHOTO_EXT:
            photos.append(p)
        elif ext in VIDEO_EXT:
            videos.append(p)
    return photos, videos


def cmd_sheet():
    photos, videos = scan()
    if not photos:
        sys.exit(f"No photos in {SRC}. Put the originals there first.")
    SHEETS.mkdir(parents=True, exist_ok=True)
    for old in SHEETS.glob("sheet-*.jpg"):
        old.unlink()

    per = COLS * ROWS
    made = 0
    for start in range(0, len(photos), per):
        batch = photos[start:start + per]
        W, H = COLS * THUMB, ROWS * (THUMB + 26)
        sheet = Image.new("RGB", (W, H), (28, 24, 20))
        draw = ImageDraw.Draw(sheet)
        for i, path in enumerate(batch):
            try:
                im = Image.open(path)
                im.draft("RGB", (THUMB * 2, THUMB * 2))   # fast JPEG downscale
                im = ImageOps.exif_transpose(im)          # phone shots carry orientation=6
                im = im.convert("RGB")
            except Exception as e:                        # unreadable file: leave a marker
                im = Image.new("RGB", (THUMB, THUMB), (60, 30, 30))
                ImageDraw.Draw(im).text((8, 8), f"unreadable\n{e}"[:120], fill=(255, 200, 200))
            im.thumbnail((THUMB - 8, THUMB - 8), Image.LANCZOS)
            cx, cy = (i % COLS) * THUMB, (i // COLS) * (THUMB + 26)
            sheet.paste(im, (cx + (THUMB - im.width) // 2, cy + (THUMB - 8 - im.height) // 2 + 4))
            draw.text((cx + 6, cy + THUMB + 4), f"{start + i:03d}  {path.name[:34]}", fill=(210, 200, 185))
        out = SHEETS / f"sheet-{start // per:02d}.jpg"
        sheet.save(out, quality=78, optimize=True)
        made += 1
        print(f"  {out.relative_to(ROOT)}  ({len(batch)} photos)")

    print(f"\n{len(photos)} photos across {made} contact sheet(s).")
    if videos:
        total = sum(v.stat().st_size for v in videos) / 1048576
        print(f"{len(videos)} video(s), {total:.0f} MB total — these do NOT go in git. See the README note.")


def cmd_manifest():
    """One row per photo. Nothing is published until `publish` says yes, which
    keeps the site's own consent rule enforceable rather than aspirational."""
    photos, _ = scan()
    existing = {}
    if MANIFEST.exists():
        with MANIFEST.open(encoding="utf-8", newline="") as f:
            existing = {r["file"]: r for r in csv.DictReader(f)}

    rows = []
    for i, p in enumerate(photos):
        rel = str(p.relative_to(SRC)).replace("\\", "/")
        row = existing.get(rel, {})
        # The folder a photo was dropped into is the best first guess at its group,
        # so sorting 100 files into sections is mostly a matter of where they landed.
        default_group = rel.split("/")[0] if "/" in rel else ""
        rows.append({
            "file": rel,
            "publish": row.get("publish", "no"),
            "consent": row.get("consent", ""),      # who agreed, if a person is in it
            "people": row.get("people", ""),        # yes if anyone is identifiable in it
            "slug": row.get("slug", f"photo-{i:03d}"),
            "caption": row.get("caption", ""),
            "alt": row.get("alt", ""),          # falls back to caption when left blank
            "place": row.get("place", ""),
            "when": row.get("when", ""),
            "group": row.get("group", default_group),   # section on photographs.html
            "span": row.get("span", ""),        # feature | tall | wide, or blank for a plain cell
            "cover": row.get("cover", ""),      # yes = this photo is the album's cover
            "hero": row.get("hero", "no"),      # exactly one row says yes; it builds at HERO_MAX
            "tags": row.get("tags", ""),        # comma separated; drives ?tag= and "also"
            "notes": row.get("notes", ""),      # the long description, raw material for posts
        })
    # Write a sibling file and swap it in. Opening the manifest itself with "w"
    # truncates it before the write, so any error mid-write destroys every caption
    # and consent record in it. That has happened. Do not go back to the simple form.
    fd, tmp = tempfile.mkstemp(dir=str(MANIFEST.parent), suffix=".csv")
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, MANIFEST)
    kept = sum(1 for r in rows if r["publish"].strip().lower() == "yes")
    print(f"{MANIFEST.relative_to(ROOT)}: {len(rows)} rows, {kept} marked publish=yes")
    print("Edit it, set publish=yes on the ones you want, then run: python tools/photos.py build")


def cmd_build():
    if not MANIFEST.exists():
        sys.exit("No manifest yet. Run: python tools/photos.py manifest")
    OUT.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open(encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["publish"].strip().lower() == "yes"]
    if not rows:
        sys.exit("Nothing marked publish=yes in the manifest.")

    total = skipped = 0
    for r in rows:
        src = SRC / r["file"]
        if not src.exists():
            print(f"  MISSING {r['file']}")
            continue
        # A blank group means this is a page backdrop (hero.jpg, land.jpg, road.jpg),
        # which site.css loads from assets/ — not a gallery photo. Writing it straight
        # to its real home removes a manual copy step that was easy to forget.
        dst = (ROOT / "assets" if not r.get("group", "").strip() else OUT) / f"{r['slug']}.jpg"
        # Re-encoding a hundred unchanged photos on every run buys nothing. Delete the
        # built file (or touch the original) to force one.
        if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
            skipped += 1
            total += dst.stat().st_size / 1024
            continue
        im = Image.open(src)
        # Rotate upright while the orientation tag still exists — the repaste below
        # drops all EXIF, so doing this afterwards would lose the tag unread.
        im = ImageOps.exif_transpose(im).convert("RGB")
        max_edge = HERO_MAX if r.get("hero", "").strip().lower() == "yes" else WEB_MAX
        im.thumbnail((max_edge, max_edge), Image.LANCZOS)
        clean = Image.new("RGB", im.size)     # new image => EXIF, incl. GPS, is dropped
        clean.paste(im)
        dst = OUT / f"{r['slug']}.jpg"
        clean.save(dst, quality=WEB_QUALITY, optimize=True, progressive=True)
        kb = dst.stat().st_size / 1024
        total += kb
        print(f"  {dst.name:28s} {im.width}x{im.height}  {kb:6.0f} KB")
    print(f"\n{len(rows)} photos -> {OUT.relative_to(ROOT)}, {total/1024:.1f} MB total")
    print("These are the only image files that belong in a commit.")


def published():
    """Manifest rows marked publish=yes, with the consent rule enforced rather than
    hoped for. The site promises "no face published without the person agreeing to it
    first" — so a row with a person in it and an empty consent cell stops the render."""
    if not MANIFEST.exists():
        sys.exit("No manifest yet. Run: python tools/photos.py manifest")
    with MANIFEST.open(encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r.get("publish", "").strip().lower() == "yes"]

    unconsented = [r for r in rows
                   if r.get("people", "").strip().lower() == "yes"
                   and not r.get("consent", "").strip()]
    if unconsented:
        print("Refusing to render. These rows have a person in the frame and no consent:\n")
        for r in unconsented:
            print(f"  {r['file']}  (slug: {r.get('slug', '?')})")
        sys.exit("\nFill the consent column, or set publish=no. This rule is the site's own.")
    return rows


def replace_between(text, start_mark, end_mark, body, what):
    """Swap only what sits between the two markers. Everything a human wrote around
    them survives untouched, which is what makes re-running this safe."""
    pat = re.compile(re.escape(start_mark) + r".*?" + re.escape(end_mark), re.S)
    if not pat.search(text):
        sys.exit(f"No {start_mark} ... {end_mark} block in {what}. Add the markers first.")
    return pat.sub(lambda _: body, text, count=1)


def tidy_tags(raw):
    """Lower-case, comma-separated, no duplicates, order kept. Typing "Children, food"
    and "children,Food" in two rows should not make two different tags."""
    seen, out = set(), []
    for t in raw.split(","):
        t = " ".join(t.split()).lower()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return ",".join(out)


def figure(r, i):
    """One gallery cell. width/height come off the built file: without them a
    hundred lazy images collapse the page height and every scroll jumps."""
    src = OUT / f"{r['slug']}.jpg"
    if not src.exists():
        sys.exit(f"{src.relative_to(ROOT)} is missing. Run: python tools/photos.py build")
    w, h = Image.open(src).size
    span = r.get("span", "").strip().lower()
    cls = "photo-card" + (f" photo-card--{span}" if span in {"feature", "tall", "wide"} else "")
    cap = html.escape(r.get("caption", "").strip())
    alt = html.escape((r.get("alt") or r.get("caption", "")).strip())
    delay = min(0.06 + i * 0.04, 0.34)      # stagger the first few, then stop waiting
    tags = html.escape(tidy_tags(r.get("tags", "")))
    # The id makes every photograph addressable — photographs.html#school-meal opens
    # straight into it, so a written piece can point at one frame.
    return (
        f'      <figure id="{r["slug"]}" class="{cls} reveal" style="--d:{delay:.2f}s"\n'
        f'              data-tags="{tags}"\n'
        f'              tabindex="0" role="button" aria-label="Open photograph: {cap}">\n'
        f'        <img src="assets/photos/{r["slug"]}.jpg" alt="{alt}"\n'
        f'             width="{w}" height="{h}" loading="lazy" decoding="async">\n'
        f'        <figcaption>{cap}</figcaption>\n'
        f'      </figure>'
    )


def cmd_render():
    # A blank group means the photo is a page backdrop, not a gallery cell.
    rows = [r for r in published() if r.get("group", "").strip()]
    note = f"{MARK_START} — generated by tools/photos.py render. Do not edit by hand. -->"

    # --- photographs.html: every published photo, in labelled sections -------------
    known = {g for g, _, _ in GROUPS}
    sections = []
    album_index = []          # (key, title, count) for the bar at the top of the page
    for key, title, blurb in GROUPS:
        if key == "rest":
            batch = [r for r in rows if r.get("group", "").strip().lower() not in known]
        else:
            batch = [r for r in rows if r.get("group", "").strip().lower() == key]
        if not batch:
            continue
        cells = "\n".join(figure(r, i) for i, r in enumerate(batch))
        # The album's cover: whichever row says cover=yes, else the first photograph
        # in the set. A closed <details> is the whole point — the page is seven covers
        # until something is opened, so there is nothing to scroll past.
        pick = next((r for r in batch if r.get("cover", "").strip().lower() == "yes"), batch[0])
        n = len(batch)
        album_index.append((key, title, n))
        sections.append(
            f'  <details class="album" id="{key}">\n'
            f'    <summary class="album-cover" style="background-image:'
            f'linear-gradient(to top, rgba(8,10,18,.88), rgba(8,10,18,.25)),'
            f'url(assets/photos/{pick["slug"]}.jpg)">\n'
            f'      <span class="album-eyebrow">{n} photograph{"s" if n != 1 else ""}</span>\n'
            f'      <span class="album-title">{title}</span>\n'
            f'      <span class="album-sub">{blurb}</span>\n'
            f'      <span class="album-cue" aria-hidden="true"></span>\n'
            f'    </summary>\n'
            f'    <div class="gallery-grid inner">\n{cells}\n    </div>\n'
            f'  </details>'
        )
    # The bar names the albums, not the tags. It listed tags until "red earth",
    # "indoors" and "monsoon" ended up sitting directly above "The land" — two
    # different ways of cutting the same 29 photographs, stacked on top of each
    # other. Naming the albums makes the bar a table of contents: one entry per
    # set below it, and clicking an entry opens that set.
    #
    # href is a real "#key" fragment so it still jumps with JavaScript off; the
    # opening is done in gallery.js, which is also what closes the other albums.
    chips = "".join(
        f'      <a class="tag-chip" href="#{key}" data-album="{key}">'
        f'{html.escape(title)} <small>{n}</small></a>\n' for key, title, n in album_index)
    tagbar = ('  <nav class="tag-bar inner reveal" aria-label="Jump to an album">\n'
              '      <a class="tag-chip tag-all is-on" href="#" data-album="">everything '
              f'<small>{len(rows)}</small></a>\n{chips}  </nav>') if album_index else ""

    archive = ROOT / "photographs.html"
    text = archive.read_text(encoding="utf-8")
    body = note + "\n" + tagbar + "\n" + "\n\n".join(sections) + "\n  " + MARK_END
    archive.write_text(replace_between(text, MARK_START, MARK_END, body, archive.name),
                       encoding="utf-8")
    print(f"  photographs.html   {len(rows)} photographs in {len(sections)} section(s)")

    # land.html deliberately has no gallery. A curated copy of the archive put eight
    # photographs on two pages at once; one photograph belongs in exactly one place.

    # --- PHOTOS.md: the log, below whatever preamble is written above the marker ----
    # Moved under docs/ with the other notes; keep working if it is still at the root.
    log = next((p for p in (ROOT / "docs" / "PHOTOS.md", ROOT / "PHOTOS.md") if p.exists()),
               ROOT / "docs" / "PHOTOS.md")
    lines = ["<!-- GALLERY:START — generated by tools/photos.py render. Do not edit by hand. -->",
             "", "| slug | caption on site | place · when | notes |", "|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r.get("group", ""), r.get("slug", ""))):
        when = " · ".join(x for x in (r.get("place", "").strip(), r.get("when", "").strip()) if x)
        cells_md = [r.get("slug", ""), r.get("caption", ""), when, r.get("notes", "").strip()]
        if r.get("consent", "").strip():
            cells_md[3] = (cells_md[3] + " " if cells_md[3] else "") + f"Consent: {r['consent'].strip()}."
        lines.append("| " + " | ".join(c.replace("|", "\\|").replace("\n", " ") for c in cells_md) + " |")
    lines += ["", MARK_END]
    log.write_text(replace_between(log.read_text(encoding="utf-8"),
                                   MARK_START, MARK_END, "\n".join(lines), log.name),
                   encoding="utf-8")
    print(f"  PHOTOS.md          {len(rows)} rows")
    print("\nRun it again — the files should not change. That is the check.")


if __name__ == "__main__":
    cmds = {"sheet": cmd_sheet, "manifest": cmd_manifest, "build": cmd_build,
            "render": cmd_render}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit(f"usage: python tools/photos.py [{'|'.join(cmds)}]")
    SRC.mkdir(exist_ok=True)
    cmds[sys.argv[1]]()
