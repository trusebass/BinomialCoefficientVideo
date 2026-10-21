"""Scene 2 — Choosing (the Swiss lottery, 6 out of 42)."""

from components import *
import s01_lookup

DRAW = [3, 11, 17, 24, 30, 41]
BALL_R = 0.26
GRID_C = np.array([-3.6, 0.1, 0])
SLOT_Y, SLOT_X0, SLOT_DX = 1.55, 0.6, 1.1
ORDINALS = ["1st", "2nd", "3rd", "4th", "5th", "6th"]
# four quick reorderings of the six slots; the last one restores the draw order
SHUFFLES = [[2, 0, 5, 1, 4, 3], [4, 3, 0, 5, 2, 1], [1, 5, 3, 0, 4, 2], [0, 1, 2, 3, 4, 5]]


def ball(n):
    # No fill: animating only the circle (ball[0]) makes play() add it to the
    # scene as its own mobject, drawn on top of the ball group. An opaque fill
    # would then cover the number.
    c = Circle(radius=BALL_R, stroke_color=RULE, stroke_width=2, fill_opacity=0)
    return VGroup(c, mono(str(n), 20, INK).move_to(c))


def grid():
    balls = VGroup(*[ball(n) for n in range(1, 43)])
    balls.arrange_in_grid(rows=6, cols=7, buff=0.14).move_to(GRID_C)
    return balls


def slot_pos(i):
    return np.array([SLOT_X0 + i * SLOT_DX, SLOT_Y, 0])


def fraction(num, den, font_size=44):
    """A fraction built from two ab_tex rows and a bar, so the parts of the
    numerator and denominator can be transformed one by one."""
    n = ab_tex(*num, font_size=font_size)
    d = ab_tex(*den, font_size=font_size)
    bar = Line(LEFT, RIGHT, color=INK, stroke_width=2.2)
    bar.set_width(max(n.width, d.width) + 0.15)
    return VGroup(n, bar, d).arrange(DOWN, buff=0.1)


def general_formula():
    f = fraction(["n", "!"], ["(n-k)", "!", r"\,k", "!"], 52)
    eq = ab_tex("=", font_size=52)
    b = ab_tex(r"\binom{n}{k}", font_size=52)
    return VGroup(f, eq, b).arrange(RIGHT, buff=0.25).move_to(UP * 0.6)


def choose_label(formula):
    t = display("n choose k", 52).next_to(formula, DOWN, buff=0.7)
    line = focus_line(VGroup(*t[1:7]), buff=0.1)   # glyphs c-h-o-o-s-e
    return t, line


def end_state():
    f = general_formula()
    t, line = choose_label(f)
    return VGroup(f, t, line)


