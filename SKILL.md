---
name: singapore-internship-poster
description: Generate branded marketing posters/flyers/ads AND social media captions for Josh's "Study + Paid Internship in Singapore" program. Use any time Josh asks for a poster, flyer, ad, promo graphic, or social creative for the Singapore study-and-internship program — even if he just says "make me an ad" or describes a promo without saying "poster." Also use when he asks for post captions, WhatsApp/Instagram/Facebook captions, or wording for a poster — generates short punchy captions and long structured captions in his own voice. Produces a finished PNG in one of twenty layouts (bold corporate, clean split, elegant gold-framed, torn-paper skyline, photo overlay, step timeline, gradient highlights, night glow, stamp collage, magazine split, luggage tag, certificate award, neon edge, flat pop, dark chevron, studio split, boarding pass ticket, cinematic movie poster, postcard, chat mockup) in five palettes, using his own photos, plus a caption generator for short/long captions from a reusable config.
---

# Singapore Internship Poster Generator

Produces marketing poster PNGs for the "Study + Paid Internship in Singapore" program,
matching the look of Josh's existing ad set (torn-paper skylines, bold corporate
banners, elegant gold-framed layouts with photo clusters). Rendering is done with
Pillow only — no browser, no network, no external image-generation dependency — so it
runs anywhere this skill is installed.

## Workflow

