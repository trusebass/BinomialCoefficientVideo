"""Scene 3 — The statement that connects them (the binomial theorem)."""

from components import *
import s01_lookup
import s02_choosing


def theorem(font_size=56):
    """(a+b)^n = sum C(n,k) a^(n-k) b^k, every piece its own part."""
    return ab_tex("(a+b)^n", "=", r"\sum_{k=0}^{n}", r"\binom{n}{k}",
                  r"\,a^{n-k}", "b^{k}", font_size=font_size)


def theorem_corner():
    """The theorem after it moves to the upper left at scale 0.7."""
    t = theorem().scale(0.7)
    return t.to_corner(UL, buff=SAFE).shift(DOWN * 0.05)


def cell_binom(cell, n, k):
    """A small binom(n, k) that fits inside a cell, in the cell's text color."""
    b = ab_tex(rf"\binom{{{n}}}{{{k}}}", color=cell.label.get_fill_color())
    return b.scale_to_fit_height(cell.box.height * 0.84).move_to(cell.box)


def swap(old, new, run_time=0.5):
    """Fade `old` out completely, then fade `new` in: the two never overlap.
    (FadeTransform would stretch one into the other and show both at once.)"""
    return Succession(FadeOut(old, scale=0.85, run_time=run_time / 2),
                      FadeIn(new, scale=0.85, run_time=run_time / 2))


def end_state():
    t = theorem_corner()
    tri = s01_lookup.triangle()
    return VGroup(t, tri, tri.row_labels(), tri.k_labels())


class S03Theorem(BeatScene):
    SCENE_ID = "S03"

    def construct(self):
        prev = s02_choosing.end_state()
        self.add(prev)
        old_binom = prev[0][2]

        t = theorem()
        binom = part(t, r"\binom{n}{k}")
        power = part(t, "(a+b)^n")
        rest = VGroup(*[p for p in t if p is not binom and p is not power])

        # The two things to connect, side by side: (a+b)^n mirrors C(n,k),
        # which stays exactly where Scene 2 left it.
        lone_power = ab_tex("(a+b)^n", font_size=56)
        lone_power.move_to([-old_binom.get_x(), old_binom.get_y(), 0])
        self.beat("(a+b)^n on the left, C(n,k) stays on the right",
                  FadeOut(VGroup(prev[0][0], prev[0][1], prev[1], prev[2])),
                  FadeIn(lone_power, shift=RIGHT * 0.2))
        box = focus_box(lone_power, buff=0.12)
        self.beat("outline (a+b)^n", Create(box))
        box_b = focus_box(old_binom, buff=0.12)
        self.beat("outline moves to C(n,k)", ReplacementTransform(box, box_b))
        self.beat("the binomial theorem bridges them",
                  FadeOut(box_b, run_time=0.4),
                  ReplacementTransform(lone_power, power, run_time=T_MORPH),
                  ReplacementTransform(old_binom, binom, run_time=T_MORPH),
                  FadeIn(rest, lag_ratio=0.1, run_time=T_MORPH))

        # Walk through the formula, one yellow outline at a time.
        steps = [("multiply out: (a+b)^n", [r"(a+b)^n"]),
                 ("a sum over all combinations", [r"\sum_{k=0}^{n}"]),
                 ("powers of a and b", [r"\,a^{n-k}", "b^{k}"]),
                 ("coefficient", [r"\binom{n}{k}"])]
        box = note = None
        for desc, keys in steps:
            new = focus_box(VGroup(*[part(t, k) for k in keys]), buff=0.1)
            anims = [Create(new)] if box is None else [ReplacementTransform(box, new)]
            if note is not None:
                anims.append(FadeOut(note))
                note = None
            if "powers" in desc:
                note = ab_tex("(n-k) + k = n", font_size=32, color=MUTED)
                note.next_to(new, DOWN, buff=0.3)
                anims.append(FadeIn(note, shift=UP * 0.1))
            self.beat(desc, *anims)
            box = new

        # "the number from Pascal's triangle": formula to the corner, triangle in
        tri = s01_lookup.triangle()
        corner = theorem_corner()
        self.beat("formula to the upper left, triangle fades in",
                  FadeOut(box),
                  Transform(t, corner, run_time=T_MORPH),
                  FadeIn(tri, run_time=T_MORPH))

        self.beat("row labels n = 0 ... 6", LaggedStart(
            *[FadeIn(l, shift=RIGHT * 0.1) for l in tri.row_labels()], lag_ratio=LAG))
        self.beat("position labels k = 0 ... 6", LaggedStart(
            *[FadeIn(l, shift=UP * 0.1) for l in tri.k_labels()], lag_ratio=LAG))

        # Rows 0-4: every number cross-fades to binom(n, k), then back.
        cells = [(n, k) for n in range(5) for k in range(n + 1)]
        binoms = {nk: cell_binom(tri.cell(*nk), *nk) for nk in cells}
        labels = {nk: tri.cell(*nk).label for nk in cells}
        # One LaggedStart entry per row: the swap sweeps down the triangle.
        rows = lambda a, b: [AnimationGroup(*[swap(a[n, k], b[n, k]) for k in range(n + 1)])
                             for n in range(5)]
        self.beat("cells show binom(n, k)", LaggedStart(*rows(labels, binoms),
                                                        lag_ratio=0.35, run_time=1.6))
        self.beat("cells back to numbers", LaggedStart(*rows(binoms, labels),
                                                       lag_ratio=0.35, run_time=1.6))
