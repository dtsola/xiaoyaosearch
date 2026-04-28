#!/usr/bin/env python3
"""Read a nested value from user_prefs.json and print it.

Used by SKILL.md / workflow shell snippets to consume user preferences.

Usage:
    python3 get_pref.py global tts rate
    python3 get_pref.py global bgm volume --default 0.05
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tts.backends import user_prefs_get  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('keys', nargs='+', help='Nested key path, e.g. global tts rate')
    parser.add_argument('--default', default='', help='Value to print if key is missing')
    args = parser.parse_args()

    val = user_prefs_get(*args.keys)
    print(val if val is not None else args.default)


if __name__ == '__main__':
    main()
