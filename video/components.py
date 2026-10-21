"""Reusable building blocks (script Part B). Every scene imports this module.

Manim vocabulary used throughout:
  Mobject    anything that can be on screen. VMobject = a vector shape made of
             Bézier curves; VGroup = a list of VMobjects that moves as one.
  Animation  something that changes mobjects over `run_time` seconds. Scenes
             run animations with self.play(...) and hold with self.wait(...).
  .animate   `mob.animate.shift(UP)` builds an animation from any method call:
             Manim makes a copy, applies the call to it, and interpolates.
"""

import json
import re
from math import comb
from pathlib import Path

from palette import *

ROOT = Path(__file__).resolve().parent

# ---------------------------------------------------------------- LaTeX
# A custom template: the default preamble has no xcolor, which ab_tex needs.
TEX = TexTemplate()
TEX.add_to_preamble(
    r"\usepackage{xcolor}"
    rf"\definecolor{{abA}}{{HTML}}{{{A_BLUE.to_hex()[1:]}}}"
    rf"\definecolor{{abB}}{{HTML}}{{{B_ORANGE.to_hex()[1:]}}}"
)
config.tex_template = TEX

# Commands whose arguments are not math and must not be recolored.
_VERBATIM_ARGS = {"text", "textrm", "mathrm", "operatorname", "color",
                  "textcolor", "begin", "end", "hspace", "definecolor"}


