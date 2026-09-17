# Template style guide

Three templates are available, each modeled on a distinct style from Josh's reference
poster set. Pick based on the vibe the campaign needs.

## `bold_impact` (red/navy, high-energy corporate)
Thin top ribbon banner, then the huge two-tone headline leads immediately underneath
it — the hero content comes first, not buried under the badge. The star badge and
tagline sit in a row right below the headline instead of above it, then the hero
photo, a row of feature icons, two side-by-side info boxes ("PROGRAM REQUIREMENTS" /
"WHAT'S INCLUDED"), finishing with a bold contact bar. Best for a punchy, sales-y
flyer — lots of text density, good when you want to list courses/diplomas alongside
requirements. Recommended palette: `red_navy`. Bottom-bar-pinned at up to 1080x1330
(it'll grow a little taller only if an unusually long requirements/benefits list
needs the room), comfortably within Instagram's 1350px feed-post limit.

## `clean_split` (modern corporate, navy + gold)
Eyebrow pill + hexagon badge up top, three-line headline, optional discount pill, one
large hero photo, then two clean white boxes (REQUIREMENTS / BENEFITS) in a light
grid, ending in a solid navy CTA bar. Best for a polished, "corporate brochure" look.
Recommended palette: `navy_gold`.

## `elegant_pills` (framed, editorial)
A thin gold border frames the whole poster. Headline + tagline sit on the left with a
stack of rounded "pill" benefit rows; the right side shows two photos stacked
vertically (`photos.hero` on top, `photos.secondary[0]` below), each spanning the
full column width and half the column height, sized to match the full height of the
pill list rather than a fixed size — so the stack grows or shrinks with however many
benefits you list. Bottom bar is a single WhatsApp contact line. Best when you have
4-6 benefits to list and two strong photos. Needs both `photos.hero` and
`photos.secondary` (first entry); if `secondary` is omitted the second slot falls
back to a placeholder. Recommended palette: `green_gold` or `navy_gold`.

## `torn_paper` (skyline photo, torn-edge scrapbook look)
Full-width hero photo with a hand-torn bottom edge, arrow-chevron and dot decorations
in the corners. Below that, two even, full-width columns split the rest of the poster:
one column stacks the two torn photo insets top-to-bottom so they fill the whole column
height; the other holds the headline, tagline, and the "WHAT YOU GET" checklist, sized
to fill that same height (the copy column's natural height is measured first, then the
photo column is scaled to match it, so neither side ends in dead white space). A
contact line runs full-width underneath both columns. Best for a scrappy, high-energy
social post with two strong photos to show off. Recommended palette: `red_navy` or
`navy_gold`.

## `photo_overlay` (clean photo strip, solid color panel underneath)
A clean, un-covered hero photo strip runs across the top (roughly the top third of
the poster) with a gold seam accent below it, then a solid-color panel in the bottom
two-thirds carries all the copy: eyebrow pill, large headline, tagline, benefit chips,
and contact info, all with generous type and spacing so the panel reads as the
dominant half of the poster rather than an afterthought under the photo. No text ever
sits on top of the photo itself. The photo strip crops to fill edge-to-edge (zoomed
in, no letterbox bars); it's vertically centered by default, but set
`photos.hero_anchor_y` lower (e.g. `0.1`-`0.2`) for a tall/portrait photo so an
important subject near the top — a statue's head, a building's roofline — doesn't get
cropped off. Best for a bold, modern look with one strong hero photo. Recommended
palette: `navy_gold` or `red_navy` (the `primary_dark` color drives the panel).

## `steps_timeline` (numbered journey / process)
Headline, an optional compact photo strip, then a vertical numbered timeline (1, 2, 3,
4...) with a connecting line, each step showing a title and short description. Best
for explaining the application process (Apply -> Visa -> Study -> Internship) rather
than listing static benefits/requirements. Recommended palette: `navy_gold`.

