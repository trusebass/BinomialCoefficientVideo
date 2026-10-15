"""Scene 8 — Folding the tree into the triangle."""

from components import *
import s01_lookup
import s07_tree

CS = 1.15                         # cell scale of the dx = 1.7 lattice
TRACE_WORDS = ["aab", "aba", "baa"]


def lattice3():
    return Lattice(3, dx=1.7, dy=1.35, top=2.8, cell_scale=CS, term_size=28)


def product_node(word, pos):
    """A tree node showing the product so far, in a cell wide enough for it."""
    lab = ab_tex(product_tex(word), font_size=30)
    rect = RoundedRectangle(width=max(lab.width + 0.32, 0.56), height=0.56,
                            corner_radius=0.12, stroke_color=INK if not word else INK2,
                            stroke_width=2.5, fill_color=BG, fill_opacity=1)
    return VGroup(rect, lab.move_to(rect)).move_to(pos)


def kb(word):
    """Lattice coordinates (n, k) of a pick word: n letters, k of them b."""
    return len(word), word.count("b")


def trace_labels(lat):
    node = lat.cells[3, 1]
    col = VGroup(*[mono(w, 26, ab=True) for w in TRACE_WORDS]).arrange(DOWN, buff=0.14)
    col.next_to(node, DOWN, buff=0.35)
    b = ab_tex(r"\binom{3}{1} = 3", font_size=40).next_to(col, RIGHT, buff=0.6)
    return col, b


def end_state():
    lat = lattice3()
    col, b = trace_labels(lat)
    return VGroup(lat.all_edges(), lat.all("cells"), lat.all("terms"), col, b), lat


class S08Fold(BeatScene):
    SCENE_ID = "S08"

    def construct(self):
        prev, tree = s07_tree.end_state()
        self.add(prev)
        edges_g, labels_g, nodes_g, head, tal = prev
        for e in tree.edges.values():
            e.set_z_index(-1)

        # Edge labels go; the edge colors now say x a (blue) / x b (orange).
        self.beat("edge labels become edge colors", FadeOut(labels_g), FadeOut(head),
                  FadeOut(tal), *[e.animate.set_stroke(A_BLUE if w[-1] == "a" else B_ORANGE,
                                                       width=3, opacity=0.6)
                                  for w, e in tree.edges.items()])

        # Every node shows the product so far.
        cur = {w: tree.pos(w) for w in tree.nodes}
        nodes = {w: product_node(w, cur[w]) for w in tree.nodes}
        new_edges = {w: edge_between(nodes[w[:-1]], nodes[w], pad=0.05) for w in tree.edges}
        self.beat("letters become prefix products",
                  *[ReplacementTransform(tree.nodes[w], nodes[w]) for w in tree.nodes],
                  *[e.animate.put_start_and_end_on(new_edges[w].get_start(), new_edges[w].get_end())
                    for w, e in tree.edges.items()], run_time=T_MORPH)
        edges = tree.edges

        # Edges follow their nodes while nodes move: an updater is called on
        # every frame and re-clips the edge between the two node outlines.
        def follow(w):
            def upd(e):
                a, b = clip_between(nodes[w[:-1]].get_center(), nodes[w].get_center(),
                                    box_of(nodes[w[:-1]]), box_of(nodes[w]), pad=0.05)
                e.put_start_and_end_on(a, b)
            return upd

        def move_nodes(targets, desc):
            for w, e in edges.items():
                e.add_updater(follow(w))
            self.beat(desc, *[nodes[w].animate.move_to(p) for w, p in targets.items()],
                      run_time=1.4)
            for e in edges.values():   # nothing may move during the hold
                e.clear_updaters()

        lat = lattice3()
        badges, alive = {}, set(tree.nodes)

        def merge_row(n):
            """Duplicates at row n collapse into one node with a count badge."""
            reps, anims = {}, []
            for w in words(n):
                reps.setdefault(kb(w), w)
            for w in words(n):
                if reps[kb(w)] != w and w in alive:
                    self.remove(nodes[w])   # it sits exactly on its twin
                    alive.discard(w)
            for w in [w for w in edges if len(w) == n]:
                twin = next(v for v in edges if len(v) == n and kb(v[:-1]) == kb(w[:-1])
                            and v[-1] == w[-1])
                if twin != w:
                    self.remove(edges[w])
            for (nn, k), w in reps.items():
                badge = PascalCell(comb(nn, k), comb(nn, nn // 2), scale=0.62)
                badge.move_to(nodes[w].get_corner(UR) + np.array([-0.04, 0.02, 0]))
                badges[nn, k] = (badge, w)
                anims.append(FadeIn(badge, scale=0.6))
            return anims

        # Rows 0-2 to their lattice places; row 3 keeps its offset to its parent.
        targets = {}
        for w in tree.nodes:
            if len(w) <= 2:
                targets[w] = lat.pos(*kb(w))
            else:
                targets[w] = lat.pos(*kb(w[:2])) + (tree.pos(w) - tree.pos(w[:2]))
        move_nodes(targets, "rows 0-2 fold; ab and ba slide together, subtrees overlap")
        self.beat("badges: 1 | 1 1 | 1 2 1 (two paths reach ab)",
                  LaggedStart(*sum([merge_row(n) for n in range(3)], []), lag_ratio=0.1))

        move_nodes({w: lat.pos(*kb(w)) for w in words(3) if w in alive},
                   "row 3 folds: three a^2b meet, three ab^2 meet")
        self.beat("badges: 1 3 3 1", LaggedStart(*merge_row(3), lag_ratio=0.1))

        # Badges become Pascal cells; terms shrink and sit above them.
        anims = []
        for (n, k), (badge, w) in badges.items():
            anims += [ReplacementTransform(badge, lat.cells[n, k]),
                      ReplacementTransform(nodes[w][1], lat.terms[n, k]),
                      FadeOut(nodes[w][0])]
        for (n, k, s), e in lat.edges.items():
            w = next(v for v in edges if kb(v[:-1]) == (n, k) and v[-1] == s
                     and edges[v] in self.mobjects)
            anims.append(ReplacementTransform(edges[w], e))
        self.beat("badges grow into Pascal cells: this is Pascal's triangle", *anims,
                  run_time=T_MORPH)

        # The Scene 1 triangle laid over the same places.
        s1 = s01_lookup.triangle()
        ghost = VGroup(*[s1.cell(n, k).copy().move_to(lat.pos(n, k))
                         for n in range(4) for k in range(n + 1)])
        ghost.set_opacity(0.5).set_z_index(-0.9)
        self.beat("Scene 1 triangle overlaid at 0.5", FadeIn(ghost))
        self.beat("overlay fades", FadeOut(ghost))

        # The three paths into a^2b.
        col, b = trace_labels(lat)
        path = None
        for w, lab in zip(TRACE_WORDS, col):
            new = VGroup(*lat.path_lines(w))
            self.beat(f"trace {w}", steps=[
                [FadeOut(path, run_time=0.4)] if path else [],
                [trace_path(new), FadeIn(lab, shift=UP * 0.1, run_time=0.75)]])
            path = new
        self.beat("binom(3,1) = 3", FadeOut(path, run_time=0.4), FadeIn(b, shift=LEFT * 0.15))
