"""Scene 6 — A coefficient counts choices."""

from components import *
import s05_multiply

ROW_YS = [0.85, 0.2, -0.45]
LEFT_WORDS = ["baa", "aba", "aab"]          # b supplied by bracket 1, 2, 3
LEFT_SETS = ["{1}", "{2}", "{3}"]
RIGHT_WORDS = ["bba", "bab", "abb"]         # b's supplied by brackets {1,2} ...
RIGHT_SETS = ["{1,2}", "{1,3}", "{2,3}"]
RIGHT_SETS_A = ["{3}", "{2}", "{1}"]        # ... which leaves the a's here


def column(words_, sets, x_word, x_set, title_tex, forced="a"):
    pws = VGroup(*[PickWord(w, forced=forced).move_to([x_word, y, 0])
                   for w, y in zip(words_, ROW_YS)])
    sts = VGroup(*[mono(s, 26, INK) for s in sets])
    for s, y in zip(sts, ROW_YS):
        s.move_to([x_set, y, 0], aligned_edge=LEFT)
    title = ab_tex(title_tex, font_size=40, color=MUTED)
    title.move_to([(pws.get_left()[0] + sts.get_right()[0]) / 2, 1.6, 0])
    return pws, sts, title


def brace_with(sets, tex):
    br = Brace(sets, RIGHT, buff=0.15, color=MUTED)
    lab = ab_tex(tex, font_size=38).next_to(br, RIGHT, buff=0.15)
    return br, lab


def left_column():
    return column(LEFT_WORDS, LEFT_SETS, -5.1, -3.75, "a^{2}b")


def right_column():
    return column(RIGHT_WORDS, RIGHT_SETS, 1.55, 3.0, "ab^{2}")


def link_group():
    """'choosing' next to a small binom(n,k) labelled 'n choose k'."""
    word = display("choosing", 32)
    b = ab_tex(r"\binom{n}{k}", font_size=36)
    lab = mono("n choose k", 18, MUTED).next_to(b, DOWN, buff=0.12)
    g = VGroup(word, VGroup(b, lab)).arrange(RIGHT, buff=0.45)
    g[0].align_to(b, DOWN).shift(UP * 0.12)
    return g.move_to([2.2, 2.95, 0])


def end_state():
    tri, _ = s05_multiply.corner_triangle()
    return VGroup(tri)


class S06Counts(BeatScene):
    SCENE_ID = "S06"

    def construct(self):
        prev = s05_multiply.end_state()
        self.add(prev)
        row, m, stacks, tri, tri_box = prev

        choosing = display("choosing", 60).move_to([0, -1.7, 0])
        under = focus_line(choosing, buff=0.12)
        self.beat("'choosing', underlined",
                  FadeOut(tri_box), FadeIn(choosing, shift=UP * 0.15), Create(under))

        link = link_group()
        self.beat("'choosing' moves next to binom(n,k) 'n choose k'",
                  FadeOut(under),
                  ReplacementTransform(choosing, link[0]),
                  FadeIn(link[1], shift=LEFT * 0.2), run_time=T_MORPH)

        # Left column: the three pick words of a^2b become tuples.
        lw, ls, lt = left_column()
        a2b_words = stacks[1]           # aab, aba, baa in tree order
        src = {w.text: w for w in a2b_words}
        keep = [m[3]] + list(a2b_words)
        self.beat("a^2b: its three pick words become (b,a,a), (a,b,a), (a,a,b)",
                  FadeOut(VGroup(*[p for p in m if p is not m[3]]),
                          *[c for c in stacks if c is not a2b_words]),
                  ReplacementTransform(m[3], lt[0]),
                  *[ReplacementTransform(src[w], pw) for w, pw in zip(LEFT_WORDS, lw)],
                  run_time=T_MORPH)
        self.add(lt)
        self.beat("the bracket that gives the b: {1}, {2}, {3}",
                  LaggedStart(*[FadeIn(s, shift=LEFT * 0.15) for s in ls], lag_ratio=0.2))
        lbr, llab = brace_with(ls, r"\binom{3}{1} = 3")
        self.beat("brace: binom(3,1) = 3", GrowFromCenter(lbr), FadeIn(llab, shift=LEFT * 0.1))

        # Right column: ab^2.
        rw, rs, rt = right_column()
        self.beat("ab^2: (b,b,a), (b,a,b), (a,b,b)", FadeIn(rt),
                  LaggedStart(*[FadeIn(w, shift=UP * 0.1) for w in rw], lag_ratio=0.2))
        rbr, rlab = brace_with(rs, r"\binom{3}{2} = 3")
        self.beat("sets {1,2}, {1,3}, {2,3}, brace binom(3,2) = 3",
                  LaggedStart(*[FadeIn(s, shift=LEFT * 0.15) for s in rs], lag_ratio=0.2),
                  GrowFromCenter(rbr), FadeIn(rlab, shift=LEFT * 0.1))

        general = ab_tex(r"\text{coefficient of }", "a^{n-k}b^{k}", "=", r"\binom{n}{k}",
                         font_size=42).move_to([0, -1.55, 0])
        self.beat("coefficient of a^(n-k) b^k = binom(n,k)", Write(general, run_time=T_WRITE))

        # Symmetry: the b-brackets decide the a-brackets.
        self.beat("right column: a's full, b's dimmed",
                  *sum([pw.force("b") for pw in rw], []))
        rs_a = VGroup(*[mono(s, 26, INK).move_to(old, aligned_edge=LEFT)
                        for s, old in zip(RIGHT_SETS_A, rs)])
        rbr_a, rlab_a = brace_with(rs_a, r"\binom{3}{1} = 3")
        self.beat("sets of a-brackets {3}, {2}, {1}; brace binom(3,1)",
                  *[FadeTransform(o, n) for o, n in zip(rs, rs_a)],
                  Transform(rbr, rbr_a), FadeTransform(rlab, rlab_a), run_time=T_MORPH)
        sym = ab_tex(r"\binom{3}{1}", "=", r"\binom{3}{2}", font_size=44).move_to([0, -2.75, 0])
        self.beat("binom(3,1) = binom(3,2)", FadeIn(sym, shift=UP * 0.15))
        sym_n = ab_tex(r"\binom{n}{k}", "=", r"\binom{n}{n-k}", font_size=44).move_to(sym)
        self.beat("binom(n,k) = binom(n,n-k)",
                  TransformMatchingTex(sym, sym_n, transform_mismatches=True, run_time=T_MORPH))

        # The corner triangle mirrors onto itself.
        axis = Line(tri.get_top() + UP * 0.12, tri.get_bottom() + DOWN * 0.12,
                    color=MUTED, stroke_width=1.5)
        self.beat("mirror axis on the corner triangle", Create(axis))
        swaps = []
        for n in range(4):
            for k in range(n + 1):
                # Mobjects are drawn in group order, so a label moved into a
                # later cell would sit under that cell's box; z_index lifts it.
                tri.cell(n, k).label.set_z_index(1)
                if k != n - k:
                    swaps.append(tri.cell(n, k).label.animate(path_arc=PI * 0.6)
                                 .move_to(tri.cell(n, n - k).box))
        self.beat("every number swaps with its mirror twin: nothing changes",
                  *swaps, run_time=1.2)

        rest = [mob for mob in self.mobjects if mob is not tri
                and not any(mob in c.get_family() for c in tri.cells)]
        self.beat("fade everything except the corner triangle",
                  FadeOut(Group(*rest)))