## `gradient_highlights` (diagonal gradient, circular badge)
The whole poster is a diagonal gradient carrying the design -- a 3-stop blend
(accent color -> primary -> deep primary) rather than a straight accent-to-dark
fade, which avoids a muddy midtone and reads noticeably more colourful for palettes
where the primary color is its own distinct hue: `red_navy` (gold into red into
navy, the most vivid option) and `teal_coral` (coral into teal, closest to the
original reference) both pop. `navy_gold` and `green_gold` stay more subdued since
their primary and dark shades are the same hue family -- pick those when you want
the calmer, more corporate read instead. Small brand name top corner, big bold
headline + tagline, an optional circular badge (straight, centered text inside a
ring, auto-wrapped and auto-shrunk to fit, e.g. "GROW YOUR CAREER IN SINGAPORE"),
then a full-width white card with a photo
(`photos.hero`) on one side and a "Program Highlights" heading (or your own
`section_heading`) + a vertical list of pill-style benefit rows with diagonal-arrow
bullets on the other (`benefits` -- ignores `benefits_icons`, no icon glyphs needed
here). If no photo is supplied, a placeholder gradient fills that space so the
layout still reads correctly. Footer has an icon badge + `footer_tagline_lines` (2
short bold lines) on the left and one contact line on the right, with a small
decorative dot-constellation in between. Supports `mirror` (brand/badge/headline
swap to the left; the card's photo and text columns swap too, so the photo follows
the badge/headline side).

