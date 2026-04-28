# Video Podcast Maker — Workflow Phase 3: Publish

> **When to load:** Load after the 4K video is rendered with BGM, or when the user asks about subtitles, publish info, cleanup, verification, or generating vertical shorts.
>
> **Covers:** Steps 12-15 (subtitles → publish info → verify + cleanup → optional vertical shorts).
>
> **Previous phase:** See `workflow-production.md` for Steps 5-11.

---

## Step 12: Add Subtitles

> **Preferred approach: Remotion-native subtitles (no FFmpeg re-encode needed)**
>
> The `Video.tsx` template already includes `<Subtitles src={staticFile("podcast_audio.srt")} />`.
> This renders SRT subtitles inside Remotion using React/CSS — positioned at the bottom of the 4K frame,
> with text outline, font, and style matching the project theme. No FFmpeg subtitle pass is needed.
>
> **When to skip this step:** If the video was rendered with the standard `Video.tsx` template
> (which includes `<Subtitles>`), Step 12 is a no-op — just copy `video_with_bgm.mp4` as `final_video.mp4`.
>
> **When FFmpeg subtitles may still be needed:** Legacy videos rendered without the `Subtitles` component,
> or special subtitle styling not achievable in CSS (e.g., karaoke effects).

**Auto mode:** Skip subtitles — copy `video_with_bgm.mp4` as `final_video.mp4`.
**Interactive mode:** Ask user: "Add burned-in subtitles? (Usually not needed — Remotion renders subtitles natively)"

### Subtitle Preferences

Read `subtitle` preferences. If `subtitle.enabled == false`, skip subtitle burning (copy video_with_bgm.mp4 as final_video.mp4).

If FFmpeg subtitle burn is explicitly requested (legacy/special cases only):

Resolve `fontName: "auto"` by `language`:
- zh-CN → `PingFang SC`
- en-US → `Arial`

```bash
# Alignment=2: bottom-center. MarginV uses ASS PlayResY (default 288), NOT video pixels.
# MarginV=6 ≈ 6/288 = ~2% from bottom edge, good for all resolutions.
# WARNING: Only burn from video_with_bgm.mp4, NEVER from final_video.mp4 (avoids double-burn).
ffmpeg -y -i videos/{name}/video_with_bgm.mp4 \
  -vf "subtitles=videos/{name}/podcast_audio.srt:force_style='FontName=PingFang SC,FontSize=20,PrimaryColour=&H00333333,OutlineColour=&H00FFFFFF,Bold=0,Outline=2,Shadow=0,Alignment=2,MarginV=6'" \
  -c:v libx264 -crf 18 -preset slow -s 3840x2160 \
  -c:a copy videos/{name}/final_video.mp4
```

If skipping (default for Remotion-native subtitle videos):
```bash
cp videos/{name}/video_with_bgm.mp4 videos/{name}/final_video.mp4
```

---

## Step 13: Complete Publish Info (Part 2)

Generate Bilibili chapters from `timing.json`:

```
00:00 Opening
00:23 Features
00:55 Demo
01:20 Summary
```

Format: `MM:SS Chapter Title`, each gap ≥5s.

### Publish Info Format by Platform

**Agent behavior:** Generate publish info matching `platform` preference.

**bilibili format:**
- 标题公式、标签、简介
- 章节时间戳 (if `content.chapters == true`)

