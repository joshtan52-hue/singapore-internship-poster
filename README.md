# Singapore Internship Poster Generator

A Claude Agent Skill that generates branded marketing posters, flyers, and social
captions for a "Study + Paid Internship in Singapore" program — entirely with
[Pillow](https://python-pillow.org/) (no browser, no external image-generation API,
no network calls at render time), so it runs anywhere Python 3 is available.

It ships as a **Claude Skill**: point Claude (via [Claude Code](https://claude.com/product/claude-code),
the [Claude Agent SDK](https://docs.claude.com/en/api/agent-sdk/overview), or
[Cowork](https://claude.ai)) at this repo and it will read `SKILL.md` to learn how to
use it — ask a few questions about copy/photos, pick a template and palette, write a
JSON config, and render a finished poster PNG plus matching captions.

## What it can make

- **24 distinct poster layouts** — corporate flyers, framed/editorial looks,
  ticket/postcard/boarding-pass metaphors, a cinematic movie-poster style, a
  chat-mockup UI screenshot, infographic-style benefit grids, and more. Full list
  and when to use each one: [`references/style_guide.md`](references/style_guide.md).
- **5 color palettes** (red/navy, navy/gold, green/gold, teal/coral, burgundy/cream),
  swappable independently of the template.
- **Photo-aware layout tools** — crop-retention checking (`scripts/check_crop.py`) and
  palette/photo color-harmony swatches (`scripts/palette_swatch.py`) so photos get
  matched to slots and palettes deliberately instead of by guesswork.
- **A caption generator** (`scripts/generate_captions.py`) that produces short
  (WhatsApp-status style) and long (structured feed-post style) captions from a
  reusable phrase-bank config, so every poster ships with matching copy.

## Repo layout

```
SKILL.md                   Instructions Claude reads to operate this skill
scripts/
  generate_poster.py       CLI entry point: config JSON -> poster PNG
  templates.py             One render_<template>() function per layout
  poster_engine.py         Shared drawing helpers (photo crop/fit, gradients, text wrap, icons)
  generate_captions.py     CLI entry point: caption config -> short/long captions
  check_crop.py            Reports how much of a photo survives a given crop box
  check_palette.py         Rough numeric palette/photo hue-clash check
  palette_swatch.py        Visual palette-vs-photo comparison strip generator
examples/                  One example config per template, plus a caption config
references/
  style_guide.md           What each template looks like and when to use it
  config_schema.md          Full field-by-field config reference
  caption_style.md          Caption voice guide and phrase-bank system
  headline_bank.md          Longer headline/hook line options
assets/
  fonts/                    Bundled display + icon fonts (Lato, Poppins, Font Awesome)
  photo_library/            Drop-in spot for your own campaign photos (empty by default)
```

## Quick start (standalone, without Claude)

```bash
pip install pillow

# Render a poster from one of the example configs
python3 scripts/generate_poster.py \
  --config examples/clean_split.json \
  --out poster.png \
  --photos-dir assets/photo_library

# Generate matching captions
python3 scripts/generate_captions.py \
  --config examples/caption_config.json \
  --short 1 --long 1 \
  --out captions.md
```

Copy any file in `examples/` as a starting point for your own poster — the fields are
documented in `references/config_schema.md`. Drop your own photos into
`assets/photo_library/` (or point `--photos-dir` at wherever they live) and reference
them by filename in a config's `photos.hero` / `photos.secondary` / `photos.gallery`
fields.

## Using it as a Claude Skill

Point Claude at this repo (as a Claude Code plugin skill, an Agent SDK skill
directory, or a Cowork skill) and it will pick up `SKILL.md` automatically. From
there you can just ask in natural language — "make me a poster for the internship
program" — and Claude will interview you for the missing details, pick a template and
palette, render it, and hand back the PNG plus captions.

## Customizing

- **New template:** add a `render_<name>()` function to `scripts/templates.py`
  following the pattern of the existing ones, register it in `TEMPLATE_FUNCS` inside
  `scripts/generate_poster.py`, then add an example config and a paragraph to
  `references/style_guide.md`.
- **New palette:** add an entry to the `PALETTES` dict in `scripts/templates.py`.
- **Caption voice:** edit the phrase banks at the top of `scripts/generate_captions.py`
  (`SHORT_HOOKS`, `LONG_HEADLINES`, etc.) and update `references/caption_style.md` to
  match.

## License

No license file is included yet — add one (MIT is a common default for this kind of
tooling) before treating this as open source.
