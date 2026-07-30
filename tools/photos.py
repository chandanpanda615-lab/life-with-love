#!/usr/bin/env python3
"""Photo intake for Maati Katha. Standard library + Pillow, nothing else.

Drop originals in _incoming/ (gitignored), then:

    python tools/photos.py sheet    # contact sheets, so the whole set can be looked at
    python tools/photos.py manifest # write/refresh _incoming/manifest.csv
    python tools/photos.py build    # web-sized, EXIF-stripped copies -> assets/photos/

Originals never enter git. Only what build/ produces is committed.
"""
import csv, os, sys, subprocess
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

    fields = ["file", "publish", "consent", "slug", "caption", "place", "when", "hero"]
    rows = []
    for i, p in enumerate(photos):
        rel = str(p.relative_to(SRC)).replace("\\", "/")
        row = existing.get(rel, {})
        rows.append({
            "file": rel,
            "publish": row.get("publish", "no"),
            "consent": row.get("consent", ""),      # who agreed, if a person is in it
            "slug": row.get("slug", f"photo-{i:03d}"),
            "caption": row.get("caption", ""),
            "place": row.get("place", ""),
            "when": row.get("when", ""),
            "hero": row.get("hero", "no"),      # exactly one row says yes; it builds at HERO_MAX
        })
    with MANIFEST.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
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

    total = 0
    for r in rows:
        src = SRC / r["file"]
        if not src.exists():
            print(f"  MISSING {r['file']}")
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


if __name__ == "__main__":
    cmds = {"sheet": cmd_sheet, "manifest": cmd_manifest, "build": cmd_build}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit(f"usage: python tools/photos.py [{'|'.join(cmds)}]")
    SRC.mkdir(exist_ok=True)
    cmds[sys.argv[1]]()