**youtube format:**
- SEO-optimized title (<70 chars)
- Keyword-rich description with timestamps
- Tags and hashtags (#tag1 #tag2)
- Chapters (if `content.chapters == true`, first line must be `0:00`)

**xiaohongshu format:**
- 标题（≤20字）— short, punchy, emoji-friendly
- 正文（200-500字）— 种草/knowledge-sharing style with emoji
- 话题标签 5-10 个，格式 `#话题#`（双井号）
- 无章节时间戳（小红书不支持）

**douyin format:**
- 文案（100-200字）— casual, emoji-friendly, conversational tone
- 话题标签 3-8 个，格式 `#话题`（单井号）
- 无章节时间戳
- Note: Douyin is shorts-only — no horizontal long-form video

**weixin-channels format:**
- 文案（100-300字）— knowledge-sharing style, suitable for forwarding
- 话题标签 3-8 个，格式 `#话题`（单井号）
- 无章节时间戳
- Note: WeChat Channels is shorts-only — no horizontal long-form video

---

## Step 14: Verify Output & Cleanup

### 14.1 Verification

```bash
VIDEO_DIR="videos/{name}"
echo "=== File Check ==="
for f in podcast.txt podcast_audio.wav podcast_audio.srt timing.json output.mp4 final_video.mp4; do
  [ -f "$VIDEO_DIR/$f" ] && echo "✓ $f" || echo "✗ $f missing"
done

echo "=== Technical Specs ==="
RES=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$VIDEO_DIR/final_video.mp4")
[ "$RES" = "3840,2160" ] && echo "✓ Resolution: 3840x2160 (4K)" || echo "✗ Resolution: $RES (not 4K)"
DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$VIDEO_DIR/final_video.mp4" | cut -d. -f1)
echo "✓ Duration: ${DUR}s"
SIZE=$(ls -lh "$VIDEO_DIR/final_video.mp4" | awk '{print $5}')
echo "✓ File size: $SIZE"
```

### 14.2 Cleanup

**Both modes:** Only clean TTS temp files (part_*.wav, concat_list.txt) automatically. **NEVER delete output.mp4 or video_with_bgm.mp4** until the user has reviewed final_video.mp4 and explicitly confirmed it's acceptable. These files are needed to re-do BGM/subtitle steps without a full re-render (~8 min).

```bash
VIDEO_DIR="videos/{name}"
# Safe to auto-clean: TTS intermediate files only
rm -f "$VIDEO_DIR"/part_*.wav "$VIDEO_DIR"/concat_list.txt
echo "✓ TTS temp files cleaned"
echo ""
echo "Kept (delete manually after confirming final_video.mp4):"
echo "  output.mp4 — clean render without BGM/subtitles"
echo "  video_with_bgm.mp4 — render with BGM, no subtitles"
```

### 14.3 Final Report

```
=== Video Complete ===
✓ File: final_video.mp4
✓ Resolution: 3840x2160 (4K)
✓ Duration: XXs
✓ Size: XXX MB
✓ Thumbnails: thumbnail_remotion_16x9.png, thumbnail_remotion_4x3.png
✓ Publish info: publish_info.md
✓ Temp files cleaned
```

---

## Step 15: Generate Vertical Shorts (Optional)

**When:** After long-form video is complete (Step 14). Optional step.

**Agent behavior:** Offer to generate vertical shorts. If user agrees, run automatically.

### Generate shorts from sections

```bash
python3 ${SKILL_DIR}/scripts/generate_shorts.py --input-dir videos/{name}/ --title "视频标题"
```

This produces `videos/{name}/shorts/{section_name}/` for each qualifying section (>20s, not hero/outro) with:
- `short_audio.wav` — extracted audio slice
- `short_timing.json` — timing for intro (3s) + content + CTA (3s)
- `short_info.json` — composition metadata
- `register_snippet.tsx` — Root.tsx registration code

### Create short compositions

For each generated short:
1. Copy `templates/ShortVideo.tsx` as `src/remotion/{SectionName}ShortVideo.tsx`
2. Replace `SectionContent` placeholder with the actual section component from the long-form video
3. Update `SHORT_CONFIG` with values from `short_info.json`
4. Register composition in `Root.tsx` using `register_snippet.tsx`
5. Ensure `short_audio.wav` is in the short's directory (used via `--public-dir`)

### Render shorts

```bash
npx remotion render src/remotion/index.ts {CompId} videos/{name}/shorts/{section}/short.mp4 --video-bitrate 16M --public-dir videos/{name}/
```

Each short is a standalone 9:16 4K video (2160×3840) with:
- 3-second intro title card
- Section content (vertical layout, all components auto-adapt)
- 3-second CTA card ("关注看完整版")
