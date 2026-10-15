"""Exact beat times from the partial movie files Manim wrote.

Manim renders every play()/wait() call into its own small file, listed in
order in partial_movie_files/<Scene>/partial_movie_file_list.txt, and then
joins them. Counting the frames in those files gives the exact start time of
every play, which BeatScene's play indices are mapped onto.
"""

import json
from pathlib import Path

import av

ROOT = Path(__file__).resolve().parent.parent


def play_starts(video):
    """Start time (s) of each play in `video`, plus its end time last."""
    video = Path(video)
    lst = video.parent / "partial_movie_files" / video.stem / "partial_movie_file_list.txt"
    files = [l.split("'")[1].removeprefix("file:") for l in lst.read_text().splitlines()
             if l.startswith("file")]
    times, t = [0.0], 0.0
    for f in files:
        with av.open(f) as c:
            s = c.streams.video[0]
            t += s.frames / float(s.average_rate)
        times.append(t)
    return times


def beats(scene_id, video):
    """Beats of a scene with exact 'start' and 'freeze' times added."""
    data = json.loads((ROOT / "out" / "beats" / f"{scene_id}.json").read_text())
    starts = play_starts(video)
    if len(starts) - 1 != data["plays"]:
        raise RuntimeError(f"{scene_id}: {len(starts) - 1} partial files but "
                           f"{data['plays']} plays logged; re-render the scene")
    for b in data["beats"]:
        b["start"] = starts[b["start_play"]]
        b["freeze"] = starts[b["freeze_play"]]
    return data["beats"], starts[-1]