def _brace_end(s, i):
    """Index of the brace that closes the one at s[i]."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{" and s[j - 1] != "\\":
            depth += 1
        elif s[j] == "}" and s[j - 1] != "\\":
            depth -= 1
            if depth == 0:
                return j
    raise ValueError(f"unbalanced braces in {s!r}")


def color_ab(tex):
    r"""Wrap every stand-alone letter a / b in \textcolor.

    Letters inside command names (\frac, \binom, \max) and inside \text{...}
    are left alone. Coloring inside LaTeX survives into Manim: SVG glyphs that
    are not black keep their color, the rest get the mobject's `color`.
    """
    out, i = [], 0
    while i < len(tex):
        if tex[i] == "\\":
            m = re.match(r"\\([A-Za-z]+|.)", tex[i:])
            out.append(m.group(0))
            i += len(m.group(0))
            if m.group(1) in _VERBATIM_ARGS:
                if i < len(tex) and tex[i] == "[":
                    j = tex.index("]", i)
                    out.append(tex[i:j + 1])
                    i = j + 1
                if i < len(tex) and tex[i] == "{":
                    j = _brace_end(tex, i)
                    out.append(tex[i:j + 1])
                    i = j + 1
            continue
        c = tex[i]
        if c in "ab":
            out.append(r"\textcolor{ab%s}{%s}" % ("A" if c == "a" else "B", c))
        else:
            out.append(c)
        i += 1
    return "".join(out)


def ab_tex(*tex_strings, color=INK, font_size=48, **kw):
    r"""MathTex in which every a is blue and every b is orange (B.2).

    Split into parts exactly like MathTex: separate arguments, or
    `{{ ... }}` groups (in Manim 0.22 a `{{` only opens a group at the start
    of the string or after a space). Each part's `tex_string` is the original,
    uncolored, stripped TeX, so TransformMatchingTex and `part()` can find
    parts by what you wrote, e.g. part(m, r"\binom{n}{k}").
    """
    segments = []
    for s in tex_strings:
        segments += MathTex._split_double_braces(str(s))
    segments = [s for s in segments if s.strip()]
    m = MathTex(*[color_ab(s) for s in segments], color=color,
                font_size=font_size, **kw)
    for p, s in zip(m.submobjects, segments):
        p.tex_string = s.strip()
    return m


def part(tex_mob, tex):
    """The part of an ab_tex whose (stripped) TeX equals `tex`."""
    for p in tex_mob.submobjects:
        if p.tex_string == tex:
            return p
    raise KeyError(f"{tex!r} not in {[p.tex_string for p in tex_mob]}")


def parts(tex_mob, tex):
    """All parts of an ab_tex whose TeX equals `tex`."""
    return [p for p in tex_mob.submobjects if p.tex_string == tex]


# ---------------------------------------------------------------- text
def mono(s, font_size=24, color=INK, ab=False):
    """Monospace Text. With ab=True every a/b glyph gets its letter color.

    Text drops whitespace from its glyph list, so glyph i is the i-th
    non-space character of s.
    """
    t = Text(s, font=MONO_FONT, font_size=font_size, color=color)
    if ab:
        chars = [c for c in s if not c.isspace()]
        for g, c in zip(t, chars):
            if c == "a":
                g.set_color(A_BLUE)
            elif c == "b":
                g.set_color(B_ORANGE)
    return t


def mono_power(base, exp, tail="", font_size=26, color=INK):
    """'2^3 = 8' in mono with a real raised exponent.

    Bale Mono only has the superscript digits 1, 2, 3; for the others Pango
    silently borrows a glyph from another font. So the exponent is a small
    mono Text placed by hand.
    """
    b = mono(base, font_size, color)
    e = mono(str(exp), font_size * 0.62, color)
    e.next_to(b, RIGHT, buff=0.03).align_to(b, UP).shift(UP * b.height * 0.35)
    g = VGroup(b, e)
    if tail:
        t = mono(tail, font_size, color).next_to(g, RIGHT, buff=0.18).align_to(b, DOWN)
        g.add(t)
    return g


def bottoms_at(mobs, y):
    """Put every mobject's bottom at height y. For words without descenders
    (like pick words of a's and b's) that lines them up on one baseline;
    aligning centers or tops would not, since b is taller than a."""
    for m in mobs:
        m.shift(UP * (y - m.get_bottom()[1]))
    return mobs


def display(s, font_size=48, color=INK):
    return Text(s, font=DISPLAY_FONT, weight=SEMIBOLD, font_size=font_size,
                color=color)


def serif(s, font_size=30, color=INK):
    return Text(s, font=SERIF_FONT, font_size=font_size, color=color)


# ---------------------------------------------------------------- focus + dim
def focus_box(mob, buff=0.08, color=FOCUS_YELLOW):
    """Rule A.1-3: the single yellow outline."""
    return SurroundingRectangle(mob, color=color, stroke_width=3,
                                corner_radius=0.08, buff=buff)


def focus_line(mob, buff=0.08, color=FOCUS_YELLOW, stroke_width=3):
    return Underline(mob, color=color, stroke_width=stroke_width, buff=buff)


def dim(mob, factor=DIM, **kw):
    """Animation: scale every opacity in `mob` to `factor` x its original.

    The first call remembers each piece's own opacity (an edge at 0.6 stays
    relative to 0.6), so dim(mob, 1) restores exactly what was there.
    """
    target = mob.copy()
    for m, t in zip(mob.family_members_with_points(),
                    target.family_members_with_points()):
        if not hasattr(m, "base_op"):
            m.base_op = (m.get_fill_opacity(), m.get_stroke_opacity())
        t.set_fill(opacity=m.base_op[0] * factor, family=False)
        t.set_stroke(opacity=m.base_op[1] * factor, family=False)
    return Transform(mob, target, **kw)


def undim(mob, **kw):
    return dim(mob, 1.0, **kw)


def pulse(mob, scale=1.15, run_time=0.4):
    """Scale up and back (Scene 1: the child cell 'pulses').

    rate_func=there_and_back runs the animation forward and then backward,
    so the mobject ends exactly where it started (a still frame).
    """
    return mob.animate(rate_func=there_and_back, run_time=run_time).scale(scale)


def halo(mob, width=8):
    """A BG-colored outline behind a mobject's stroke, so it stays readable
    when it is drawn over a cell (`background=True` = drawn underneath)."""
    return mob.set_stroke(BG, width=width, background=True)


# ---------------------------------------------------------------- beats (A.5)
class BeatScene(Scene):
    """A Scene that logs every beat for out/beats.csv.

    Use self.beat("description", anim1, anim2, run_time=...) for every step:
    it notes the start time, plays the animations together, then holds BEAT
    seconds on a still frame. Nothing else in the scenes calls self.wait().
    """

    SCENE_ID = "S00"

    def setup(self):
        super().setup()
        self._beats = []

    def beat(self, desc, *anims, steps=None, **play_kw):
        """One beat. Either `anims` (played together) or `steps`: a list of
        steps played back to back with no pause, each a list of animations or
        a function returning one. A function runs only when its step starts,
        so it sees the scene as the previous step left it.

        Use steps instead of Succession when a later step transforms
        something that does not exist yet: Succession adds every animation's
        mobject to the scene at its very start.
        """
        start = self.renderer.num_plays
        for step in steps or ([anims] if anims else []):
            step = step() if callable(step) else step
            if step:
                self.play(*step, **play_kw)
        # Every play() and wait() becomes one partial movie file. We log the
        # index of the first play of the beat and of the hold; tools/timeline.py
        # turns indices into exact times by counting the frames in those files.
        # (renderer.time is unreliable: cached animations add their nominal
        # length, fresh ones their whole-frame length.)
        self._beats.append({"start_play": start, "freeze_play": self.renderer.num_plays,
                            "desc": desc})
        self.wait(BEAT)

    def tear_down(self):
        super().tear_down()
        out = ROOT / "out" / "beats"
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{self.SCENE_ID}.json").write_text(json.dumps({
            "scene": self.SCENE_ID,
            "class": type(self).__name__,
            "module": type(self).__module__,
            "plays": self.renderer.num_plays,
            "beats": self._beats,
        }, indent=1))


class BeatCameraScene(MovingCameraScene, BeatScene):
    """BeatScene with a movable camera (Scenes 8, 9, 11 only)."""


# ---------------------------------------------------------------- Pascal (B.3, B.4)
CELL_W, CELL_H, CELL_R, CELL_FONT = 0.62, 0.44, 0.08, 24


class PascalCell(VGroup):
    """Rounded cell with a count, shaded by value / row max (B.3)."""

    def __init__(self, value, row_max, scale=1.0, **kw):
        super().__init__(**kw)
        fill, ink = cell_colors(value, row_max)
        self.value, self.row_max = value, row_max
        self.box = RoundedRectangle(width=CELL_W, height=CELL_H,
                                    corner_radius=CELL_R, stroke_width=0,
                                    fill_color=fill, fill_opacity=1)
        self.label = mono(str(value), CELL_FONT, ink).move_to(self.box)
        self.add(self.box, self.label)
        self.scale(scale)

    @property
    def k(self):
        """Current size relative to the unscaled 0.62 x 0.44 cell."""
        return self.box.width / CELL_W

    def _label_for(self, value, color):
        return mono(str(value), CELL_FONT, color).scale(self.k).move_to(self.box)

    def set_value(self, value, row_max=None):
        """Animation that changes the number and the fill together."""
        row_max = self.row_max if row_max is None else row_max
        fill, ink = cell_colors(value, row_max)
        self.value, self.row_max = value, row_max
        return AnimationGroup(
            self.box.animate.set_fill(fill),
            Transform(self.label, self._label_for(value, ink)),
        )


class PascalTriangle(VGroup):
    """Rows 0..rows of PascalCells, centred on the origin (B.4)."""

    def __init__(self, rows, dx=0.68, dy=0.50, **kw):
        super().__init__(**kw)
        self.rows, self.dx, self.dy = rows, dx, dy
        self.cells = []
        for n in range(rows + 1):
            mx = comb(n, n // 2)
            row = VGroup(*[
                PascalCell(comb(n, k), mx).move_to([(k - n / 2) * dx, -n * dy, 0])
                for k in range(n + 1)])
            self.cells.append(row)
            self.add(row)
        self.move_to(ORIGIN)

    def cell(self, n, k):
        return self.cells[n][k]

    def row(self, n):
        return self.cells[n]

    @property
    def k(self):
        return self.cells[0][0].k

    def row_label(self, n, buff=0.35):
        """'n = 2' in MUTED mono, right-aligned in a column left of the triangle."""
        lab = mono(f"n = {n}", 22 * self.k, MUTED)
        left = self.cells[self.rows][0].get_left()[0] - buff * self.k
        lab.move_to([left - lab.width / 2, self.cells[n][0].get_y(), 0])
        return lab

    def row_labels(self, ns=None):
        return VGroup(*[self.row_label(n)
                        for n in (range(self.rows + 1) if ns is None else ns)])

    def k_labels(self, buff=0.25):
        """'k = 0 ... k = rows' under the last row (Scene 3)."""
        return VGroup(*[
            mono(f"k={k}", 16 * self.k, MUTED).next_to(c, DOWN, buff=buff * self.k)
            for k, c in enumerate(self.cells[self.rows])])

    def rule_plus(self, n, k):
        """A '+' between (n-1, k-1) and (n-1, k), so the row reads "3 + 3"
        above the cell (n, k) they add up to. BG halo for contrast."""
        a, b = self.cell(n - 1, k - 1), self.cell(n - 1, k)
        plus = MathTex("+", font_size=22 * self.k, color=INK)
        plus.move_to((a.get_center() + b.get_center()) / 2)
        return halo(plus, 6).set_z_index(2)


# ---------------------------------------------------------------- brackets (B.5)
class BracketRow(VGroup):
    """(a+b)·(a+b)·…: one MathTex, regrouped so letters can be addressed."""

    def __init__(self, n, font_size=48, numbers=True, **kw):
        super().__init__(**kw)
        args = []
        for i in range(n):
            if i:
                args.append(r"\cdot")
            args += ["(", "a", "+", "b", ")"]
        self.tex = ab_tex(*args, font_size=font_size)
        p = self.tex.submobjects
        self.brackets, self.dots = VGroup(), VGroup()
        j = 0
        for i in range(n):
            if i:
                self.dots.add(p[j])
                j += 1
            self.brackets.add(VGroup(*p[j:j + 5]))
            j += 5
        self.add(self.tex)
        self.numbers = VGroup()
        if numbers:
            y = self.tex.get_bottom()[1] - 0.25
            for i, br in enumerate(self.brackets):
                num = mono(str(i + 1), 20, MUTED)
                num.move_to([br.get_x(), y - num.height / 2, 0])
                self.numbers.add(num)
            self.add(self.numbers)
        self._marks = []

    def letter(self, i, letter):
        return self.brackets[i][1 if letter == "a" else 3]

    def pick(self, i, letter):
        """Yellow box on the chosen letter of bracket i, dim the other one."""
        other = "b" if letter == "a" else "a"
        box = focus_box(self.letter(i, letter), buff=0.06)
        self._marks.append(box)
        return [Create(box), self.letter(i, other).animate.set_opacity(0.3)]

    def reset(self):
        anims = [FadeOut(b) for b in self._marks]
        anims += [br[j].animate.set_opacity(1) for br in self.brackets for j in (1, 3)]
        self._marks = []
        return anims


# ---------------------------------------------------------------- pick words (B.6)
class PickWord(VGroup):
    """A tuple like (b, a, a) in mono with colored letters."""

    def __init__(self, word, font_size=28, forced=None, **kw):
        super().__init__(**kw)
        self.word = word
        self.text = mono("(" + ", ".join(word) + ")", font_size, ab=True)
        # glyphs: "(" then letter, "," alternating, then ")"
        self.letters = [self.text[1 + 2 * i] for i in range(len(word))]
        self.add(self.text)
        if forced:
            for g, c in zip(self.letters, word):
                g.set_opacity(0.4 if c == forced else 1)

    def force(self, letter):
        """Animations: dim every `letter` to 0.4, show the other at full."""
        return [g.animate.set_opacity(0.4 if c == letter else 1)
                for g, c in zip(self.letters, self.word)]


# ---------------------------------------------------------------- edge clipping
def box_of(mob, pad=0.0):
    """(xmin, xmax, ymin, ymax) of a mobject's bounding box."""
    return (mob.get_left()[0] - pad, mob.get_right()[0] + pad,
            mob.get_bottom()[1] - pad, mob.get_top()[1] + pad)


