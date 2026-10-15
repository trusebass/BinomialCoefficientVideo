# Why Pascal's Triangle Counts Choices — animation

Built from `../Binomial Coefficient - Video Script.md` with Manim Community v0.22.

## Running it

```sh
./render.sh            # all scenes at 1080p60, joined into out/binomial_full.mp4
./render.sh l          # quick drafts at 480p15
./render.sh h S08      # re-render one scene, then re-join everything

.venv/bin/manim -ql s05_multiply.py S05Multiply     # one scene, draft
.venv/bin/manim -qh -s s05_multiply.py S05Multiply  # only its last frame, as a PNG
.venv/bin/python tools/contact.py S05 media/videos/s05_multiply/480p15/S05Multiply.mp4
                                                    # every beat's still frame on one sheet
.venv/bin/python tools/seam.py out/clips/S04.mp4 out/clips/S05.mp4
                                                    # does S05 start where S04 ended?
```

Output:
- `out/binomial_full.mp4`: the one continuous clip for Premiere
- `out/clips/S01.mp4 … S12.mp4`: the per-scene clips
- `out/beats.csv`: one row per beat. `start_time_in_full_video` is when the beat's
  animation starts; `freeze_from` is when it has finished. From `freeze_from` on, the frame
  is still for 0.5 s, so any frame there is safe to freeze.
- `narration/s01.txt …`: the spoken text per scene, copied from the script (reference only).

## Files

| File | What it is |
|---|---|
| `palette.py` | Colors, fonts, timing constants (script Part A), OKLab color mixing |
| `components.py` | `ab_tex`, `PascalCell`, `PascalTriangle`, `BracketRow`, `PickWord`, `DecisionTree`, `Lattice`, `trace_path`, `flow_count`, and `BeatScene` (Part B) |
| `s01_lookup.py … s12_galton.py` | One scene class each. Each file has an `end_state()` that rebuilds its last frame; the next scene starts from it, so the clips join without a jump |
| `tools/timeline.py` | Exact beat times from the frame counts of Manim's partial movie files |
| `tools/assemble.py` | Joins the clips (`ffmpeg -f concat -c copy`), writes `beats.csv`, checks the length |
| `preview_components.py` | One still per component, for checking the look |

## Manim, as learned on this project

**The model.** A `Scene` subclass draws in `construct()`. Everything on screen is a *mobject*
(`VMobject` = vector shape, `VGroup` = a group that moves as one). `self.play(anim, …)` runs
animations together; `self.wait(t)` holds. Every `play`/`wait` is rendered into its own small
"partial movie file", and ffmpeg joins them into the scene's video. That's also why
re-renders are fast: an unchanged `play` call is reused from cache.

**Config precedence.** CLI flags (`-ql`, `-qh`) < `manim.cfg` < `config.x = …` in Python code.
Code wins, so `palette.py` only sets the background; setting the resolution there would
silently turn your `-ql` drafts into full-HD renders.

**LaTeX.** `MathTex` runs real LaTeX: TeX → DVI → SVG (dvisvgm) → Bézier paths. Colors set
*inside* the TeX (`\textcolor`) survive into Manim. `ab_tex` uses that to color every a/b,
skipping letters inside commands like `\frac` or `\binom`.

**Splitting formulas into parts.** Pass several strings (`ab_tex("(a+b)", "^{n}")`) or use
`{{ … }}`. In v0.22 a `{{` only opens a group at the start of the string or after a space:
`{{a}}^{2}{{b}}` does *not* split the `b`. `TransformMatchingTex` pairs parts whose TeX
strings are equal: the parts that match slide into place, and the rest fade.

**`Text`.** Rendered by Pango. The glyph list skips whitespace: in `Text("(b, a, a)")`,
glyph 3 is the second letter. If a font lacks a character, Pango silently borrows it from
another font. Bale Mono has ¹²³ but not ⁰ or ⁴, which is why `mono_power` builds exponents by hand.

**`.animate` is a builder.** `mob.animate.shift(UP)` copies the mobject, applies the call to
the copy and interpolates towards it. Two consequences:
- it isn't an `Animation` until `play` receives it;
- two `.animate` calls on the *same* mobject in one `play` fight. Each starts from the
  original, and the last one wins (Scene 11's edges stayed behind because of this).

Chain changes instead: `edges.animate.shift(v).set_stroke(opacity=0.15)`.

**Draw order.** Mobjects are drawn in the order they were added, group members in group order.
A label that moves into a later cell disappears under that cell's box (Scene 6's mirror).
Fix it with `set_z_index(1)`.

**`Transform` vs `ReplacementTransform`.** `Transform(a, b)` reshapes `a` to look like `b`, but
`a` is still the object on screen and `b` never gets added. `ReplacementTransform(a, b)` ends
with `b` on screen and `a` removed. Use the second when you'll keep working with `b`
(Scene 9's re-layout bug).

**`Succession` adds every mobject at its start.** Anything a later step transforms appears
on screen from the first frame. `BeatScene.beat(steps=[…])` plays steps as separate
`play` calls instead. A step can be a function, so its animations are built from the
scene as the previous step left it.

**Updaters.** `mob.add_updater(f)` calls `f(mob)` on every frame. In Scene 8 they keep each
edge clipped between its two moving nodes. Remove them afterwards (`clear_updaters()`), so
the holds are truly still frames.

**Rate functions.** `rate_func=there_and_back` runs an animation forward and back, so a pulse
ends exactly where it started. In `LaggedStart` with `lag_ratio=r` and N animations, each
lasts `run_time / (1 + r·(N-1))`.

**Many objects, one animation.** The 400 Galton balls are driven by a single
`UpdateFromAlphaFunc`: it maps the animation's progress (0 to 1) to a time, and from that
time to every ball's position. That's far cheaper than 400 separate animations.

**Camera.** `MovingCameraScene` has `self.camera.frame`, a rectangle you can animate
(`frame.animate.scale(1.15)` pulls out). After that, "screen" and "world" coordinates
differ by the zoom. A "reframe" can also be done by moving the content instead (Scene 9),
which keeps the next scene's camera standard.

**Timing.** `self.renderer.time` adds a cached animation's *nominal* length but a fresh one's
*whole-frame* length (`floor(run_time × fps)` frames). After a few re-renders it drifts from
the real video. `BeatScene` therefore logs play indices, and `tools/timeline.py` counts the
real frames.

## Open points

- **Bale Mono license.** It's the mono font (`MONO_FONT` in `palette.py`); check that its
  license allows use in a published video. To switch, set `MONO_FONT = "IBM Plex Mono"` and re-render.
- **Scene 1 reading-off.** The script asks for lines from each coefficient to its cell. A
  straight line from the left would cross the other cells of the row, so each number flies
  from its cell to sit under its term instead.
- **Scene 8 overlay.** "The Scene 1 triangle fades in at exactly the same positions": the
  Scene 1 cells (larger) appear behind the lattice cells at 0.5 opacity, as a halo.
- **Order of the ending.** The end card is the last beat of Scene 11; the Galton coda follows
  it, as A.5 asks. To end on the title instead, move that beat in Premiere.
