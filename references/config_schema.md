# Poster config schema

A poster is described by one JSON config file, passed to `scripts/generate_poster.py --config`.

## Top-level fields

| Field | Type | Notes |
|---|---|---|
| `template` | string | One of `bold_impact`, `clean_split`, `elegant_pills`, `torn_paper`, `photo_overlay`, `steps_timeline`, `gradient_highlights`, `night_glow`, `stamp_collage`, `magazine_split`, `luggage_tag`, `certificate_award`, `neon_edge`, `flat_pop`, `dark_chevron`, `studio_split`, `boarding_pass`, `movie_poster`, `postcard`, `chat_mockup`. See `style_guide.md` for which to pick. Most render at 1080x1620; `bold_impact` renders at 1080x1527 (A4); `neon_edge`, `flat_pop`, and `dark_chevron` render at 1080x1350 (Instagram 4:5 feed post); `studio_split` renders at 1080x1080 (Instagram square feed post); `boarding_pass` and `chat_mockup` render at up to 1080x1620, cropped to actual content height; `movie_poster` and `postcard` render full-size at 1080x1620. |
| `palette` | string | One of `red_navy`, `navy_gold`, `green_gold`, `teal_coral`, `burgundy_cream`. Controls the primary/accent colors. |
| `eyebrow` | string | Small banner/pill text near the top (e.g. "KICKSTART YOUR GLOBAL CAREER!"). Optional. |
| `badge_text` | string | Text inside a badge. For `bold_impact`/`clean_split` it's the top-right star badge (e.g. "YOUR FUTURE STARTS HERE!"); for `stamp_collage`, `luggage_tag`, and `certificate_award` it's the spiky starburst "sticker" badge (e.g. "NO AGENCY FEES", "GUARANTEED INTERNSHIP"). Optional. |
| `headline_lines` | list of `{"text": str, "color": "primary"\|"navy"\|"gold"}` | Each item is one line of the big headline, rendered in its own color. 2-3 lines works best. |
| `tagline` | string | One-line subhead under the headline. Optional. |
| `discount_text` | string | e.g. "50% DISCOUNT". Only used by `clean_split`; omit to hide the discount pill. |
| `requirements` | list of strings | Eligibility bullets (age, education, passport, English, etc). |
| `requirements_icons` | list of strings | Icon name per requirement, same order/length as `requirements`. See icon list below. |
| `benefits` | list of strings | Program benefits/features. `elegant_pills` can take 4-8 of these; `postcard` shows up to 6; other templates show up to 4. |
| `benefits_icons` | list of strings | Icon name per benefit. |
| `benefits_extra` | list of strings | Only used by `bold_impact`'s second info box (e.g. courses/diplomas offered). Falls back to `benefits` if omitted. |
| `benefits_heading` | string | Only used by `torn_paper` — the section header above the benefits checklist (defaults to "BENEFITS"). |
| `contact_label` | string | Only used by `elegant_pills` — the small line above the phone number. |
| `contact_lines` | list of `{"icon": str, "text": str}` | Phone/WhatsApp number shown in the bottom bar. **Josh only wants a phone/WhatsApp number here — never an email address or an @handle**, even for `night_glow`'s pipe-separated contact row (which originally showed a handle + email + phone in the reference design; drop the first two, keep only the phone number). |
| `cta` | string | Call-to-action text in the bottom bar (e.g. "CONTACT US TODAY!"). Optional. |
| `steps` | list of `{"title": str, "description": str}` | Only used by `steps_timeline` — the numbered journey steps. |
| `photos.side` | string (filename) | Only used by `steps_timeline` — an optional photo running down the right side alongside the numbered steps (narrows the step column to make room). Separate from `photos.hero`, which (if set) shows as a full-width strip above the steps instead. |
| `mirror` | boolean | Flips the layout left-to-right — swaps which side the badge/eyebrow, info boxes, or photo/pill columns sit on. Supported by `bold_impact`, `clean_split`, `elegant_pills`, `torn_paper`, `gradient_highlights` (exact effect depends on the template; see `style_guide.md`). Not used by `photo_overlay`, `steps_timeline`, `night_glow`, `stamp_collage`, `magazine_split`, `luggage_tag`, `certificate_award`, `neon_edge`, `flat_pop`, `dark_chevron`, `studio_split`, `boarding_pass`, `movie_poster`, `postcard`, `chat_mockup`. Default `false`. |
| `dark_mode` | boolean | Renders the poster on a dark background instead of the palette's normal light/cream one, remapping text and panel colors for contrast (headline lines colored `navy` become white, lines colored `primary` become the palette's `gold`). Supported by `clean_split`, `magazine_split` (light-background templates only) and `dark_chevron` (deepens its already-dark background further). Has no effect on templates that only ever render on a dark or photo-heavy background (`night_glow`, `neon_edge`, `studio_split`, etc.) or on light-only templates that don't implement it. Default `false`. |
| `photos` | object | `{"hero": "<filename>", "secondary": ["<filename>", ...], "hero_anchor_y": 0.0-1.0, "gallery": [{"file": "<filename>", "label": "<caption>"}, ...], "side": "<filename>"}`. Filenames are resolved against `--photos-dir`. `secondary` is used by `torn_paper`'s two photo insets, `elegant_pills`'s second stacked photo (`secondary[0]`), `luggage_tag`'s two stacked photos, `magazine_split`'s smaller top-right photo (`secondary[0]`), `dark_chevron`'s optional second stacked photo under the hero (`secondary[0]`), `studio_split`'s optional second stacked photo splitting its photo column in half (`secondary[0]`), and `chat_mockup`'s optional image-bubble message (`secondary[0]`, only used by a `{"from": "me", "photo": true}` entry in `messages`); other templates (including `gradient_highlights`, inside its highlights card, and `night_glow`/`magazine_split`/`luggage_tag`, as a hero photo) use `hero`. `gallery` is used by `stamp_collage` (6 items, each with a `label` caption), `magazine_split` (3 items, each with a `label`), and `certificate_award` (4 items, `label` not used — arch photos have no caption). `side` is only used by `steps_timeline` (see the `photos.side` row above). If a photo is missing, a placeholder gradient is used instead so you can still see the layout. `hero_anchor_y` is only used by `photo_overlay`'s top photo strip — its crop-to-fill zooms in and centers vertically by default (`0.5`); lower it toward `0.1`-`0.2` to keep the top of a tall subject (a statue's head, a building's roofline) from being cropped off. |
| `brand_name` | string | Small bold brand-name text near the top of the poster (e.g. your agency/brand name). Used by `gradient_highlights` (top corner), `dark_chevron` (top-right, defaults to "STUDY SINGAPORE"), `neon_edge` (top-left brand row, defaults to "STUDY SINGAPORE"), `studio_split` (top-left, next to the sparkle mark, defaults to "STUDY SINGAPORE"), and `boarding_pass` (small pill over the photo; omitted entirely if left blank/unset). Optional. |
| `body_text` | string | Only used by `studio_split` — the short paragraph under the headline (wraps automatically). Optional. |
| `website_text` | string | Only used by `studio_split` — a line under the CTA button (e.g. a website URL or "WhatsApp +65 ..."). Falls back to the first `contact_lines` entry's text if omitted. Optional. |
| `badge_circle_text` | string | Only used by `gradient_highlights` — straight, horizontally-centered text inside the circular badge (e.g. "GROW YOUR CAREER IN SINGAPORE"), auto-wrapped and auto-shrunk to fit the ring. Omit to hide the badge entirely. |
| `section_heading` | string | Only used by `gradient_highlights` — heading above the benefits card (defaults to "Program Highlights"). |
| `footer_tagline_lines` | list of strings | Only used by `gradient_highlights` — 1-2 short bold lines next to the footer icon badge (defaults to `["Start Your", "Singapore Journey"]`). |
| `footer_icon` | string | Only used by `gradient_highlights` — icon name shown in the footer badge circle (defaults to `graduation-cap`). See icon list below. |
| `subtitle` | string | Only used by `night_glow` — the line next to the brand pill, under the headline (e.g. "IN SINGAPORE"). |
| `brand_pill_text` | string | Only used by `night_glow` — text inside the small outlined pill next to the subtitle (e.g. "APPLY NOW"). |
| `session_heading` | string | Only used by `night_glow` — heading inside the glass card (defaults to "JOIN THE PROGRAM"). |
| `session_description` | string | Only used by `night_glow` — paragraph inside the glass card. |
| `bottom_description` | string | Only used by `night_glow` — paragraph in the left column of the bottom detail block. |
| `ribbon_text` | string | Used by `stamp_collage`, `luggage_tag`, and `certificate_award` — a short rotated ribbon-banner line near the top (e.g. "COLLECT YOUR TICKET TO SINGAPORE"). Optional. |
| `duration_text` | string | Used by `stamp_collage`, `magazine_split`, `luggage_tag`, `certificate_award` — a pill showing the program/pass duration (e.g. "1 YEAR STUDENT PASS"). Optional. |
| `stamp_text` | string | Used by `stamp_collage`, `magazine_split`, `luggage_tag`, `certificate_award`, `boarding_pass` (defaults to "BOARDING NOW") — text inside a round "stamp" badge (e.g. "INTAKE OPEN NOW", "APPLY NOW"). Wraps automatically across 1-3 lines. Optional. |
| `footer_banner_text` | string | Used by `stamp_collage`, `luggage_tag`, `magazine_split` (inside its outlined box) — a bold full-width closing banner line (e.g. "LIMITED SLOTS AVAILABLE FOR THIS INTAKE"). Optional. |
| `benefits_heading` | string | Also used by `stamp_collage`, `magazine_split`, `luggage_tag`, `certificate_award` as the pill/heading above their checklist (e.g. "INCLUDED WITH YOUR PASS", "WHAT YOU GET"). |
| `masthead_title` / `masthead_subtitle` | string | Only used by `magazine_split` — the navy masthead bar's title (defaults to "THE SINGAPORE OPPORTUNITY") and small subtitle line underneath it. |
| `hero_caption` | string | Only used by `magazine_split` — a small caption line under the large hero photo. Optional. |
| `cta` / `cta_short` | string | `magazine_split` uses `cta` for the line inside its outlined "limited slots" box and `cta_short` for its bottom contact-bar button text (defaults to "ENQUIRE TODAY!"). `stamp_collage` and `luggage_tag` use `cta` for their contact-bar button text (defaults to "CONTACT US TODAY!" / "APPLY NOW!"). |
| `awarded_to_label` / `recipient_name` | string | Only used by `certificate_award` — the small caps line (defaults to "THIS OPPORTUNITY IS AWARDED TO") and the large name under it (defaults to "You" — leave as "You" for a generic ad, or personalize per recipient). |
| `closing_text` | string | Used by `certificate_award` (the bold line above the contact info, defaults to "MESSAGE ME TO CLAIM YOUR SLOT") and `neon_edge` (the bold line in the light closing panel, defaults to "INTAKE CLOSES SOON!"). |
| `edge_text` | string | Only used by `neon_edge` — the big glowing headline that runs vertically up the left edge (defaults to "STUDY IN SINGAPORE"). Keep it short; it auto-shrinks to fit the poster height but reads best under ~20 characters. |
| `footer_line` | string | Only used by `neon_edge` — the small lead-in text above the contact line in the footer (defaults to "Book your spot now at"). |
| `stamp_text` (or the older `curve_text`) | string | Only used by `flat_pop` — straight text inside a ringed circle badge under the black sticker badge (defaults to "SINGAPORE"; satisfies the mandatory Singapore mention if it isn't already in the headline/tagline). Was curved text bleeding off the left edge in earlier versions of this template — now a self-contained round badge like the skill's other stamp badges. `curve_text` still works as a fallback for old configs but `stamp_text` is preferred. |
| `from_code` / `to_code` | string | Only used by `boarding_pass` — the big 3-letter-style codes on the ticket's route line (defaults `"HOME"` / `"SIN"`). |
| `from_city` / `to_city` | string | Only used by `boarding_pass` — small city labels under `from_code`/`to_code` (defaults `"Your City"` / `"Singapore"`). |
| `passenger_label` / `passenger_value` | string | Only used by `boarding_pass` — the ticket's "passenger" field (defaults `"PASSENGER"` / `"YOU"`). |
| `status_label` / `status_value` | string | Only used by `boarding_pass` — the ticket's status field, next to passenger (defaults `"STATUS"` / `"CONFIRMED"`). |
| `boarding_fields` | array of `{"label", "value"}` | Only used by `boarding_pass` — up to 4 items rendered in a 2x2 grid below the tear line (e.g. PROGRAM, DURATION, INTAKE, FEES). Defaults to a generic diploma/1-year-pass/open-intake/no-agency-fee set if omitted. |
| `ticket_code` | string | Only used by `boarding_pass` — small text under the barcode graphic (defaults `"SG-2026-INTAKE"`). |
| `presents_text` | string | Only used by `movie_poster` — small tracked line at the very top (defaults `"STUDY SINGAPORE PRESENTS"`). |
| `starring_text` | string | Only used by `movie_poster` — gold credit line below the tagline (defaults `"STARRING: YOU"`). |
| `rating_text` | string | Only used by `movie_poster` — text inside the small bordered rating badge, e.g. an age requirement (defaults `"APPROVED · AGES 18-40"`). |
| `credits` | array of strings | Only used by `movie_poster` — short benefit phrases rendered as a tiny movie-credits line joined with " • " (defaults to a generic paid-internship/diploma/visa/no-fees set). |
| `release_text` | string | Only used by `movie_poster` — small line above the CTA in the bottom bar (defaults `"NOW ENROLLING"`). |
| `stamp_country` / `stamp_denomination` | string | Only used by `postcard` — text inside the postage-stamp graphic (defaults `"SINGAPORE"` / `"AIRMAIL"`). |
| `postmark_text` | string | Only used by `postcard` — text inside the round postmark badge overlapping the stamp's corner (defaults `"APPLY TODAY"`). |
| `note_heading` / `note_text` | string | Only used by `postcard` — the left "note" column below the photo (defaults `"A quick note..."` / a short generic message). |
| `ps_text` | string | Only used by `postcard` — an optional second line under a divider in the left note column, styled like a postscript (defaults to a short "no agency fees" line). Set to `""`/`null` to omit. |
| `who_heading` / `requirements` | string / array of strings | Only used by `postcard` — an optional mini-checklist (up to 4 items) under the note, e.g. age/education/passport requirements (defaults to a generic set). Set `who_heading` to `""`/`null` to omit the whole block. |
| `duration_text` | string | Also used by `postcard` (small pill above the "TO:" address block, defaults `"1 YEAR STUDENT PASS"`; set to `""`/`null` to omit) in addition to its existing use in `magazine_split` and `stamp_collage`. |
| `industries` | array of strings | Only used by `postcard` — an optional list rendered as "OPEN INDUSTRIES" joined with " • " under the benefits in the address column. Omitted entirely if left unset. |
| `closer_text` | string | Only used by `postcard` — small centered line at the very bottom (defaults `"SEND THIS TO YOURSELF — YOUR FUTURE IS WAITING"`). |
| `contact_name` / `contact_status` | string | Only used by `chat_mockup` — the header bar's contact name and status line (defaults `"Study Singapore"` / `"Online"`). |
| `messages` | array of `{"from": "them"\|"me", "text"}` (or `{"from": "me", "photo": true}`) | Only used by `chat_mockup` — the chat bubble scrollback, rendered in order with alternating left/right alignment. A `"photo": true` entry renders `photos.secondary[0]` as an image bubble instead of text. Defaults to a short generic Q&A conversation if omitted. Note: emoji do not render reliably with this skill's fonts (they show as blank boxes) — avoid them in message text. |
| `input_placeholder` | string | Only used by `chat_mockup` — placeholder text in the bottom message-input-bar mockup (defaults `"Type a message..."`). |
| `closing_lines` | list of strings | Only used by `flat_pop` — 2 short bold lines in the bottom black bar (defaults to `["ONLY UNTIL", "INTAKE CLOSES!"]`). |
| `side_heading` | list of strings | Only used by `dark_chevron` — a 2-line heading in the left column, first line gold, second white (defaults to `["GROW YOUR", "CAREER"]`). |
| `diploma_points` | list of strings | Only used by `dark_chevron` — a short bulleted list under `tagline` in the left column (defaults to 4 lines about the hands-on diploma). Pair it with a short lead-in `tagline` like "Our hands-on diploma includes:". Keep each point to one short phrase (2-6 words) since the column is narrow. |

## Available icon names

`graduation-cap`, `briefcase`, `dollar`, `percent`, `check`, `check-circle`, `phone`, `whatsapp`,
`plane`, `globe`, `handshake`, `comments`, `id-card`, `calendar`, `clock`, `map-marker`, `users`,
`star`, `envelope`, `book`, `money`, `passport`, `language`, `home`, `arrow-right`.

## Minimal example

```json
{
  "template": "clean_split",
  "palette": "navy_gold",
  "headline_lines": [
    {"text": "STUDY AND", "color": "navy"},
    {"text": "PAID INTERNSHIP", "color": "gold"},
    {"text": "IN SINGAPORE", "color": "navy"}
  ],
  "requirements": ["Age 18 to 40", "High School Graduate"],
  "requirements_icons": ["calendar", "graduation-cap"],
  "benefits": ["Paid Internship", "Career Growth"],
  "benefits_icons": ["briefcase", "check-circle"],
  "contact_lines": [{"icon": "phone", "text": "+65 8000 0000"}],
  "photos": {"hero": "marina_bay.jpg"}
}
```
