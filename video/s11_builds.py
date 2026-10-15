"""Scene 11 — The triangle builds itself."""

from components import *
import s01_lookup
import s10_two_ways

ZOOM = 1.15        # camera pull-out: the frame becomes 15% larger
TITLE = "Why Pascal's Triangle Counts Choices"


def lattice7():
    return Lattice(7, dx=1.0, dy=0.85, top=3.1, terms=False)


def title_card():
    return display(TITLE, 56)


def end_state():
    return VGroup(title_card())


class S11Builds(BeatCameraScene):
    SCENE_ID = "S11"

    def construct(self):
        prev = s10_two_ways.end_state()
        self.add(prev)

        lat = lattice7()
        self.beat("one path at the top: the root 1",
                  FadeOut(prev), FadeIn(lat.cells[0, 0], scale=0.7))

        def row_steps(n, t):
            """Create the edges into row n, send counts down both edges of every
            node of row n-1, and let each child show the sum of what arrives."""
            toks = {}

            def edges():
                return [LaggedStart(*[Create(e) for e in lat.row_edges(n - 1)],
                                    lag_ratio=0.05, run_time=t * 0.25)]

            def flow():
                anims = []
                for k in range(n):
                    v = lat.cells[n - 1, k].value
                    for s in "ab":
                        a, tok = lat.flow(n - 1, k, s, v, stop=0.75, font_size=18,
                                          run_time=t * 0.5)
                        toks[n - 1, k, s] = tok
                        anims.append(a)
                return anims

            def fill():
                anims = []
                for k in range(n + 1):
                    child = lat.cells[n, k]
                    anims.append(FadeIn(child, scale=0.8))
                    for key in ((n - 1, k, "a"), (n - 1, k - 1, "b")):
                        if key in toks:
                            anims.append(FadeOut(toks[key], target_position=child.get_center(),
                                                 scale=0.5))
                return [AnimationGroup(*anims, run_time=t * 0.25)]

            return [edges, flow, fill]

        for n in (1, 2, 3):
            self.beat(f"row {n} fills in by adding what arrives", steps=row_steps(n, 1.2))
        self.beat("rows 4-7 fill in faster: row 7 = 1 7 21 35 35 21 7 1",
                  steps=sum([row_steps(n, 0.6) for n in range(4, 8)], []))

        # Pull out to the Scene 1 composition: (a+b)^n left, triangle right.
        frame = self.camera.frame
        cells, edges = lat.all("cells"), lat.all_edges()
        center = cells.get_center()
        shift = np.array([s01_lookup.TRI_CX * ZOOM, 0, 0]) - center
        power = VGroup(s01_lookup.power_line()).move_to([s01_lookup.LEFT_CX, 0.2, 0])
        power.scale(ZOOM, about_point=ORIGIN)   # screen position -> world position
        self.beat("edges fade, camera pulls out, (a+b)^n returns on the left",
                  frame.animate.scale(ZOOM),
                  cells.animate.shift(shift),
                  # one builder per mobject: two .animate calls on the same
                  # edges would each start from the original and fight
                  edges.animate.shift(shift).set_stroke(opacity=0.15),
                  FadeIn(power, shift=RIGHT * 0.2), run_time=1.2)

        left4, _ = s01_lookup.left_side(4)
        left4.scale(ZOOM, about_point=ORIGIN)
        row_box = focus_box(lat.row(4))
        self.beat("row 4 highlighted; a^4 + 4a^3b + 6a^2b^2 + 4ab^3 + b^4",
                  Create(row_box), TransformMatchingTex(power, left4, run_time=T_MORPH))

        six = part(left4[1], "6")
        boxes = VGroup(focus_box(six, buff=0.05), focus_box(lat.cells[4, 2]))
        paths = VGroup(*[l for w in s10_two_ways.WORDS for l in lat.path_lines(w)])
        paths.set_stroke(opacity=0.4).set_z_index(-0.5)
        self.beat("the 6 and its cell; the six paths behind the cells",
                  FadeOut(row_box), Create(boxes),
                  LaggedStart(*[Create(p) for p in paths], lag_ratio=0.03, run_time=1.2))

        title = title_card()

        def card():
            frame.scale(1 / ZOOM).move_to(ORIGIN)   # instant: the screen is empty
            return [FadeIn(title, shift=UP * 0.15)]

        self.beat("end card", steps=[[FadeOut(Group(*self.mobjects))], card])
