"""Scene 4 — The question: why should adding count choices?"""

from components import *
import s01_lookup
import s03_theorem

# Six cells where the addition rule is shown, one beat each: (row, position).
RULE_CELLS = [(2, 1), (3, 2), (4, 1), (5, 2), (6, 3), (6, 5)]


def big_triangle():
    return s01_lookup.triangle().scale_to_fit_height(6).move_to(ORIGIN)


def small_triangle():
    return s01_lookup.triangle().scale_to_fit_width(3.9).move_to([4.6, 0, 0])


def question():
    b = ab_tex(r"\binom{n}{k}", font_size=72)
    q = display("?", 110, INK)
    p = ab_tex("(a+b)^n", font_size=72)
    return VGroup(b, q, p).arrange(RIGHT, buff=0.9).move_to([-2.4, 0, 0])


def end_state():
    return VGroup(small_triangle(), question())


class S04Question(BeatScene):
    SCENE_ID = "S04"

    def construct(self):
        prev = s03_theorem.end_state()
        self.add(prev)
        tri = prev[1]

        big = big_triangle()
        self.beat("triangle to the centre, height 6",
                  FadeOut(VGroup(prev[0], prev[2], prev[3])),
                  Transform(tri, big, run_time=T_MORPH))
        tri = big   # Transform keeps the old object; give it the new geometry
        self.remove(prev[1])
        self.add(tri)

        marks = None
        for n, k in RULE_CELLS:
            box = focus_box(VGroup(tri.cell(n - 1, k - 1), tri.cell(n - 1, k)))
            arrows, plus = tri.rule_arrows(n, k)
            new = VGroup(box, arrows, plus)
            child = tri.cell(n, k)
            child.set_z_index(1)
            a, b = tri.cell(n - 1, k - 1).value, tri.cell(n - 1, k).value
            self.beat(f"rule: {a} + {b} = {child.value} at row {n}", Succession(
                AnimationGroup(*([FadeOut(marks)] if marks else []), Create(box),
                               GrowArrow(arrows[0]), GrowArrow(arrows[1]),
                               FadeIn(plus), run_time=0.7),
                pulse(child)))
            marks = new

        self.beat("triangle shrinks to the right third",
                  FadeOut(marks), tri.animate.become(small_triangle()),
                  run_time=T_MORPH)
        q = question()
        self.beat("binom(n,k)  ?  (a+b)^n", LaggedStart(
            FadeIn(q[0], shift=RIGHT * 0.2), FadeIn(q[1], scale=0.7),
            FadeIn(q[2], shift=LEFT * 0.2), lag_ratio=0.3, run_time=1.2))
