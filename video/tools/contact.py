"""Contact sheet of every beat's still frame, for reviewing a scene quickly.

    .venv/bin/python tools/contact.py S01 media/videos/s01_lookup/480p15/S01Lookup.mp4

Reads out/beats/S01.json, grabs the frame at the end of each beat's
animation (the frame Premiere would freeze), and tiles them with numbers.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

from timeline import beats as scene_beats

ROOT = Path(__file__).resolve().parent.parent


def grab(video, t, out):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(video),
                    "-frames:v", "1", str(out)], check=True)


def main(scene, video, cols=4, width=480, first=1, last=None):
    beats, _ = scene_beats(scene, video)
    last = len(beats) if last is None else last
    picks = list(enumerate(beats, 1))[first - 1:last]
    tiles = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, b in picks:
            p = Path(tmp) / f"{i}.png"
            grab(video, b["freeze"] + 0.15, p)  # inside the BEAT hold
            im = Image.open(p).convert("RGB")
            im = im.resize((width, int(im.height * width / im.width)))
            d = ImageDraw.Draw(im)
            d.rectangle([0, 0, width, 16], fill=(0, 0, 0))
            d.text((4, 2), f"{i}: {b['desc']}"[:80], fill=(255, 255, 0))
            tiles.append(im)
    h = tiles[0].height
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * width, rows * h), (40, 40, 40))
    for j, im in enumerate(tiles):
        sheet.paste(im, ((j % cols) * width, (j // cols) * h))
    out = ROOT / "out" / "contact" / f"{scene}_{first}-{last}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(out)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[1], *(int(x) for x in a[2:]))
