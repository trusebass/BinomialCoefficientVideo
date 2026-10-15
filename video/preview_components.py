"""One still per component, for checking the look (D.3 step 1).

    manim -ql -s preview_components.py TrianglePreview
"""

from components import *


class TrianglePreview(Scene):
    def construct(self):
        tri = PascalTriangle(6).scale_to_fit_height(5).move_to(RIGHT * 2.8)
        self.add(tri, tri.row_labels())
        self.add(ab_tex(r"(a+b)^n").move_to(LEFT * 3.6))


class BracketPreview(Scene):
    def construct(self):
        row = BracketRow(3).move_to(UP * 3.1)
        self.add(row)
        for i, c in enumerate("aba"):
            row.pick(i, c)  # returns animations; for a still we apply the end state
            row.letter(i, "b" if c == "a" else "a").set_opacity(0.3)
        self.add(*row._marks)
        words = VGroup(PickWord("baa", forced="a"), PickWord("aba", forced="a"),
                       PickWord("abb")).arrange(DOWN)
        f = ab_tex(r"(a+b)^n = \sum_{k=0}^{n} \binom{n}{k}\, a^{n-k} b^{k}")
        g = ab_tex(r"\text{coefficient of } a^{n-k}b^{k} = \binom{n}{k}")
        VGroup(words, f, g).arrange(DOWN, buff=0.5).shift(DOWN * 0.6)
        self.add(words, f, g)


class TreePreview(Scene):
    def construct(self):
        t = DecisionTree(3)
        self.add(*t.edges.values(), *t.edge_labels.values(), *t.nodes.values())
        lines = t.path_lines("aba")
        self.add(*lines)


class LatticePreview(Scene):
    def construct(self):
        lat = Lattice(4, top=2.9)
        self.add(lat.all_edges(), lat.all("cells"), lat.all("terms"))
        anim, tok = flow_count(lat.pos(2, 1), lat.pos(3, 1), 2, A_BLUE)
        anim.interpolate(0.5)
        self.add(tok)
