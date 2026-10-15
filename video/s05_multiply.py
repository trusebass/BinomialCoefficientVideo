"""Scene 5 — Multiplying out, one pick per bracket."""

from components import *
import s04_question

PICKS = words(3)        # aaa, aab, aba, abb, baa, bab, bba, bbb
TALLY_Y = 0.6
GROUPS = [["aaa"], ["aab", "aba", "baa"], ["abb", "bab", "bba"], ["bbb"]]


def header():
    """BracketRow(3) in the header band, '=' to its right."""
    row = BracketRow(3)
    row.shift([-2.5, 3.15, 0] - row.tex.get_center())
    eq = ab_tex("=").next_to(row.tex, RIGHT, buff=0.35)
    return row, eq


def tally():
    """a^3 + a^2b + a^2b + ab^2 + a^2b + ab^2 + ab^2 + b^3, one part per term."""
    args = []
    for j, w in enumerate(PICKS):
        args += (["+"] if j else []) + [product_tex(w)]
    t = ab_tex(*args, font_size=44).move_to([0, TALLY_Y, 0])
    return t, [t[2 * j] for j in range(8)], [t[2 * j - 1] for j in range(1, 8)]


def word_label(w):
    return mono(w, 18, MUTED)


def merged():
    """a^3 + 3a^2b + 3ab^2 + b^3, with its pick words stacked under each term."""
    m = ab_tex("a^{3}", "+", "3", "a^{2}b", "+", "3", "ab^{2}", "+", "b^{3}",
               font_size=44).move_to([0, TALLY_Y, 0])
    terms = [VGroup(m[0]), VGroup(m[2], m[3]), VGroup(m[5], m[6]), VGroup(m[8])]
    stacks = VGroup()
    for g, term in zip(GROUPS, terms):
        col = VGroup(*[word_label(w) for w in g]).arrange(DOWN, buff=0.1)
        col.next_to(term, DOWN, buff=0.25).set_x(term[-1].get_x())
        stacks.add(col)
    base = min(c[0].get_bottom()[1] for c in stacks)
    for c in stacks:                      # first words share one baseline
        c.shift(UP * (base - c[0].get_bottom()[1]))
    return m, terms, stacks


def corner_triangle():
    tri = PascalTriangle(3).scale(0.8).to_corner(UR, buff=SAFE)
    return tri, focus_box(tri.row(3))


def end_state():
    row, _ = header()
    m, _, stacks = merged()
    tri, box = corner_triangle()
    return VGroup(row, m, stacks, tri, box)