1. **Get the copy.** Ask Josh (or infer from context/prior posters in this conversation)
   for whatever of these he wants on the poster: headline, tagline, discount, list of
   requirements, list of benefits, contact info, call-to-action. Contact info is
   always just the WhatsApp/phone number — never an email address or an @handle,
   even if a reference design shows one. Don't block on every field — sensible defaults exist for most (see
   `references/config_schema.md`), and it's often faster to draft something and let
   him correct it than to interview him on every field.

   **Josh has also supplied a bank of longer headline/hook lines** in
   `references/headline_bank.md` — pull from these alongside the shorter
   punchy headlines already in use for variety across posters. They read as
   taglines/hooks rather than short headline lines (see that file for how to
   fit them into a given template), and per the rule above, always pair one
   with visible "Study + Paid Internship" wording elsewhere on the poster
   since these lines don't mention the program itself.

   **The word "Singapore" must appear somewhere in every poster's visible text** —
   headline, tagline, subtitle, brand pill, badge, or a description field, whichever
   fits the template naturally. A photo of a Singapore landmark (Merlion, Marina Bay
   Sands) is not enough on its own — the destination has to be named in text too,
   since that's the core of Josh's "Study + Paid Internship in Singapore" brand.
   Templates that already carry it structurally (e.g. `night_glow`'s
   `brand_pill_text`) satisfy this by default; for others, work it into the headline
   (e.g. add a line like "in Singapore") or tagline rather than leaving it implicit.

   **When Josh supplies his own custom header/headline text, still make sure
   "Study + Paid Internship" (or clear equivalent wording — "Paid Internship",
   "Study & Intern", etc.) is visible somewhere on the poster** — a tagline,
   eyebrow, subtitle, or badge line under his header. His custom headers won't
   always mention the offer itself, but every poster still needs to communicate
   that a study + paid internship program is what's on offer, not just the
   destination or a mood line. Don't silently drop this just because the
   supplied header doesn't include it.

   **Never mention "Airport Pickup" as a benefit/inclusion** — Josh does not
   offer this and it should never appear in requirements, benefits,
   `benefits_extra`, or captions for any poster.

   **Never mention "Visa & Accommodation Support" (or accommodation support
   generally) as a benefit/inclusion** — Josh does not offer accommodation
   support and it should never appear in requirements, benefits,
   `benefits_extra`, or captions for any poster. ("Visa Support" alone,
   without accommodation, is still fine.)

   **Never state or imply a guaranteed outcome, especially as a statistic** —
   things like "100% Visa Approval Rate" or "Guaranteed Acceptance" promise a result
   that isn't actually within the business's control (visa/embassy decisions aren't
   Josh's to guarantee) and shouldn't appear in any headline, stat card, tagline, or
   caption. General quality/value claims are fine ("Quality Education," "Hands-On
   Training," "Trusted by 500+ Students"), as is describing what the *program*
   itself delivers as a paid feature — "Guaranteed Paid Internship" describes an
   internship placement Josh's program actually provides, which is different from
   promising an external approval outcome. When in doubt, ask: is this something
   Josh's program directly delivers, or an outcome a third party (immigration,
   an employer) ultimately decides? Only the former can be phrased as guaranteed.

2. **Get photos.** Ask which photos to use, and where they live (a folder path). Josh
   maintains his own photo library — do not invent or fabricate photos. If no photos
   are available yet, generate the poster anyway with placeholder gradients so he can
   see the layout, then swap in real photos once supplied. Pass the photo folder via
   `--photos-dir` and reference photos by filename in the config's `photos.hero` /
   `photos.secondary` fields.

   **Match photo orientation to the slot's shape — check it with numbers, not
   just by eye.** Every photo box crops to fill (`cover_resize`), centered —
   that centering can't rescue a bad orientation match. A wide/landscape
   photo squeezed into a narrow, tall box gets its sides cropped off (people
   at the edges of the frame can get cut out entirely); a tall/portrait photo
   squeezed into a short, wide strip loses its top and bottom instead — one
   poster used a 736x1308 portrait photo in `photo_overlay`'s ~1080x550 hero
   strip and kept only ~29% of the image, slicing through a building roofline
   and a bridge. Before picking a photo for a given slot, run:
   ```bash
   python3 scripts/check_crop.py --photo <file> --target-w <w> --target-h <h>
   ```
   (get the target box's `w`/`h` from the relevant `render_<template>`
   function in `templates.py` — the script's own `--help` lists a few common
   ones). It prints the fraction of the photo that survives the crop; below
   ~0.6 means significant, often awkward cropping — pick a differently-shaped
   photo for that slot instead of proceeding. If the only photo available is
   a poor match for every slot, say so and ask Josh rather than forcing an
   awkward crop.

3. **Pick a template + palette.** Read `references/style_guide.md` to choose between
   `bold_impact`, `clean_split`, `elegant_pills`, `torn_paper`, `photo_overlay`,
   `steps_timeline`, `gradient_highlights`, `night_glow`, `stamp_collage`, `magazine_split`,
   `luggage_tag`, `certificate_award`, `neon_edge`, `flat_pop`, `dark_chevron`, `studio_split`,
   `boarding_pass`, `movie_poster`, `postcard`, and `chat_mockup`, and a
   matching `palette`. `gradient_highlights` and `night_glow` have no photo slot — use those
   when Josh wants a poster that isn't built around a photo. If Josh references a specific
   one of his old posters ("like the red one" / "like the gold bordered one"), match that.
   Otherwise pick whichever fits the requirements/benefits count best, or just ask him.

   **Check palette-to-photo color harmony before finalizing, not after.** Each
   template section in `style_guide.md` lists a "Recommended palette" — start
   there rather than picking an untested combination.

   For a photo-heavy template, or whenever a palette hasn't already been used
   with that exact photo before, generate a quick visual check before
   committing to the config:
   ```bash
   python3 scripts/palette_swatch.py --photo <photo1> [--photo <photo2> ...] --palette <name> --out swatch.png
   ```
   This saves a strip with the palette's color chips next to thumbnails of
   the actual photo(s) — view it (the swatch PNG, not the numbers) and judge
   by eye whether the palette's primary/accent color fights the photo's
   dominant tones or frames them well. This is the reliable check — trust
   what the swatch image actually looks like over any rule of thumb about
   "warm vs cool," including the guidance in the rest of this paragraph.
   `scripts/check_palette.py --photo ... --palette ...` prints a numeric
   hue-distance flag too, but treat it as a rough, occasionally-wrong signal
   (it works off a photo's single dominant hue bucket, which can pick the
   wrong region on a photo with two very different-colored areas, like a
   blue sky above an orange sunset glow) — never rely on its CLASH/ok verdict
   alone without looking at the swatch.

   As a starting-point bias before you've generated a swatch: a saturated
   `red_navy` next to a warm orange/pink sunset photo has read as a clash
   before (fixed by switching to `teal_coral`), so lean toward `navy_gold` or
   `teal_coral` for sunset/golden-hour photos and save `red_navy` /
   `burgundy_cream` for cooler-toned or photo-free posters — but confirm with
   the swatch rather than applying this as a fixed rule, since it won't hold
   for every photo. If a render looks off once assembled, swap the palette
   and re-render before presenting rather than noting it and moving on.

   **Every template now fits Instagram's feed-post limits with no cropping.** All 20
   templates render at 1080 wide by at most 1350 tall (Instagram's 4:5 feed-post max) —
   `studio_split` renders square at 1080x1080, and most others dynamically crop to their
   actual (often shorter) content height instead of a fixed size. There's no longer a
   subset to avoid for Instagram specifically; pick whichever template fits the message,
   photo, and the variety guidance below.

   **No poster shall be repeated.** Never render two posters that share the same
   combination of template + palette + hero photo + headline copy — check what's
   already been generated earlier in the conversation (and in any `examples/*.json`
   or prior output files you can see) before picking, and change at least the
   template, palette, photo, or headline wording so every poster is visibly distinct.
   This applies within a single batch (e.g. "generate 10 posters") and across
   requests over time — don't hand back a poster identical to one Josh already has.

   **Swapping palette/photo alone is not enough variety.** `bold_impact`,
   `clean_split`, `photo_overlay`, `steps_timeline`, and `elegant_pills`
   all share a similar visual grammar (white background, colored header bar, boxed
   info sections) — recoloring and reshuffling photos across only these templates
   will still feel repetitive across a batch, even with zero literal repeats. When
   asked for multiple posters, spread the picks across templates with genuinely
   different visual structure — lean on `gradient_highlights` (full gradient
   background, circular badge), `night_glow` (dark glow, glass card, corner
   brackets), `torn_paper` (torn-edge photo scrapbook look), `stamp_collage` (dark
   ticket look, 6-photo souvenir-stamp grid), `magazine_split` (cream editorial
   layout), `luggage_tag` (ticket/tag card on a striped background), and
   `certificate_award` (personalized award/certificate look), and `studio_split`
   (minimalist dark agency-ad look: sparkle brand mark, huge bold headline, pill
   CTA button, tall portrait photo column), and `boarding_pass` (a completely different
   visual metaphor from every other template: a white "mobile boarding pass" ticket
   card sitting on a solid color surface, with a rounded-top photo strip, a FROM -> TO
   flight-route line, a perforated tear line, a boarding-details grid, and a barcode), and
   `movie_poster` (a full-bleed cinematic film-poster look: no card or panel at all, just a
   huge movie-title headline, a tagline/logline, a "STARRING: YOU" credit line, a small
   rating badge, and a tiny movie-credits line, all set directly over a dramatic full-bleed
   photo), `postcard` (a "wish you were here" postcard object: a postage stamp with a
   perforated edge, a postmark, a retro headline over the photo, and a mailing-address-style
   benefits column below it), and `chat_mockup` (a phone-screenshot-style WhatsApp/DM
   conversation with chat bubbles, an avatar, and a message-input bar -- a UI mockup rather
   than a paper/card metaphor) — reach for `boarding_pass`, `movie_poster`, `postcard`, or
   `chat_mockup` specifically when Josh says the posters feel repetitive or asks for
   something visually different, not just a recolor, rather than defaulting back to the
   white-card templates every time.

4. **Write the config JSON.** Build a config file following
   `references/config_schema.md` (copy one of `examples/*.json` as a starting point —
   one example per template). Save it somewhere temporary. If Josh wants the text
   boxes/badge/columns on the other side, set `"mirror": true` — `bold_impact`, `clean_split`, `elegant_pills`, and `torn_paper`
   all support it (see `references/style_guide.md` for what flips on each one) — rather
   than hand-editing coordinates.

5. **Render.**
   ```bash
   python3 scripts/generate_poster.py --config <config.json> --out <poster.png> --photos-dir <photo folder>
   ```
   This writes a 1080px-wide PNG (height varies per template, ~750-1350px, all within
   Instagram's feed-post limits) ready to post or print.

6. **Always generate 1 short + 1 long caption to go with it.** This is not optional —
   every poster Josh approves should come with a matching caption pair, without him
   having to ask separately. Build a small caption config from the same facts already
   in the poster config (benefits/requirements, contact) — see
   `references/caption_style.md` and `examples/caption_config.json` — then run:
   **Never carry the poster's discount/percentage-off into the caption config** —
   captions must not advertise school-fee discounts even when the poster does.
   ```bash
   python3 scripts/generate_captions.py --config <caption_config.json> --short 1 --long 1 --out <captions.md>
   ```
   Present the poster PNG and its short + long caption together.

7. **Show Josh the result** and iterate — tweak the config and re-render rather than
   trying to hand-edit the PNG. Common asks: swap template/palette, shorten headline
   lines (2-3 short lines render best — they auto-shrink to fit but stay cleanest at
   2-4 words per line), reorder benefits, change contact info. If he asks for more
   caption variety for a poster he already approved, just re-run
   `generate_captions.py` with a higher `--short`/`--long` count.

## Making a new variant / template

If Josh wants a look the three templates don't cover (e.g. the torn-paper skyline
style from his original examples), extend `scripts/templates.py` rather than trying to
force an existing template to do it — add a new `render_<name>` function following the
pattern of the existing three, using the helpers in `scripts/poster_engine.py`
(rounded/circle photo crops, drop shadows, gradients, wrapped text, FontAwesome icon
glyphs). Register it in `TEMPLATE_FUNCS` in `scripts/generate_poster.py`, and add an
example config + a paragraph in `references/style_guide.md`.

## Captions

Josh also wants social captions to go with (or independent of) the posters, in two
lengths:

- **Short** — a punchy 2-4 fragment caption ending in a call-to-action, for a
  WhatsApp status or Story. See `references/caption_style.md` for the voice (based on
  his own examples) and the phrase-bank approach that keeps re-generated batches
  varied instead of repetitive.
- **Long** — a structured feed post: flag + headline, hook question, a ✔️ benefits
  checklist, a 🔹 industries list, and a closing 📩/📱 CTA block.

Workflow:
1. Copy `examples/caption_config.json` and edit the facts for the current
   cohort/intake (country, phone, program duration, benefits, industries, discount).
   Don't invent facts — pull them from Josh or from the poster config already in use.
2. Run:
   ```bash
   python3 scripts/generate_captions.py --config <config.json> --short 8 --long 4 --out captions.md
   ```
3. Show Josh the batch. If he wants more variety, just re-run with a higher
   `--short`/`--long` count (omit `--seed` for a fresh random mix each time).
4. If he corrects the voice or gives new sample captions, update the phrase banks at
   the top of `scripts/generate_captions.py` (`SHORT_HOOKS`, `SHORT_PROGRAM_LINES`,
   `SHORT_VISA_FEE_LINES`, `SHORT_CTAS`, `LONG_HEADLINES`, `LONG_HOOKS`,
   `LONG_CTA_BLOCKS`) and `references/caption_style.md` to match, the same way new
   poster templates get added to `templates.py`.

## Reference files

- `references/config_schema.md` — full field-by-field poster config reference and icon name list.
- `references/style_guide.md` — what each poster template looks like and when to use it.
- `references/caption_style.md` — the short/long caption voice guide and phrase-bank system.
- `examples/*.json` — one working example config per poster template, plus `caption_config.json` for captions; copy and edit.
- `assets/photo_library/` — drop-in spot for Josh's photos if he doesn't already keep them elsewhere; point `--photos-dir` here or at wherever he keeps them.