class S02Choosing(BeatScene):
    SCENE_ID = "S02"

    def construct(self):
        prev = s01_lookup.end_state()
        self.add(prev)

        symbol = ab_tex(r"\binom{n}{k}", font_size=170)
        self.beat("the symbol n choose k, big in the middle",
                  FadeOut(prev, run_time=T_FADE), FadeIn(symbol, scale=0.85))
        corner = ab_tex(r"\binom{n}{k}", font_size=40).to_corner(UP + LEFT, buff=SAFE).shift(RIGHT * 0.7)

        balls = grid()
        slots = VGroup(*[DashedVMobject(Circle(radius=BALL_R + 0.04, color=MUTED,
                                               stroke_width=1.5), num_dashes=16)
                         .move_to(slot_pos(i)) for i in range(6)])
        ordinals = VGroup(*[mono(o, 20, MUTED).next_to(s, UP, buff=0.2)
                            for o, s in zip(ORDINALS, slots)])
        self.beat("symbol to the corner; 42 balls and six empty slots",
                  symbol.animate.become(corner),
                  LaggedStart(*[FadeIn(b, scale=0.8) for b in balls],
                              lag_ratio=0.03, run_time=1.2),
                  FadeIn(slots), FadeIn(ordinals))

        drawn, counts = [], VGroup()
        for i, num in enumerate(DRAW):
            b = balls[num - 1]
            count = mono(str(42 - i), 26, INK).next_to(slots[i], DOWN, buff=0.25)
            anims = []
            if drawn:   # rule A.1-3: the previous focus goes before the next one
                anims.append(drawn[-1][0].animate.set_stroke(INK2, width=2))
            self.beat(f"draw ball {num} into slot {i + 1}, {42 - i} left", Succession(
                AnimationGroup(*anims, b[0].animate.set_stroke(FOCUS_YELLOW, width=3),
                               run_time=0.3),
                AnimationGroup(b.animate(path_arc=-PI / 4).move_to(slot_pos(i)),
                               FadeIn(count, shift=UP * 0.1), run_time=0.9)))
            drawn.append(b)
            counts.add(count)

        # 42 · 41 · … · 37 = 42!/36!
        prod = ab_tex(*sum([[str(42 - i)] + ([r"\cdot"] if i < 5 else []) for i in range(6)], []),
                      font_size=40)
        eq1 = ab_tex("=", font_size=40)
        frac = fraction(["42", "!"], ["36", "!"], 40)
        line_a = VGroup(prod, eq1, frac).arrange(RIGHT, buff=0.2).move_to([3.35, -0.45, 0])
        numbers = [p for p in prod if p.tex_string != r"\cdot"]
        dots = [p for p in prod if p.tex_string == r"\cdot"]
        self.beat("the six counts combine into a product", Succession(
            AnimationGroup(drawn[-1][0].animate.set_stroke(INK2, width=2), run_time=0.3),
            AnimationGroup(*[ReplacementTransform(c, p) for c, p in zip(counts, numbers)],
                           *[FadeIn(d) for d in dots], run_time=T_MORPH)))
        self.beat("= 42!/36!", Write(eq1), FadeIn(frac, shift=LEFT * 0.2))

        big = VGroup(ab_tex("=", font_size=40), mono("3 776 965 920", 32, INK))
        big.arrange(RIGHT, buff=0.25).next_to(line_a, DOWN, buff=0.55)
        self.beat("= 3 776 965 920 ordered draws", FadeIn(big, shift=UP * 0.15))

        # Order does not matter: the same six balls in other orders.
        same = mono("same ticket", 24, INK).move_to([slot_pos(0)[0] + 2.75, 2.35, 0])
        shuffles = []
        order = list(range(6))   # order[slot] = index of the ball in that slot
        for perm in SHUFFLES:
            shuffles.append(AnimationGroup(*[
                drawn[j].animate(path_arc=PI / 2).move_to(slot_pos(s))
                for s, j in enumerate(perm)], run_time=0.4))
        self.beat("same ticket: four reorderings",
                  Succession(AnimationGroup(FadeOut(ordinals), FadeIn(same), run_time=T_FADE),
                             *shuffles))
        orders = mono("6! = 720 orders", 24, INK).next_to(slots, DOWN, buff=0.28)
        self.beat("6! = 720 orders", FadeIn(orders, shift=UP * 0.1))

        # Divide by 6!: 42!/(36! 6!) = 5 245 786
        frac2 = fraction(["42", "!"], ["36", "!", r"\,6", "!"], 46)
        eq2 = ab_tex("=", font_size=46)
        res = mono("5 245 786", 34, INK)
        line_b = VGroup(frac2, eq2, res).arrange(RIGHT, buff=0.25).move_to([3.35, -1.0, 0])
        self.beat("divide by 6!", FadeOut(VGroup(prod, eq1, big)),
                  ReplacementTransform(frac[0], frac2[0]),
                  ReplacementTransform(frac[1], frac2[1]),
                  ReplacementTransform(frac[2][0], frac2[2][0]),
                  ReplacementTransform(frac[2][1], frac2[2][1]),
                  FadeIn(frac2[2][2:], shift=UP * 0.1), run_time=T_MORPH)
        self.beat("= 5 245 786 tickets", Write(eq2), FadeIn(res, shift=LEFT * 0.2))

        # The general form: 42 -> n, 36 -> n - k, 6 -> k.
        gen = general_formula()
        f, eq3, binom = gen
        self.beat("numbers become n, k: n!/((n-k)! k!) = C(n,k)",
                  FadeOut(VGroup(balls, slots, same, orders), run_time=T_FADE),
                  *[ReplacementTransform(a, b) for a, b in
                    [(frac2[0][0], f[0][0]), (frac2[0][1], f[0][1]), (frac2[1], f[1]),
                     (frac2[2][0], f[2][0]), (frac2[2][1], f[2][1]),
                     (frac2[2][2], f[2][2]), (frac2[2][3], f[2][3]), (eq2, eq3)]],
                  FadeOut(res), run_time=T_MORPH)
        self.beat("= binom(n, k): the symbol from the corner",
                  ReplacementTransform(symbol, binom, run_time=T_MORPH))
        t, line = choose_label(gen)
        self.beat("n choose k", FadeIn(t, shift=UP * 0.15))
        self.beat("underline 'choose'", Create(line))
