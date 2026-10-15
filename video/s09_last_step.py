"""Scene 9 — Counting by the last step."""

from components import *
import s08_fold

S = 0.92   # rows 0-4 re-laid out at 92% (the "reframe")


def lattice4():
    return Lattice(4, dx=1.7 * S, dy=1.35 * S, top=2.95, cell_scale=s08_fold.CS * S,
                   term_size=28 * S)


def statement():
    return display("Every path arrives through exactly one of the two nodes above.",
                   34).move_to([0, -3.1, 0])


def lattice_mobs(lat, upto=None):
    return VGroup(lat.all_edges(upto), lat.all("cells", upto), lat.all("terms", upto))


def end_state():
    lat = lattice4()
    return VGroup(lattice_mobs(lat), statement()), lat


class S09LastStep(BeatScene):
    SCENE_ID = "S09"

    def construct(self):
        prev, lat = s08_fold.end_state()
        self.add(prev)
        whole = lattice_mobs(lat)

        def focus_on(lat, n, k):
            """Everything except (n,k), its two parents and the edges into it."""
            keep = {(n, k), (n - 1, k - 1), (n - 1, k)}
            into = {id(e) for e in lat.into(n, k)}
            return VGroup(*[lat.cells[p] for p in lat.cells if p not in keep],
                          *[lat.terms[p] for p in lat.terms if p not in keep],
                          *[e for e in lat.edges.values() if id(e) not in into])

        def node_sum(lat, n, k, toks, colors, total):
            """'2 + 1 = 3' under the node; the travelling numbers become its terms."""
            eq = VGroup(mono(toks[0][1].text, 30, colors[0]), mono("+", 30),
                        mono(toks[1][1].text, 30, colors[1]), mono("=", 30),
                        mono(str(total), 30)).arrange(RIGHT, buff=0.16)
            eq.next_to(lat.cells[n, k], DOWN, buff=0.3)
            return eq, [FadeOut(toks[0][0]), FadeOut(toks[1][0]),
                        ReplacementTransform(toks[0][1], eq[0]),
                        ReplacementTransform(toks[1][1], eq[2]),
                        FadeIn(eq[1]), FadeIn(eq[3]), FadeIn(eq[4])]

        def collapse(lat, n, k, eq):
            cell = lat.cells[n, k]
            return [
                [eq[4].animate.move_to(cell.label).set_opacity(0),
                 FadeOut(eq[:4], target_position=cell.get_center(), scale=0.4)],
                lambda: (self.remove(eq), [pulse(cell)])[1]]

        # ---- a^2 b in row 3 -------------------------------------------------
        others = focus_on(lat, 3, 1)
        self.beat("focus a^2b; dim all but its parents a^2, ab and two edges",
                  FadeOut(prev[3]), FadeOut(prev[4]), dim(others))

        p_ab = VGroup(*lat.path_lines("ab"), *lat.path_lines("ba"))
        self.beat("trace the two paths into ab", trace_path(p_ab[:2]), trace_path(p_ab[2:]))
        ext_a = VGroup(*lat.path_lines("aba")[2:])
        f2, tok2 = lat.flow(2, 1, "a", 2)
        self.beat("extend along blue x a into a^2b; the 2 flows along it",
                  steps=[[trace_path(ext_a)], [f2]])
        p_aa = VGroup(*lat.path_lines("aa"))
        self.beat("trace the one path into a^2", trace_path(p_aa))
        ext_b = VGroup(*lat.path_lines("aab")[2:])
        f1, tok1 = lat.flow(2, 0, "b", 1)
        self.beat("extend along orange x b; the 1 flows along it",
                  steps=[[trace_path(ext_b)], [f1]])
        eq, anims = node_sum(lat, 3, 1, (tok2, tok1), (A_BLUE, B_ORANGE), 3)
        self.beat("2 + 1 = 3 at a^2b", *anims, run_time=0.8)
        self.beat("the sum collapses into the badge 3", steps=collapse(lat, 3, 1, eq))

        # ---- row 4: re-lay out and add the row ------------------------------
        lat4 = lattice4()
        paths = VGroup(p_ab, ext_a, p_aa, ext_b)
        # ReplacementTransform: the old piece leaves the scene and the new one
        # (lat4's) takes its place, so afterwards lat4 *is* what is on screen.
        moves = [ReplacementTransform(lat.cells[key], lat4.cells[key]) for key in lat.cells]
        moves += [ReplacementTransform(lat.terms[key], lat4.terms[key]) for key in lat.terms]
        moves += [ReplacementTransform(lat.edges[key], lat4.edges[key]) for key in lat.edges]
        new_row = [lat4.row_edges(3), lat4.row(4, "cells"), lat4.row(4, "terms")]
        self.beat("lattice re-frames; row 4 appears", steps=[
            [FadeOut(paths, run_time=0.4), undim(others, run_time=0.4)],
            [*moves],
            [LaggedStart(*[Create(e) for e in new_row[0]], lag_ratio=0.08),
             LaggedStart(*[FadeIn(m, shift=DOWN * 0.1) for m in new_row[1]], lag_ratio=0.1),
             LaggedStart(*[FadeIn(m, shift=DOWN * 0.1) for m in new_row[2]], lag_ratio=0.1)]],
            run_time=T_MORPH)

        # ---- a^2 b^2 in row 4 -----------------------------------------------
        others4 = focus_on(lat4, 4, 2)
        self.beat("focus a^2b^2; dim all but a^2b, ab^2 and two edges", dim(others4))
        f3b, tok3b = lat4.flow(3, 1, "b", 3)
        self.beat("3 flows from a^2b along orange x b", f3b)
        f3a, tok3a = lat4.flow(3, 2, "a", 3)
        self.beat("3 flows from ab^2 along blue x a", f3a)
        eq6, anims = node_sum(lat4, 4, 2, (tok3b, tok3a), (B_ORANGE, A_BLUE), 6)
        self.beat("3 + 3 = 6", *anims, run_time=0.8)
        self.beat("the sum collapses into the badge 6", steps=collapse(lat4, 4, 2, eq6))

        self.beat("every path arrives through exactly one of the two nodes above",
                  undim(others4), FadeIn(statement(), shift=UP * 0.15))
