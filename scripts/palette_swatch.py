#!/usr/bin/env python3
"""
Build a quick visual reference strip: a palette's color chips next to
thumbnails of the candidate photo(s), so the palette/photo pairing can be
checked by eye before finalizing a poster config.

Usage:
    python3 scripts/palette_swatch.py --photo p1.jpg [--photo p2.jpg ...] --palette navy_gold --out swatch.png
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import poster_engine as pe
from templates import PALETTES


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--photo", action="append", required=True)
    ap.add_argument("--palette", required=True, choices=sorted(PALETTES.keys()))
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    pe.palette_photo_swatch(args.photo, PALETTES[args.palette], args.out)
    print(f"Saved swatch -> {args.out}")


if __name__ == "__main__":
    main()