def box_around(center, w, h):
    return (center[0] - w / 2, center[0] + w / 2,
            center[1] - h / 2, center[1] + h / 2)


def _exit_t(p, d, box):
    """Smallest t > 0 at which p + t*d leaves `box` (p is inside it)."""
    ts = []
    for i, (lo, hi) in enumerate(((box[0], box[1]), (box[2], box[3]))):
        if d[i] > 1e-9:
            ts.append((hi - p[i]) / d[i])
        elif d[i] < -1e-9:
            ts.append((lo - p[i]) / d[i])
    return min(ts) if ts else 0.0


def clip_between(p0, p1, box0, box1, pad=0.06):
    """The part of segment p0-p1 outside both boxes (each grown by pad).

    Edges point centre to centre but stop where they meet each node's
    outline, so they never run through a label or a cell.
    """
    p0, p1 = np.array(p0, dtype=float), np.array(p1, dtype=float)
    b0 = (box0[0] - pad, box0[1] + pad, box0[2] - pad, box0[3] + pad)
    b1 = (box1[0] - pad, box1[1] + pad, box1[2] - pad, box1[3] + pad)
    d = p1 - p0
    return p0 + d * _exit_t(p0, d, b0), p1 - d * _exit_t(p1, -d, b1)


def edge_between(m0, m1, pad=0.06, **line_kw):
    """Line between two mobjects' centres, clipped to their outlines."""
    a, b = clip_between(m0.get_center(), m1.get_center(), box_of(m0),
                        box_of(m1), pad)
    return Line(a, b, **line_kw)


