#!/usr/bin/env python3
"""
Vertical Shorts Generator for Video Podcast Maker
Reads timing.json + podcast_audio.wav from a video directory and generates
per-section short video assets (audio slice, timing, composition metadata).
"""
import os
import sys
import json
import argparse
import subprocess
import re


# ============ Constants ============

FPS = 30
INTRO_FRAMES = 90          # 3 seconds intro card
CTA_FRAMES = 90            # 3 seconds CTA card
TRANSITION_FRAMES = 10     # fade between parts
INTRO_SECONDS = INTRO_FRAMES / FPS
CTA_SECONDS = CTA_FRAMES / FPS

DEFAULT_SKIP = "hero,outro"
DEFAULT_MIN_DURATION = 20   # seconds


# ============ Helper Functions ============

def to_pascal_case(name):
    """Convert kebab/snake section name to PascalCase.

    Examples:
        "content-1"  -> "Content1"
        "pipeline"   -> "Pipeline"
        "my_section" -> "MySection"
        "arch-v2"    -> "ArchV2"
    """
    # Split on hyphens and underscores
    parts = re.split(r'[-_]', name)
    return ''.join(p.capitalize() for p in parts)


def load_timing(input_dir):
    """Read timing.json from the video directory."""
    path = os.path.join(input_dir, 'timing.json')
    if not os.path.exists(path):
        print(f"Error: timing.json not found in {input_dir}", file=sys.stderr)
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_script(input_dir):
    """Read podcast.txt and extract the first content line per section as its title.

    Returns: dict mapping section_name -> first_line_text
    """
    path = os.path.join(input_dir, 'podcast.txt')
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    section_pattern = r'\[SECTION:(\w[\w-]*)\]'
    matches = list(re.finditer(section_pattern, text))
    titles = {}
    for i, match in enumerate(matches):
        name = match.group(1)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        # First non-empty line is the title
        for line in body.split('\n'):
            line = line.strip()
            if line:
                # Truncate at first sentence-ending punctuation, cap at 30 chars
                title = re.split(r'[。！？]', line)[0][:30]
                titles[name] = title
                break
    return titles


def filter_sections(timing, min_duration, skip_names):
    """Return sections that qualify for short generation."""
    skip_set = {s.strip() for s in skip_names.split(',') if s.strip()}
    qualifying = []
    for sec in timing.get('sections', []):
        name = sec['name']
        if name in skip_set:
            continue
        if sec.get('is_silent', False):
            continue
        if sec.get('duration', 0) < min_duration:
            continue
        qualifying.append(sec)
    return qualifying


