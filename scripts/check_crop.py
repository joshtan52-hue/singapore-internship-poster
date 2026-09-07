#!/usr/bin/env python3
"""
Check what fraction of a photo survives a cover-crop into a given box size,
before committing to that photo for a poster's photo slot. A tall portrait
photo forced into a short, wide strip (or vice versa) can lose most of
itself to the crop -- this turns that risk into a number instead of
something only visible after rendering.

Usage:
    python3 scripts/check_crop.py --photo photo.jpg --target-w 1080 --target-h 550

The target box size depends on the template and which photo field you're
filling -- read the relevant render_<template> function in templates.py for
the exact numbers if unsure (search for the photo_w / photo_h / strip_h /
etc. variables near the `photos.hero` or `photos.gallery` handling). A few
common ones:
    photo_overlay hero strip:  1080 x (H*0.34) ~= 1080 x 550 (H=1620 normally)
    magazine_split secondary (small top-right): right_w x 190
    stamp_collage / certificate_award gallery items: roughly square-ish, see stamp_w/gw in code
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import poster_engine as pe


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--photo", required=True)
    ap.add_argument("--target-w", type=int, required=True)
    ap.add_argument("--target-h", type=int, required=True)
    args = ap.parse_args()

    src_size = pe.photo_size(args.photo)
    retained = pe.crop_retention(src_size, (args.target_w, args.target_h))
    print(f"{args.photo}: source {src_size[0]}x{src_size[1]}, target {args.target_w}x{args.target_h}")
    print(f"Retained fraction: {retained:.2f}")
    if retained < 0.6:
        print("Warning: a lot of this photo will be cropped away. Consider a photo whose "
              "aspect ratio is closer to the target box, or a different template/slot.")
        sys.exit(1)
    else:
        print("Looks like a reasonable fit.")


if __name__ == "__main__":
    main()
