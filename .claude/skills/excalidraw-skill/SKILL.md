---
name: excalidraw
description: Use when user requests diagrams, flowcharts, architecture charts, or visualizations. Also use proactively when explaining systems with 3+ components, complex data flows, or relationships that benefit from visual representation. Generates .excalidraw files and exports to PNG/SVG via Kroki API or locally using excalidraw-brute-export-cli.
homepage: https://github.com/Agents365-ai/excalidraw-skill
metadata: {"openclaw":{"requires":{"bins":["curl"]},"emoji":"🎨"}}
---

# Excalidraw Diagrams

## Overview

Generate `.excalidraw` JSON files and export to PNG/SVG.

**Two export options:**
- **Kroki API** (`curl`) — zero install, SVG output only
- **excalidraw-brute-export-cli** — local Firefox-based, PNG + SVG

**Supported formats:** PNG (local CLI only), SVG (both options). PDF is NOT supported.

## When to Use

**Explicit triggers:** user says "画图", "diagram", "visualize", "flowchart", "draw", "架构图", "流程图"

**Proactive triggers:**
- Explaining a system with 3+ interacting components
- Describing a multi-step process or decision tree
- Comparing architectures or approaches side by side

**Skip when:** a simple list or table suffices, or user is in a quick Q&A flow

## Prerequisites

### Option A: Kroki API (recommended — zero install, SVG only)

```bash
# Just needs curl (pre-installed on macOS/Linux/Windows Git Bash)
curl --version
```

No additional setup. SVG rendered via `https://kroki.io`.

### Option B: Local CLI (required for PNG)

The CLI uses **Firefox** (not Chromium). Check and install:

```bash
npm install -g excalidraw-brute-export-cli
npx playwright install firefox
```

**macOS patch (one-time, required):**
```bash
CLI_MAIN=$(npm root -g)/excalidraw-brute-export-cli/src/main.js
sed -i '' 's/keyboard.press("Control+O")/keyboard.press("Meta+O")/' "$CLI_MAIN"
sed -i '' 's/keyboard.press("Control+Shift+E")/keyboard.press("Meta+Shift+E")/' "$CLI_MAIN"
```

**Windows/Linux:** No patch needed.

## Workflow

1. **Check deps** — use Kroki (curl) for SVG; use local CLI for PNG
2. **Plan** — identify diagram type, pick a visual pattern, choose color palette
3. **Generate** — write `.excalidraw` JSON file (section-by-section for large diagrams)
4. **Export** — run Kroki or CLI command
5. **Report** — tell user the output file path

## Design Principles

### Default style

- `roughness: 0` — clean, modern look for all technical diagrams (use `1` only when user requests hand-drawn/casual style)
- `fontFamily: 2` (Helvetica) — professional look; use `1` (Virgil) only for casual/sketch style, `3` (Cascadia) for code snippets
- `fillStyle: "solid"` — default fill

### Font size hierarchy

| Level | Size | Use for |
|-------|------|---------|
| Title | 28px | Diagram title |
| Header | 24px | Section/group headers |
| Label | 20px | Primary element labels |
| Description | 16px | Secondary text, descriptions |
| Note | 14px | Annotations, fine print |

### Color palette

Follow the **60-30-10 rule**: 60% whitespace/neutral, 30% primary accent, 10% highlight.

**Semantic fill colors** (use with `strokeColor` one shade darker):

| Category | Fill | Stroke | Use for |
|----------|------|--------|---------|
| Primary / Input | `#dbeafe` | `#1e40af` | Entry points, APIs, user-facing |
| Success / Data | `#dcfce7` | `#166534` | Data stores, success states |
| Warning / Decision | `#fef9c3` | `#854d0e` | Decision points, conditions |
| Error / Critical | `#fee2e2` | `#991b1b` | Errors, alerts, critical paths |
| External / Storage | `#f3e8ff` | `#6b21a8` | External services, databases, AI/ML |
| Process / Default | `#e0f2fe` | `#0369a1` | Standard process steps |
| Trigger / Start | `#fed7aa` | `#c2410c` | Start nodes, triggers, events |
| Neutral / Container | `#f1f5f9` | `#475569` | Groups, swimlanes, backgrounds |

**Text colors:**

| Level | Color |
|-------|-------|
| Title | `#1e293b` |
| Label | `#334155` |
| Description | `#64748b` |

**Rule: Do not invent new colors.** Pick from this palette.

### Arrow semantics

| Style | Meaning |
|-------|---------|
| Solid (`strokeStyle: null`) | Primary flow, main path |
| Dashed (`"dashed"`) | Response, async, callback |
| Dotted (`"dotted"`) | Optional, reference, weak dependency |

## Excalidraw JSON Structure

