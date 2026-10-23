"""Join the rendered scenes into one clip and write the beat list (script A.5).

    .venv/bin/python tools/assemble.py h        # h = 1080p60, l = 480p15 drafts, k = 4K

Writes out/binomial_full.mp4, out/clips/S01.mp4 ... (the per-scene clips) and
out/beats.csv with one row per beat:
    scene, beat_number, start_time_in_full_video, description, freeze_from
`freeze_from` is when the beat's animation has finished: from there on the
frame is still for BEAT seconds, so that is the frame to freeze in Premiere.
"""

import csv
import shutil
import subprocess
import sys
from pathlib import Path

import av

from timeline import beats

ROOT = Path(__file__).resolve().parent.parent
SCENES = [
    ("S01", "s01_lookup", "S01Lookup"),
    ("S02", "s02_choosing", "S02Choosing"),
    ("S03", "s03_theorem", "S03Theorem"),
    ("S04", "s04_question", "S04Question"),
    ("S05", "s05_multiply", "S05Multiply"),
    ("S06", "s06_counts", "S06Counts"),
    ("S07", "s07_tree", "S07Tree"),
    ("S08", "s08_fold", "S08Fold"),
    ("S09", "s09_last_step", "S09LastStep"),
    ("S10", "s10_two_ways", "S10TwoWays"),
    ("S11", "s11_builds", "S11Builds"),
    ("S12", "s12_galton", "S12Galton"),
]
QUALITY_DIRS = {"l": "480p15", "m": "720p30", "h": "1080p60", "k": "2160p60"}


def stamp(t):
    m, s = divmod(t, 60)
    return f"{int(m):02d}:{s:06.3f}"


def scene_video(module, cls, q):
    return ROOT / "media" / "videos" / module / QUALITY_DIRS[q] / f"{cls}.mp4"


def build(q, full, csv_path, clips=None, verbose=True):
    """Join all scenes into `full` and write the beat list to `csv_path`.
    With `clips` (a folder), also copy every scene's clip there."""
    full, csv_path = Path(full), Path(csv_path)
    if clips:
        Path(clips).mkdir(parents=True, exist_ok=True)
    rows, offset, lines = [], 0.0, []
    for sid, module, cls in SCENES:
        video = scene_video(module, cls, q)
        bs, length = beats(sid, video)
        for i, b in enumerate(bs, 1):
            rows.append([sid, i, stamp(offset + b["start"]), b["desc"],
                         stamp(offset + b["freeze"])])
        if clips:
            shutil.copyfile(video, Path(clips) / f"{sid}.mp4")
        lines.append(f"file '{video}'")
        if verbose:
            print(f"{sid}  starts {stamp(offset)}  length {length:7.3f}s  {len(bs)} beats")
        offset += length

    lst = full.with_suffix(".concat.txt")
    lst.write_text("\n".join(lines) + "\n")
    # -c copy joins the files without re-encoding: no quality loss, no gaps,
    # and it works because every clip was rendered with the same settings.
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(lst), "-c", "copy", str(full)], check=True)
    lst.unlink()

    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["scene", "beat_number", "start_time_in_full_video", "description",
                    "freeze_from"])
        w.writerows(rows)

    with av.open(str(full)) as c:
        s = c.streams.video[0]
        frames, fps = s.frames, float(s.average_rate)
    got = frames / fps
    print(f"{full}: {stamp(got)} ({frames} frames)  expected {stamp(offset)}")
    if abs(got - offset) > 1 / fps:
        sys.exit("length mismatch: beat times would drift")
    print(f"{csv_path}: {len(rows)} beats")


def main(q="h"):
    out = ROOT / "out"
    out.mkdir(exist_ok=True)
    build(q, out / "binomial_full.mp4", out / "beats.csv", clips=out / "clips")


if __name__ == "__main__":
    main(*sys.argv[1:2])
