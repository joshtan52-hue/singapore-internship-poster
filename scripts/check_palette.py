#!/usr/bin/env python3
"""
Check whether a chosen palette's primary color clashes with the dominant
tone of the photo(s) going into a poster -- an objective pre-flight check
rather than eyeballing it, since eyeballing led to a saturated red badge
being placed next to an orange sunset photo on an earlier poster.

Run this before finalizing any config for a photo-heavy template, whenever
the palette hasn't already been used with that exact photo before.

Usage:
    python3 scripts/check_palette.py --photo photo1.jpg [--photo photo2.jpg ...] --palette red_navy
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import poster_engine as pe
from templates import PALETTES


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--photo", action="append", required=True, help="Path to a photo (repeatable)")
    ap.add_argument("--palette", required=True, choices=sorted(PALETTES.keys()))
    args = ap.parse_args()

    pal = PALETTES[args.palette]
    any_clash = False
    for photo in args.photo:
        if not os.path.exists(photo):
            print(f"{photo}: not found, skipping")
            continue
        clash, photo_hsv, pal_hsv = pe.check_palette_clash(photo, pal["primary"])
        status = "CLASH" if clash else "ok"
        print(f"{photo}: photo hue={photo_hsv[0]:.0f} sat={photo_hsv[1]:.2f}  "
              f"vs {args.palette} hue={pal_hsv[0]:.0f} sat={pal_hsv[1]:.2f}  -> {status}")
        any_clash = any_clash or clash

    print()
    if any_clash:
        print(f"Warning: {args.palette}'s primary color may clash with at least one photo above.")
        print("Try navy_gold or teal_coral, or a different photo, then re-run this check.")
        sys.exit(1)
    else:
        print(f"{args.palette} looks safe against all given photos.")


if __name__ == "__main__":
    main()