### File skeleton

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "claude-code",
  "elements": [],
  "appState": { "viewBackgroundColor": "#ffffff" }
}
```

### Element types

| type      | use for                          |
|-----------|----------------------------------|
| rectangle | boxes, components, modules       |
| ellipse   | start/end nodes, databases       |
| diamond   | decision points                  |
| arrow     | directed connections             |
| line      | undirected connections           |
| text      | standalone labels                |

### Element sizing

Calculate element width from label text to prevent truncation:

```
Latin text:  width = max(160, charCount * 9)
CJK text:   width = max(160, charCount * 18)
Mixed text:  estimate each character individually, sum up
```

Height: use `60` for single-line labels, add `24` per additional line.

### Required properties (all elements)

```json
{
  "id": "auth_service",
  "type": "rectangle",
  "x": 100, "y": 100,
  "width": 160, "height": 60,
  "angle": 0,
  "strokeColor": "#1e40af",
  "backgroundColor": "#dbeafe",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "roughness": 0,
  "opacity": 100,
  "seed": 100001,
  "boundElements": [
    { "id": "arrow_to_db", "type": "arrow" },
    { "id": "label_auth", "type": "text" }
  ]
}
```

Use **descriptive string IDs** (e.g., `"api_gateway"`, `"arrow_gw_to_auth"`) instead of random strings.

Give each element a unique `seed` (integer). Namespace by section: 100xxx, 200xxx, 300xxx.

### JSON field rules

- `boundElements`: use `null` when empty, never `[]`
- `updated`: always use `1`, never timestamps
- Do NOT include: `frameId`, `index`, `versionNonce`, `rawText`
- `points` in arrows: always start at `[0, 0]`
- `seed`: must be a positive integer, unique per element

### Text inside shapes (contained text)

When text belongs inside a shape, bind them bidirectionally:

```json
{
  "id": "label_auth",
  "type": "text",
  "text": "Auth Service",
  "fontSize": 20,
  "fontFamily": 2,
  "textAlign": "center",
  "verticalAlign": "middle",
  "strokeColor": "#1e293b",
  "containerId": "auth_service"
}
```

**CRITICAL: Text `strokeColor` is the text color.** Always set it explicitly to a dark color from the text color palette. Never omit it — omitting `strokeColor` on text can cause invisible text that blends with the shape background.

The parent shape must list the text in its `boundElements`:
```json
"boundElements": [{ "id": "label_auth", "type": "text" }]
```

### Arrow binding (bidirectional)

Arrows must bind to shapes, and shapes must reference bound arrows:

```json
{
  "id": "arrow_gw_to_auth",
  "type": "arrow",
  "points": [[0, 0], [200, 0]],
  "startBinding": { "elementId": "api_gateway", "gap": 5, "focus": 0 },
  "endBinding": { "elementId": "auth_service", "gap": 5, "focus": 0 }
}
```

Both `api_gateway` and `auth_service` must include in their `boundElements`:
```json
"boundElements": [{ "id": "arrow_gw_to_auth", "type": "arrow" }]
```

### Arrow routing

**L-shaped (elbow) arrows** — orthogonal routing with 3+ points:

```json
"points": [[0, 0], [100, 0], [100, 150]]
```

**Elbowed arrows** — automatic right-angle routing:

```json
{
  "type": "arrow",
  "points": [[0, 0], [0, -50], [200, -50], [200, 0]],
  "elbowed": true
}
```

**Curved arrows** — smooth routing with waypoints:

```json
{
  "type": "arrow",
  "points": [[0, 0], [50, -40], [200, 0]],
  "roundness": { "type": 2 }
}
```

### Grouping

Related elements share `groupIds`. Nested groups list IDs innermost-first:

```json
"groupIds": ["inner_group", "outer_group"]
```

## Diagram Patterns

Choose the right visual pattern for each diagram type.

### Spacing Reference

| Scenario | Spacing |
|----------|---------|
| Labeled arrow gap (between shapes) | 150–200px |
| Unlabeled arrow gap | 100–120px |
| Column spacing (labeled arrows) | 400px (220px box + 180px gap) |
| Column spacing (unlabeled arrows) | 340px (220px box + 120px gap) |
| Row spacing | 280–350px (150px box + 130–200px gap) |
| Zone/container padding | 50–60px around children |
| Zone/container opacity | 25–40 |
| Minimum gap between any elements | 40px |

### Flowchart (LR or TB)

- Ellipse for start/end, diamond for decisions, rectangle for process
- 200px horizontal spacing, 150px vertical spacing
- Decision branches: "Yes" goes forward, "No" goes down
- 3–10 steps (max 15)

### Architecture / System Diagram

- Column spacing per table above; use labeled arrow spacing when connections have labels
- Group related services in dashed `Neutral` containers (opacity: 30, padding: 50px)
- Gateway/entry at left or top, databases at right or bottom
- 3–8 entities (max 12)

### Sequence Diagram

- 200px between participants (rectangles at top)
- Vertical lifelines as dashed lines
- Horizontal arrows for messages, 60px vertical spacing
- Solid arrow = request, dashed arrow = response

### Mind Map

- Central node: largest (200x100), `Trigger` color
- Level 1: 150x70, `Primary` color, radial around center
- Level 2: 120x50, `Process` color
- Level 3: 90x40, `Neutral` color
- Use lines (not arrows) for connections
- 4–6 branches (max 8), 2–4 sub-topics per branch

### Swimlane

- Large transparent rectangles (`Neutral` fill, `"dashed"` stroke, opacity: 30) as lane boundaries
- Lane label as free-standing text at top-left of lane (not bound to rectangle), 28px font
- Elements flow left-to-right within lanes
- Arrows cross lanes for handoffs

## Section-by-Section Construction

For diagrams with **10+ elements**, do NOT generate the entire JSON at once. Build in sections:

1. **Plan all sections first** — list element IDs, positions, and cross-section bindings
2. **Write section 1** — create the file with initial elements
3. **Append section 2** — read the file, add new elements to the `elements` array
4. **Repeat** — continue until all sections are done
5. **Final pass** — verify all `boundElements` and `startBinding`/`endBinding` references are consistent

Namespace element seeds by section (100xxx, 200xxx, 300xxx) to avoid collisions.

## Export

### Option A: Kroki API (SVG only — zero install)

```bash
# SVG via Kroki API
curl -s -X POST https://kroki.io/excalidraw/svg \
  -H "Content-Type: application/json" \
  --data-binary "@diagram.excalidraw" \
  -o diagram.svg

