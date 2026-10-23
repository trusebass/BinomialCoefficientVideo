"""Scene 12 — Coda: the Galton board."""

import math
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
    panel.set_z_index(-2)   # always at the back, even when it is re-added later
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


BIG, BIG_FLOOR = 1.5, -2.45          # the distribution, enlarged and centred
HOME_SCALE, HOME_X = 0.9, 2.6        # the board's place when it is spelled out


def expected(t):
    """400 C(10, t) / 1024, for real t too (C via the Gamma function), so the
    line through the exact values at t = 0..10 is smooth and never dips."""
    c = math.gamma(ROWS + 1) / (math.gamma(t + 1) * math.gamma(ROWS - t + 1))
    return BALLS * c / 2 ** ROWS


def height(count):
    """Height of a pile of `count` balls (PER_LAYER per layer)."""
    return count / PER_LAYER * 2 * BALL_R


def to_big(p):
    """Board coordinates -> the enlarged, centred histogram."""
    return np.array([p[0] * BIG, BIG_FLOOR + (p[1] - FLOOR) * BIG, 0])


def to_home(mob):
    """The whole board, smaller and moved right to make room for text."""
    return mob.scale(HOME_SCALE, about_point=ORIGIN).shift(RIGHT * HOME_X)


def bin_labels():
    """0 ... 10 under the bins: how many times the ball went right."""
    return VGroup(*[mono(str(k), 16, MUTED).move_to([bin_x(k), FLOOR - 0.2, 0])
                    for k in range(ROWS + 1)])


def binomial_curve():
    """The binomial distribution over the enlarged histogram: a line through
    the exact values, and a dot at each of them."""
    pt = lambda t: to_big([(t - ROWS / 2) * DX, FLOOR + height(expected(t)), 0])
    line = ParametricFunction(pt, t_range=[-0.4, ROWS + 0.4], color=INK, stroke_width=4)
    dots = VGroup(*[Dot(pt(k), radius=0.06, color=INK) for k in range(ROWS + 1)])
    return VGroup(line, dots).set_z_index(1)


def explainer():
    """Left of the board: what the viewer is looking at."""
    title = display("Galton board", 48)
    lines = VGroup(mono("every peg: left or right, 50/50", 20, MUTED),
                   mono("bin k: k bounces to the right", 20, MUTED))
    lines.arrange(DOWN, aligned_edge=LEFT, buff=0.16)
    g = VGroup(title, lines).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
    return g.to_edge(LEFT, buff=SAFE).set_y(1.1)


def tease(above):
    t = display("Central Limit Theorem", 40)
    sub = mono("for another video", 18, MUTED)
    g = VGroup(t, sub).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
    return g.next_to(above, DOWN, buff=1.0, aligned_edge=LEFT)


class S12Galton(BeatScene):
    SCENE_ID = "S12"

    def construct(self):
        prev = s11_builds.end_state()
        self.add(prev)

        b = board()
        panel, pegs, walls, floor = b
        self.beat("every node becomes a peg: the Galton board",
                  FadeOut(prev), FadeIn(panel),
                  LaggedStart(*[FadeIn(p, scale=0.5) for p in pegs], lag_ratio=0.01, run_time=1.0),
                  Create(walls), Create(floor))

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

        # ---- the distribution, enlarged in the middle -------------------------
        labels = bin_labels()
        hist = VGroup(walls, floor, balls, labels)
        home = to_home(VGroup(panel, pegs, hist).copy())   # board pose for later
        big = hist.copy()
        big.apply_function(to_big)
        for d, src in zip(big[2], balls):                  # keep the balls round
            d.scale_to_fit_width(src.width * BIG)
        for lab, src in zip(big[3], labels):               # and the numbers upright
            lab.become(src.copy().scale(BIG).move_to(to_big(src.get_center())))
        self.beat("pegs fade; the distribution grows to the middle; bins 0-10",
                  FadeOut(panel), FadeOut(pegs),
                  Transform(VGroup(walls, floor, balls), big[:3], run_time=1.2),
                  FadeIn(big[3], run_time=1.2))
        self.remove(*labels)
        labels = big[3]

        curve = binomial_curve()
        title = display("binomial distribution", 52).move_to([0, 2.15, 0])
        self.beat("the binomial distribution drawn over it",
                  Create(curve[0], run_time=1.4), LaggedStart(
                      *[FadeIn(d, scale=0.5) for d in curve[1]], lag_ratio=0.08, run_time=1.4),
                  FadeIn(title, shift=DOWN * 0.15))
        apps = mono("probability  ·  error-correcting codes  ·  option pricing", 22, MUTED)
        apps.next_to(title, DOWN, buff=0.3)
        self.beat("where it leads: probability, codes, option pricing",
                  FadeIn(apps, shift=UP * 0.1))

        # ---- the Galton board, spelled out -----------------------------------
        h_panel, h_pegs, h_hist = home
        panel.become(h_panel)
        pegs.become(h_pegs)
        ex = explainer()
        self.beat("back to the board: 'Galton board', every peg 50/50",
                  FadeOut(VGroup(curve, title, apps), run_time=0.5),
                  Transform(VGroup(walls, floor, balls, labels), h_hist, run_time=1.2),
                  FadeIn(panel, run_time=1.2), FadeIn(pegs, run_time=1.2),
                  FadeIn(ex, shift=RIGHT * 0.2, run_time=1.2))

        # One ball's route: ten left/right choices, then its bin.
        pts, rest = tracks[0]
        route = VMobject(color=PATH_AQUA, stroke_width=5)
        route.set_points_as_corners([*pts, rest])
        to_home(route).set_z_index(1)
        self.beat("one ball's route: ten 50/50 choices", Create(route, run_time=2.0,
                                                                rate_func=linear))

        tz = tease(ex)
        self.beat("tease: the Central Limit Theorem", FadeOut(route, run_time=0.4),
                  FadeIn(tz, shift=UP * 0.15))
        self.beat("fade to background (crossfade into the end screen)",
                  FadeOut(Group(*self.mobjects), run_time=1.0))
