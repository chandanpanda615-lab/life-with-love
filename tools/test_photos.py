#!/usr/bin/env python3
"""Self-check for tools/photos.py. Plain asserts, no framework.

    python tools/test_photos.py

Covers the two things that would quietly ruin a page or break a promise:
marker injection eating hand-written copy, and the consent rule not being enforced.
"""
import csv, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import photos


def test_replace_between_keeps_everything_outside():
    before = "KEEP ABOVE\n<!-- GALLERY:START x -->\nold\n<!-- GALLERY:END -->\nKEEP BELOW"
    out = photos.replace_between(before, photos.MARK_START, photos.MARK_END, "NEW", "t")
    assert out == "KEEP ABOVE\nNEW\nKEEP BELOW", out
    # Running it on its own output must not drift: that is what makes re-rendering safe.
    again = photos.replace_between(
        "KEEP ABOVE\n<!-- GALLERY:START x -->\nNEW\n<!-- GALLERY:END -->\nKEEP BELOW",
        photos.MARK_START, photos.MARK_END, "NEW", "t")
    assert again == out, again


def test_replace_between_stops_at_the_first_block():
    """Two marker pairs in one file must not collapse into one — the regex is
    non-greedy for exactly this reason."""
    text = ("<!-- GALLERY:START a -->\n1\n<!-- GALLERY:END -->\nMIDDLE\n"
            "<!-- GALLERY:START b -->\n2\n<!-- GALLERY:END -->")
    out = photos.replace_between(text, photos.MARK_START, photos.MARK_END, "X", "t")
    assert "MIDDLE" in out and "2" in out, out


def test_missing_markers_is_an_error_not_a_silent_no_op():
    try:
        photos.replace_between("no markers here", photos.MARK_START, photos.MARK_END, "X", "t")
    except SystemExit:
        return
    raise AssertionError("a file without markers should stop the render, not pass silently")


def test_consent_guard_blocks_a_face_with_no_consent():
    """The site says no face is published without the person agreeing. A row with
    people=yes and an empty consent cell has to stop the whole render."""
    with tempfile.TemporaryDirectory() as d:
        m = Path(d) / "manifest.csv"
        with m.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=photos.FIELDS)
            w.writeheader()
            w.writerow({k: "" for k in photos.FIELDS} |
                       {"file": "school/x.jpg", "publish": "yes", "people": "yes",
                        "consent": "", "slug": "x"})
        real, photos.MANIFEST = photos.MANIFEST, m
        try:
            photos.published()
        except SystemExit:
            return
        finally:
            photos.MANIFEST = real
    raise AssertionError("published() let through a person with no consent recorded")


def test_consent_guard_allows_a_photo_with_nobody_in_it():
    with tempfile.TemporaryDirectory() as d:
        m = Path(d) / "manifest.csv"
        with m.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=photos.FIELDS)
            w.writeheader()
            w.writerow({k: "" for k in photos.FIELDS} |
                       {"file": "land/y.jpg", "publish": "yes", "people": "no", "slug": "y"})
        real, photos.MANIFEST = photos.MANIFEST, m
        try:
            rows = photos.published()
            assert len(rows) == 1, rows
        finally:
            photos.MANIFEST = real


def test_render_is_idempotent_on_the_real_files():
    """The check that matters most: run render twice, nothing may change."""
    targets = [photos.ROOT / n for n in ("land.html", "photographs.html")]
    targets += [p for p in (photos.ROOT / "docs" / "PHOTOS.md",
                            photos.ROOT / "PHOTOS.md") if p.exists()]

    def render():
        r = subprocess.run([sys.executable, str(Path(__file__).parent / "photos.py"), "render"],
                           capture_output=True, cwd=photos.ROOT)
        assert r.returncode == 0, r.stderr.decode(errors="replace")

    # Snapshot after the first run, not before it: run one is allowed to differ from
    # whatever is on disk (the template may have changed). Run two may not.
    render()
    before = [t.read_bytes() for t in targets]
    render()
    for t, b in zip(targets, before):
        assert t.read_bytes() == b, f"{t.name} changed when nothing in the manifest did"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)} passed")
