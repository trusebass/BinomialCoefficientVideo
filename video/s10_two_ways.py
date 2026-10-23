"""Scene 10 — Two ways to count the same paths."""

from components import *
import s09_last_step

WORDS = ["aabb", "abab", "abba", "baab", "baba", "bbaa"]
ENDS_B = ["aabb", "abab", "baab"]
ENDS_A = ["abba", "baba", "bbaa"]
WORD_X, WORD_Y0, WORD_DY = -5.3, 2.4, 0.56


def gen_cell(tex):
    lab = ab_tex(tex, font_size=40)
    box = RoundedRectangle(width=lab.width + 0.5, height=lab.height + 0.3,
                           corner_radius=0.12, stroke_width=0,
                           fill_color=CELL_LO, fill_opacity=1)
    return VGroup(box, lab.move_to(box))


def diagram():
    """binom(n,k) with its parents: x b from the upper left, x a from the right."""
    child = gen_cell(r"\binom{n}{k}").move_to([0, 0.35, 0])
    left = gen_cell(r"\binom{n-1}{k-1}").move_to([-1.55, 2.6, 0])
    right = gen_cell(r"\binom{n-1}{k}").move_to([1.55, 2.6, 0])
    eb = edge_between(left, child, pad=0.08, color=B_ORANGE, stroke_width=4)
    ea = edge_between(right, child, pad=0.08, color=A_BLUE, stroke_width=4)
    lb = ab_tex(r"\times b", font_size=30).next_to(eb.get_center(), LEFT, buff=0.25)
    la = ab_tex(r"\times a", font_size=30).next_to(ea.get_center(), RIGHT, buff=0.25)
    return VGroup(child, left, right, eb, ea, lb, la)


def equation():
    return ab_tex(r"\binom{n}{k}", "=", r"\binom{n-1}{k-1}", "+", r"\binom{n-1}{k}",
                  font_size=52).move_to([0, -1.55, 0])


def last_step_note(eq_part, letter, color):
    line = Underline(eq_part, color=color, stroke_width=4, buff=0.1)
    lab = mono(f"last step ×{letter}", 22, MUTED).next_to(line, DOWN, buff=0.18)
    lab[-1].set_color(color)       # only the letter in its color
    return VGroup(line, lab)


def word_mob(w):
    return mono(w, 32, ab=True)


def sorted_y(w):
    if w in ENDS_B:
        return WORD_Y0 - ENDS_B.index(w) * WORD_DY
    return WORD_Y0 - (ENDS_A.index(w) + 3) * WORD_DY - 0.45


def group_label(ws, tex, color):
    grp = VGroup(*[word_mob(w).move_to([WORD_X, sorted_y(w), 0]) for w in ws])
    br = Brace(grp, RIGHT, buff=0.18, color=color)
    lab = ab_tex(tex, font_size=40).next_to(br, RIGHT, buff=0.15)
    return VGroup(br, lab)


def right_half(mob):
    return mob.scale(0.72).shift(RIGHT * 3.35)


def end_state():
    d, eq = diagram(), equation()
    notes = VGroup(last_step_note(eq[2], "b", B_ORANGE), last_step_note(eq[4], "a", A_BLUE))
    right = right_half(VGroup(d, eq, notes))
    ws = VGroup(*[word_mob(w).move_to([WORD_X, sorted_y(w), 0]) for w in WORDS])
    gb = group_label(ENDS_B, r"\binom{3}{1} = 3", B_ORANGE)
    ga = group_label(ENDS_A, r"\binom{3}{2} = 3", A_BLUE)
    total = ab_tex("3 + 3 = 6 =", r"\binom{4}{2}", font_size=42)
    total.next_to(VGroup(ws, gb, ga), DOWN, buff=0.5).align_to(ws, LEFT)
    return VGroup(right, ws, gb, ga, total)


