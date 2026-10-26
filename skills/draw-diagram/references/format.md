# The `.draw` file format (Draw schema v2)

> Derived from Draw `src/Draw.Model` at schema **v2**, commit `e57c65b`, 2026-07-01.
> If generated files stop loading in the app, this spec has drifted — re-derive it from the
> Draw repo (`src/Draw.Model`, especially `Serialization/JsonDocumentSerializer.cs` and
> `Nodes/NodeBase.cs`) and update this header.

One diagram per file. JSON, UTF-8, conventionally 2-space indented.

## Serialization rules (get these right or the file won't load)

- **`$type` MUST be the first key of every node object.** The deserializer does not accept
  an out-of-order discriminator; putting `"id"` before `"$type"` fails the whole file.
- All property names are **camelCase** (`sourceNodeId`, `bendPoints`, `isPrimaryKey`).
- **Omit instead of null**: never write `"key": null` and never write empty collections
  (`"markers": []`, `"bendPoints": []`) — omit the key entirely. Omitted optional keys get
  the documented defaults. (The app's own writer is more verbose — it emits empty arrays,
  full `style` blocks, `"showGrid": false`, etc. Omission loads identically, and the app
  normalizes the file on its next save.)
- **Enums are PascalCase strings**, exact member names: `"Orthogonal"`, `"ZeroOrMany"`,
  `"RoundedRectangle"`, `"Interface"`, `"Er"`. Always write strings — this is what the app
  writes. (A stale comment in `ShapeKind.cs` claims integer serialization; it is wrong —
  don't let it override this rule when re-deriving the spec.)
- **Colors** are `#AARRGGBB` strings (8 hex digits, alpha first): `#FF3574F0`. Alpha is never
  omitted.
- **IDs** are lowercase hyphenated GUIDs (`"9b2f4c1e-7a3d-4e8b-a1c5-2d6f8e0b3a47"`), unique
  across **all** nodes AND connectors in the file.
- **Points/rects** are objects: `{"x": 40, "y": 40}` / `{"x": 40, "y": 40, "width": 170, "height": 80}`.
- Dates (metadata) are ISO-8601 strings: `"2026-07-01T12:00:00+00:00"`.

## Root object

```json
{
  "schemaVersion": 2,
  "diagramType": "Class",
  "title": "Payment methods",
  "nodes": [ ... ],
  "connectors": [ ... ],
  "metadata": { "createdUtc": "2026-07-01T12:00:00+00:00", "modifiedUtc": "2026-07-01T12:00:00+00:00" }
}
```

| Property | Type | Notes |
|---|---|---|
| `schemaVersion` | int | **Always exactly `2`.** Greater is rejected at load; 0/1 triggers a legacy color migration you don't want. |
| `diagramType` | enum | `Freeform` \| `Class` \| `UseCase` \| `Er` \| `MindMap` (note: `Er`, not `ER`). Informational — sets the app's default palette, doesn't restrict node types. |
| `title` | string? | Diagram title. Set it. |
| `showGrid` | bool | Omit (default false = grid hidden). |
| `nodes` | array | See node types below. Order matters for z-order tie-breaks. |
| `connectors` | array | See connector below. |
| `defaultShapeStyle` | object | Omit — UI state for newly created shapes, not diagram content. |
| `metadata` | object | `author?`, `createdUtc?`, `modifiedUtc?` (ISO-8601), `appVersion?`. Set the two timestamps to generation time; **never invent `appVersion`**; omit `author` unless known. |

## Common node fields (all `$type`s)

| Property | Type | Notes |
|---|---|---|
| `$type` | string | **First key.** One of the discriminators below. |
| `id` | GUID string | Unique. |
| `bounds` | `{x,y,width,height}` | World units. What you write is exactly what renders — there is **no auto-layout and no load-time size clamping** (an undersized class/entity box renders with clipped rows). Keep everything on the 10-unit grid. |
| `zIndex` | int | Render order at load is `zIndex` ascending, array order breaks ties. Give every node an explicit contiguous `zIndex` (0..n−1) matching array order; `systemBoundary` nodes first/lowest. |
| `style` | object | Omit for theme-following defaults (recommended). See "Style objects". |
| `markers` | string[] | Optional badge icons; omit when empty. Values: `Todo`, `InProgress`, `Done`, `Stuck`, `Important`, `Idea`, `Question`, `Warning`, `Chat`, `Happy`, `Angry`, `Phone`, `Mail`, `Car`, `Island`, `PalmTree`, `Flag`, `Heart`, `Coffee`, `Calendar`, `MapPin`. |

## Node types

### `shape` — basic/flowchart shape with centered text

```json
{ "$type": "shape", "id": "…", "bounds": {…}, "zIndex": 0, "kind": "Diamond", "text": "Valid?" }
```

| Property | Type | Notes |
|---|---|---|
| `kind` | enum | See full list below. Default `Rectangle`. |
| `text` | string | Centered, wraps (usable width ≈ width − 12). Default `""`. |
| `cornerRadius` | number | Only meaningful for `RoundedRectangle`/`MindMapTopicRounded`. Default 12 — omit unless overriding. |

`kind` values — geometric: `Rectangle`, `RoundedRectangle`, `Ellipse`, `Circle`, `Diamond`,
`Parallelogram`, `Trapezoid`, `Triangle`, `Note` (UML note with folded corner), `Hexagon`,
`Pentagon`, `Octagon`, `Star`, `Cross`, `Cloud`, `Callout`.
Flowchart: `Terminator` (start/end pill), `Cylinder` (database), `Document`,
`PredefinedProcess` (subroutine), `ManualInput`, `OffPageConnector`, `Display`, `Delay`.
Block arrows: `ArrowRight`, `ArrowLeft`, `ArrowUp`, `ArrowDown`, `ArrowDouble`.
Mind-map: `MindMapTopic`, `MindMapTopicRounded` (avoid unless building mind maps).

### `class` — UML classifier (class / interface / enum)

```json
{
  "$type": "class", "id": "…", "bounds": {…}, "zIndex": 1,
  "kind": "Interface", "name": "IPaymentMethod",
  "members": [
    { "visibility": "Public", "name": "authorize", "type": "bool",
      "parameters": "amount: decimal", "kind": "Operation" }
  ]
}
```

| Property | Type | Notes |
|---|---|---|
| `kind` | enum | `Class` \| `Interface` \| `Enum`. Default `Class`. The `«interface»`/`«enumeration»` stereotype header is **derived from this** — never write `«interface»` into `name`. |
| `name` | string | Classifier name only. |
| `isAbstract` | bool | Default false. Set true for abstract classes (name renders italic). |
| `members` | array | Rendered top-to-bottom in array order (fields, then operations, is the convention). |

Member object:

| Property | Type | Notes |
|---|---|---|
| `visibility` | enum | `Public` \| `Private` \| `Protected` \| `Package` — rendered as `+ - # ~`. Default `Public`. |
| `name` | string | Member name only (no markers, no type). |
| `type` | string? | Field type / operation return type, free text. Omit for none. |
| `parameters` | string? | Operations only, free text without parentheses: `"amount: decimal, currency: string"`. Omit for none. |
| `kind` | enum | `Field` \| `Operation` \| `EnumLiteral`. Default `Field`. |
| `isStatic` | bool | Default false (renders underlined). |
| `isAbstract` | bool | Default false (renders italic). |

Rendered row text is generated by the app: field → `+ name: Type`, operation →
`+ name(params): Type`, enum literal → bare `name`. Don't duplicate any of that into `name`.

### `entity` — ER/database table

```json
{
  "$type": "entity", "id": "…", "bounds": {…}, "zIndex": 0,
  "name": "orders",
  "columns": [
    { "name": "id", "type": "int", "isPrimaryKey": true, "isNullable": false },
    { "name": "user_id", "type": "int", "isForeignKey": true, "isNullable": false }
  ]
}
```

Column object:

| Property | Type | Notes |
|---|---|---|
| `name` | string | Column name only — flags drive the rendered `PK`/`FK`/`UNIQUE`/`NOT NULL` suffixes; never append them to the name. |
| `type` | string? | Free SQL text: `"varchar(255)"`, `"decimal(10,2)"`. |
| `isPrimaryKey` | bool | Default false. PK rows render bold + underlined. |
| `isForeignKey` | bool | Default false. |
| `isNullable` | bool | **Default TRUE.** Write `"isNullable": false` explicitly for every PK and every NOT NULL column. (`NOT NULL` is auto-suppressed on PK rows.) |
| `isUnique` | bool | Default false. |

### `actor` — UML actor (stick figure)

```json
{ "$type": "actor", "id": "…", "bounds": {"x": 30, "y": 150, "width": 48, "height": 84}, "zIndex": 4, "name": "Customer" }
```

Always use the default 48×84 size (widening fattens the figure). The name label renders below
the figure, does not wrap and does not clip — keep names ≤ 10 chars and leave ≥ 60 units of
clear space either side.

### `useCase` — UML use case (ellipse)

```json
{ "$type": "useCase", "id": "…", "bounds": {…}, "zIndex": 1, "text": "Place order" }
```

Text wraps at width − 20.

### `systemBoundary` — titled rectangle drawn behind use cases

```json
{ "$type": "systemBoundary", "id": "…", "bounds": {…}, "zIndex": 0, "title": "Web shop" }
```

Containment is **visual only** — nothing enforces it. The boundary must geometrically contain
its use cases (see layout.md) and must come **first** in `nodes` with the lowest `zIndex`.

### `package` / `component` / `deployment` — UML structure nodes

```json
{ "$type": "package", "id": "…", "bounds": {…}, "zIndex": 0, "title": "Draw.Model" }
{ "$type": "component", "id": "…", "bounds": {…}, "zIndex": 1, "name": "OrderService" }
{ "$type": "deployment", "id": "…", "bounds": {…}, "zIndex": 2, "name": "AppServer" }
```

`package` carries `title`; `component` and `deployment` carry `name`. Defaults: package
160×110, component 160×90, deployment 150×120.

### `image` — exists in the format (base64 payload) but is out of scope for generation.

## Connector

```json
{
  "id": "…",
  "sourceNodeId": "…", "targetNodeId": "…",
  "kind": "Generalization",
  "route": "Orthogonal"
}
```

| Property | Type | Notes |
|---|---|---|
| `id` | GUID string | Unique (shared ID space with nodes). |
| `sourceNodeId` / `targetNodeId` | GUID string | Must reference existing node ids (a connector to a missing node loads but is silently invisible). Never equal to each other (a self-link renders degenerately). |
| `kind` | enum | See semantics table below. Default `Association`. |
| `sourceCardinality` / `targetCardinality` | enum | ER crow's feet: `Unspecified` (none) \| `One` \| `Many` \| `ZeroOrOne` \| `OneOrMany` \| `ZeroOrMany`. Omit when unspecified. |
| `route` | enum | `Straight` \| `Orthogonal` \| `Rounded` — **these three exact strings only**. Default `Straight`. |
| `bendPoints` | Point[] | Waypoint hints; the actual path is **recomputed at load** from node bounds (endpoints ray-cast from node centers). Omit by default — see layout.md for the one case to use them. |
| `sourceLabel` / `centerLabel` / `targetLabel` | string? | Optional labels. |
| `sourceAnchor` / `targetAnchor` | `{x,y}`? | **Fractions in [0,1]² of the node's bounds** (not world coords!). `{"x":1,"y":0.5}` = middle of right edge. Omit for automatic attachment. Use only to separate parallel edges between the same node pair. |
| `sourceLabelOffset` / `centerLabelOffset` / `targetLabelOffset` | `{x,y}`? | World-unit label nudges. Omit. |
| `style` | object | Omit (see Style objects — connector styles have a trap). |

### RelationshipKind semantics (decorations are automatic — set nothing else)

| `kind` | Source end | Target end | Line | Direction convention |
|---|---|---|---|---|
| `Association` | — | — | solid | undirected |
| `DirectedAssociation` | — | open arrow | solid | source → target (flowchart arrows use this) |
| `Aggregation` | hollow diamond | — | solid | **source = whole**, target = part |
| `Composition` | filled diamond | — | solid | **source = whole**, target = part |
| `Generalization` | — | hollow triangle | solid | **source = derived**, target = base |
| `Realization` | — | hollow triangle | dashed | **source = implementor**, target = interface |
| `Dependency` | — | open arrow | dashed | source depends on target |
| `Include` | — | open arrow | dashed | source = base use case, target = included; auto-labels `«include»` — do NOT emit `centerLabel` |
| `Extend` | — | open arrow | dashed | source = extending, target = extended; auto-labels `«extend»` — do NOT emit `centerLabel` |
| `Relationship` | crow's foot per `sourceCardinality` | crow's foot per `targetCardinality` | solid | ER: **source = FK-holding child table**, target = referenced parent |
| `MindMapBranch` | tapered ribbon | | | source = parent topic (avoid unless building mind maps) |

Dashes, arrowheads, diamonds, triangles and «include»/«extend» stereotypes all come from
`kind`. Never simulate them with styles or labels.

## Style objects (only for deliberate overrides)

**Default = omit `style` entirely.** A node without `style` follows the app theme: theme
surface fill, accent-blue `#FF3574F0` stroke at 1.5, Inter 12 theme-colored text, centered.
A connector without `style` gets the neutral gray `#FF9A9AA0` stroke. This is what
hand-created shapes look like, and it adapts to light/dark theme.

Node `style` (all keys optional — omitted keys get defaults):

```json
"style": {
  "fill": "#FFFFF7D6",
  "stroke": { "color": "#FF3574F0", "thickness": 1.5, "dash": "Solid" },
  "font": { "family": "Inter", "size": 12, "bold": false, "italic": false, "color": "#FF1E1F22" },
  "textAlignment": "Center",
  "verticalTextAlignment": "Center"
}
```

- `fill` omitted/null = **follow the theme**. Never write the literal theme defaults
  (`#FFEBEDF0` fill / `#FF1E1F22` text) — that pins the color and breaks dark mode.
- `stroke.dash`: `Solid` | `Dash` | `Dot` | `DashDot`.
- `textAlignment`: `Left` | `Center` | `Right`; `verticalTextAlignment`: `Top` | `Center` | `Bottom`.
- `paletteId`: omit — it refers to the app's quick-style swatches.
- **Connector-style trap**: inside a connector `style`, a `stroke` object whose `color` is
  omitted defaults to accent **blue**, not connector gray. If you override a connector's
  thickness/dash, also write `"color": "#FF9A9AA0"` explicitly to keep the native look.

## Invariant checklist (why each matters)

1. `$type` first key of each node — polymorphic deserialization requires it.
2. `schemaVersion: 2` — >2 rejected, <2 migrated (colors nulled).
3. Unique lowercase GUID `id`s — **duplicate node ids crash the app on open**. Connector endpoints must reference existing nodes (dangling ones are silently invisible); no self-links.
4. `zIndex` contiguous 0..n−1 matching array order, boundaries first — render order is `zIndex` then array position.
5. Sizes must satisfy the layout.md formulas — nothing clamps or fixes them at load.
6. Omit instead of null; omit empty arrays — loads identically to the app's more verbose output.
7. Enums as exact PascalCase strings; `route` only `Straight`/`Orthogonal`/`Rounded`.
8. `isNullable: false` explicitly on PK/NOT NULL columns — the default is true.
9. Kind drives all decorations and direction conventions (derived→base, whole→part, child-table→parent).
10. Stereotypes/flags are structured data (`kind: "Interface"`, `isPrimaryKey`), never text in names.
11. Theme-following = omit style/fill/color keys; never write literal theme default colors.
12. Everything on the 10-unit grid (positions, sizes, bend points; anchors excepted — they're fractions; actor size 48×84 excepted — it's fixed).