class S05Multiply(BeatScene):
    SCENE_ID = "S05"

    def construct(self):
        prev = s04_question.end_state()
        self.add(prev)
        tri_old, (binom, q, power_n) = prev[0], prev[1]

        row, eq = header()
        power3 = ab_tex("(a+b)", "^{3}").move_to(row.tex)
        self.beat("(a+b)^n becomes (a+b)^3 in the header",
                  FadeOut(VGroup(tri_old, binom, q)),
                  ReplacementTransform(power_n, power3, run_time=T_MORPH))
        self.beat("(a+b)^3 = (a+b)(a+b)(a+b), bracket numbers",
                  *[TransformFromCopy(power3[0], br) for br in row.brackets],
                  FadeOut(power3), FadeIn(row.dots), FadeIn(row.numbers, shift=UP * 0.1),
                  FadeIn(eq), run_time=T_MORPH)

        t_full, t_terms, t_plus = tally()
        work = {}   # objects that live from one step to the next

        def fly(w, rt):
            def step():
                target = ab_tex(w[0], r"\cdot", w[1], r"\cdot", w[2])
                target.next_to(eq, RIGHT, buff=0.35)
                work["target"] = target
                return [AnimationGroup(
                    *[TransformFromCopy(row.letter(i, w[i]), target[2 * i]) for i in range(3)],
                    FadeIn(target[1]), FadeIn(target[3]), run_time=rt)]
            return step

        def simplify(w, rt):
            def step():
                target = work["target"]
                # TransformFromCopy left the parts as separate scene mobjects;
                # swap them for their parent so it can be transformed as one.
                self.remove(*target.submobjects)
                self.add(target)
                prod = ab_tex(product_tex(w)).next_to(eq, RIGHT, buff=0.35)
                work["prod"] = prod
                return [TransformMatchingShapes(target, prod, run_time=rt)]
            return step

        def to_tally(j, w, rt):
            def step():
                lab = word_label(w).next_to(t_terms[j], DOWN, buff=0.25)
                bottoms_at([lab], TALLY_Y - 0.72)
                anims = [ReplacementTransform(work["prod"], t_terms[j]), FadeIn(lab)]
                if j:
                    anims.append(FadeIn(t_plus[j - 1]))
                anims += row.reset()
                return [AnimationGroup(*anims, run_time=rt)]
            return step

        def pick_steps(j, w, rt):
            """All steps of one pick: 3 letter choices, fly, simplify, tally."""
            return ([lambda i=i: [AnimationGroup(*row.pick(i, w[i]), run_time=rt)]
                     for i in range(3)]
                    + [fly(w, 2 * rt), simplify(w, 2 * rt), to_tally(j, w, 2 * rt)])

        # Picks 1-2: every step is its own beat.
        names = ["pick bracket 1", "pick bracket 2", "pick bracket 3",
                 "copies fly right of =", "multiply into one term", "term joins the tally"]
        for j in range(2):
            for name, step in zip(names, pick_steps(j, PICKS[j], 0.4)):
                self.beat(f"{PICKS[j]}: {name}", steps=[step])
        # Picks 3-5: one beat per pick.
        for j in range(2, 5):
            self.beat(f"{PICKS[j]}: whole pick", steps=pick_steps(j, PICKS[j], 0.22))
        # Picks 6-8: one quick beat for all three.
        self.beat("bab, bba, bbb: quick", steps=sum(
            [pick_steps(j, PICKS[j], 0.12) for j in range(5, 8)], []))

        counter = mono("2 · 2 · 2 = 8 terms", 24, INK)
        counter.to_edge(RIGHT, buff=SAFE).set_y(3.15)
        self.beat("counter 2·2·2 = 8 terms", FadeIn(counter, shift=DOWN * 0.1))

        # Collect like terms: slide into groups, then merge.
        labels = {w: m for w, m in zip(PICKS, [mob for mob in self.mobjects
                                              if isinstance(mob, Text) and mob.text in PICKS])}
        order = sum(GROUPS, [])
        g_args = []
        for i, w in enumerate(order):
            g_args += (["+"] if i else []) + [product_tex(w)]
        grouped = ab_tex(*g_args, font_size=44)
        gap = 0.45
        for i, w in enumerate(order):   # spread the groups apart
            g = next(gi for gi, grp in enumerate(GROUPS) if w in grp)
            grouped[2 * i].shift(RIGHT * g * gap)
            if i:
                g_prev = next(gi for gi, grp in enumerate(GROUPS) if order[i - 1] in grp)
                grouped[2 * i - 1].shift(RIGHT * (g + g_prev) / 2 * gap)
        grouped.move_to([0, TALLY_Y, 0])
        slide = []
        for i, w in enumerate(order):
            j = PICKS.index(w)
            dx = grouped[2 * i].get_center() - t_terms[j].get_center()
            slide += [t_terms[j].animate.move_to(grouped[2 * i]),
                      labels[w].animate.shift(dx)]
        slide += [p.animate.move_to(grouped[2 * i + 1]) for i, p in enumerate(t_plus)]
        self.beat("like terms slide together", *slide, run_time=T_MORPH)

        m, terms, stacks = merged()
        merge = [FadeOut(eq), FadeOut(counter)]
        plus_targets = [m[1], None, None, m[4], None, None, m[7]]
        for p, target in zip(t_plus, plus_targets):
            merge.append(ReplacementTransform(p, target) if target else FadeOut(p))
        for g, term, col in zip(GROUPS, terms, stacks):
            mono_part = term[-1]
            for i, w in enumerate(g):
                src = t_terms[PICKS.index(w)]
                merge.append(ReplacementTransform(src, mono_part) if i == 0
                             else FadeOut(src, target_position=mono_part))
                merge.append(labels[w].animate.move_to(col[i]))
            if len(term) > 1:
                merge.append(FadeIn(term[0], shift=RIGHT * 0.1))
        self.beat("merge: a^3 + 3a^2b + 3ab^2 + b^3", *merge, run_time=T_MORPH)

        coef_boxes = VGroup(focus_box(m[2]), focus_box(m[5]))
        self.beat("outline the coefficients 3, 3", Create(coef_boxes))
        tri, box = corner_triangle()
        self.beat("corner triangle, row 3 highlighted", Succession(
            AnimationGroup(FadeOut(coef_boxes), FadeIn(tri), run_time=T_FADE),
            Create(box, run_time=0.5)))