class S10TwoWays(BeatScene):
    SCENE_ID = "S10"

    def construct(self):
        prev, lat = s09_last_step.end_state()
        self.add(prev)

        # Every b-step in the lattice: x b edges bold, x a edges pushed back.
        b_edges = [e for (n, k, st), e in lat.edges.items() if st == "b"]
        a_edges = [e for (n, k, st), e in lat.edges.items() if st == "a"]
        self.beat("highlight every b-step (x b edge) in the lattice",
                  *[e.animate.set_stroke(width=6, opacity=1) for e in b_edges],
                  *[e.animate.set_stroke(opacity=0.15) for e in a_edges])

        d = diagram()
        child, left, right, eb, ea, lb, la = d
        keep = {id(m) for m in (lat.cells[4, 2], lat.cells[3, 1], lat.cells[3, 2],
                                lat.edges[3, 1, "b"], lat.edges[3, 2, "a"])}
        rest = [m for m in prev.get_family() if m.has_points() and
                not any(id(a) in keep for a in [m, *[p for p in prev.get_family()
                                                      if m in p.get_family()]])]
        self.beat("a^2b^2 and its parents become binom(n,k) and its parents",
                  FadeOut(VGroup(*rest)),
                  ReplacementTransform(lat.cells[4, 2], child),
                  ReplacementTransform(lat.cells[3, 1], left),
                  ReplacementTransform(lat.cells[3, 2], right),
                  ReplacementTransform(lat.edges[3, 1, "b"], eb),
                  ReplacementTransform(lat.edges[3, 2, "a"], ea),
                  FadeIn(lb), FadeIn(la), run_time=T_MORPH)

        # The three binomials, one after the other as the narration names them.
        box = focus_box(child)
        self.beat("outline binom(n,k)", Create(box))
        for cell, name in ((left, "binom(n-1,k-1), top left"), (right, "binom(n-1,k), top right")):
            new = focus_box(cell)
            self.beat(f"outline {name}", ReplacementTransform(box, new))
            box = new

        eq = equation()
        self.beat("binom(n,k) = binom(n-1,k-1) + binom(n-1,k)",
                  FadeOut(box, run_time=0.4), Write(eq, run_time=T_WRITE))
        nb = last_step_note(eq[2], "b", B_ORANGE)
        self.beat("underline: last step x b", Create(nb[0]), FadeIn(nb[1], shift=UP * 0.1))
        na = last_step_note(eq[4], "a", A_BLUE)
        self.beat("underline: last step x a", Create(na[0]), FadeIn(na[1], shift=UP * 0.1))

        # Concrete check with n = 4, k = 2 on the left half.
        right_g = VGroup(d, eq, nb, na)
        self.beat("diagram and equation move to the right half",
                  right_g.animate.scale(0.72).shift(RIGHT * 3.35), run_time=T_MORPH)
        ws = {w: word_mob(w).move_to([WORD_X, WORD_Y0 - i * WORD_DY, 0])
              for i, w in enumerate(WORDS)}
        self.beat("the six pick words of a^2b^2", LaggedStart(
            *[FadeIn(ws[w], shift=RIGHT * 0.15) for w in WORDS], lag_ratio=0.12))
        boxes = VGroup(*[focus_box(ws[w][-1], buff=0.05) for w in WORDS])
        self.beat("outline each word's last letter", LaggedStart(
            *[Create(b) for b in boxes], lag_ratio=0.08))
        moves = []
        for w, b in zip(WORDS, boxes):
            dy = sorted_y(w) - ws[w].get_y()
            moves += [ws[w].animate.shift(UP * dy), b.animate.shift(UP * dy)]
        self.beat("sort by the last letter", *moves, run_time=T_MORPH)
        gb = group_label(ENDS_B, r"\binom{3}{1} = 3", B_ORANGE)
        self.beat("ends in b: binom(3,1) = 3", FadeOut(boxes),
                  GrowFromCenter(gb[0]), FadeIn(gb[1], shift=LEFT * 0.1))
        ga = group_label(ENDS_A, r"\binom{3}{2} = 3", A_BLUE)
        self.beat("ends in a: binom(3,2) = 3", GrowFromCenter(ga[0]),
                  FadeIn(ga[1], shift=LEFT * 0.1))
        total = ab_tex("3 + 3 = 6 =", r"\binom{4}{2}", font_size=42)
        total.next_to(VGroup(*ws.values(), gb, ga), DOWN, buff=0.5).align_to(ws[WORDS[0]], LEFT)
        self.beat("3 + 3 = 6 = binom(4,2)", Write(total, run_time=T_WRITE))
