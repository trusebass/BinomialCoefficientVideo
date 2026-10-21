"""Scene 1 — The lookup table.

    manim -ql s01_lookup.py S01Lookup      (draft)
    manim -qh s01_lookup.py S01Lookup      (final, 1080p60)
"""

from components import *

LEFT_CX = -3.6
TRI_CX = 2.8

# The expansions of (a+b)^n as (coefficient, monomial) pairs; coefficient 1 is
# not written, exactly like on paper.
EXPANSIONS = {
    0: [(1, "1")],
    1: [(1, "a"), (1, "b")],
    2: [(1, "a^{2}"), (2, "ab"), (1, "b^{2}")],
    3: [(1, "a^{3}"), (3, "a^{2}b"), (3, "ab^{2}"), (1, "b^{3}")],
    4: [(1, "a^{4}"), (4, "a^{3}b"), (6, "a^{2}b^{2}"), (4, "ab^{3}"), (1, "b^{4}")],
}


def triangle():
    """The Scene 1 triangle: rows 0-6, height 5, centred at x = 2.8."""
    return PascalTriangle(6).scale_to_fit_height(5).move_to(RIGHT * TRI_CX)


def power_line(n="n"):
    """(a+b)^n with the exponent as its own part, so TransformMatchingTex
    keeps (a+b) in place and only swaps the exponent."""
    return ab_tex("(a+b)", f"^{{{n}}}", font_size=48)


def expansion_line(n):
    """'= a^2 + 2ab + b^2' with every coefficient and monomial its own part.

    Returns (tex, terms): terms[k] is the VGroup of parts for term k.
    """
    args, owners = ["="], [None]
    for k, (c, m) in enumerate(EXPANSIONS[n]):
        if k:
            args.append("+")
            owners.append(None)
        if c > 1:
            args.append(str(c))
            owners.append(k)
        args.append(m)
        owners.append(k)
    tex = ab_tex(*args, font_size=42)
    terms = [VGroup(*[p for p, o in zip(tex, owners) if o == k])
             for k in range(n + 1)]
    return tex, terms


def left_side(n):
    """Both lines of the left side for row n, placed and fitted."""
    top = power_line(n)
    eq, terms = expansion_line(n)
    eq.scale_to_fit_width(min(eq.width, 4.9))
    VGroup(top, eq).arrange(DOWN, buff=0.45).move_to([LEFT_CX, 0.2, 0])
    return VGroup(top, eq), terms


def row_label(tri, n):
    return mono(f"n = {n}", 22 * tri.k, MUTED).next_to(tri.row(n), LEFT, buff=0.3)


def end_state():
    """Everything on screen when Scene 1 ends (Scene 2 starts from it)."""
    tri = triangle()
    left, _ = left_side(4)
    pair = focus_box(VGroup(tri.cell(3, 1), tri.cell(3, 2)))
    plus = tri.rule_plus(4, 2)
    return VGroup(tri, left, pair, plus)


class S01Lookup(BeatScene):
    SCENE_ID = "S01"

    def construct(self):
        tri = triangle()

        # LaggedStart starts each row a little after the previous one:
        # every row fades in for 0.5 s, the next starts 0.2 s later.
        self.beat("triangle appears row by row", LaggedStart(
            *[FadeIn(r, shift=DOWN * 0.15) for r in tri.cells],
            lag_ratio=0.4, run_time=0.5 * (1 + 0.4 * 6)))

        left = VGroup(power_line()).move_to([LEFT_CX, 0.2, 0])
        self.beat("(a+b)^n on the left", Write(left, run_time=T_WRITE))

        label = box = notes = None
        for n in range(5):
            new_left, terms = left_side(n)
            new_label = row_label(tri, n)
            new_box = focus_box(tri.row(n))
            anims = [TransformMatchingTex(left, new_left, run_time=T_MORPH)]
            if label is None:
                anims += [FadeIn(new_label), Create(new_box)]
            else:
                anims += [ReplacementTransform(label, new_label),
                          ReplacementTransform(box, new_box)]
            if notes is not None:
                anims.append(FadeOut(notes))
                notes = None
            self.beat(f"n = {n}: row {n} and its expansion", *anims)
            left, label, box = new_left, new_label, new_box

            if n in (2, 3):
                # Reading off: each number flies from its cell to sit under
                # its term, including the 1s that are never written.
                notes = VGroup(*[
                    mono(str(tri.cell(n, k).value), 22, MUTED).next_to(t, DOWN, buff=0.18)
                    for k, t in enumerate(terms)])
                notes.set_y(min(nt.get_y() for nt in notes))
                self.beat(f"n = {n}: coefficients read off the row", LaggedStart(
                    *[TransformFromCopy(tri.cell(n, k).label, nt)
                      for k, nt in enumerate(notes)], lag_ratio=LAG, run_time=1.0))

        # The addition rule, shown once: 3 + 3 -> 6.
        pair = focus_box(VGroup(tri.cell(3, 1), tri.cell(3, 2)))
        self.beat("outline the two 3s in row 3",
                  FadeOut(box), FadeOut(label), Create(pair))
        plus = tri.rule_plus(4, 2)
        self.beat("plus sign between the 3s", FadeIn(plus, scale=0.6))
        six = tri.cell(4, 2)
        six.set_z_index(1)
        self.beat("the 6 pulses", pulse(six))
