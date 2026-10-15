#eth/itet #eth/hs26 #video

# Why Pascal's Triangle Counts Choices — video script and animation spec

Working title alternatives: "Pascal's triangle is a path counter" · "Why adding counts choices"

**What this document is.** The complete narration plus animation instructions for a ~12-minute explainer video. It is written so that a fresh Claude chat or a Claude Code session can build the animations from it without further context. It is based on the draft `Binomial Coefficient.md` (same folder). Part E lists every change made to the draft.

**Conventions in this document**
- Plain paragraphs = narration (spoken text).
- Lines starting with `>` = animation instructions, as in the draft.
- **Timing is not decided here.** The voiceover is recorded separately and laid over the animation in Premiere Pro. The animation is rendered as **one continuous clip**, with every animation following the previous one after only a short pause. Holds are added later in Premiere as freeze frames. Read section A.5 before building anything.
- Formulas are written in LaTeX. In the animation, render every formula with `MathTex`.
- Throughout the video, **k counts the number of b's**: (a+b)ⁿ = Σ C(n,k) aⁿ⁻ᵏ bᵏ. The Skript (Satz 1.12) uses the mirrored convention aᵏbⁿ⁻ᵏ. Both give the same numbers because the triangle is symmetric. Do not mix them.

---

## Part A — Visual system

