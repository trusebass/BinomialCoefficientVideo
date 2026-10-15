"""Scene 12 — Coda: the Galton board."""

import random

from components import *
import s11_builds

ROWS, BALLS = 10, 400
DX, DY, TOP = 0.62, 0.40, 2.75        # peg grid: peg (n, k) at ((k - n/2) DX, TOP - n DY)
BALL_R, PER_LAYER = 0.05, 6           # 6 balls side by side fill one bin layer
FLOOR = -3.2
BIN_TOP = FLOOR + 2.0
RELEASE = 0.04                        # seconds between two balls
HOP, FALL = 0.085, 0.35               # time per peg row, time for the final drop


def peg(n, k):
    return np.array([(k - n / 2) * DX, TOP - n * DY, 0])


def bin_x(k):
    return (k - ROWS / 2) * DX


def board():
    pegs = VGroup(*[Dot(peg(n, k), radius=0.05, color=MUTED)
                    for n in range(ROWS) for k in range(n + 1)])
    walls = VGroup(*[Line([bin_x(k) - DX / 2, FLOOR, 0], [bin_x(k) - DX / 2, BIN_TOP, 0],
                          color=MUTED, stroke_width=2) for k in range(ROWS + 2)])
    floor = Line([bin_x(0) - DX / 2, FLOOR, 0], [bin_x(ROWS) + DX / 2, FLOOR, 0],
                 color=MUTED, stroke_width=2)
    panel = RoundedRectangle(width=8.2, height=7.0, corner_radius=0.15, stroke_color=RULE,
                             stroke_width=1.5, fill_color=PANEL, fill_opacity=1)
    panel.move_to([0, (TOP + 0.6 + FLOOR - 0.15) / 2, 0])
    return VGroup(panel, pegs, walls, floor)


def simulate():
    """Left/right bounces from a seeded generator, so every render is the same."""
    rng = random.Random(7)
    return [[rng.random() < 0.5 for _ in range(ROWS)] for _ in range(BALLS)]


def stack_pos(k, m):
    """Where the m-th ball to land in bin k rests."""
    layer, col = divmod(m, PER_LAYER)
    return np.array([bin_x(k) + (col - (PER_LAYER - 1) / 2) * 2 * BALL_R,
                     FLOOR + BALL_R + layer * 2 * BALL_R, 0])


def ball_track(path, rest):
    """Waypoints of one ball: above each peg it hits, then its resting place."""
    pts, k = [peg(0, 0) + UP * 0.45], 0
    for n, right in enumerate(path):
        pts.append(peg(n, k) + UP * 0.12)
        k += right
    pts.append(np.array([bin_x(k), TOP - ROWS * DY + 0.12, 0]))
    return pts, rest


def position(track, t):
    """Ball position t seconds after its release."""
    pts, rest = track
    n_hops = len(pts) - 1
    if t < n_hops * HOP:
        i, s = divmod(t / HOP, 1)
        a, b = pts[int(i)], pts[int(i) + 1]
        x = a[0] + (b[0] - a[0]) * s
        y = a[1] + (b[1] - a[1]) * s * s + 0.18 * s * (1 - s)   # small hop
        return np.array([x, y, 0])
    s = min((t - n_hops * HOP) / FALL, 1)
    a = pts[-1]
    return np.array([a[0] + (rest[0] - a[0]) * s, a[1] + (rest[1] - a[1]) * s * s, 0])


def expected_outline():
    """INK step outline of the expected heights 400 C(10,k) / 1024."""
    pts = [[bin_x(0) - DX / 2, FLOOR, 0]]
    for k in range(ROWS + 1):
        h = BALLS * comb(ROWS, k) / 2 ** ROWS / PER_LAYER * 2 * BALL_R
        pts += [[bin_x(k) - DX / 2, FLOOR + h, 0], [bin_x(k) + DX / 2, FLOOR + h, 0]]
    pts.append([bin_x(ROWS) + DX / 2, FLOOR, 0])
    return VMobject(color=INK, stroke_width=3).set_points_as_corners(pts)


class S12Galton(BeatScene):
    SCENE_ID = "S12"

    def construct(self):
        prev = s11_builds.end_state()
        self.add(prev)

        b = board()
        self.beat("every node becomes a peg: the Galton board",
                  FadeOut(prev), FadeIn(b[0]),
                  LaggedStart(*[FadeIn(p, scale=0.5) for p in b[1]], lag_ratio=0.01, run_time=1.0),
                  Create(b[2]), Create(b[3]))

        paths = simulate()
        filled = [0] * (ROWS + 1)
        tracks = []
        for path in paths:
            k = sum(path)
            tracks.append(ball_track(path, stack_pos(k, filled[k])))
            filled[k] += 1
        balls = VGroup(*[Dot(radius=BALL_R, color=A_BLUE).move_to(tr[0][0]).set_opacity(0)
                         for tr in tracks])
        fly = (ROWS + 1) * HOP + FALL
        total = (BALLS - 1) * RELEASE + fly

        # One animation drives all 400 balls: alpha (0..1) -> time -> positions.
        def place(group, alpha):
            t = alpha * total
            for i, (ball, tr) in enumerate(zip(group, tracks)):
                dt = t - i * RELEASE
                if dt < 0:
                    ball.set_opacity(0)
                else:
                    ball.set_opacity(1).move_to(position(tr, min(dt, fly)))

        self.add(balls)
        self.beat("400 balls fall; each bounces left or right at every peg",
                  UpdateFromAlphaFunc(balls, place, run_time=total, rate_func=linear))

        outline = expected_outline()
        mid = mono("98.4", 20, INK).next_to(outline.get_top(), UP, buff=0.12)
        note = ab_tex(r"400 \cdot \binom{10}{k} / 1024", font_size=30, color=MUTED)
        note.next_to(b[0], RIGHT, buff=0.4).set_y(FLOOR + 1.0)
        self.beat("expected heights 400 C(10,k) / 1024 as an outline",
                  Create(outline, run_time=1.2), FadeIn(mid), FadeIn(note))
