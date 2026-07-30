#!/usr/bin/env python3
"""Pull the sharpest, most distinct frames out of the village videos.

    python tools/extract_video_gems.py

Reads every .mp4 in _incoming/_videos/ and writes candidate frames to
_incoming/video-frames/ at native resolution. From there they join the photos
in the normal intake: `photos.py sheet` to look at them, `manifest` to record
consent, `build` to publish. Nothing here decides what gets published.

Frames are written exactly as the camera recorded them. There is no upscaling
and no sharpening: this footage is 1080p, and inventing pixels it never had is
what made the previous set of images look fake.
"""
import os
import cv2
import numpy as np

VID_DIR = os.path.join("_incoming", "_videos")
OUT_DIR = os.path.join("_incoming", "video-frames")

SCAN_STRIDE = 3          # score every 3rd frame; 10fps of sampling is plenty
HIST_LIMIT = 0.92        # above this correlation two frames are the same picture


def score_frame(frame):
    """
    Multi-metric frame quality score:
    - Laplacian variance (sharpness)
    - Sobel gradient magnitude (edge detail)
    - Contrast (std dev of grayscale intensity)
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Ignore dark/underexposed frames
    mean_brightness = np.mean(gray)
    if mean_brightness < 35 or mean_brightness > 235:
        return 0.0

    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    contrast = np.std(gray)

    # Sobel edge density
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    edge_density = np.mean(np.sqrt(sobelx**2 + sobely**2))

    # Combined score
    score = (laplacian_var * 0.5) + (contrast * 1.5) + (edge_density * 2.0)
    return score


def frame_hist(frame):
    """Hue/saturation histogram, for telling two frames apart by content."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h = cv2.calcHist([hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
    return cv2.normalize(h, h).flatten()


def pick_frames(path):
    """Score the whole video, then return the best well-separated frames.

    Two passes on purpose. Holding every scanned frame in memory to sort them
    later costs about 2.5 GB on a 44-second 1080p clip; scoring first and
    seeking back for the handful that won costs nothing.
    """
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total / fps if fps else 0

    scores = []
    idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % SCAN_STRIDE == 0:
            scores.append((idx, score_frame(frame)))
        idx += 1
    scores.sort(key=lambda s: s[1], reverse=True)

    # Enough variety to curate from, without dumping the whole clip on the floor.
    # ponytail: crude duration-based cap, revisit if a clip is long enough that 8 isn't enough
    want = max(3, min(8, round(duration / 6)))
    min_gap = int(fps * 4)        # 1.5s was too tight — a slow pan repeats itself

    kept, hists = [], []
    for f_idx, score in scores:
        if len(kept) >= want:
            break
        if any(abs(f_idx - k[0]) < min_gap for k in kept):
            continue
        cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
        ok, frame = cap.read()
        if not ok:
            continue
        h = frame_hist(frame)
        # A time gap alone doesn't help on a static shot: check the picture too.
        if any(cv2.compareHist(h, prev, cv2.HISTCMP_CORREL) > HIST_LIMIT for prev in hists):
            continue
        kept.append((f_idx, score, frame))
        hists.append(h)

    cap.release()
    kept.sort(key=lambda k: k[0])
    return kept, fps, duration


def main():
    if not os.path.isdir(VID_DIR):
        raise SystemExit(f"No {VID_DIR}. Put the video files there first.")
    videos = [f for f in sorted(os.listdir(VID_DIR)) if f.lower().endswith((".mp4", ".mov"))]
    if not videos:
        raise SystemExit(f"No videos in {VID_DIR}.")
    os.makedirs(OUT_DIR, exist_ok=True)

    written = 0
    for name in videos:
        stem = os.path.splitext(name)[0]
        kept, fps, duration = pick_frames(os.path.join(VID_DIR, name))
        print(f"\n{name}  ({duration:.0f}s)")
        for f_idx, score, frame in kept:
            t = f_idx / fps
            h, w = frame.shape[:2]
            out = os.path.join(OUT_DIR, f"{stem}_f{f_idx:05d}_t{t:.1f}s.jpg")
            cv2.imwrite(out, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            written += 1
            print(f"  t={t:5.1f}s  {w}x{h}  score={score:6.1f}  {os.path.basename(out)}")

    print(f"\n{written} frames -> {OUT_DIR}")
    print("Next: python tools/photos.py sheet")


if __name__ == "__main__":
    main()
