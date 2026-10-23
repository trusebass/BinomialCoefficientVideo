"""Write-once snapshots of rendered clips, for importing into Premiere.

    .venv/bin/python tools/export.py h S03 S08     # those scenes + a full video
    .venv/bin/python tools/export.py h all         # every scene + a full video

Manim overwrites media/videos/... on every render, and assemble.py overwrites
out/. A clip Premiere references there silently changes under the edit. So
Premiere should only ever import from exports/: every run of this script makes
a new folder exports/<date>_<time>/ with uniquely named files, and nothing
ever writes into an existing one.

Per scene: S08_<stamp>.mp4 and S08_<stamp>_beats.csv (times inside the clip).
Full:      binomial_full_<stamp>.mp4 and beats_<stamp>.csv.
"""

import csv
import shutil
import sys
from datetime import datetime
from pathlib import Path

from assemble import QUALITY_DIRS, SCENES, build, scene_video, stamp
from timeline import beats

ROOT = Path(__file__).resolve().parent.parent


def snapshot(q, ids, full=True):
    tag = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    dest = ROOT / "exports" / f"{tag}_{QUALITY_DIRS[q]}"
    dest.mkdir(parents=True, exist_ok=False)   # never reuse a folder
    for sid, module, cls in SCENES:
        if ids != ["all"] and sid not in ids:
            continue
        video = scene_video(module, cls, q)
        shutil.copyfile(video, dest / f"{sid}_{tag}.mp4")
        bs, _ = beats(sid, video)
        with open(dest / f"{sid}_{tag}_beats.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["scene", "beat_number", "start_time_in_clip", "description",
                        "freeze_from"])
            w.writerows([[sid, i, stamp(b["start"]), b["desc"], stamp(b["freeze"])]
                         for i, b in enumerate(bs, 1)])
        print(f"{dest.name}/{sid}_{tag}.mp4")
    if full:
        build(q, dest / f"binomial_full_{tag}.mp4", dest / f"beats_{tag}.csv", verbose=False)
    return dest


if __name__ == "__main__":
    a = sys.argv[1:]
    snapshot(a[0] if a else "h", a[1:] or ["all"])
