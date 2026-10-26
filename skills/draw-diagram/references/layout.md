# Layout & sizing rules for generated `.draw` diagrams

The app has **no auto-layout**: the bounds you write are exactly what renders, and nothing
resizes an undersized node at load. Compute all node sizes first, then positions, then
connectors. `roundUp10(x)` = round up to the next multiple of 10; every `x`, `y`, `width`,
`height` and bend point must be a multiple of 10 (grid = 10 world units).

## 1. Text-width estimation (Inter font, you can't measure)

| Context | px per character |
|---|---|
| 12px regular (shape text, use-case text) | 6.6 |
| 12px bold (class/entity headers) | 7.2 |
| 11px regular (member/column rows) | 6.2 |

Overestimating is safe (a little extra width looks fine); never underestimate.

## 2. Sizing formulas

**Class node** (`rows` = total members; `stereo` = kind is `Interface` or `Enum`):

- `H = roundUp10(44 + 18*rows + (stereo ? 20 : 0))`
  (44 = 28 header + 8 padding + 8 slack; the +20 covers the «interface»/«enumeration» line
  the app's own minimum ignores — without it the last row clips.)
- `W = roundUp10(max(170, 7.2*len(name) + 30, 6.2*len(longestRow) + 30))`, capped at 420.
  `longestRow` uses the rendered forms `+ name: Type` / `+ name(params): Type`. If a row
  would exceed the cap, shorten the parameter list to `(...)`.

**Entity node** (`cols` = column count):

- `H = roundUp10(44 + 18*cols)`
- `W = roundUp10(max(180, 7.2*len(name) + 30, 6.2*len(longestColText) + 30))` where column
  text is `name: type` plus rendered flags (` PK`, ` FK`, ` UNIQUE`, ` NOT NULL` — NOT NULL
  is suppressed on PK rows).

**Use case**: try W = 170; single line if `6.6*len(text) ≤ W − 20`, else wrap
(`lines = ceil(6.6*len / (W − 20))`); keep lines ≤ 2 by raising W up to 220 first.
`H = roundUp10(max(72, 18*lines + 44))`.

**Actor**: always 48×84 (widening fattens the stick figure). Names ≤ 10 chars; the label
overflows the bounds without clipping, so keep ≥ 60 units clear either side.

**Shapes (flowchart)**: process `Rectangle` W = `roundUp10(max(120, 6.6*charsPerLine + 20))`,
H = 60; `Terminator` 140×50; decision `Diamond` W = `roundUp10(max(140, 13*charsPerLine))`,
H = 80 (text area ≈ half the bounds); `Parallelogram` 150×60. Insert `\n` manually for text
longer than ~18 chars.

**Other defaults** (use when content doesn't dictate size): shape 120×70, class 170×110,
entity 180×120, useCase 130×72, systemBoundary 320×220, package 160×110, component 160×90,
deployment 150×120.

## 3. UML class diagrams — layered by inheritance

1. Build the generalization/realization DAG (edges derived→base). A node's layer = longest
   path from a root base; interfaces/root bases at layer 0 (top), derived types below.
2. Compute all sizes first (§2).
3. Vertical: `y(layer 0) = 40`; `y(layer k) = y(layer k−1) + maxHeight(layer k−1) + 80`.
4. Horizontal within a layer: order nodes by the average x of their parents (barycenter);
   place left→right with **60-unit gaps**, starting at x = 40. Then center each parent over
   the horizontal span of its children (snap to grid).
5. Association-only neighbors (no inheritance link): same layer as their strongest partner,
   directly adjacent; if a connector to them would cross an unrelated node, move them one
   layer down, off to the side.
6. Routes: `Generalization`/`Realization` → `"Orthogonal"` (siblings share the horizontal
   mid-level bus, giving tidy axis-aligned risers), no bend points. `Association`/`Dependency`
   between adjacent nodes → `"Straight"`; between non-adjacent nodes → `"Orthogonal"`.
7. Disconnected clusters: lay out each independently, then place side by side, tops aligned,
   **120 units** between cluster bounding boxes; wrap to a new band below at ~1600 total width.

## 4. ER diagrams

1. Size every entity first (§2). One connector per FK: `kind: "Relationship"`,
   **source = referencing child table** (FK holder), target = referenced parent.
   `sourceCardinality`: `ZeroOrMany` (default) or `OneOrMany` (mandatory child);
   `targetCardinality`: `One`, or `ZeroOrOne` when the FK column is nullable.
2. Placement grid: `cols = ceil(sqrt(n))`. Most-connected table in/near the center; then
   greedily place the unplaced table with the most already-placed neighbors into the free
   cell nearest those neighbors — every table should be orthogonally adjacent to at least
   one related table.
3. Cell pitch: column pitch = max table width + 120; row pitch = max table height + 80.
   Snap each table's top-left to the grid; left-align within a column, top-align within a row.
4. Route: `"Orthogonal"` (crow's feet render cleanly on axis-aligned ends); `"Rounded"` is
   fine for small 2–4 table diagrams. No bend points.
5. Anchors: omit. Exception — multiple relationships between the same pair of tables: spread
   them on the facing sides with explicit anchors (`{"x":1,"y":0.33}` / `{"x":1,"y":0.66}`
   on the source side and matching `{"x":0,…}` targets).
6. `centerLabel` = FK column name is helpful when the diagram has ≤ 8 relationships; skip it
   on bigger diagrams.

## 5. Use-case diagrams

1. `nodes` array order (and `zIndex`): **systemBoundary first**, then use cases, then actors.
2. Use cases in a single column inside the boundary (two columns of 60-unit gap when > 5):
   x = boundaryX + 40; first y = boundaryY + 50 (title clearance); then
   `y(next) = y(prev) + H(prev) + 40`.
3. Compute use-case positions first at a provisional origin, then derive the boundary as
   their union inflated by 40 left/right/bottom and 50 top (rounded to grid), then translate
   everything to its final position. The boundary must fully contain its use cases —
   containment is visual only, nothing enforces it.
4. Actors: primary actors on the left — right edge 120 units left of the boundary; each actor
   vertically centered on the average center of the use cases it connects to; ≥ 120 units
   between actors. Secondary/system actors mirrored on the right, same gaps.
5. Connectors: actor↔use case → `"Association"`, `route: "Straight"`, no anchors.
   `Include`: source = base, target = included. `Extend`: source = extending, target =
   extended. Both auto-render dashed arrows with «include»/«extend» labels — no `centerLabel`.

## 6. Flowcharts / explanatory diagrams

1. Top-down spine: all main-path nodes centered on one vertical axis (e.g. centerX = 300);
   `y(next) = y(prev) + H(prev) + 60`. Start/end = `Terminator`, steps = `Rectangle`,
   decisions = `Diamond`, I/O = `Parallelogram`, subroutine = `PredefinedProcess`,
   data store = `Cylinder`. Prefer left-right flow beyond ~8 sequential steps.
2. Sequential edges: `kind: "DirectedAssociation"`, `route: "Straight"` (aligned nodes give
   a clean vertical segment).
3. Decision branches: "yes" continues down the spine (edge gets `centerLabel: "yes"`);
   the "no" branch goes right — branch node at `x = spineCenterX + diamondW/2 + 140`,
   vertically centered on the diamond; branch edge `"Straight"` with `centerLabel: "no"`.
4. Loop-backs/rejoins are the **one case for explicit `bendPoints`**: `route: "Orthogonal"`
   with bend points in a clear vertical lane 60 units outside the widest node on that side,
   e.g. `[{"x": laneX, "y": ySourceCenter}, {"x": laneX, "y": yTargetCenter}]`. Every bend
   point on the grid and ≥ 20 units clear of every node's bounds.
5. Keep ≥ 60 units vertical and ≥ 80 units horizontal clearance between non-adjacent nodes
   so straight/orthogonal segments never cross an intermediate node; when an edge must span
   several rows, use `"Orthogonal"` plus a lane bend point instead of `"Straight"`.

## 7. General rules (all diagram types)

- **Start content near (40, 40) — this is a hard rule.** The app opens documents at zoom 1
  with the viewport at the origin and does NOT auto-fit to content; a diagram placed far from
  the origin opens looking like an empty document (until the user hits Fit to content).
  Keep all coordinates positive.
- ≥ 40 units clear between any two node rectangles that aren't boundary+content.
- Default to **no** `bendPoints` — routing is recomputed at load from node bounds and stays
  clean whenever the clearances above are respected.
- Omit `style` everywhere unless the user asked for specific colors/emphasis.
- One diagram per file. For a large model, prefer several focused files (per namespace /
  subsystem / table cluster) over one giant diagram; suggest the split to the user.