def extract_audio(input_dir, section, output_dir):
    """Extract section audio from podcast_audio.wav using ffmpeg."""
    src = os.path.join(input_dir, 'podcast_audio.wav')
    if not os.path.exists(src):
        print(f"  Error: podcast_audio.wav not found in {input_dir}", file=sys.stderr)
        return False
    dst = os.path.join(output_dir, 'short_audio.wav')
    cmd = [
        'ffmpeg', '-y',
        '-ss', str(section['start_time']),
        '-t', str(section['duration']),
        '-i', src,
        '-c', 'copy',
        dst,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  Error extracting audio: {result.stderr.strip()}", file=sys.stderr)
        return False
    return True


def generate_timing(section, output_dir):
    """Write short_timing.json for a single-section short.

    Structure:
      - intro: INTRO_FRAMES (no audio)
      - content: section's original duration_frames (audio plays here)
      - cta: CTA_FRAMES (no audio)

    Total frames = intro + content + cta
    """
    content_frames = section['duration_frames']
    total_frames = INTRO_FRAMES + content_frames + CTA_FRAMES

    short_timing = {
        "total_duration": section['duration'] + INTRO_SECONDS + CTA_SECONDS,
        "fps": FPS,
        "total_frames": total_frames,
        "source_section": section['name'],
        "sections": [
            {
                "name": "intro",
                "label": "Intro",
                "start_frame": 0,
                "duration_frames": INTRO_FRAMES,
                "is_silent": True,
            },
            {
                "name": section['name'],
                "label": section.get('label', section['name']),
                "start_frame": INTRO_FRAMES,
                "duration_frames": content_frames,
                "is_silent": False,
            },
            {
                "name": "cta",
                "label": "CTA",
                "start_frame": INTRO_FRAMES + content_frames,
                "duration_frames": CTA_FRAMES,
                "is_silent": True,
            },
        ],
    }

    path = os.path.join(output_dir, 'short_timing.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(short_timing, f, indent=2, ensure_ascii=False)

    return short_timing


def generate_composition_stub(section, video_title, output_dir, short_timing, section_title):
    """Write short_info.json and register_snippet.tsx for a short."""
    comp_id = to_pascal_case(section['name']) + 'Short'
    content_frames = section['duration_frames']
    total_frames = short_timing['total_frames']

    # short_info.json — composition metadata
    info = {
        "comp_id": comp_id,
        "section_name": section['name'],
        "section_title": section_title,
        "video_title": video_title,
        "content_frames": content_frames,
        "intro_frames": INTRO_FRAMES,
        "cta_frames": CTA_FRAMES,
        "transition_frames": TRANSITION_FRAMES,
        "total_frames": total_frames,
        "width": 2160,
        "height": 3840,
        "fps": FPS,
    }
    info_path = os.path.join(output_dir, 'short_info.json')
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)

    # register_snippet.tsx — code to add to Root.tsx
    snippet = f'''// Register {comp_id} in Root.tsx <Composition> list:
// Import the component:
//   import {{ {comp_id}Video }} from "./{comp_id}Video";
//
// Add inside <Composition> list:
<Composition
  id="{comp_id}"
  component={{{comp_id}Video}}
  durationInFrames={{{total_frames}}}
  fps={{{FPS}}}
  width={{2160}}
  height={{3840}}
  defaultProps={{defaultVideoProps}}
/>
'''
    snippet_path = os.path.join(output_dir, 'register_snippet.tsx')
    with open(snippet_path, 'w', encoding='utf-8') as f:
        f.write(snippet)

    return comp_id


def render_short(output_dir, comp_id, index_path):
    """Render a short video using npx remotion render."""
    output_file = os.path.join(output_dir, f'{comp_id}.mp4')
    cmd = [
        'npx', 'remotion', 'render',
        index_path, comp_id,
        output_file,
        '--video-bitrate', '16M',
        '--public-dir', output_dir,
    ]
    print(f"    Rendering: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    Render failed: {result.stderr.strip()}", file=sys.stderr)
        return False
    print(f"    \u2713 Rendered: {output_file}")
    return True


# ============ Main ============

def main():
    parser = argparse.ArgumentParser(
        description='Generate vertical short video assets from podcast sections',
        epilog='Example: python3 scripts/generate_shorts.py --input-dir videos/how-llms-work/ --title "LLM\u5de5\u4f5c\u539f\u7406"'
    )
    parser.add_argument('--input-dir', required=True,
                        help='Video directory containing timing.json and podcast_audio.wav')
    parser.add_argument('--title', default='',
                        help='Video title shown as subtitle on intro card (default: "")')
    parser.add_argument('--min-duration', type=float, default=DEFAULT_MIN_DURATION,
                        help=f'Minimum section duration in seconds (default: {DEFAULT_MIN_DURATION})')
    parser.add_argument('--skip', default=DEFAULT_SKIP,
                        help=f'Comma-separated section names to skip (default: "{DEFAULT_SKIP}")')
    parser.add_argument('--render', action='store_true',
                        help='Also render shorts after generating (runs npx remotion render)')
    parser.add_argument('--index', default='src/remotion/index.ts',
                        help='Remotion index path for --render (default: src/remotion/index.ts)')

    args = parser.parse_args()
    input_dir = args.input_dir.rstrip('/')

    # Load data
    timing = load_timing(input_dir)
    script_titles = load_script(input_dir)

    # Filter qualifying sections
    sections = filter_sections(timing, args.min_duration, args.skip)

    if not sections:
        skip_list = [s.strip() for s in args.skip.split(',') if s.strip()]
        print(f"No qualifying sections found.")
        print(f"  Skipped names: {skip_list}")
        print(f"  Min duration: {args.min_duration}s")
        all_names = [s['name'] for s in timing.get('sections', [])]
        print(f"  All sections: {all_names}")
        sys.exit(0)

    shorts_dir = os.path.join(input_dir, 'shorts')
    os.makedirs(shorts_dir, exist_ok=True)

    print(f"Generating shorts for {len(sections)} sections:\n")

    generated = []

    for sec in sections:
        name = sec['name']
        duration = sec.get('duration', 0)
        frames = sec.get('duration_frames', 0)
        section_title = script_titles.get(name, sec.get('label', name))

        print(f"  [{name}] {duration:.1f}s ({frames} frames)")

        # Create output directory
        output_dir = os.path.join(shorts_dir, name)
        os.makedirs(output_dir, exist_ok=True)

        # 1. Extract audio
        if extract_audio(input_dir, sec, output_dir):
            print(f"    \u2713 Audio extracted")
        else:
            print(f"    \u2717 Audio extraction failed, skipping")
            continue

        # 2. Generate timing
        short_timing = generate_timing(sec, output_dir)
        total = short_timing['total_frames']
        print(f"    \u2713 Timing generated ({total} frames)")

        # 3. Generate composition stub
        comp_id = generate_composition_stub(sec, args.title, output_dir, short_timing, section_title)
        print(f"    \u2713 Composition: {comp_id}")

        generated.append({
            'comp_id': comp_id,
            'section_name': name,
            'total_frames': total,
            'output_dir': output_dir,
        })

        # 4. Optionally render
        if args.render:
            render_short(output_dir, comp_id, args.index)

        print()

    # Summary
    print("=" * 50)
    print(f"Generated {len(generated)} shorts in {shorts_dir}/")
    for g in generated:
        print(f"  {g['comp_id']}: {g['section_name']} ({g['total_frames']} frames)")

    print(f"\nNext steps:")
    print(f"  1. Create Remotion composition files for each short")
    print(f"  2. Render with --public-dir pointing to the short's directory")
    print(f"  3. npx remotion render src/remotion/index.ts <CompId> <output.mp4> --video-bitrate 16M --public-dir <short-dir>/")


if __name__ == '__main__':
    main()