# Via local Kroki Docker (offline)
curl -s -X POST http://localhost:8000/excalidraw/svg \
  -H "Content-Type: application/json" \
  --data-binary "@diagram.excalidraw" \
  -o diagram.svg
```

### Option B: Local CLI (PNG + SVG)

```bash
# PNG at 2x scale (recommended)
excalidraw-brute-export-cli -i diagram.excalidraw -o diagram.png -f png -s 2

# PNG at 1x scale
excalidraw-brute-export-cli -i diagram.excalidraw -o diagram.png -f png -s 1

# SVG
excalidraw-brute-export-cli -i diagram.excalidraw -o diagram.svg -f svg -s 1
```

**Required flags:** `-f` (format: `png` or `svg`) and `-s` (scale: `1`, `2`, or `3`).

## Anti-Patterns

**Never put `text` on large background/zone rectangles.** Excalidraw centers text in the middle of the shape, overlapping contained elements. Instead, use a free-standing `text` element positioned at the top of the zone.

**Avoid cross-zone arrows.** Long diagonal arrows create visual spaghetti. Route arrows within zones or along zone edges. If a cross-zone connection is unavoidable, route it along the perimeter.

**Use arrow labels sparingly.** Labels placed at the arrow midpoint overlap on short arrows. Keep labels to ≤12 characters and ensure ≥120px clear space between connected shapes. Omit labels when the connection meaning is obvious from context.

**Don't use filled backgrounds on containers that hold other elements.** Use `opacity: 30` (or 25-40 range) for zone/container rectangles so contained elements remain visible.

**Always set explicit `strokeColor` on text elements.** Text `strokeColor` is the rendered text color. If omitted, text may inherit the parent shape's background color and become invisible. Use `#1e293b` (title), `#334155` (label), or `#64748b` (description) from the text color palette.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Kroki returns error | Ensure file is valid JSON with `"type": "excalidraw"` and `"elements"` array |
| Kroki only outputs SVG | Use local CLI (`excalidraw-brute-export-cli`) for PNG |
| Export fails with "Missing required flag" | Always pass `-f png` and `-s 2` |
| Export fails with "Executable doesn't exist" | Run `npx playwright install firefox` |
| macOS: timeout waiting for file chooser | Apply the macOS Meta patch above |
| Arrow `points` not relative to origin | `points` always start at `[0,0]` |
| Missing `id` on elements | Use descriptive string IDs per element |
| Overlapping elements | Use spacing reference table; minimum 40px gap |
| Arrows not interactive in excalidraw.com | Add `boundElements` to shapes referencing all bound arrows/text |
| Text not centered in shape | Set `containerId` on text AND add text to shape's `boundElements` |
| All text same size | Use font size hierarchy: 28 → 24 → 20 → 16 → 14 |
| Diagram looks monotone | Apply semantic colors from the palette, follow 60-30-10 rule |
| Text invisible / same color as background | Always set `strokeColor` on text elements to a dark color (`#1e293b`, `#334155`, or `#64748b`) |
| Text overlaps inside zone/container | Don't bind text to zone rectangles; use free-standing text at top |
| Text truncated in shapes | Use width formula: `max(160, charCount * 9)`, double for CJK |
| `boundElements: []` causes issues | Use `null` for empty boundElements, never `[]` |
