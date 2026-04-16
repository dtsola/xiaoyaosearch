# Excalidraw Diagrams — Hand-Drawn Style, Zero Manual Layout

A Claude Code skill that generates and exports Excalidraw diagrams to PNG/SVG via natural language.

[中文文档](README.md)

## Why use this skill

- **Natural language to diagram** — describe what you want in plain English or Chinese, get a professional diagram back. No dragging boxes, no manual layout.
- **Zero learning curve** — you don't need to learn Excalidraw's JSON format, Mermaid syntax, or any DSL. Just talk.
- **Zero install option** — the Kroki API path needs nothing but `curl`. No npm packages, no Docker, no browser automation.
- **Proactive diagrams** — the skill triggers automatically when Claude detects a complex system explanation would benefit from a visual. You don't even have to ask.
- **Professional design system** — semantic color palette (60-30-10 rule), font size hierarchy, arrow semantics (solid/dashed/dotted), and diagram-type-specific layout patterns built in.
- **5 diagram patterns** — Flowchart, Architecture, Sequence, Mind Map, and Swimlane, each with dedicated layout rules and spacing conventions.
- **Anti-pattern guard rails** — documents common pitfalls (zone text overlap, spaghetti arrows, label collisions) so Claude avoids them before they happen.
- **Smart sizing** — auto-calculates element width from label text (`max(160, charCount * 9)`) with CJK-aware estimation, preventing text truncation.
- **Precise spacing system** — pixel-exact spacing rules for labeled vs unlabeled arrows, column/row gaps, and zone padding — no more overlapping elements.
- **3 arrow routing modes** — straight, L-shaped elbow, and curved waypoint routing for clean diagram connections.
- **Editable output** — the `.excalidraw` file can be opened in [excalidraw.com](https://excalidraw.com) for manual tweaks, with full interactive arrow binding preserved.
- **Works offline** — the local CLI option (Firefox-based) runs entirely on your machine with no network dependency.

## How it compares

| Capability | **This Skill** | Native Claude Code | Other Skills |
|------------|:-:|:-:|:-:|
| Generate Excalidraw JSON | ✓ Guided by design system | ✓ Can write but no layout rules | ✓ Varies |
| Export PNG/SVG | ✓ Automatic | ✗ Manual — user must ask | Partial |
| Zero-install export (Kroki API) | ✓ Just needs curl | ✗ No fallback | No |
| Proactive triggering | ✓ Auto-triggers for 3+ components | ✗ Only when explicitly asked | No |
| Semantic color palette | ✓ 60-30-10 rule | ✗ No design rules | Partial |
| Precise spacing rules | ✓ Pixel-exact specs | ✗ Guesswork layout | Partial |
| Anti-pattern guard rails | ✓ Built-in pitfall docs | ✗ No protection | No |
| Smart sizing (CJK-aware) | ✓ Auto-adapts | ✗ Prone to truncation | No |
| Arrow routing (straight/elbow/curved) | ✓ 3 modes | ✗ Straight only | Partial |
| Bidirectional arrow binding | ✓ Full interactivity | ✗ Static connections | Partial |
| Bilingual (EN + Chinese) | ✓ Keyword triggers | ✗ No keyword triggers | No |
| End-to-end workflow | ✓ Generate → Export → Report | ✗ Generate only | Partial |
| Self-contained (single file) | ✓ One SKILL.md | N/A | No (4-6 files) |

**Key advantages over native Claude Code:**
- **Complete pipeline** — Claude Code can write Excalidraw JSON, but won't auto-export images or follow design conventions. This skill automates the full generate-to-deliverable workflow
- **Professional quality** — built-in semantic colors, precise spacing, arrow routing, and font hierarchy produce production-ready diagrams without manual tweaking
- **Error prevention** — anti-pattern guard rails prevent text overlap, arrow spaghetti, and other common layout issues
- **Proactive diagramming** — auto-triggers when discussing architecture, not just when you ask for a diagram

## Why a skill, not an MCP server?

Excalidraw's JSON format is just an array of elements with x/y/width/height — Claude can write it natively. A skill teaches Claude *how* to draw; an MCP server gives Claude *a tool* to draw. When the LLM can do the job itself, teaching is better than tooling.

| Aspect | Skill | MCP Server |
|--------|-------|------------|
| How it works | Prompt injected into Claude's context | Separate running service process |
| Generation | Claude writes JSON directly (native LLM ability) | Requires code to handle JSON generation |
| Flexibility | Claude understands semantics, free-form layout | Fixed API parameters, limited flexibility |
| Install | Copy one file | Start a service, configure MCP |
| Dependencies | Zero (the skill itself has none) | Node.js / Python runtime |
| Export | Calls existing tools (curl / CLI) | Must build export logic or still call curl |

MCP is valuable when Claude needs capabilities it *can't* do alone — database access, browser automation, authenticated APIs. Diagram generation is **design + JSON writing**, which is exactly what LLMs excel at.

## What it does

- Generates `.excalidraw` JSON files from natural language descriptions
- Exports SVG via **Kroki** API — zero install, just `curl`
- Exports PNG/SVG locally using `excalidraw-brute-export-cli` (Firefox-based)
- Triggers automatically when diagrams would help explain complex systems
- Applies semantic colors, font hierarchy, and arrow styles automatically
- Auto-calculates element width from label text with CJK-aware sizing
- Builds large diagrams section-by-section to avoid token limits
- Produces fully interactive files with bidirectional arrow binding

## Features

### Semantic color palette

8 color categories mapped to meaning — Primary (blue), Success (green), Warning (yellow), Error (red), External (purple), Process (sky), Trigger (orange), Neutral (slate). Follows the 60-30-10 rule: 60% whitespace, 30% primary accent, 10% highlight.

### Diagram patterns

| Pattern | Layout | Best for |
|---------|--------|----------|
| Flowchart | LR or TB, 200px spacing | Processes, decision trees |
| Architecture | Column-based with precise gap rules | System design, microservices |
| Sequence | 200px between participants | API flows, protocols |
| Mind Map | Radial, decreasing size per level | Brainstorming, concept maps |
| Swimlane | Horizontal lanes with crossover arrows | Cross-team workflows |

### Precise spacing system

| Scenario | Spacing |
|----------|---------|
| Labeled arrow gap | 150–200px |
| Unlabeled arrow gap | 100–120px |
| Column spacing (labeled) | 400px |
| Column spacing (unlabeled) | 340px |
| Zone padding | 50–60px |

### Arrow routing

3 modes: straight (default), L-shaped elbow (`points` with right angles), and curved waypoint (`roundness: { type: 2 }`).

### Arrow semantics

| Style | Meaning |
|-------|---------|
| Solid | Primary flow |
| Dashed | Response, async |
| Dotted | Optional, weak dependency |

### Smart element sizing

Auto-calculates width from label text: `max(160, charCount * 9)` for Latin, `max(160, charCount * 18)` for CJK. Prevents text truncation in generated diagrams.

### Font hierarchy

Title (28px) → Header (24px) → Label (20px) → Description (16px) → Note (14px)

### Anti-pattern guard rails

Built-in documentation of common pitfalls — zone text centering traps, cross-zone arrow spaghetti, label collision on short arrows, and container opacity rules — so Claude avoids mistakes before they happen.

## Dependencies

| Tool | Purpose |
|------|---------|
| `curl` | Send `.excalidraw` to Kroki API for SVG rendering |
| `excalidraw-brute-export-cli` | Local CLI to export `.excalidraw` → PNG/SVG |
| `Playwright + Firefox` | Headless browser used by the local CLI |

`curl` is pre-installed on macOS, Linux, and Windows (Git Bash / WSL).

## Install the Skill

**Claude Code (global):**
```bash
git clone https://github.com/Agents365-ai/excalidraw-skill.git ~/.claude/skills/excalidraw
```

**Claude Code (project-specific):**
```bash
git clone https://github.com/Agents365-ai/excalidraw-skill.git .claude/skills/excalidraw
```

**OpenClaw:**
```bash
git clone https://github.com/Agents365-ai/excalidraw-skill.git skills/excalidraw
```

**SkillsMP:** Search `excalidraw` on [skillsmp.com](https://skillsmp.com) for one-click install.

## Install Dependencies

### Option A: Kroki API (recommended — zero install, SVG only)

```bash
# curl is already available — just verify:
curl --version
```

No additional setup. SVG rendered via `https://kroki.io`.

### Option B: Local CLI (required for PNG)

```bash
npm install -g excalidraw-brute-export-cli
npx playwright install firefox
```

### Platform notes

| Platform | Extra step |
|----------|------------|
| **macOS** | Apply one-time patch (see below) |
| **Windows** | No extra steps needed |
| **Linux** | No extra steps needed |

### macOS patch (one-time, required for local CLI)

The CLI uses `Control+O` / `Control+Shift+E` but macOS requires `Meta` (Cmd):

```bash
CLI_MAIN=$(npm root -g)/excalidraw-brute-export-cli/src/main.js
sed -i '' 's/keyboard.press("Control+O")/keyboard.press("Meta+O")/' "$CLI_MAIN"
sed -i '' 's/keyboard.press("Control+Shift+E")/keyboard.press("Meta+Shift+E")/' "$CLI_MAIN"
```

## Usage

Just describe what you want:

```
Create a microservices e-commerce architecture with API Gateway, auth/user/order/product/payment services,
Kafka message queue, notification service, and separate databases for each service
```

Claude will generate the `.excalidraw` file and export it to PNG automatically.

## Example

**Prompt:**
> Create a microservices e-commerce architecture with Mobile/Web/Admin clients, API Gateway,
> Auth/User/Order/Product/Payment services, Kafka message queue, Notification service,
> and User DB / Order DB / Product DB / Redis Cache / Stripe API

**Output:**

![Microservices Architecture](assets/microservices-example.png)

## Files

- `SKILL.md` — skill instructions loaded by Claude Code
- `README.md` — Chinese documentation (default)
- `README_EN.md` — this file (English)
- `assets/` — example diagrams

## License

MIT

## Support

If this skill helps you, consider supporting the author:

<table>
  <tr>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Agents365-ai/images_payment/main/qrcode/wechat-pay.png" width="180" alt="WeChat Pay">
      <br>
      <b>WeChat Pay</b>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Agents365-ai/images_payment/main/qrcode/alipay.png" width="180" alt="Alipay">
      <br>
      <b>Alipay</b>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Agents365-ai/images_payment/main/qrcode/buymeacoffee.png" width="180" alt="Buy Me a Coffee">
      <br>
      <b>Buy Me a Coffee</b>
    </td>
  </tr>
</table>

## Author

**Agents365-ai**

- Bilibili: https://space.bilibili.com/441831884
- GitHub: https://github.com/Agents365-ai
