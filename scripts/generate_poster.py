#!/usr/bin/env python3
"""
Generate a Singapore Study + Paid Internship marketing poster.

Usage:
    python3 generate_poster.py --config path/to/config.json --out path/to/poster.png [--photos-dir path/to/photos]

The config JSON controls copy, palette, template choice, and which photos to
use. See ../references/config_schema.md for the full field reference and
../examples/*.json for ready-to-edit starting points.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import templates as t

TEMPLATE_FUNCS = {
    "bold_impact": t.render_bold_impact,
    "clean_split": t.render_clean_split,
    "elegant_pills": t.render_elegant_pills,
    "torn_paper": t.render_torn_paper,
    "photo_overlay": t.render_photo_overlay,
    "steps_timeline": t.render_steps_timeline,
    "gradient_highlights": t.render_gradient_highlights,
    "night_glow": t.render_night_glow,
    "stamp_collage": t.render_stamp_collage,
    "magazine_split": t.render_magazine_split,
    "luggage_tag": t.render_luggage_tag,
    "certificate_award": t.render_certificate_award,
    "neon_edge": t.render_neon_edge,
    "flat_pop": t.render_flat_pop,
    "dark_chevron": t.render_dark_chevron,
    "studio_split": t.render_studio_split,
    "boarding_pass": t.render_boarding_pass,
    "movie_poster": t.render_movie_poster,
    "postcard": t.render_postcard,
    "chat_mockup": t.render_chat_mockup,
}


def resolve_photos(cfg, photos_dir):
    """If photos-dir is given, treat photo fields as filenames inside it.
    A resolved path that would land outside photos_dir (via '..' segments
    or an absolute path) is rejected rather than opened, so a config file
    can't be used to read files from outside the intended photo directory."""
    if not photos_dir:
        return cfg
    photos = cfg.get("photos", {})
    photos_dir_real = os.path.realpath(photos_dir)

    def resolve(p):
        if not p:
            return p
        candidate = os.path.realpath(os.path.join(photos_dir, p))
        if os.path.commonpath([candidate, photos_dir_real]) != photos_dir_real:
            return None
        return candidate if os.path.exists(candidate) else p

    if "hero" in photos:
        photos["hero"] = resolve(photos["hero"])
    if "side" in photos:
        photos["side"] = resolve(photos["side"])
    if "secondary" in photos:
        photos["secondary"] = [resolve(p) for p in photos["secondary"]]
    if "gallery" in photos:
        # gallery items are {"file": "<filename>", "label": "<caption>"} objects
        for item in photos["gallery"]:
            if isinstance(item, dict) and "file" in item:
                item["file"] = resolve(item["file"])
    cfg["photos"] = photos
    return cfg


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True, help="Path to a poster config JSON file")
    ap.add_argument("--out", required=True, help="Output PNG path")
    ap.add_argument("--photos-dir", default=None,
                     help="Optional directory to resolve relative photo filenames against")
    args = ap.parse_args()

    try:
        with open(args.config) as f:
            cfg = json.load(f)
    except FileNotFoundError:
        raise SystemExit(f"Config file not found: {args.config}")
    except json.JSONDecodeError as e:
        raise SystemExit(f"Config file '{args.config}' is not valid JSON: {e}")

    template = cfg.get("template", "bold_impact")
    if template not in TEMPLATE_FUNCS:
        raise SystemExit(f"Unknown template '{template}'. Choose from: {list(TEMPLATE_FUNCS)}")

    cfg = resolve_photos(cfg, args.photos_dir)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    out_path = TEMPLATE_FUNCS[template](cfg, args.out)
    print(f"Saved poster -> {out_path}")


if __name__ == "__main__":
    main()
