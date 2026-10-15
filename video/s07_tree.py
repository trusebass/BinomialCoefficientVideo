"""Scene 7 — The decision tree."""

from components import *
import s05_multiply
import s06_counts


def header(n):
    """(a+b)^0, then (a+b), (a+b)·(a+b), ... in the top-left corner."""
    if n == 0:
        h = ab_tex("(a+b)", "^{0}", font_size=36)
    else:
        args = []
        for i in range(n):
            args += ([r"\cdot"] if i else []) + ["(a+b)"]
        h = ab_tex(*args, font_size=36)
    return h.to_corner(UL, buff=SAFE).shift(UP * 0.15)


def tally(n):
    return mono_power("2", n, f"= {2 ** n}", 26).to_corner(UR, buff=SAFE).shift(UP * 0.15)


def products(tree, lvl):
    return VGroup(*[ab_tex(product_tex(w), font_size=30, color=MUTED)
                    .next_to(tree.nodes[w], DOWN, buff=0.22) for w in words(lvl)])


def tree_parts(tree, upto):
    """Edges, edge labels and nodes of levels 0..upto, in drawing order."""
    ws = [w for l in range(upto + 1) for w in words(l)]
    return (VGroup(*[tree.edges[w] for w in ws if w]),
            VGroup(*[tree.edge_labels[w] for w in ws if w]),
            VGroup(*[tree.nodes[w] for w in ws]))


def end_state():
    tree = DecisionTree(3)
    edges, labels, nodes = tree_parts(tree, 3)
    return VGroup(edges, labels, nodes, header(3), tally(3)), tree


class S07Tree(BeatScene):
    SCENE_ID = "S07"

    def construct(self):
        prev = s06_counts.end_state()
        self.add(prev)

        tree = DecisionTree(3)
        head, tal = header(0), tally(0)
        self.beat("root 1, header (a+b)^0, tally 2^0 = 1",
                  FadeOut(prev), GrowFromCenter(tree.nodes[""]),
                  FadeIn(head), FadeIn(tal))

        prods = None
        for lvl in (1, 2, 3):
            ws = words(lvl)
            new_head, new_tal = header(lvl), tally(lvl)
            anims = [LaggedStart(*[Create(tree.edges[w]) for w in ws], lag_ratio=0.1, run_time=0.6),
                     LaggedStart(*[FadeIn(tree.edge_labels[w]) for w in ws], lag_ratio=0.1),
                     LaggedStart(*[GrowFromCenter(tree.nodes[w]) for w in ws], lag_ratio=0.1),
                     TransformMatchingTex(head, new_head, run_time=T_MORPH),
                     FadeTransform(tal, new_tal)]
            if prods is not None:
                anims.append(FadeOut(prods))
            self.beat(f"level {lvl}: x a left, x b right; 2^{lvl} = {2 ** lvl}", *anims)
            head, tal = new_head, new_tal
            prods = products(tree, lvl)
            self.beat(f"path products under level {lvl}",
                      LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in prods], lag_ratio=0.1))

        # The Scene 5 tally line under the leaves: same terms, same pick words.
        t_full, t_terms, _ = s05_multiply.tally()
        t_full.move_to([0, -2.75, 0])
        t_words = VGroup(*[s05_multiply.word_label(w).next_to(t, DOWN, buff=0.2)
                           for w, t in zip(s05_multiply.PICKS, t_terms)])
        bottoms_at(t_words, t_full.get_bottom()[1] - 0.42)
        self.beat("Scene 5 tally line returns under the leaves",
                  FadeIn(t_full, shift=UP * 0.2), FadeIn(t_words, shift=UP * 0.2))
        self.beat("tally line and products fade", FadeOut(t_full), FadeOut(t_words),
                  FadeOut(prods))

        # One path: 1 -> x a -> x b -> x a.
        path = VGroup(*tree.path_lines("aba"))
        self.beat("trace the path aba", trace_path(path))
        leaf = tree.nodes["aba"]
        prod = ab_tex("a", r"\cdot", "b", r"\cdot", "a", "=", "a^{2}b", font_size=32)
        prod.next_to(leaf, DOWN, buff=0.25)
        self.beat("a·b·a = a^2 b next to the leaf", FadeIn(prod, shift=UP * 0.1))

        # A fourth bracket doubles the paths again: 16 leaves.
        dots, d_edges = VGroup(), VGroup()
        for w in words(3):
            for c, side in (("a", -1), ("b", 1)):
                p = tree.pos(w) + np.array([side * tree.width / 28, -tree.level_dy, 0])
                d = Dot(p, radius=0.06, color=INK2)
                dots.add(d)
                d_edges.add(Line(tree.pos(w), p, buff=0, color=INK2, stroke_width=2)
                            .put_start_and_end_on(
                                tree.pos(w) + normalize(p - tree.pos(w)) * NODE_R,
                                p - normalize(p - tree.pos(w)) * 0.06))
        head4, tal4 = header(4), tally(4)
        self.beat("level 4: 16 leaves, 2^4 = 16",
                  FadeOut(path, run_time=0.4), FadeOut(prod, run_time=0.4),
                  LaggedStart(*[Create(e) for e in d_edges], lag_ratio=0.03, run_time=0.8),
                  LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.03, run_time=0.8),
                  TransformMatchingTex(head, head4, run_time=T_MORPH),
                  FadeTransform(tal, tal4))
        head3, tal3 = header(3), tally(3)
        self.beat("back to the depth-3 tree",
                  FadeOut(dots), FadeOut(d_edges),
                  TransformMatchingTex(head4, head3, run_time=T_MORPH),
                  FadeTransform(tal4, tal3))
