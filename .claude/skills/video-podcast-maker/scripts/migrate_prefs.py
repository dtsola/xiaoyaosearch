#!/usr/bin/env python3
"""Migrate user_prefs.json to the current schema version.

Replaces the prose migration table that used to live in workflow-script.md.

Strategy:
1. If `user_prefs.json` is missing, copy `user_prefs.template.json` into place.
2. Apply structural transforms that deep-merge cannot do (e.g. v1.1 string
   `tts.voice` → v1.2 per-backend `tts.voices` object).
3. Deep-merge the template into the existing prefs so any new fields added in
   later versions get their default values, while user customizations win.
4. Stamp `version` to the current PREFS_VERSION and save.

Idempotent: re-running on already-current prefs is a no-op (version match).

Usage:
    python3 scripts/migrate_prefs.py            # migrate ${SKILL_DIR}/user_prefs.json in place
    python3 scripts/migrate_prefs.py --dry-run  # report what would change without writing
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from learn_design import (  # noqa: E402
    PREFS_VERSION,
    _load_template,
    _deep_merge,
    save_prefs,
)


# Default voice map for v1.1 -> v1.2 conversion. Old prefs only had a single
# `tts.voice` string (used by azure + edge); doubao/cosyvoice didn't exist yet.
V1_2_DEFAULT_VOICES = {
    "azure": "zh-CN-XiaoxiaoNeural",
    "edge": "zh-CN-XiaoxiaoNeural",
    "doubao": "BV001_streaming",
    "cosyvoice": "longxiaochun",
}


def _structural_migrate(prefs):
    """Apply structural rewrites that deep-merge cannot do.

    Returns (prefs, changes) where `changes` is a list of human-readable
    descriptions for the report.
    """
    changes = []
    tts = prefs.setdefault("global", {}).setdefault("tts", {})

    # v1.1 -> v1.2: tts.voice (string) -> tts.voices (per-backend object)
    if "voice" in tts and "voices" not in tts:
        old_voice = tts.pop("voice")
        voices = dict(V1_2_DEFAULT_VOICES)
        # Preserve the old voice for the two backends that historically used it.
        if isinstance(old_voice, str) and old_voice:
            voices["azure"] = old_voice
            voices["edge"] = old_voice
        tts["voices"] = voices
        changes.append(f"converted tts.voice='{old_voice}' -> tts.voices object")

    # v1.2 -> v1.3: progressBar bool -> object {enabled, height, fontSize, ...}
    visual = prefs.setdefault("global", {}).setdefault("visual", {})
    pb = visual.get("progressBar")
    if isinstance(pb, bool):
        visual["progressBar"] = {
            "enabled": pb,
            "height": 6,
            "fontSize": 18,
            "activeColor": "auto",
            "position": "bottom",
        }
        changes.append(f"expanded progressBar={pb} -> object")

    return prefs, changes


def migrate(prefs_path, dry_run=False):
    """Migrate the prefs file at `prefs_path`. Returns a status dict."""
    template = _load_template()

    if not os.path.exists(prefs_path):
        if dry_run:
            return {"action": "would_create", "from": None, "to": PREFS_VERSION, "changes": []}
        save_prefs(template, prefs_path)
        return {"action": "created", "from": None, "to": PREFS_VERSION, "changes": []}

    import json
    with open(prefs_path, encoding="utf-8") as f:
        prefs = json.load(f)

    from_version = prefs.get("version", "1.0")
    if from_version == PREFS_VERSION:
        return {"action": "noop", "from": from_version, "to": PREFS_VERSION, "changes": []}

    prefs, changes = _structural_migrate(prefs)
    merged = _deep_merge(template, prefs)
    merged["version"] = PREFS_VERSION

    if dry_run:
        return {"action": "would_migrate", "from": from_version, "to": PREFS_VERSION, "changes": changes}

    save_prefs(merged, prefs_path)
    return {"action": "migrated", "from": from_version, "to": PREFS_VERSION, "changes": changes}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--prefs", default=None, help="Path to user_prefs.json (default: ${SKILL_DIR}/user_prefs.json)")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without writing")
    args = parser.parse_args()

    prefs_path = args.prefs or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "user_prefs.json",
    )

    result = migrate(prefs_path, dry_run=args.dry_run)
    action = result["action"]
    frm, to = result["from"], result["to"]
    changes = result["changes"]

    if action == "noop":
        print(f"user_prefs.json is already at v{to} — no migration needed")
    elif action == "created":
        print(f"Created user_prefs.json at v{to} from template")
    elif action == "would_create":
        print(f"[dry-run] Would create user_prefs.json at v{to} from template")
    elif action == "migrated":
        print(f"Migrated user_prefs.json from v{frm} to v{to}")
        for c in changes:
            print(f"  - {c}")
    elif action == "would_migrate":
        print(f"[dry-run] Would migrate user_prefs.json from v{frm} to v{to}")
        for c in changes:
            print(f"  - {c}")


if __name__ == "__main__":
    main()
