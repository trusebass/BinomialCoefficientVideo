"""Check that consecutive clips join without a visible jump.

    .venv/bin/python tools/seam.py clipA.mp4 clipB.mp4

Compares the last frame of A with the first frame of B and saves both
side by side to out/contact/seam.png. Prints the mean and max pixel
difference (0 = identical).
"""

import sys
import tempfile
from pathlib import Path

import av
from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parent.parent


def frame(video, out, last):
    """Save the first or last frame of a video (decoded with PyAV)."""
    with av.open(str(video)) as c:
        img = None
        for f in c.decode(video=0):
            img = f.to_image()
            if not last:
                break
    img.save(out)


def main(a, b):
    with tempfile.TemporaryDirectory() as tmp:
        fa, fb = Path(tmp) / "a.png", Path(tmp) / "b.png"
        frame(a, fa, last=True)
        frame(b, fb, last=False)
        ia, ib = Image.open(fa).convert("RGB"), Image.open(fb).convert("RGB")
        diff = ImageChops.difference(ia, ib)
        stat = ImageStat.Stat(diff)
        print(f"mean diff {sum(stat.mean) / 3:.2f}   max diff {max(m for _, m in diff.getextrema())}")
        sheet = Image.new("RGB", (ia.width * 3, ia.height))
        sheet.paste(ia, (0, 0))
        sheet.paste(ib, (ia.width, 0))
        sheet.paste(diff.point(lambda v: min(255, v * 8)), (ia.width * 2, 0))
        out = ROOT / "out" / "contact" / f"seam_{Path(a).stem}_{Path(b).stem}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(out)
        print(out)


if __name__ == "__main__":
    main(*sys.argv[1:3])