# ---------------------------------------------------------------- tree (B.7)
NODE_R = 0.28


def node_letter(word):
    """The tex shown in a tree node: '1' for the root, else the last letter."""
    return "1" if not word else word[-1]


def product_tex(word):
    """'aba' -> 'a^{2}b' (a's first, the order the expansion writes them)."""
    if not word:
        return "1"
    na, nb = word.count("a"), word.count("b")
    s = ""
    if na:
        s += "a" + (f"^{{{na}}}" if na > 1 else "")
    if nb:
        s += "b" + (f"^{{{nb}}}" if nb > 1 else "")
    return s


def words(level):
    """All pick words of a length in tree order: aa, ab, ba, bb."""
    out = [""]
    for _ in range(level):
        out = [w + c for w in out for c in "ab"]
    return out


class DecisionTree:
    """Positions and mobjects of the binary decision tree (B.7).

    Not a VGroup on purpose: scenes reveal it level by level, so the pieces
    live in dicts keyed by pick word ("" = root, "ab" = a then b) and the
    scene adds them when it wants them.
    """

    def __init__(self, depth=3, root=(0, 2.9), level_dy=1.4, width=11.0):
        self.depth, self.root, self.level_dy, self.width = depth, root, level_dy, width
        self.nodes, self.edges, self.edge_labels = {}, {}, {}
        for lvl in range(depth + 1):
            for w in words(lvl):
                self.nodes[w] = self.make_node(w)
                if w:
                    self.edges[w] = self.make_edge(w)
                    self.edge_labels[w] = self.make_edge_label(w)

    def pos(self, word):
        L, D = len(word), self.depth
        span = 2 ** (D - L)
        i0 = int(word.translate(str.maketrans("ab", "01")) or "0", 2) * span
        step = self.width / (2 ** D - 1)
        x = -self.width / 2 + step * (i0 + (span - 1) / 2)
        return np.array([self.root[0] + x, self.root[1] - L * self.level_dy, 0])

    def make_node(self, word):
        c = INK if not word else (A_BLUE if word[-1] == "a" else B_ORANGE)
        circle = Circle(radius=NODE_R, stroke_color=c, stroke_width=2.5,
                        fill_color=BG, fill_opacity=1)
        lab = ab_tex(node_letter(word), font_size=34).move_to(circle)
        return VGroup(circle, lab).move_to(self.pos(word))

    def make_edge(self, word):
        return Line(self.pos(word[:-1]), self.pos(word), buff=NODE_R,
                    color=INK2, stroke_width=2)

    def make_edge_label(self, word):
        e = self.edges[word]
        d = normalize(e.get_end() - e.get_start())
        normal = np.array([d[1], -d[0], 0]) if word[-1] == "a" else np.array([-d[1], d[0], 0])
        lab = ab_tex(r"\times " + word[-1], font_size=22)
        lab.move_to(e.point_from_proportion(0.42) + normal * (0.12 + lab.width / 2))
        return lab

    def level(self, lvl, what="nodes"):
        d = getattr(self, what)
        return VGroup(*[d[w] for w in words(lvl) if w in d])

    def path_lines(self, word, color=PATH_AQUA, width=6):
        """Copies of the edges along `word`, styled as a traced path."""
        return [Line(self.edges[word[:i]].get_start(), self.edges[word[:i]].get_end(),
                     color=color, stroke_width=width)
                for i in range(1, len(word) + 1)]