## `night_glow` (dark glow gradient, event-card style)
A dark, glowing gradient background (palette's primary color as a soft top-left glow,
palette's gold as a warm blob, blended into near-black) frames the poster. Big bold
headline, a `subtitle` line next to an outlined `brand_pill_text` pill, then a full-
width hero photo strip (`photos.hero`), then a translucent "glass" card
(`session_heading` + `session_description`). Below a thin divider, a
corner-bracketed detail block splits into `bottom_description` (left, a paragraph)
and `requirements` (right, a bold checklist) -- reusing the requirement facts instead
of an event date/venue. Bottom row is `contact_lines` joined with "  |  ",
handle-style. Best for a moodier, high-contrast promo when you want something that
doesn't read as a typical white-card poster. Recommended palette: `burgundy_cream` or
`red_navy` for the warm-glow look, `navy_gold` for a cooler, more corporate mood.
Does not support `mirror`.

## `stamp_collage` (dark ticket look, souvenir-stamp photo grid)
A dark diagonal-striped background (like a passport/ticket backdrop) behind a rotated
red-style ribbon banner, a big two-tone headline, a `duration_text` pill, a starburst
"sticker" badge (`badge_text`, e.g. "NO AGENCY FEES"), a round "stamp" badge
(`stamp_text`, e.g. "INTAKE OPEN NOW"), and a cream panel holding a 3x2 grid of white
postage-stamp-style photo cards — each with a perforated border and a caption label
underneath. Below the panel: a `benefits_heading` pill, a 4-item checklist with
alternating accent-colored check badges, a bold `footer_banner_text` banner, and a
contact bar. Needs `photos.gallery` (6 `{"file", "label"}` items) — this is the one
template built to show off a full set of photos at once. Best for a punchy,
souvenir-postcard/scrapbook look. Recommended palette: `teal_coral` or `green_gold`.
Does not support `mirror`.

## `magazine_split` (cream editorial layout, newspaper style)
A cream page inside a thin double-line frame, with a navy masthead bar up top
(`masthead_title`, `masthead_subtitle`, and a small Singapore flag chip), then a big
headline. Below that: a large hero photo (`photos.hero`) on the left with a caption
(`hero_caption`), and a smaller photo (`photos.secondary[0]`) + a `benefits_heading` +
checklist stacked on the right. A 3-photo captioned row (`photos.gallery`, 3 items)
runs underneath, then an outlined box with `footer_banner_text` + `cta` and a round
"APPLY NOW"-style stamp (`stamp_text`), finishing with a contact bar
(`cta_short` + `contact_lines`). Best for a clean, trustworthy, newspaper/magazine
feel. Recommended palette: `red_navy` or `navy_gold`. Does not support `mirror`.

## `luggage_tag` (ticket/tag card on a striped background)
A dark diagonal-striped background behind a large cream card shaped like a luggage
tag (rounded card with a punched hole + strap loop at the top). Inside the card: a
rotated `ribbon_text` banner, a two-tone headline, a divider, a big photo
(`photos.hero`) + two stacked smaller photos (`photos.secondary`, 2 items), a
starburst sticker (`badge_text`) overlapping the photo's corner, a `duration_text`
pill, a `benefits_heading` pill, a numbered 4-item checklist (alternating accent
colors), and a round stamp badge (`stamp_text`) near the bottom of the card. The card
height is measured from its own content, so it never leaves dead space. Outside the
card: a `footer_banner_text` banner and a contact bar. Best for a ticket/travel-themed
promo. Recommended palette: `navy_gold` or `red_navy`. Does not support `mirror`.

## `certificate_award` (personalized award/certificate look)
A cream page inside a double gold border frame with corner accent dots. A
`ribbon_text` banner up top, then "`awarded_to_label`" (small caps, defaults to
"THIS OPPORTUNITY IS AWARDED TO") above a large `recipient_name` (defaults to "You"
— personalize this per recipient if Josh wants a 1:1 feel, otherwise leave it generic),
a headline, and a starburst sticker (`badge_text`) in the top-right corner. A row of 4
arch-topped photos (`photos.gallery`, 4 items, captions not used) follows, then a
`duration_text` pill, a `benefits_heading` pill, a numbered 4-item checklist, a round
stamp badge (`stamp_text`), and a closing line (`closing_text`) above the contact
info. Best for a warm, personalized "you've been selected" feel rather than a generic
ad. Recommended palette: `burgundy_cream` or `navy_gold`. Does not support `mirror`.

## `neon_edge` (dark, glowing vertical sidebar text)
A near-black poster with a giant bold headline glowing softly and running
bottom-to-top up the left edge like a neon sign (`edge_text`), a small
triangle "mountain mark" + `brand_name` top-right of the main column, one
large photo, a solid-color stat panel (`duration_text` + `tagline`), a light
closing-statement panel (`closing_text`), a row of up to 3 benefit chips, and
a dark contact footer. Sized to 1080x1350 (Instagram 4:5 feed post). Needs
`photos.hero`. Recommended palette:
`teal_coral` or `red_navy`. Does not support `mirror`.

## `flat_pop` (vivid flat-color background, ringed stamp badge, sticker badge)
A bold, high-contrast poster on a single vivid flat-color background (the
palette's gold), with a white corner blob, a black rounded "sticker" badge
(`badge_text`), a ringed circle badge with straight centered text
(`stamp_text` -- defaults to "SINGAPORE", satisfying the mandatory Singapore
mention structurally), a big stat headline (`headline_lines`) + `tagline`,
one large photo, and a black closing bar with a 2-line closing statement
(`closing_lines`), a contact line, and the brand mark. Sized to 1080x1350
(Instagram 4:5 feed post). Needs `photos.hero`. Recommended palette:
`green_gold` or `red_navy` (its gold tone is the most vivid background of
the five). Does not support `mirror`.

## `dark_chevron` (dark modern-corporate, gold chevron accents)
A near-black poster (`primary_dark`) with gold double-chevron accents
(top-left and a mirrored pair bottom-right), `brand_name` top-right, a photo
in the upper-right, a 2-line `side_heading` + short lead-in `tagline` + a
short bulleted list (`diploma_points`, defaults to 4 short points about the
hands-on diploma) with plus-mark and dot-grid decorative accents on the left,
a big two-tone closing headline (`headline_lines`) below the photo with an
underline accent, a small dot grid, and a contact row (`cta` +
`contact_lines`). Sized to 1080x1350 (Instagram 4:5 feed post). Needs
`photos.hero`; optionally add `photos.secondary[0]` to stack a second photo
underneath the hero photo (each gets half the photo column's height) instead
of one full-height photo. Recommended palette: `navy_gold` or `red_navy`.
Does not support `mirror`.

## `studio_split` (minimalist dark agency-ad look, sparkle brand mark)
A solid dark poster (`navy`) styled after modern agency/portfolio ads: a
small sparkle/asterisk brand mark + `brand_name` top-left, a huge 2-4 line
bold `headline_lines` (always rendered near-white regardless of any
per-line `color` hint, to match this style's monochrome look), a short
`body_text` paragraph, a pill-shaped outlined CTA button (`cta`) with an
arrow icon, an optional `website_text` (or falls back to the first
`contact_lines` entry) below the button, and a 3-dot row bottom-left. A
tall portrait photo fills the right ~40% of the poster, with a light
rounded notch (holding its own 3-dot row) tucked behind the photo's
top-right corner and a dot-grid accent overlapping its bottom-left corner.
Sized to 1080x1080 (Instagram square feed post). Needs `photos.hero` --
because the photo column is narrow and tall, a portrait-oriented photo
works far better here than a landscape one (check with `check_crop.py`
before picking). Recommended palette: `navy_gold` for night/sunset photos
(the dark navy background echoes the sky), or match per the palette-swatch
workflow for other photos. Does not support `mirror`.

## `boarding_pass` (mobile boarding-pass ticket, airline metaphor)
Structurally different from every other template in this skill -- built
around an airline mobile-boarding-pass metaphor ("your ticket to Singapore")
instead of the usual headline+benefits+CTA stack. A solid-color surface
(`primary_dark`) holds a white ticket card with a drop shadow: a
rounded-top-corners photo strip with an optional `brand_name` pill over it
(omit `brand_name` for a plain, unobstructed photo), a big
`from_code` -> `to_code` route line (e.g. "HOME" -> "SIN") with a dashed
flight path and a plane icon between the two codes, a passenger/status row
(`passenger_label`/`passenger_value`, `status_label`/`status_value`), a
perforated tear line (dashed rule with circular notches cut into the card's
left/right edges), a 2x2 `boarding_fields` grid (program/duration/intake/
fees or whatever four fields you supply), a barcode graphic with
`ticket_code` underneath, and a round `stamp_text` badge (defaults
"BOARDING NOW"). Below the card, on the surface color: a closing `cta` line
and the `contact_lines` row. Reach for this one specifically when Josh says
the posters feel repetitive or asks for something visually different --
it doesn't share any layout DNA with the card/split/chevron templates.
Cropped to its actual content height (the ticket card doesn't stretch to
fill the full canvas), typically well under Instagram's 1350px feed-post
limit. Needs `photos.hero`
sized for a wide ~2.4:1 strip (960x400) -- a photo with some travel/journey
association (passport, luggage, airport, boarding) reinforces the ticket
metaphor especially well, but any well-cropping photo works. Does not
support `mirror` or `dark_mode` (it's already built around a dark surface +
white card, which doesn't map cleanly onto the dark-mode remapping used by
the light-background templates).

## `movie_poster` (full-bleed cinematic film-poster look)
No card, panel, or white space at all -- the hero photo fills the entire
1080x1350 canvas (Instagram 4:5 feed post) edge to edge, with a dark gradient rising from the bottom
(and a light one at the very top) so type stays legible directly over the
image, like an actual film poster. A small tracked `presents_text` line up
top, a huge centered movie-title-style `headline_lines`, a one-line
`tagline` (logline), a gold `starring_text` credit line (defaults
"STARRING: YOU"), a small bordered `rating_text` badge (doubles nicely as
the age-requirement line, e.g. "APPROVED · AGES 18-40"), a tiny tracked
`credits` line listing the program benefits, and a solid-color release bar
at the very bottom with `release_text` + `cta` + `contact_lines`. Reach for
this one (alongside `boarding_pass`) when Josh says the posters feel
repetitive -- it shares no layout DNA with any card/split/chevron template,
since there's no card at all. Needs `photos.hero` -- since the whole canvas
is the photo, pick something dramatic and high-contrast (a skyline at dusk,
a single strong subject) rather than a busy group photo; check retention
with `check_crop.py` at 1080x1350 first. Recommended palette: match the
photo's mood via the palette-swatch workflow -- `navy_gold` or `red_navy`
for night/skyline photos tends to work well since the palette mainly shows
up in the small bottom release bar and the gold headline/starring accents,
not as a big color block. Does not support `mirror` or `dark_mode` (already
full-bleed dark by design).

## `postcard` (a "wish you were here" postcard object)
A different object-metaphor from every other template -- meant to read as an
actual postcard rather than a card/ticket/panel. A thick white print-style
border frames a large photo; a postage-stamp graphic (perforated edge,
plane icon, `stamp_country`/`stamp_denomination`) sits in the photo's
top-right corner, with a circular postmark (`postmark_text`) in the photo's top-left corner. A big
retro `headline_lines` (e.g. "GREETINGS FROM" /
"SINGAPORE") sits on a dark band near the photo's bottom edge. Below the
photo, a thin vertical divider splits the border area into a left "note"
column (`note_heading` + `note_text`, an optional `ps_text` postscript line
under a divider, and an optional `who_heading` + `requirements`
mini-checklist) and a right "mailing address" column (an optional
`duration_text` pill, up to 6 `benefits` as address-style lines, an
optional `industries` list, and `contact_lines`), like the postcard's
addressee block -- both columns default to enough content that the space
below the photo doesn't read as empty, plus a small `closer_text` line at
the very bottom. Sized to fit within Instagram's 1350px feed-post limit --
needs `photos.hero` sized for a ~1020x820 area (near-square) --
check `check_crop.py` first; a scenic, recognizable-landmark photo (skyline,
Merlion, a well-known building) sells the postcard concept best. Recommended
palette: match via the palette-swatch workflow -- `navy_gold` tends to work
well for sunset/golden-hour photos since gold echoes the glow and navy
grounds the shadows. Does not support `mirror` or `dark_mode`.

## `chat_mockup` (phone-screenshot WhatsApp/DM conversation)
A UI mockup instead of a paper/card/ticket metaphor -- a phone-screenshot-
style rendering of a WhatsApp/DM conversation about the program. A colored
header bar holds a circular avatar (`photos.hero`, cropped small and round)
plus `contact_name` + `contact_status`. Below it, `messages` (a list of
`{"from": "them"|"me", "text"}` items, alternating left/right like a real
chat, each with a timestamp underneath) render as rounded speech bubbles --
white for "them", the palette's primary color for "me". A
`{"from": "me", "photo": true}` entry renders `photos.secondary[0]` as an
image bubble instead of text (e.g. a photo of a past student batch shared
mid-conversation). A message-input-bar mockup with a send button closes out
the bottom. This one doubles as social proof, since it reads as a real
conversation rather than an ad. Important: emoji do not render reliably
with this skill's fonts (they show as blank boxes in the rendered PNG) --
write message text without emoji. Needs `photos.hero` for the avatar (any
reasonably centered photo works, since it's cropped small and circular) and
optionally `photos.secondary[0]` if a message uses `"photo": true`.
Recommended palette: `green_gold` reads closest to WhatsApp's own green, but
any palette works since the photo/color footprint is small. Does not
support `mirror` or `dark_mode`.

## Instagram sizing

Every template now fits Instagram's feed-post limits with no cropping or
letterboxing. `studio_split` renders square at 1080x1080 (1:1); every other
template renders at 1080 wide by at most 1350 tall (4:5, Instagram's max
portrait feed-post ratio) -- most crop dynamically to their actual content
height, which is often shorter than 1350 (see each template's entry above
for its typical range). There's no longer a subset of templates to avoid
for Instagram specifically -- pick based on the vibe/variety guidance in
`SKILL.md` instead.

## Rearranging boxes with `mirror`

Every template accepts `"mirror": true` to flip which side things sit on, without
touching any code:

- **bold_impact**: the top-right badge moves to the top-left, and the two info boxes
  swap order (WHAT'S INCLUDED first, then PROGRAM REQUIREMENTS).
- **clean_split**: the eyebrow pill and badge swap sides, and the REQUIREMENTS /
  BENEFITS boxes swap order.
- **elegant_pills**: the photo and the benefit-pill column swap sides
  (photos left / pills right instead of the default pills left / photos right).
- **torn_paper**: the photo-insets column and the headline column swap sides.
- **gradient_highlights**: the brand name, circular badge, and headline/tagline
  column swap to the left; the highlights card and footer stay full-width.

Render the same config twice — once default, once with `mirror: true` — to compare
before picking one.

## Choosing a palette
- `red_navy` — urgent, high-contrast, good for "act now" campaigns.
- `navy_gold` — premium, trustworthy, general-purpose default.
- `green_gold` — calmer, growth/education-coded.
- `teal_coral` — fresh, modern; works well for non-Singapore destinations (e.g. Australia).
- `burgundy_cream` — rich, upscale; good alternative to green_gold/navy_gold for variety.

Every template is destination-agnostic — the country/city only ever comes from
`headline_lines`, `tagline`, and the photos you supply. Swap the location text and
palette to reuse the same layout for a different country or promo without touching any code.

## General tips
- Keep `headline_lines` to 2-3 short lines; longer lines auto-shrink but stay legible longest at 2-3 words per line.
- 3-4 items look best in `requirements`/`benefits` for `bold_impact` and `clean_split`; `elegant_pills` can hold up to ~6 in its pill list.
- Always pass real photos via `--photos-dir` once available — the gradient placeholder is only there so drafts still look complete before real photos are supplied.
