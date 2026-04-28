# Video Podcast Maker — Workflow Steps Index

> **When to load:** Whenever you need to locate a specific step. This file is only an index — load the phase file that contains the step you need.

The 15-step workflow (plus an optional Step 4.5 pronunciation pre-flight) is split across three phase files. **Load just the phase you need** — avoid pulling all three unless doing a full top-to-bottom pass.

---

## Phase 1 — Scripting

Pre-workflow (design reference) → Startup (load preferences) → **Steps 1-4** (topic, research, sections, narration script).

→ **[workflow-script.md](workflow-script.md)**

| Step | What it covers |
|------|----------------|
| Pre-workflow | Optional design pattern extraction from reference video/image |
| Startup | Load `user_prefs.json` + version migration |
| Step 1 | Define topic direction (audience, style, tone, duration) |
| Step 2 | Research topic (web search/fetch) |
| Step 3 | Design 5-7 sections + content density tier |
| Step 4 | Write narration script (`podcast.txt`) + duration dry-run |

---

## Phase 2 — Production

**Steps 5-11** (media → publish draft → thumbnail → TTS → Remotion composition → 4K render → BGM).

→ **[workflow-production.md](workflow-production.md)**

| Step | What it covers |
|------|----------------|
| Step 5 | Collect media assets (optional, text-only by default) |
| Step 6 | Generate publish info (part 1 — title/tags/description) |
| Step 7 | Generate video thumbnail (16:9 + 4:3, Remotion or AI) |
| Step 8 | Generate TTS audio (`generate_tts.py` → wav/srt/timing.json) |
| Step 9 | Create Remotion composition + Studio preview (mandatory stop) |
| Step 10 | Render 4K video (`output.mp4`) |
| Step 11 | Mix with background music (`video_with_bgm.mp4`) |

---

## Phase 3 — Publish

**Steps 12-15** (subtitles → publish info part 2 → verify + cleanup → optional shorts).

→ **[workflow-publish.md](workflow-publish.md)**

| Step | What it covers |
|------|----------------|
| Step 12 | Add subtitles (usually skipped — Remotion renders natively) |
| Step 13 | Complete publish info (part 2 — chapters, platform-specific format) |
| Step 14 | Verify output + cleanup (`final_video.mp4`) |
| Step 15 | Generate vertical shorts (optional, `generate_shorts.py`) |

---

## Related references

- **`design-guide.md`** — Visual design rules, component selection, typography, icons. **Required reading before Step 9.**
- **`troubleshooting.md`** — Errors, BGM options, preference commands, design-learning issues.
