---
name: draw-diagram
description: Generate .draw diagram files for the Draw diagramming app (Avalonia desktop app). Use when the user asks for a .draw file, a diagram they can edit in Draw, or an editable UML class/interface diagram, ER/database diagram, use-case diagram, flowchart, or explanatory schema with shapes and connectors — e.g. "diagram these classes as a .draw file" or "make me an ER diagram of this schema for Draw". Creates new files only.
---

# draw-diagram — generate editable `.draw` diagrams

Produce a `.draw` file (JSON, one diagram per file) that the Draw desktop app opens and the
user can then edit by hand. This skill is self-contained: everything needed is in this
directory — never look for the Draw app's source code.

## Scope

- **Generate new files only.** Never modify an existing `.draw` file; to "update" a diagram,
  generate a fresh file (overwriting the old one only if the user asks).
- Output path: whatever the user names; default `docs/diagrams/<kebab-name>.draw` in the
  current project (create the directory if needed).
- Supported: UML class/interface/enum diagrams, ER/database diagrams, use-case diagrams,
  flowcharts, and free-form explanatory schemas (shapes + arrows). Not supported: mind maps,
  image nodes, updating layouts.

## Workflow

1. **Determine the diagram type and content source.** Content may come from code you read
   (classes/interfaces for UML), SQL/migrations/ORM models (ER), or the user's description
   (flowcharts, schemas). For UML from code, confirm scope if ambiguous (which
   namespace/folder, include private members or not — default: public + protected only,
   skip trivial members when a type has many).
2. **Read both references in this skill — always, before writing any JSON:**
   - [references/format.md](references/format.md) — the exact JSON format (node types,
     connectors, enums, serialization rules).
   - [references/layout.md](references/layout.md) — sizing formulas and placement rules.
3. **Read the matching example** in [examples/](examples/) (`class.draw`, `er.draw`,
   `use-case.draw`, `flowchart.draw`) and use it as a structural template.
4. **Build the diagram in this order:** list nodes with content → compute every node's
   size (layout.md §2) → compute positions (layout.md §3–7) → add connectors → assign
   ids and zIndex → write the file.
5. **Self-check against the invariants below**, then tell the user the file path and that
   it opens in Draw (File → Open).

## Hard invariants (violations break the file in the app or render it wrong)

1. `"$type"` is the **first key** of every node object.
2. `"schemaVersion": 2` — exactly.
3. Every `id` a unique lowercase GUID (duplicate node ids crash the app on open);
   connector `sourceNodeId`/`targetNodeId` reference existing nodes; source ≠ target.
4. `zIndex` explicit and contiguous (0..n−1) in array order; `systemBoundary` nodes first.
5. Node sizes satisfy layout.md §2 — the app never fixes undersized boxes.
6. Enums are exact PascalCase strings (`"Orthogonal"`, `"ZeroOrMany"`, `"Interface"`);
   `route` is only `Straight`/`Orthogonal`/`Rounded`.
7. Omit keys instead of writing `null`; omit empty arrays; omit `style` (theme-following)
   unless the user asked for colors.
8. Entity columns: `"isNullable": false` written explicitly on every PK/NOT NULL column
   (the default is true).
9. Structured data, not text markup: `kind: "Interface"` not `«interface»` in the name;
   `isPrimaryKey: true` not `"PK"` in the column name; visibility enums not `+/-` prefixes.
10. Connector decorations (arrows, diamonds, triangles, dashes, «include»/«extend») come
    from `kind` — never emit labels or styles to imitate them. Directions: Generalization/
    Realization source = derived; Aggregation/Composition source = whole; ER Relationship
    source = FK-holding child table.
11. All coordinates/sizes/bend points on the 10-unit grid (exceptions: anchors are 0–1
    fractions; actors are fixed 48×84).
12. Colors, when explicitly requested, are `#AARRGGBB` strings.

## Bundled files

- `references/format.md` — full `.draw` v2 JSON spec (derived from Draw schema v2, commit
  `e57c65b`; if the app rejects a well-formed file, the spec may have drifted — regenerate
  it from the Draw repo's `src/Draw.Model`).
- `references/layout.md` — sizing formulas + per-diagram-type placement heuristics.
- `examples/class.draw` — interface, abstract class, two subclasses, enum; realization,
  generalizations, directed association, composition.
- `examples/er.draw` — users/orders/order_items; FK relationships with crow's-foot
  cardinalities and PK/FK/NOT NULL flags.
- `examples/use-case.draw` — system boundary (first in array), use cases, two actors,
  an «include»; boundary-derived bounds.
- `examples/flowchart.draw` — terminator/process/diamond spine, labeled yes/no branch,
  loop-back with `bendPoints`.