The look matches the interactive page **The Binomial World** (https://claude.ai/artifact/LmdnKo1mjxAKiKDES2qhnu), using its dark theme. Open the page in dark mode as the visual reference: the Pascal triangle at the top of the page is the exact cell style to reproduce.

### A.1 Colors

| Token (Python constant) | Hex | Use |
|---|---|---|
| `BG` | `#101318` | Frame background |
| `PANEL` | `#171B22` | Rare: backing for a boxed formula or the Galton board |
| `INK` | `#EEF0F4` | Main text, numbers, counts, operators, `+`, `=` |
| `INK2` | `#B7BCC8` | Secondary text, tree edges after creation |
| `MUTED` | `#8A90A0` | Labels (n = 3, bracket numbers 1 2 3), axes, dimmed context |
| `RULE` | `#2A2F39` | Lines and edges at rest, cell outlines |
| `A_BLUE` | `#3987E5` | **Every letter a**, every ×a edge |
| `B_ORANGE` | `#D95926` | **Every letter b**, every ×b edge |
| `PATH_AQUA` | `#199E70` | A path being traced through the tree or lattice |
| `FOCUS_YELLOW` | `#C98500` | The one thing the narration points at right now |
| `CELL_LO` | `#1B2433` | Pascal cell fill at value 0 |
| `CELL_HI` | `#6DA7EC` | Pascal cell fill at the largest value of its row |

**Color rules (these carry the explanation, keep them strict):**
1. The letter **a is always blue, b is always orange**: in formulas, in tree nodes, in edge labels ×a / ×b, and in lattice edges. The viewer should be able to read any frame by color alone.
2. Coefficients and path counts are `INK`, in the monospace font.
3. `FOCUS_YELLOW` marks one thing at a time: a `SurroundingRectangle` with stroke width 3 and corner radius 0.08, or an underline. Remove it before the next focus appears.
4. `PATH_AQUA` is used only for traced paths: stroke width 6 drawn on top of the edges, `Create` at 0.25 s per edge, then fade out over 0.4 s unless the narration keeps pointing at it.
5. Context that is not in focus is dimmed to opacity 0.35 instead of being removed, so the viewer never loses the picture.

**Pascal cell color.** Fill = `interpolate_color(CELL_LO, CELL_HI, t)` with `t = value / max(row)`. Text color: `BG` if t > 0.55, else `INK`. This is the same rule as the page.

### A.2 Typography

| Role | Font | Used for | Manim |
|---|---|---|---|
| Display | IBM Plex Sans Condensed, SemiBold | Scene questions ("Why?"), the key statement in Scene 9, end card | `Text(..., font="IBM Plex Sans Condensed", weight=SEMIBOLD)`, font_size 44–56 |
| Mono | The website's monospace (Bale Mono, per the website notes). Fallback: IBM Plex Mono (used in The Binomial World) | Counts inside cells, tallies `2^3 = 8`, labels `n = 3`, pick words `aab`, tuples `(b, a, a)`, bracket numbers | `Text(..., font="<mono>")`, font_size 20–30 |
| Math | LaTeX default (Latin Modern) | Every formula | `MathTex`, font_size 40–60 |
| Serif (optional) | Source Serif 4 | Only if an on-screen sentence is needed (Scene 2 definition) | `Text`, font_size 30 |

Before starting, put the font files in `fonts/` and install them system-wide. Check with `fc-list | grep -i -E "plex|bale|source serif"`. Manim's `Text` silently falls back to a default font if the name does not match, so render a test frame first. If Bale Mono is used, confirm its license allows use in a published video.

### A.3 Motion

- Default `rate_func = smooth`. Durations: `Write` ≤ 1.2 s, `FadeIn`/`FadeOut` 0.5 s, `Transform` / `TransformMatchingTex` 0.8–1.2 s, sequences with `LaggedStart(lag_ratio=0.15)`.
- After every animation step ("beat"), pause for only `BEAT = 0.5` s (see A.5). Never hold longer to match the narration.
- The camera stays still except in two places: the merge in Scene 8 (one smooth reframe) and the final pull-out in Scene 11. Use `MovingCameraScene` only there.
- No glow, no particle effects, no bouncing. The only "special" motion is counts flowing along edges (Scenes 9 and 11).

### A.4 Layout

- Frame 1920×1080, 60 fps; manim frame 14.22 × 8 units. Safe margin 0.6 units on every side.
- Header band y ∈ [2.9, 3.6] holds the persistent formula or tally of the scene (e.g. `(a+b)·(a+b)·(a+b)` and `2^3 = 8`).
- Split-screen scenes use centers x = −3.6 (left) and x = +3.6 (right).

### A.5 Timing and output: one continuous clip

The voiceover is recorded separately and edited over the animation in Premiere Pro. Anything that needs to stay on screen longer is extended there with freeze frames. So:

1. **Do not estimate or match narration timing.** Never write a `self.wait()` longer than `BEAT`, and never stretch an animation so it lasts as long as a sentence. Wherever the script mentions a hold, render a single `BEAT` instead; the real hold is made in Premiere.
2. **One beat = one animation step + `self.wait(BEAT)`** with `BEAT = 0.5` (constant in `palette.py`). Animation speeds (run times in A.3) stay as specified, because they define how the motion looks, not how long the shot lasts.
3. **Every beat ends on a still frame.** Nothing may move during the pause: no ambient motion, no slow drifts, no updaters animating idle objects, no fade that continues into the next beat. Any frame in the pause can then be frozen cleanly in Premiere.
4. **Scene boundaries get the same short pause.** No title cards or fades to black between scenes unless the script asks for them. Scene 12 (coda) is included at the end.
5. **Output = one continuous video file**, `binomial_full.mp4`, 1920×1080, 60 fps, H.264 (or ProRes 422 for editing if disk space allows). Build each scene as its own `Scene` class (easier to fix and re-render), render them all at the same settings, and concatenate them in order without gaps or transitions (`ffmpeg -f concat -c copy`). Keep the per-scene clips as well.
6. **Beat marker list.** Write `beats.csv` next to the video with one row per beat: `scene, beat_number, start_time_in_full_video, short description` (e.g. `S09, 4, 06:12.350, "2 + 1 = 3 collapses into badge"`). Record the time inside each scene with `self.renderer.time` at the start of each beat, and offset it by the summed lengths of the previous scenes when concatenating. This makes it quick to find the frame to freeze for each sentence of the voiceover.

---

## Part B — Reusable components (Manim Community Edition)

Build these once in `components.py`. All scenes import them.

**B.1 `palette.py`** — the constants of A.1, plus `config.background_color = BG`, `config.frame_rate = 60`, `config.pixel_width = 1920`, `config.pixel_height = 1080`.

**B.2 `ab_tex(tex, **kw)`** — a `MathTex` in which every a and b is colored. Write the letters isolated with double braces, e.g. `ab_tex(r"{{a}}^{2}{{b}}")`, then color submobjects whose TeX string is exactly `a` or `b`:

```python
def ab_tex(tex, **kw):
    m = MathTex(tex, **kw)
    for part in m.submobjects:
        s = part.get_tex_string().strip()
        if s == "a": part.set_color(A_BLUE)
        elif s == "b": part.set_color(B_ORANGE)
    return m
```
Do **not** use `set_color_by_tex("a", ...)`: it matches any part containing the letter a, including `\frac` and `\max`.

**B.3 `PascalCell(value, row_max)`** — `RoundedRectangle(width=0.62, height=0.44, corner_radius=0.08)`, no stroke, fill per A.1, value centered in the mono font at font_size 24. Method `.set_value(v, row_max)` animates the number and the fill together.

**B.4 `PascalTriangle(rows, dx, dy)`** — cells at `x = (k − n/2)·dx`, `y = top − n·dy`, for n = 0..rows, k = 0..n. Defaults dx = 0.68, dy = 0.50. Optional row labels `n = 0 … ` in `MUTED` mono to the left of each row. Must look identical to the page hero.

**B.5 `BracketRow(n)`** — `(a+b)·(a+b)·…` with each bracket a `VGroup` [`(`, a, `+`, b, `)`] so single letters can be highlighted. Bracket numbers 1, 2, 3 … in `MUTED` mono below each bracket. Methods: `.pick(i, letter)` returns the animations that put a `FOCUS_YELLOW` rectangle on that letter and dim the other letter of the bracket to 0.3; `.reset()`.

**B.6 `PickWord(word)`** — a mono tuple like `(b, a, a)`. Letters colored a/b. Option `forced="a"` dims all a's to 0.4 so it is visible that only the b-positions were chosen.

**B.7 `DecisionTree(depth)`** — root node "1" (circle r = 0.28, `INK` stroke). Every other node is a circle r = 0.28 with the letter just picked (stroke and letter in the letter's color). Left child = ×a, right child = ×b, always. Edges: `Line` stroke `INK2` width 2. Edge labels `×a` / `×b` (`ab_tex`, font_size 22) at the edge midpoint, offset outward. Level spacing 1.4 units, leaves spread over 11 units. With ×a always on the left, the leaves read left to right as aaa, aab, aba, abb, baa, bab, bba, bbb.

**B.8 `Lattice(rows, dx, dy)`** — node (n, k) at `x = (k − n/2)·dx`, `y = top − n·dy`. Each node holds a term label `a^{n−k}b^{k}` (`ab_tex`, font_size 30) and a count badge (B.3 style). Edges: from (n, k) to (n+1, k) is ×a, drawn **down-left** in `A_BLUE` at opacity 0.6; to (n+1, k+1) is ×b, drawn **down-right** in `B_ORANGE` at opacity 0.6.

**B.9 `trace_path(word)`** — returns animations that draw the path of a pick word (e.g. "aba") in `PATH_AQUA` over the tree or lattice.

**B.10 `flow_count(parent, child, value, color)`** — a small mono number `value` that travels along the edge from parent to child (0.6 s, `smooth`), colored like the edge. Used in Scenes 9 and 11.

---

## Part C — Script

### Scene 1 — The lookup table

Like me, you probably met this triangle in school, when you first learned algebra. It was handed to you as a tool: to multiply out a binomial like (a+b) raised to some power, you find the matching row and read off the coefficients.

> Left (x = −3.6): `ab_tex` of `(a+b)^n`. Right (x = +2.8): `PascalTriangle(rows=6)`, scaled to height 5. Triangle cells appear row by row with `LaggedStart` (0.2 s per row).
> Cycle n = 0 … 4, one beat per n. For each n: a mono label `n = 2` appears to the left of that row, the row's cells get a `FOCUS_YELLOW` outline, and the left side transforms (`TransformMatchingTex`) into the expansion:
> n=0: `1` · n=1: `a + b` · n=2: `a^2 + 2ab + b^2` · n=3: `a^3 + 3a^2b + 3ab^2 + b^3` · n=4: `a^4 + 4a^3b + 6a^2b^2 + 4ab^3 + b^4`.
> Coefficients in the expansion are `INK`. Draw a thin `MUTED` line from each coefficient to its cell for n = 2 and n = 3 only, so the reading-off is clear without clutter.

Each number is the sum of the two numbers above it, so the table is easy to extend. And that is usually where the story ends.

> Show the rule once: in row 3, outline the two 3's in `FOCUS_YELLOW`, draw two short `INK` arrows from them into the 6 of row 4, a `+` between the 3's, the 6 pulses (scale 1.15 and back, 0.4 s).

### Scene 2 — Choosing

Somewhere else, maybe in a probability class, you met this symbol: n choose k. It counts the ways to choose k elements from a set of n elements, when the order of the chosen elements does not matter.

Take the Swiss lottery. Six numbers are drawn from the numbers 1 to 42. If the order of the draw mattered, there would be 42 possibilities for the first number, 41 for the second, and so on down to 37 for the sixth. That is 42 factorial divided by 36 factorial, almost 3.8 billion ordered draws.

> Grid of 42 balls (7 columns × 6 rows): circles r = 0.26, stroke `RULE`, number inside in mono `INK` font_size 20. Grid on the left half.
> Six balls are picked one at a time (example draw 3, 11, 17, 24, 30, 41): each ball turns `FOCUS_YELLOW` outlined and flies to one of six slots on the right labeled `1st … 6th` (mono `MUTED`). Under each slot the number of balls still available appears: 42, 41, 40, 39, 38, 37.
> The six numbers combine into `42 \cdot 41 \cdot 40 \cdot 39 \cdot 38 \cdot 37 = \frac{42!}{36!}` and then `= 3\,776\,965\,920` (mono for the digits).

But to win, you only need the right six numbers, in any order. Each set of six numbers can be ordered in 6 factorial, that is 720, ways, and all 720 orders are the same ticket. So we divide by 6 factorial: 5,245,786 different results.

> The six slot balls shuffle through 4 quick reorderings (0.4 s each) under the mono label `same ticket`. Counter `6! = 720 orders`.
> The formula transforms: `\frac{42!}{36!}` → `\frac{42!}{36!\,6!} = 5\,245\,786`.

This expression has a name. With n elements and k chosen, it is n factorial divided by (n minus k) factorial and k factorial, the binomial coefficient, written like this and read "n choose k".

> Transform the numbers into the general form: 42 → n, 6 → k, 36 → n − k: `\frac{n!}{(n-k)!\,k!} = \binom{n}{k}`. Below it, in the display font: `n choose k`. Underline the word `choose` in `FOCUS_YELLOW` and keep it underlined to the end of the scene.

### Scene 3 — The statement that connects them

What you might not have seen written out is the statement that connects these two things, the binomial theorem:

> Center, font_size 56: `(a+b)^n = \sum_{k=0}^{n} \binom{n}{k}\, a^{n-k} b^{k}` with `ab_tex`. Isolate the parts `(a+b)^n`, `\sum_{k=0}^{n}`, `\binom{n}{k}`, `a^{n-k}`, `b^{k}` so each can be outlined.

Read it from left to right. If you multiply out (a+b) to the n-th power, you get a sum over all combinations of powers of a and b, from a to the n down to b to the n, where the two exponents always add up to n. And each of these terms is multiplied by a coefficient, the number from Pascal's triangle.

> Walk through the formula with `FOCUS_YELLOW` outlines, synchronised to the words: "multiply out" → `(a+b)^n`; "a sum over all combinations" → `\sum_{k=0}^{n}`; "powers of a and b" → `a^{n-k} b^{k}`, with a small `MUTED` note below it: `(n-k) + k = n`; "coefficient" → `\binom{n}{k}`.
> On "the number from Pascal's triangle": the formula moves to the upper left (scale 0.7), the triangle from Scene 1 fades in on the right.

So the entries of Pascal's triangle are binomial coefficients. The row is n, and the position in the row, counted from zero at the left, is k.

> Row labels `n = 0 … 6` on the left of the triangle (mono `MUTED`). Under row 6, position labels `k = 0 … 6`. Then, for rows 0–4, each cell's number cross-fades to a small `\binom{n}{k}` and back (0.8 s, `LaggedStart` across the cells).

### Scene 4 — The question

My question is: why? The numbers in this triangle come from a simple rule, each one is the sum of the two above it. Why should the same numbers count the ways to choose k things out of n? What does lottery counting have to do with multiplying out brackets?

> The triangle moves to the center and scales up to height 6. The addition rule animates on six cells in turn (parents outlined, two arrows, child pulses), one beat each.
> Then the triangle shrinks to the right third. On the left, `\binom{n}{k}` and `(a+b)^n` appear side by side, with a large `?` in the display font between them.

### Scene 5 — Multiplying out, one pick per bracket

To answer this, let's slow down and look at what multiplying out actually does. Take n equals three: (a+b) times (a+b) times (a+b). To multiply this out, you pick one term from each bracket, either its a or its b, and multiply your three picks. You do this for every possible combination of picks, and add up all the results.

> Header: `BracketRow(3)` at y = 3.1, bracket numbers 1 2 3 below. Right of it: `=`.
> Go through the 8 picks in the order aaa, aab, aba, abb, baa, bab, bba, bbb. For each pick: `BracketRow.pick` outlines the chosen letter in each bracket (the other letter dims); copies of the three chosen letters fly right of the `=` and form e.g. `a \cdot b \cdot a`, which transforms into `a^2 b`; the term then moves to the tally line at y = 0.6, appended with `+`.
> Pacing: the first two picks are shown step by step, each step its own beat. The next three run faster (one beat per pick), and the last three run as one quick sequence (one beat for all three).
> Under every term in the tally, keep its pick word (`aab`, `aba`, …) in mono `MUTED`, font_size 18. Scene 6 needs these.
> Top right counter (mono): `2 \cdot 2 \cdot 2 = 8` terms.

There are two choices in each of the three brackets, so two times two times two, eight combinations.

> Final tally line: `a^3 + a^2b + a^2b + ab^2 + a^2b + ab^2 + ab^2 + b^3`.

Now we collect like terms. a cubed appears once, a squared b three times, a b squared three times, b cubed once. One, three, three, one: row three of the triangle.

> Like terms slide together (each group keeps its pick words underneath), then merge into `a^3 + 3a^2b + 3ab^2 + b^3`. The coefficients appear in `INK`, outlined briefly in `FOCUS_YELLOW`. A small triangle (rows 0–3) in the top right corner highlights row 3.

### Scene 6 — A coefficient counts choices

So a coefficient counts how many ways there are to arrive at a term by choosing one letter from each bracket.

> The word `choosing` in the display font with a `FOCUS_YELLOW` underline. It then shrinks and moves next to a small `\binom{n}{k}` with the label `n choose k`, linking back to Scene 2.

Look at a squared b. Its coefficient is three, because there are three ways to make it. Exactly one bracket has to give its b, and then the other two give a. So the only real decision is which of the three brackets supplies the b. That is choosing one bracket out of three, three choose one, which is three.

> Left column: three `PickWord`s stacked, `(b, a, a)`, `(a, b, a)`, `(a, a, b)`, with `forced="a"`: the b's at full opacity, the a's at 0.4. Next to each, in mono, the chosen bracket as a set: `{1}`, `{2}`, `{3}`. A brace on the right: `\binom{3}{1} = 3`.

The same works for every term. For a b squared, we choose which two of the three brackets supply a b. That gives three choose two, which is again three. In general, the coefficient of a to the n minus k, b to the k, is the number of ways to choose which k of the n brackets supply a b. That is n choose k. This is the binomial theorem, and it is the first half of our answer.

> Right column: `(b, b, a)`, `(b, a, b)`, `(a, b, b)` with sets `{1,2}`, `{1,3}`, `{2,3}`, brace `\binom{3}{2} = 3`.
> Then the general statement at the bottom: `\text{coefficient of } a^{n-k}b^{k} = \binom{n}{k}`.

Notice also that choosing the brackets for the b's automatically decides the brackets for the a's: they are the remaining ones. So three choose one equals three choose two, and in general n choose k equals n choose n minus k. This is why Pascal's triangle is symmetric.

> In the right column, swap the opacities: a's full, b's 0.4. The sets change to the a-positions: `{3}`, `{2}`, `{1}`, so the brace now reads `\binom{3}{1}`. The equation `\binom{3}{1} = \binom{3}{2}` appears, then `\binom{n}{k} = \binom{n}{n-k}`.
> The corner triangle mirrors about its vertical center line (draw the axis as a solid `MUTED` line, 1 px); the cells do not move, which shows the symmetry.

But this still does not explain the rule that builds the triangle. Why is each entry the sum of the two entries above it?

> Fade everything except the corner triangle.

### Scene 7 — The decision tree

To see that, we draw the same multiplication as a tree of decisions. We start at the top with one, because (a+b) to the zero is one: nothing has been multiplied yet. Every bracket we multiply by adds one level to the tree: at each node we either multiply by the bracket's a, going left, or by its b, going right.

> Root `1` at (0, 2.9). Header top left: `(a+b)^0`, which grows to `(a+b)\cdot(a+b)\cdots` as levels are added. Top right tally (mono): `2^0 = 1`.
> Level 1: two edges `Create`, labeled `×a` (blue, left) and `×b` (orange, right); nodes a and b appear. Under the new level, the path products appear in `MUTED` (`a`, `b`) — beat — then fade. Tally `2^1 = 2`.
> Level 2: same. Products shown under the leaves: `a^2`, `ab`, `ab`, `b^2`. Tally `2^2 = 4`.

A path from the top down to the bottom is one way to pick a letter from each bracket, and the product along the path is one term of the expansion. Every new bracket doubles the number of paths, so before collecting like terms there are 2 to the n of them.

> Level 3. Products under the leaves: `a^3, a^2b, a^2b, ab^2, a^2b, ab^2, ab^2, b^3`. Tally `2^3 = 8`. Briefly bring back the Scene 5 tally line under the leaves to show these are the same eight terms with the same pick words, then fade it.
> Trace one path with `trace_path("aba")`: 1 → ×a → ×b → ×a, the product `a \cdot b \cdot a = a^2b` appears next to the leaf.
> Level 4 quickly: 16 leaves drawn as small dots (r = 0.06, `INK2`), tally `2^4 = 16` — beat — then `Restore` to the depth-3 tree.

### Scene 8 — Folding the tree into the triangle

Now one change. Instead of writing only the letter we just picked into each node, let's write the product so far: everything multiplied along the path from the top down to that node.

> Every node's letter transforms into its prefix product: level 1 `a`, `b`; level 2 `a^2`, `ab`, `ab`, `b^2`; level 3 `a^3, a^2b, a^2b, ab^2, a^2b, ab^2, ab^2, b^3`. Nodes become rounded cells wide enough for the term.

Some nodes in the same row now hold the same product. In row two, a b appears twice: once as a then b, once as b then a. Two nodes with the same product have the same future: whatever we multiply next, they produce the same terms. So we can merge them into one node, as long as we remember how many paths arrive there.

> Implementation: every node moves to its lattice position (n, k), where k = number of b's in its path (`Lattice` geometry, dx = 1.7, dy = 1.35, top = 2.8). Edges follow their endpoints (updaters or `always_redraw`). Nodes that land on the same position are replaced by one node with a count badge equal to how many landed there. Duplicate edges coincide and are merged the same way.
> Do it row by row so it can be followed: row 2 first (the two ab nodes slide together → badge `2`; their subtrees slide with them and overlap). Then row 3 (three a²b → `3`, three ab² → `3`). a³, b³ and the root get badge `1`.
> Edge colors switch to lattice style: ×a edges blue, ×b edges orange, opacity 0.6.

What is left is a triangle. Each node is a term, a to the n minus k, b to the k, and the number in it counts the paths from the top that reach it. One. One, one. One, two, one. One, three, three, one. This is Pascal's triangle.

> The count badges grow into Pascal cells (B.3 style, blue ramp); the term labels shrink and sit above the cells in `MUTED`-dimmed color. The Scene 1 triangle (rows 0–3) fades in at exactly the same positions at opacity 0.5 to show the match — beat — then fades out.

So an entry of Pascal's triangle counts paths. A path to a to the n minus k, b to the k, is a sequence of n steps, k of them to the right, multiplying by b, and the rest to the left, multiplying by a. Choosing which k steps go right is choosing k out of n. That is n choose k, the same count as before.

> Trace the three paths into a²b one after the other with `trace_path`: "aab", "aba", "baa". Each word appears next to the node in mono. Then `\binom{3}{1} = 3` next to the node.

### Scene 9 — Counting by the last step

Now we can finally see the rule. Pick a node, say a squared b in row three, and ask: one step earlier, where was each path that ends here?

> Focus on node (3, 1) = a²b. Dim everything to 0.35 except it and its two parents, a² at (2, 0) and ab at (2, 1), and the two edges into it.

There are only two possibilities. Either the path was at a b, and its last step multiplied by a. Or it was at a squared, and its last step multiplied by b. There is no third way in, and no path can come in both ways. So the number of paths into a squared b is the number of paths into a b plus the number of paths into a squared. Two plus one, three.

> Trace the 2 paths into ab in `PATH_AQUA`, then extend both along the blue ×a edge into a²b. `flow_count(ab, a²b, 2, A_BLUE)`: the 2 travels along the blue edge.
> Trace the 1 path into a², extend along the orange ×b edge, `flow_count(a², a²b, 1, B_ORANGE)`.
> At a²b, mono text `2 + 1 = 3` (the 2 in blue-edge position, the 1 in orange-edge position), which then collapses into the badge `3`.

This works for every node. Here is the six in row four, the term a squared b squared. Its paths come either from a squared b, ending with a b, three of them, or from a b squared, ending with an a, also three. Three plus three is six.

> Extend the lattice to row 4 (`Create` edges, nodes appear with their counts). Reframe the camera so rows 0–4 fit.
> Same sequence for (4, 2) = a²b²: `flow_count(a²b, a²b², 3, B_ORANGE)` along the orange edge, `flow_count(ab², a²b², 3, A_BLUE)` along the blue edge, `3 + 3 = 6`.

That is the rule of Pascal's triangle. Each entry is the sum of the two above it, because every path to a node arrives through exactly one of the two nodes above it.

> Display font, bottom of the frame: `Every path arrives through exactly one of the two nodes above.`

### Scene 10 — Two ways to count the same paths

Now put the two halves together. We have counted the paths to the same node in two different ways.

Counting the steps: a path to a to the n minus k, b to the k, is a choice of which k of its n steps are b-steps. That gives n choose k paths.

Counting by the last step: the paths that end with a b-step come from the node with k minus one b's in the row above, and the paths that end with an a-step come from the node with k b's in the row above.

Both counts describe the same set of paths, so they must be equal: n choose k equals n minus one choose k minus one, plus n minus one choose k.

> Generic diagram, center: child cell labeled `\binom{n}{k}`; above-left parent `\binom{n-1}{k-1}` connected by an orange ×b edge; above-right parent `\binom{n-1}{k}` connected by a blue ×a edge. Same geometry as the lattice.
> Equation builds at the bottom: `\binom{n}{k} = \binom{n-1}{k-1} + \binom{n-1}{k}`. Underline `\binom{n-1}{k-1}` in orange with the mono label `last step ×b`, underline `\binom{n-1}{k}` in blue with `last step ×a`.

In the language of brackets: to choose which k of the n brackets give a b, look at the last bracket. If it gives b, you still have to choose k minus one b's from the first n minus one brackets. If it gives a, you have to choose all k b's from the first n minus one brackets. Every choice falls into exactly one of these two cases.

> Concrete check with n = 4, k = 2 on the left half: the six pick words of a²b² in a column, mono: `aabb, abab, abba, baab, baba, bbaa`. Their last letters get outlined. The words sort into two groups by last letter:
> ending in b: `aabb, abab, baab` → label `\binom{3}{1} = 3` (one b among the first three letters);
> ending in a: `abba, baba, bbaa` → label `\binom{3}{2} = 3` (two b's among the first three letters).
> `3 + 3 = 6 = \binom{4}{2}`.

### Scene 11 — The triangle builds itself

So adding and choosing are the same thing, seen from two directions. Start with one path at the top. Let every node send its paths down both of its edges, and let every node add up what arrives.

> Lattice rows 0–7: dx = 1.0, dy = 0.85, top = 3.1, cells 0.62 × 0.44. Term labels off (too small at this scale).
> Row by row: from each node of row n−1, `flow_count` along both edges at the same time (blue along ×a, orange along ×b); the children fill in with their sums and their cell color ramps in. Rows 1–3 at 1.2 s per row, rows 4–7 at 0.6 s per row.
> Row 7 values must read 1 7 21 35 35 21 7 1.

The table you learned in school was never only a lookup table. Each number counts paths through a tree of choices: the ways to choose which k of n brackets give a b. And adding the two numbers above is nothing more than sorting those choices by what happened in the last bracket.

> Edges fade to opacity 0.15. The camera pulls out slightly and the triangle moves to the right, so the frame matches Scene 1 exactly: `(a+b)^n` on the left, triangle on the right.
> Final beat: highlight row 4; the left side shows `a^4 + 4a^3b + 6a^2b^2 + 4ab^3 + b^4`; the coefficient 6 and its cell get `FOCUS_YELLOW`; behind the cells, the six paths into that node are drawn in `PATH_AQUA` at opacity 0.4.
> End card: title in the display font, centered.

### Scene 12 — Coda, optional

One last picture. Replace every node with a peg and drop balls from the top. At each peg a ball bounces left or right with equal chance. A ball that lands in slot k bounced right k times out of n, and there are n choose k such paths, each with probability one over 2 to the n. So the pile in slot k grows in proportion to n choose k. This is the binomial distribution, built by gravity, and it is where this triangle leads next: statistics, error-correcting codes, option pricing. But that is another video.

> Galton board on a `PANEL` background: 10 rows of pegs (dots r = 0.05, `MUTED`) at the lattice positions; 11 bins at the bottom.
> 400 balls (r = 0.05, `A_BLUE`) fall one after another, left/right decided by a seeded random generator (`random.Random(7)`) so the render is reproducible. Balls stack in the bins.
> Overlay the expected heights 400 · C(10,k) / 1024 as an `INK` step outline (center bin: 98.4).

---

## Part D — Production

**D.1 Tools.** Manim Community Edition (v0.18 or newer, Python 3.11), a LaTeX installation with `amsmath` and `amssymb`, ffmpeg. Manim fits this video because the formulas are LaTeX-native, `TransformMatchingTex` handles the formula morphs, and the tree/lattice animations are geometry. Motion Canvas (TypeScript) has a better timeline editor but weaker formula support, so Manim is the better choice here.

**D.2 Project layout**
```
video/
  fonts/                 # font files, installed system-wide
  palette.py             # Part A.1 constants + config
  components.py          # Part B
  s01_lookup.py … s12_galton.py   # one Scene class per file
  narration/s01.txt …    # narration text per scene, copied from Part C (reference only)
  render.sh              # renders all scenes, concatenates them, writes beats.csv
  out/binomial_full.mp4  # the one continuous clip for Premiere
  out/beats.csv          # beat markers (A.5)
```

**D.3 Workflow**
1. Build `palette.py` and `components.py`. Render one still per component (`manim -s`) and compare with The Binomial World in dark mode.
2. Build the scenes in order, following A.5: each beat followed by `self.wait(BEAT)` and nothing longer. Do not use `manim-voiceover` or any audio syncing.
3. Draft renders at `-ql`, final renders at `-qh` (1080p60), or `-qk` for 4K.
4. Concatenate all scenes into `out/binomial_full.mp4` with no gaps or transitions, and write `out/beats.csv`.
5. Sebastian records the voiceover and lays it over the clip in Premiere Pro, adding freeze frames wherever a frame needs to stay on screen longer.

**D.4 Checks before the final render**
- Pascal values (rows 0–7): 1 · 1 1 · 1 2 1 · 1 3 3 1 · 1 4 6 4 1 · 1 5 10 10 5 1 · 1 6 15 20 15 6 1 · 1 7 21 35 35 21 7 1.
- Lottery: 42!/36! = 3,776,965,920; C(42,6) = 5,245,786; 6! = 720.
- Tree leaves left to right: aaa, aab, aba, abb, baa, bab, bba, bbb, with products a³, a²b, a²b, ab², a²b, ab², ab², b³.
- Lattice: ×a always down-left and blue, ×b always down-right and orange. Node (n, k) has k b's.
- Every a is blue and every b is orange in every frame. Grep the code for any `MathTex` containing a or b that is not built with `ab_tex`.
- Fonts render as the intended faces (no fallback).
- No text overlaps edges or cells; check stills at the end of every scene.
- No `self.wait()` longer than `BEAT`, and nothing moves during any wait (A.5).
- The rendered clip is much shorter than the finished video (the narration runs ≈ 12 min with the coda). That is expected: Premiere sets the length.

---

## Part E — Changes made to the draft

1. **"n choose k" definition.** The draft said "choose n elements from a sequence of length k". Corrected to "choose k elements from a set of n elements". It is a set because the order does not matter.
2. **How multiplying out works.** "Multiply each term in the brackets by each other term" is replaced by "pick one term from each bracket and multiply the picks". This is the idea the whole video builds on, so it has to be exact.
3. **The ab² paragraph.** The draft said ab² comes from "choosing two a's from three". ab² has one a and two b's. It now says "choose which two brackets give b", which is C(3,2). The symmetry argument (choosing the b-brackets automatically decides the a-brackets) is kept and made explicit. The animation tuples were changed to match: (b,b,a), (b,a,b), (a,b,b).
4. **One convention for k.** k = number of b's everywhere, with (a+b)ⁿ = Σ C(n,k) aⁿ⁻ᵏbᵏ. This matches your a²b ↔ C(3,1) example. "Diagonal columns" became "position in the row, counted from zero".
5. **Lottery.** Added the numbers: 42!/36! ≈ 3.8 billion ordered draws, 6! = 720 orders, C(42,6) = 5,245,786.
6. **New Scenes 8–11** complete the argument the draft stopped before: fold the tree into the triangle by merging equal products, count paths by the last step (sum of the two above), show that both counts are the same paths, and let the triangle build itself.
7. **Scene 12 (optional)** connects the lattice to the Galton board and the binomial distribution as an outro.
8. Timing: the animation is rendered as one continuous clip with short pauses only; you set the holds in Premiere with freeze frames (A.5). Per-scene time estimates were removed.
9. Your tree design (multiplication signs on the edges, products shown in another color below the last row, the 2ⁿ tally, the growing (a+b)·(a+b)… header) is kept as you described it in Scene 7.