def trace_path(lines, per_edge=0.25):
    """B.9: draw path segments one after another (returns an animation)."""
    return Succession(*[Create(l, run_time=per_edge, rate_func=linear) for l in lines])


# ---------------------------------------------------------------- lattice (B.8)
def term_tex(n, k):
    """a^{n-k} b^{k} written out the way the expansion writes it."""
    return product_tex("a" * (n - k) + "b" * k)


class Lattice:
    """Node (n, k) = the term a^(n-k) b^k; k counts the b's (B.8).

    ×a edges go down-left (blue), ×b edges go down-right (orange). Like the
    tree, this is a set of dicts so scenes can reveal pieces in any order.
    """

    def __init__(self, rows, dx=1.7, dy=1.35, top=2.8, cell_scale=1.0,
                 terms=True, term_size=30, edge_opacity=0.6, edge_width=3,
                 counts=True):
        self.rows, self.dx, self.dy, self.top = rows, dx, dy, top
        self.cell_scale, self.edge_opacity = cell_scale, edge_opacity
        self.cells, self.terms, self.edges = {}, {}, {}
        for n in range(rows + 1):
            mx = comb(n, n // 2)
            for k in range(n + 1):
                if counts:
                    self.cells[n, k] = PascalCell(comb(n, k), mx, scale=cell_scale
                                                  ).move_to(self.pos(n, k))
                if terms:
                    self.terms[n, k] = self.make_term(n, k, term_size)
                if n < rows:
                    for step in "ab":
                        self.edges[n, k, step] = self.make_edge(n, k, step,
                                                                edge_width)

    def pos(self, n, k):
        return np.array([(k - n / 2) * self.dx, self.top - n * self.dy, 0])

    def make_term(self, n, k, font_size):
        """The term a^(n-k) b^k, sitting just above the cell."""
        tex = ab_tex(term_tex(n, k), font_size=font_size, color=MUTED)
        return tex.next_to(self.pos(n, k) + UP * CELL_H * self.cell_scale / 2,
                           UP, buff=0.06)

    def node_box(self, n, k):
        """Bounding box of everything drawn at (n, k): cell plus term."""
        mobs = [d[n, k] for d in (self.cells, self.terms) if (n, k) in d]
        if not mobs:
            w, h = CELL_W * self.cell_scale, CELL_H * self.cell_scale
            return box_around(self.pos(n, k), w, h)
        return box_of(VGroup(*mobs))

    def child(self, n, k, step):
        return (n + 1, k + (step == "b"))

    def make_edge(self, n, k, step, width):
        c = self.child(n, k, step)
        a, b = clip_between(self.pos(n, k), self.pos(*c),
                            self.node_box(n, k), self.node_box(*c), pad=0.06)
        e = Line(a, b, stroke_width=width,
                 color=A_BLUE if step == "a" else B_ORANGE,
                 stroke_opacity=self.edge_opacity)
        e.z_index = -1  # drawn behind cells, labels and traced paths
        return e

    def flow(self, n, k, step, value, stop=0.8, **kw):
        """flow_count along the edge (n, k) -> child, in the edge's color.
        It stops at `stop` of the edge so it does not cover the child's label."""
        e = self.edges[n, k, step]
        return flow_count(e.get_start(), e.point_from_proportion(stop), value,
                          A_BLUE if step == "a" else B_ORANGE, **kw)

    def row_edges(self, n):
        """Edges from row n down to row n+1."""
        return VGroup(*[self.edges[n, k, s] for k in range(n + 1) for s in "ab"])

    def into(self, n, k):
        """The (at most two) edges arriving at (n, k)."""
        out = []
        if k <= n - 1:
            out.append(self.edges[n - 1, k, "a"])
        if k >= 1:
            out.append(self.edges[n - 1, k - 1, "b"])
        return out

    def row(self, n, what="cells"):
        d = getattr(self, what)
        return VGroup(*[d[n, k] for k in range(n + 1) if (n, k) in d])

    def all(self, what="cells", upto=None):
        upto = self.rows if upto is None else upto
        return VGroup(*[self.row(n, what) for n in range(upto + 1)])

    def all_edges(self, upto=None):
        upto = self.rows if upto is None else upto
        return VGroup(*[self.row_edges(n) for n in range(upto)])

    def path_lines(self, word, color=PATH_AQUA, width=6):
        lines, n, k = [], 0, 0
        for c in word:
            e = self.edges[n, k, c]
            lines.append(Line(e.get_start(), e.get_end(), color=color,
                              stroke_width=width).set_z_index(-0.5))
            n, k = self.child(n, k, c)
        return lines


def flow_count(start, end, value, color, font_size=24, run_time=0.6):
    """B.10: a number that travels from `start` to `end` (points).

    Returns (animation, mobject) so the scene can fade or merge the number
    after it arrives. The BG backing keeps it readable on top of the edge.
    """
    num = mono(str(value), font_size, color)
    back = BackgroundRectangle(num, color=BG, fill_opacity=1, buff=0.05)
    tok = VGroup(back, num).move_to(start).set_z_index(1)
    anim = MoveAlongPath(tok, Line(start, end), run_time=run_time,
                         rate_func=smooth)
    return anim, tok
