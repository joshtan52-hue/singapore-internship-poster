"""
Three poster templates for the Singapore Study + Paid Internship campaign.
Each function takes a config dict (see references/config_schema.md) and an
output path, and writes a PNG poster.
"""
import os
import math
import random
from PIL import Image, ImageDraw
import poster_engine as pe

W, H = 1080, 1620
PAD = 60

PALETTES = {
    "red_navy": dict(primary=(200, 16, 46), primary_dark=(11, 43, 74), navy=(11, 43, 74),
                      gold=(255, 199, 44), bg=(255, 255, 255), panel=(246, 247, 249), text=(24, 32, 46)),
    "navy_gold": dict(primary=(22, 36, 68), primary_dark=(12, 20, 42), navy=(22, 36, 68),
                       gold=(197, 157, 54), bg=(250, 248, 240), panel=(255, 255, 255), text=(24, 32, 46)),
    "green_gold": dict(primary=(19, 74, 48), primary_dark=(10, 44, 28), navy=(19, 74, 48),
                        gold=(197, 157, 54), bg=(250, 248, 240), panel=(255, 255, 255), text=(24, 32, 46)),
    "teal_coral": dict(primary=(11, 94, 101), primary_dark=(6, 56, 61), navy=(11, 94, 101),
                        gold=(240, 130, 90), bg=(247, 250, 250), panel=(255, 255, 255), text=(20, 34, 36)),
    "burgundy_cream": dict(primary=(97, 22, 39), primary_dark=(60, 12, 22), navy=(97, 22, 39),
                            gold=(201, 162, 39), bg=(252, 248, 240), panel=(255, 255, 255), text=(35, 20, 22)),
}


def _pal(cfg):
    name = cfg.get("palette", "navy_gold")
    if name not in PALETTES:
        raise ValueError(f"Unknown palette '{name}'. Choose from: {list(PALETTES)}")
    return PALETTES[name]


def _checklist_colors(pal):
    return [pal["primary"], pal["gold"], pal["primary_dark"], pal["navy"]]


def _dark_bg_border(pal, dark):
    """Border/outline color for elements drawn directly on the page
    background: normal palette navy in light mode, a lightened version in
    dark mode so thin outlines stay visible against a dark canvas."""
    return pe.lighten(pal["navy"], 0.35) if dark else pal["navy"]


def _color(cfg, name):
    pal = _pal(cfg)
    return pal.get(name, pal["primary"])


def _icon_badge(img, center, diameter, bg_color, icon_name, icon_size, icon_color=(255, 255, 255)):
    d = ImageDraw.Draw(img)
    r = diameter / 2
    d.ellipse([center[0] - r, center[1] - r, center[0] + r, center[1] + r], fill=bg_color)
    fnt = pe.font("icons", icon_size)
    ch = pe.icon_char(icon_name)
    bbox = d.textbbox((0, 0), ch, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((center[0] - tw / 2 - bbox[0], center[1] - th / 2 - bbox[1]), ch, font=fnt, fill=icon_color)


def _feature_row(img, xy, w, icon_name, title, subtitle, pal, icon_bg=None, title_size=24, sub_size=18):
    d = ImageDraw.Draw(img)
    x, y = xy
    icon_bg = icon_bg or pal["primary"]
    _icon_badge(img, (x + 28, y + 28), 56, icon_bg, icon_name, 26)
    tf = pe.font("poppins-bold", title_size)
    sf = pe.font("lato-regular", sub_size)
    pe.draw_multiline(d, (x + 72, y + 4), title, tf, w - 72, pal["text"])
    if subtitle:
        pe.draw_multiline(d, (x + 72, y + 4 + title_size + 6), subtitle, sf, w - 72, (110, 110, 118))
    return y + 68


def _headline(img, xy, lines_cfg, pal, max_width, base_size=64, font_name="poppins-bold", line_gap=6, align="left"):
    d = ImageDraw.Draw(img)
    x, y = xy
    if not lines_cfg:
        return y
    size = base_size
    fnt = pe.font(font_name, size)
    # shrink to fit widest line
    widest = max(d.textlength(l["text"], font=fnt) for l in lines_cfg)
    while widest > max_width and size > 24:
        size -= 2
        fnt = pe.font(font_name, size)
        widest = max(d.textlength(l["text"], font=fnt) for l in lines_cfg)
    asc, desc = fnt.getmetrics()
    for l in lines_cfg:
        color = pal.get(l.get("color", "primary"), pal["primary"])
        tw = d.textlength(l["text"], font=fnt)
        lx = x if align == "left" else x + (max_width - tw) / 2
        d.text((lx, y), l["text"], font=fnt, fill=color)
        y += asc + desc + line_gap
    return y


def _contact_bar(img, y0, h, cfg, pal, bg=None):
    bg = bg or pal["primary"]
    d = ImageDraw.Draw(img)
    d.rectangle([0, y0, W, y0 + h], fill=bg)
    contacts = cfg.get("contact_lines", [])
    cta = cfg.get("cta", "")
    fnt_cta = pe.font("poppins-bold", 30)
    fnt_c = pe.font("lato-bold", 28)
    x = PAD
    if cta:
        d.text((x, y0 + h / 2 - 18), cta, font=fnt_cta, fill=(255, 255, 255))
        x += d.textlength(cta, font=fnt_cta) + 50
    for c in contacts:
        _icon_badge(img, (x + 20, y0 + h / 2), 44, (255, 255, 255), c["icon"], 22, icon_color=bg)
        d.text((x + 48, y0 + h / 2 - 16), c["text"], font=fnt_c, fill=(255, 255, 255))
        x += 48 + d.textlength(c["text"], font=fnt_c) + 40


# ---------------------------------------------------------------- TEMPLATE A
def render_bold_impact(cfg, out_path):
    pal = _pal(cfg)
    # Targets Instagram's 4:5 feed-post max (1080x1350): H is the normal
    # bottom-bar-pinned height, canvas_h is scratch headroom in case an
    # unusually long requirements/benefits list needs more room -- the
    # final crop below only grows past H if content actually needs it.
    H = 1330
    canvas_h = H + 300
    img = Image.new("RGB", (W, canvas_h), pal["bg"])
    d = ImageDraw.Draw(img)

    # top ribbon
    ribbon_h = 64
    d.rectangle([0, 0, W, ribbon_h], fill=pal["primary"])
    fnt = pe.font("poppins-bold", 26)
    eyebrow = cfg.get("eyebrow", "KICKSTART YOUR GLOBAL CAREER!")
    d.text((PAD, ribbon_h / 2 - 15), eyebrow, font=fnt, fill=(255, 255, 255))

    mirror = cfg.get("mirror", False)

    # Badge stays pinned at the top-right (top-left when mirrored), right under
    # the ribbon, in its original fixed spot -- it no longer pushes the
    # headline down; the headline starts right under the ribbon regardless.
    if cfg.get("badge_text"):
        if mirror:
            bx0, by0, bx1, by1 = PAD, ribbon_h + 18, PAD + 220, ribbon_h + 130
        else:
            bx0, by0, bx1, by1 = W - 260, ribbon_h + 18, W - 40, ribbon_h + 130
        d.rounded_rectangle([bx0, by0, bx1, by1], radius=16, outline=pal["gold"], width=4, fill=pal["navy"])
        stars = pe.icon_char("star") * 5
        d.text((bx0 + 20, by0 + 10), stars, font=pe.font("icons", 16), fill=pal["gold"])
        pe.draw_multiline(d, (bx0 + 16, by0 + 36), cfg["badge_text"], pe.font("poppins-bold", 20),
                           bx1 - bx0 - 32, (255, 210, 60), align="center")

    # Headline leads the poster right under the thin ribbon -- it's the hero
    # content, so it isn't pushed down by the badge sitting in the opposite
    # corner. Mirrored posters put the badge at the same left edge the
    # headline starts from, though, so there it still has to start below the
    # badge to avoid running straight through it.
    y = ribbon_h + 36
    if mirror and cfg.get("badge_text"):
        y = max(y, by1 + 24)
    # When the badge sits top-right (non-mirrored), the headline starts at
    # the same y as the badge -- keep its wrap width clear of the badge
    # horizontally too, or a wide first line can draw underneath/behind it
    # and go invisible where the two overlap.
    headline_w = W - 2 * PAD
    if cfg.get("badge_text") and not mirror:
        headline_w = min(headline_w, (W - 260) - PAD - 20)
    y = _headline(img, (PAD, y), cfg["headline_lines"], pal, headline_w, base_size=76)
    y += 10
    if cfg.get("tagline"):
        y = pe.draw_multiline(d, (PAD, y), cfg["tagline"], pe.font("lato-bold", 24), W - 2 * PAD, pal["text"])
        y += 8
    if cfg.get("badge_text"):
        y = max(y, by1 + 24)

    # hero photo (trimmed shorter than the standard-canvas version so
    # everything still fits comfortably within the 1350px-tall canvas)
    photo_h = 260
    hero = pe.load_photo(cfg.get("photos", {}).get("hero"), (W - 2 * PAD, photo_h), "HERO PHOTO", 0)
    photo = pe.rounded_photo(hero, (W - 2 * PAD, photo_h), 24)
    img.paste(photo, (PAD, y), photo)
    y += photo_h + 20

    # feature icon row (up to 4 short benefits)
    feats = cfg.get("benefits", [])[:4]
    ficons = cfg.get("benefits_icons", ["check", "briefcase", "dollar", "globe"])
    col_w = (W - 2 * PAD) // 2
    row_h = 74
    for i, feat in enumerate(feats):
        cx = PAD + (i % 2) * col_w
        cy = y + (i // 2) * row_h
        icon = ficons[i] if i < len(ficons) else "check"
        _feature_row(img, (cx, cy), col_w - 20, icon, feat, "", pal, icon_bg=pal["primary"])
    y += row_h * ((len(feats) + 1) // 2) + 10

    # two-column info boxes (order swaps when mirrored)
    box_w = (W - 2 * PAD - 30) // 2
    row_line_h = 44
    box_h = row_line_h * max(len(cfg.get("requirements", [])), len(cfg.get("benefits_extra", cfg.get("benefits", [])))) + 84
    box_h = max(box_h, 260)

    def _req_box(x0):
        d.rounded_rectangle([x0, y, x0 + box_w, y + box_h], radius=14, outline=pal["primary"], width=3)
        d.rectangle([x0, y, x0 + box_w, y + 54], fill=pal["primary"])
        d.text((x0 + 20, y + 12), "PROGRAM REQUIREMENTS", font=pe.font("poppins-bold", 22), fill=(255, 255, 255))
        ry = y + 70
        req_icons = cfg.get("requirements_icons", ["calendar", "graduation-cap", "passport", "language"])
        for i, req in enumerate(cfg.get("requirements", [])):
            icon = req_icons[i] if i < len(req_icons) else "check"
            _icon_badge(img, (x0 + 40, ry + 18), 40, pal["gold"], icon, 18, icon_color=pal["navy"])
            text_bottom = pe.draw_multiline(d, (x0 + 72, ry + 4), req, pe.font("lato-bold", 20), box_w - 92, pal["text"])
            ry = max(ry + row_line_h, text_bottom + 8)

    def _incl_box(x0):
        d.rounded_rectangle([x0, y, x0 + box_w, y + box_h], radius=14, outline=pal["primary"], width=3)
        d.rectangle([x0, y, x0 + box_w, y + 54], fill=pal["primary"])
        d.text((x0 + 20, y + 12), "WHAT'S INCLUDED", font=pe.font("poppins-bold", 22), fill=(255, 255, 255))
        ry = y + 70
        incl = cfg.get("benefits_extra", cfg.get("benefits", []))
        incl_icons = cfg.get("benefits_extra_icons", cfg.get("benefits_icons", ["check"] * len(incl)))
        for i, b in enumerate(incl):
            icon = incl_icons[i] if i < len(incl_icons) else "check"
            _icon_badge(img, (x0 + 40, ry + 18), 40, pal["gold"], icon, 18, icon_color=pal["navy"])
            text_bottom = pe.draw_multiline(d, (x0 + 72, ry + 4), b, pe.font("lato-bold", 20), box_w - 92, pal["text"])
            ry = max(ry + row_line_h, text_bottom + 8)

    x2 = PAD + box_w + 30
    if mirror:
        _incl_box(PAD)
        _req_box(x2)
    else:
        _req_box(PAD)
        _incl_box(x2)
    y += box_h + 16

    # bottom contact bar (fixed height, bottom-aligned)
    bar_h = 110
    y_bar = max(y + 14, H - bar_h)
    _contact_bar(img, y_bar, bar_h, cfg, pal, bg=pal["primary"])

    img = img.crop((0, 0, W, min(canvas_h, y_bar + bar_h)))
    img.save(out_path)
    return out_path


# ---------------------------------------------------------------- TEMPLATE B
def render_clean_split(cfg, out_path):
    pal = _pal(cfg)
    dark = cfg.get("dark_mode", False)
    bg_color = pal["primary_dark"] if dark else pal["bg"]
    panel_color = pe.lighten(pal["primary_dark"], 0.18) if dark else pal["panel"]
    text_color = (224, 224, 230) if dark else pal["text"]
    tagline_color = (195, 195, 202) if dark else (90, 90, 96)
    accent_fill = pal["primary"] if dark else pal["navy"]
    headline_pal = dict(pal, navy=(255, 255, 255), primary=pal["gold"]) if dark else pal
    img = Image.new("RGB", (W, H), bg_color)
    d = ImageDraw.Draw(img)

    mirror = cfg.get("mirror", False)
    y = PAD - 10
    if cfg.get("eyebrow"):
        fnt = pe.font("poppins-bold", 20)
        txt = cfg["eyebrow"]
        tw = d.textlength(txt, font=fnt)
        ex0 = W - PAD - (tw + 40) if mirror else PAD
        d.rounded_rectangle([ex0, y, ex0 + tw + 40, y + 44], radius=22, fill=pal["gold"])
        d.text((ex0 + 20, y + 10), txt, font=fnt, fill=(255, 255, 255))
    if cfg.get("badge_text"):
        bw, bh = 220, 90
        bx0, by0 = (PAD, y - 6) if mirror else (W - PAD - bw, y - 6)
        d.rounded_rectangle([bx0, by0, bx0 + bw, by0 + bh], radius=14, fill=accent_fill)
        pe.draw_multiline(d, (bx0 + 16, by0 + 18), cfg["badge_text"], pe.font("poppins-bold", 20),
                           bw - 32, pal["gold"], align="center")
    y += 56

    y = _headline(img, (PAD, y), cfg["headline_lines"], headline_pal, W - 2 * PAD, base_size=66)
    y += 6
    if cfg.get("tagline"):
        y = pe.draw_multiline(d, (PAD, y), cfg["tagline"], pe.font("lato-regular", 22), W - 2 * PAD, tagline_color)
        y += 20

    if cfg.get("discount_text"):
        fnt = pe.font("poppins-bold", 26)
        tw = d.textlength(cfg["discount_text"], font=fnt)
        pill_w = tw + 100
        d.rounded_rectangle([PAD, y, PAD + pill_w, y + 64], radius=32, fill=pal["gold"])
        _icon_badge(img, (PAD + 32, y + 32), 40, (255, 255, 255), "percent", 18, icon_color=pal["gold"])
        d.text((PAD + 60, y + 18), cfg["discount_text"], font=fnt, fill=(255, 255, 255))
        y += 84

    # hero photo
    photo_h = 400
    hero = pe.load_photo(cfg.get("photos", {}).get("hero"), (W - 2 * PAD, photo_h), "HERO PHOTO", 1)
    photo = pe.rounded_photo(hero, (W - 2 * PAD, photo_h), 24)
    pe.paste_with_shadow(img, photo, (PAD, y), 24, blur=16, opacity=60)
    y += photo_h + 36

    # requirements + benefits boxes (2x2 icon grid each)
    box_w = (W - 2 * PAD - 24) // 2
    reqs = cfg.get("requirements", [])[:4]
    bens = cfg.get("benefits", [])[:4]
    req_icons = cfg.get("requirements_icons", ["calendar", "graduation-cap", "passport", "language"])
    ben_icons = cfg.get("benefits_icons", ["book", "briefcase", "check-circle", "globe"])
    box_h = 240

    box_border = pe.lighten(panel_color, 0.15) if dark else (225, 225, 230)
    title_color = (255, 255, 255) if dark else pal["navy"]

    def info_box(x0, title, items, icons):
        d.rounded_rectangle([x0, y, x0 + box_w, y + box_h], radius=16, fill=panel_color,
                             outline=box_border, width=2)
        d.text((x0 + 22, y + 18), title, font=pe.font("poppins-bold", 20), fill=title_color)
        iy = y + 62
        for i, item in enumerate(items):
            ic = icons[i] if i < len(icons) else "check"
            _icon_badge(img, (x0 + 40, iy + 15), 32, accent_fill, ic, 14)
            text_bottom = pe.draw_multiline(d, (x0 + 64, iy + 4), item, pe.font("lato-semibold", 17), box_w - 84, text_color)
            iy = max(iy + 42, text_bottom + 12)

    if mirror:
        info_box(PAD, "BENEFITS", bens, ben_icons)
        info_box(PAD + box_w + 24, "REQUIREMENTS", reqs, req_icons)
    else:
        info_box(PAD, "REQUIREMENTS", reqs, req_icons)
        info_box(PAD + box_w + 24, "BENEFITS", bens, ben_icons)
    y += box_h + 30

    # bottom bar: CTA left (colored) + contact right (light)
    bar_h = 100
    img = img.crop((0, 0, W, y + bar_h))
    d = ImageDraw.Draw(img)
    d.rectangle([0, y, W, y + bar_h], fill=accent_fill)
    if cfg.get("cta"):
        d.text((PAD, y + 28), cfg["cta"], font=pe.font("poppins-bold", 26), fill=pal["gold"])
    cx = W - PAD
    contacts = cfg.get("contact_lines", [])
    total_w = 0
    fnt_c = pe.font("lato-bold", 26)
    for c in contacts:
        total_w += 46 + d.textlength(c["text"], font=fnt_c) + 30
    cx = W - PAD - total_w
    for c in contacts:
        _icon_badge(img, (cx + 18, y + bar_h / 2), 40, pal["gold"], c["icon"], 18, icon_color=pal["navy"])
        d.text((cx + 44, y + bar_h / 2 - 15), c["text"], font=fnt_c, fill=(255, 255, 255))
        cx += 46 + d.textlength(c["text"], font=fnt_c) + 30

    img.save(out_path)
    return out_path


# ---------------------------------------------------------------- TEMPLATE C
def render_elegant_pills(cfg, out_path):
    pal = _pal(cfg)
    img = Image.new("RGB", (W, H), pal["bg"])
    d = ImageDraw.Draw(img)

    border = 22
    d.rounded_rectangle([border, border, W - border, H - border], radius=28, outline=pal["gold"], width=4)

    inner_pad = border + 44
    mirror = cfg.get("mirror", False)

    text_w = int((W - 2 * inner_pad) * 0.5)
    photo_w = W - inner_pad - (inner_pad + text_w + 30)
    photo_x = inner_pad + text_w + 30 if not mirror else inner_pad
    text_x = inner_pad if not mirror else inner_pad + photo_w + 30

    inner_pad_eff = text_x
    y = inner_pad
    if cfg.get("eyebrow"):
        fnt = pe.font("poppins-bold", 20)
        tw = d.textlength(cfg["eyebrow"], font=fnt)
        d.rounded_rectangle([inner_pad_eff, y, inner_pad_eff + tw + 36, y + 42], radius=21, fill=pal["navy"])
        d.text((inner_pad_eff + 18, y + 9), cfg["eyebrow"], font=fnt, fill=pal["gold"])
        y += 62

    headline_w = text_w
    y = _headline(img, (inner_pad_eff, y), cfg["headline_lines"], pal, headline_w, base_size=52)
    y += 6
    if cfg.get("tagline"):
        y = pe.draw_multiline(d, (inner_pad_eff, y), cfg["tagline"], pe.font("lato-bold", 20), headline_w,
                               pal["navy"])
        y += 26

    # text column: benefit pills (compute geometry first so the single photo
    # on the right can be sized to match this column's full height)
    top_y = inner_pad + (60 if cfg.get("eyebrow") else 0)
    pill_y = max(y, top_y)
    bens = cfg.get("benefits", [])
    ben_icons = cfg.get("benefits_icons", ["check"] * len(bens))
    pill_h = 62
    pill_gap = 16
    text_bottom = pill_y + len(bens) * (pill_h + pill_gap) - pill_gap if bens else pill_y

    # two photos stacked in the right column, each filling half of the
    # column's full height (which matches the text column's height) and the
    # column's full width -- big, roughly equal-sized photos rather than a
    # single hero or small circular thumbnails
    photos_cfg = cfg.get("photos", {})
    right_x = photo_x
    right_w = photo_w
    total_h = max(text_bottom - top_y, 200)
    photo_gap = 16
    half_h = int((total_h - photo_gap) / 2)

    secondary = photos_cfg.get("secondary", [])
    photo_paths = [photos_cfg.get("hero"), secondary[0] if secondary else None]
    py = top_y
    for i, path in enumerate(photo_paths):
        ph = pe.load_photo(path, (right_w, half_h), "PHOTO", 2 + i)
        ph_img = pe.rounded_photo(ph, (right_w, half_h), 22)
        pe.paste_with_shadow(img, ph_img, (right_x, py), 22, blur=15, opacity=50)
        py += half_h + photo_gap

    for i, b in enumerate(bens):
        icon = ben_icons[i] if i < len(ben_icons) else "check"
        py = pill_y + i * (pill_h + pill_gap)
        d.rounded_rectangle([inner_pad_eff, py, inner_pad_eff + headline_w, py + pill_h], radius=pill_h // 2,
                             fill=pal["navy"])
        _icon_badge(img, (inner_pad_eff + pill_h / 2, py + pill_h / 2), pill_h - 16, pal["gold"], icon, 20,
                    icon_color=pal["navy"])
        d.text((inner_pad_eff + pill_h + 6, py + pill_h / 2 - 13), b, font=pe.font("poppins-medium", 22),
                fill=(255, 255, 255))
    content_bottom = max(pill_y + len(bens) * (pill_h + pill_gap), top_y + total_h)

    # bottom contact bar (directly follows content, then crop canvas to fit)
    bar_h = 110
    bar_y = content_bottom + 40
    img = img.crop((0, 0, W, bar_y + bar_h + border))
    d = ImageDraw.Draw(img)
    d.rectangle([border, bar_y, W - border, bar_y + bar_h], fill=pal["navy"])
    # redraw border on the (now shorter) canvas so the frame still closes at the bottom
    d.rounded_rectangle([border, border, W - border, bar_y + bar_h + border - 1], radius=28,
                         outline=pal["gold"], width=4)
    d.rectangle([border, bar_y, W - border, bar_y + bar_h], fill=pal["navy"])
    contacts = cfg.get("contact_lines", [])
    if contacts:
        c = contacts[0]
        _icon_badge(img, (inner_pad + 26, bar_y + bar_h / 2), 52, pal["gold"], c["icon"], 24, icon_color=pal["navy"])
        label = cfg.get("contact_label", "FOR MORE INFORMATION, WHATSAPP ME AT:")
        d.text((inner_pad + 66, bar_y + 20), label, font=pe.font("lato-regular", 16), fill=(230, 230, 235))
        d.text((inner_pad + 66, bar_y + 42), c["text"], font=pe.font("poppins-bold", 30), fill=(255, 255, 255))

    img.save(out_path)
    return out_path


# ---------------------------------------------------------------- TEMPLATE D
def render_torn_paper(cfg, out_path):
    pal = _pal(cfg)
    canvas_h = H + 200
    img = Image.new("RGB", (W, canvas_h), pal["bg"])
    d = ImageDraw.Draw(img)

    # hero photo with torn bottom edge
    hero_h = 480
    hero = pe.load_photo(cfg.get("photos", {}).get("hero"), (W, hero_h), "SKYLINE PHOTO", 0)
    torn = pe.torn_photo(hero, (W, hero_h), edge="bottom", amplitude=18, seed=7)
    img.paste(torn, (0, 0), torn)

    # decorative chevrons + dots over the photo
    pe.chevrons(d, (36, 46), 4, 13, 22, (255, 255, 255), direction="right", width=6)
    pe.dot_row(d, (W - 150, 46), 3, 10, 40, (255, 255, 255))

    y0 = hero_h - 6
    mirror = cfg.get("mirror", False)

    # Two even-width columns fill the remaining canvas: a stacked-photo column
    # and a copy column (headline / tagline / "what you get" list). Both are
    # sized to match each other's height -- the copy column's natural content
    # height is measured first (headline + tagline wrap dynamically), then the
    # two stacked photos are scaled to fill that exact same height, so neither
    # side is left with empty space below its content.
    gap_cols = 44
    col_w = (W - 2 * PAD - gap_cols) // 2
    photo_x = PAD + col_w + gap_cols if mirror else PAD
    text_x = PAD if mirror else PAD + col_w + gap_cols
    top_y = y0 + 30
    insets_gap = 28

    fnt_head = pe.font("poppins-bold", 40)
    fnt_ben = pe.font("lato-semibold", 30)
    ben_row_h = 58
    heading_gap = 64

    # --- measurement pass: figure out how tall the copy column wants to be,
    # without touching the real canvas, so the photo column can match it.
    scratch = Image.new("RGB", (W, H))
    scratch_d = ImageDraw.Draw(scratch)
    my = _headline(scratch, (text_x, top_y), cfg["headline_lines"], pal, col_w, base_size=88,
                    font_name="poppins-bold", line_gap=0)
    if cfg.get("tagline"):
        my = pe.draw_multiline(scratch_d, (text_x, my + 10), cfg["tagline"], pe.font("lato-bold", 28), col_w, pal["text"])
    if cfg.get("benefits_heading", "WHAT YOU GET"):
        my += heading_gap
        my += 50  # heading line height
    my += sum(ben_row_h for _ in cfg.get("benefits", []))
    content_h = max(my - top_y, 360)

    inset1_h = int((content_h - insets_gap) * 0.52)
    inset2_h = content_h - insets_gap - inset1_h

    inset1 = pe.load_photo(cfg.get("photos", {}).get("secondary", [None, None])[0] if cfg.get("photos", {}).get("secondary") else None,
                            (col_w, inset1_h), "PHOTO", 1)
    inset1_t = pe.torn_photo(inset1, (col_w, inset1_h), edge="bottom", amplitude=12, seed=3)
    pe.paste_with_shadow(img, inset1_t, (photo_x, top_y), 4, blur=10, opacity=50)

    inset2 = pe.load_photo(cfg.get("photos", {}).get("secondary", [None, None])[1] if len(cfg.get("photos", {}).get("secondary", [])) > 1 else None,
                            (col_w, inset2_h), "PHOTO", 2)
    inset2_t = pe.torn_photo(inset2, (col_w, inset2_h), edge="top", amplitude=12, seed=4)
    inset2_y = top_y + inset1_h + insets_gap
    pe.paste_with_shadow(img, inset2_t, (photo_x, inset2_y), 4, blur=10, opacity=50)

    if cfg.get("discount_text"):
        bw, bh = 150, 110
        # small badge overlapping the seam between the two stacked photos
        bx0 = photo_x + col_w - bw - 20
        by0 = top_y + inset1_h - bh // 2 + insets_gap // 2
        d.rounded_rectangle([bx0, by0, bx0 + bw, by0 + bh], radius=14, fill=pal["navy"])
        parts = cfg["discount_text"].split()
        big = parts[0]
        rest = " ".join(parts[1:]) or "OFF"
        fnt_big = pe.font("poppins-bold", 34)
        tw = d.textlength(big, font=fnt_big)
        d.text((bx0 + (bw - tw) / 2, by0 + 14), big, font=fnt_big, fill=(255, 255, 255))
        fnt_rest = pe.font("lato-bold", 22)
        tw2 = d.textlength(rest, font=fnt_rest)
        d.text((bx0 + (bw - tw2) / 2, by0 + 60), rest, font=fnt_rest, fill=pal["gold"])

    # --- real copy column, drawn to the same measurements as the dry run
    ry = _headline(img, (text_x, top_y), cfg["headline_lines"], pal, col_w, base_size=88,
                    font_name="poppins-bold", line_gap=0)
    if cfg.get("tagline"):
        ry = pe.draw_multiline(d, (text_x, ry + 10), cfg["tagline"], pe.font("lato-bold", 28), col_w, pal["text"])

    if cfg.get("benefits_heading", "WHAT YOU GET"):
        ry += heading_gap
        d.text((text_x, ry), cfg.get("benefits_heading", "WHAT YOU GET"), font=fnt_head, fill=pal["primary"])
        ry += 50
    for b in cfg.get("benefits", []):
        fnt_ic = pe.font("icons", 26)
        d.text((text_x, ry), pe.icon_char("check"), font=fnt_ic, fill=pal["gold"])
        pe.draw_multiline(d, (text_x + 42, ry - 2), b, fnt_ben, col_w - 42, pal["text"])
        ry += ben_row_h

    content_bottom = max(top_y + content_h, inset2_y + inset2_h)
    y = content_bottom + 34
    contact_y = y
    pe.dot_row(d, (PAD + 20, contact_y + 22), 3, 10, 34, pal["navy"])
    contacts = cfg.get("contact_lines", [])
    cx = PAD + 150
    for c in contacts:
        _icon_badge(img, (cx + 26, contact_y + 22), 52, pal["navy"], c["icon"], 24)
        d.text((cx + 62, contact_y + 4), c["text"], font=pe.font("poppins-bold", 34), fill=pal["primary"])
        cx += 62 + d.textlength(c["text"], font=pe.font("poppins-bold", 34)) + 50
    pe.chevrons(d, (W - 60, contact_y + 22), 4, 13, 22, pal["navy"], direction="left", width=6)

    content_bottom = contact_y + 70
    img = img.crop((0, 0, W, min(canvas_h, content_bottom + 20)))
    img.save(out_path)
    return out_path


# ---------------------------------------------------------------- TEMPLATE E
def render_photo_overlay(cfg, out_path):
    """A large, completely clean hero photo on top (no text, no scrim -- just
    the photo) with all copy living in a solid color panel underneath it."""
    pal = _pal(cfg)
    pal_text = dict(pal)
    pal_text["primary"] = (255, 255, 255)
    pal_text["navy"] = (255, 255, 255)

    # Photo is a smaller top strip -- the solid-color copy panel underneath
    # is the dominant "half" of the poster, with larger type and roomier
    # spacing throughout so it reads as generously sized, not just relatively
    # bigger because the photo shrank.
    photo_h = int(H * 0.34)
    hero = pe.load_photo(cfg.get("photos", {}).get("hero"), (W, photo_h), "HERO PHOTO", 0)
    # cover (crop-to-fill), zoomed in rather than letterboxed -- but anchored
    # so an important subject near the top of the source photo (a statue's
    # head, a building's roofline) doesn't get sliced off by the crop. Default
    # anchor is centered; set photos.hero_anchor_y closer to 0 in the config
    # to keep more of the top of a tall photo in frame.
    anchor_y = cfg.get("photos", {}).get("hero_anchor_y", 0.5)
    photo = pe.cover_resize(hero, W, photo_h, anchor_y=anchor_y)

    canvas_h = H + 200
    img = Image.new("RGB", (W, canvas_h), pal["primary_dark"])
    img.paste(photo, (0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, photo_h, W, photo_h + 6], fill=pal["gold"])  # seam accent, not on the photo

    y = photo_h + 60
    row_started = False
    if cfg.get("eyebrow"):
        fnt = pe.font("poppins-bold", 20)
        tw = d.textlength(cfg["eyebrow"], font=fnt)
        d.rounded_rectangle([PAD, y, PAD + tw + 40, y + 50], radius=25, outline=pal["gold"], width=2)
        d.text((PAD + 20, y + 14), cfg["eyebrow"], font=fnt, fill=(255, 255, 255))
        row_started = True
    if cfg.get("discount_text"):
        fnt = pe.font("poppins-bold", 24)
        tw = d.textlength(cfg["discount_text"], font=fnt)
        bw = tw + 50
        bx0 = W - PAD - bw
        d.rounded_rectangle([bx0, y, bx0 + bw, y + 50], radius=25, fill=pal["gold"])
        d.text((bx0 + 25, y + 14), cfg["discount_text"], font=fnt, fill=(255, 255, 255))
        row_started = True
    if row_started:
        y += 78

    y = _headline(img, (PAD, y), cfg["headline_lines"], pal_text, W - 2 * PAD, base_size=76)
    y += 12
    if cfg.get("tagline"):
        y = pe.draw_multiline(d, (PAD, y), cfg["tagline"], pe.font("lato-regular", 34), W - 2 * PAD,
                               (225, 225, 232))
        y += 36
    y += 14

    # benefit chips, wrapped across rows -- width is predicted *before*
    # drawing so a chip that would overflow the right margin wraps to a new
    # row instead of drawing off the edge (including the very last chip)
    bens = cfg.get("benefits", [])[:6]
    ben_icons = cfg.get("benefits_icons", ["check"] * len(bens))
    cx, cy = PAD, y
    row_h = 0
    fnt_chip = pe.font("poppins-medium", 23)
    icon_size = 20
    for i, b in enumerate(bens):
        icon = ben_icons[i] if i < len(ben_icons) else "check"
        predicted_w = 22 + icon_size + 12 + d.textlength(b, font=fnt_chip) + 22
        if cx + predicted_w > W - PAD and cx > PAD:
            cx = PAD
            cy += row_h + 18
        w_chip, h_chip = pe.chip(d, img, (cx, cy), b, icon, pal, fill=(255, 255, 255, 235),
                                  text_color=pal["navy"], font_size=23, icon_size=icon_size)
        row_h = h_chip
        cx += w_chip + 18
    y = cy + row_h + 50

    # contact line
    contacts = cfg.get("contact_lines", [])
    cx = PAD
    for c in contacts:
        _icon_badge(img, (cx + 26, y + 26), 52, pal["gold"], c["icon"], 24, icon_color=(255, 255, 255))
        d.text((cx + 58, y + 8), c["text"], font=pe.font("poppins-bold", 32), fill=(255, 255, 255))
        cx += 58 + d.textlength(c["text"], font=pe.font("poppins-bold", 32)) + 46
    y += 90

    img = img.crop((0, 0, W, min(canvas_h, y)))
    img.save(out_path)
    return out_path


# ---------------------------------------------------------------- TEMPLATE G
def render_steps_timeline(cfg, out_path):
    pal = _pal(cfg)
    img = Image.new("RGB", (W, H), pal["bg"])
    d = ImageDraw.Draw(img)

    y = PAD - 10
    if cfg.get("eyebrow"):
        fnt = pe.font("poppins-bold", 20)
        tw = d.textlength(cfg["eyebrow"], font=fnt)
        d.rounded_rectangle([PAD, y, PAD + tw + 40, y + 44], radius=22, fill=pal["gold"])
        d.text((PAD + 20, y + 10), cfg["eyebrow"], font=fnt, fill=(255, 255, 255))
        y += 62

    y = _headline(img, (PAD, y), cfg["headline_lines"], pal, W - 2 * PAD, base_size=60)
    y += 6
    if cfg.get("tagline"):
        y = pe.draw_multiline(d, (PAD, y), cfg["tagline"], pe.font("lato-regular", 22), W - 2 * PAD, (90, 90, 96))
    y += 20

    # optional compact hero strip
    photos_cfg = cfg.get("photos", {})
    if photos_cfg.get("hero"):
        strip_h = 200
        hero = pe.load_photo(photos_cfg.get("hero"), (W - 2 * PAD, strip_h), "PHOTO", 6)
        photo = pe.rounded_photo(hero, (W - 2 * PAD, strip_h), 20)
        img.paste(photo, (PAD, y), photo)
        y += strip_h + 30
    else:
        y += 10

    # vertical numbered steps with connecting line -- optionally with a
    # photo running down the right side (photos.side), which narrows the
    # step column to make room
    steps = cfg.get("steps", [])
    circle_d = 64
    line_x = PAD + circle_d / 2
    step_top = y
    row_gap = 34
    side_photo_file = photos_cfg.get("side")
    if side_photo_file is not None:
        col_gap = 34
        side_w = int((W - 2 * PAD - col_gap) * 0.34)
        step_area_right = PAD + (W - 2 * PAD - col_gap) - side_w
    else:
        side_w = 0
        step_area_right = W - PAD
    text_wrap_w = step_area_right - (PAD + circle_d + 30)
    rows = []
    fnt_num = pe.font("poppins-bold", 26)
    fnt_title = pe.font("poppins-bold", 24)
    fnt_desc = pe.font("lato-regular", 19)
    for i, step in enumerate(steps):
        title = step.get("title", "")
        desc = step.get("description", "")
        desc_lines = pe.wrap_text(desc, fnt_desc, text_wrap_w, d) if desc else []
        row_h = max(circle_d, 34 + len(desc_lines) * 26)
        rows.append(row_h)

    # connecting line (from center of first circle to center of last circle)
    if rows:
        last_center_y = step_top + sum(rows[:-1]) + row_gap * (len(rows) - 1) + circle_d / 2
        d.line([(line_x, step_top + circle_d / 2), (line_x, last_center_y)], fill=pal["gold"], width=4)

    cy = step_top
    for i, step in enumerate(steps):
        row_h = rows[i]
        d.ellipse([PAD, cy, PAD + circle_d, cy + circle_d], fill=pal["primary"])
        num = str(i + 1)
        nw = d.textlength(num, font=fnt_num)
        d.text((PAD + circle_d / 2 - nw / 2, cy + circle_d / 2 - 17), num, font=fnt_num, fill=(255, 255, 255))
        tx = PAD + circle_d + 30
        d.text((tx, cy + 2), step.get("title", ""), font=fnt_title, fill=pal["text"])
        desc = step.get("description", "")
        if desc:
            pe.draw_multiline(d, (tx, cy + 36), desc, fnt_desc, text_wrap_w, (100, 100, 108))
        cy += row_h + row_gap
    y = cy - row_gap + 30

    if side_photo_file is not None:
        side_h = max(200, (cy - row_gap) - step_top)
        side_x = step_area_right + col_gap
        hero_side = pe.load_photo(side_photo_file, (side_w, int(side_h)), "PHOTO", 7)
        photo_side = pe.rounded_photo(hero_side, (side_w, int(side_h)), 20)
        img.paste(photo_side, (side_x, step_top), photo_side)
        y = max(y, step_top + side_h + 30)

    # bottom contact bar
    bar_h = 110
    img = img.crop((0, 0, W, y + bar_h))
    d = ImageDraw.Draw(img)
    d.rectangle([0, y, W, y + bar_h], fill=pal["primary"])
    if cfg.get("cta"):
        d.text((PAD, y + 22), cfg["cta"], font=pe.font("poppins-bold", 24), fill=pal["gold"])
    contacts = cfg.get("contact_lines", [])
    fnt_c = pe.font("lato-bold", 26)
    total_w = sum(46 + d.textlength(c["text"], font=fnt_c) + 30 for c in contacts)
    cx = W - PAD - total_w
    for c in contacts:
        _icon_badge(img, (cx + 18, y + bar_h / 2), 40, pal["gold"], c["icon"], 18, icon_color=pal["navy"])
        d.text((cx + 44, y + bar_h / 2 - 15), c["text"], font=fnt_c, fill=(255, 255, 255))
        cx += 46 + d.textlength(c["text"], font=fnt_c) + 30

    img.save(out_path)
    return out_path


# ---------------------------------------------------------------- TEMPLATE: gradient_highlights
def render_gradient_highlights(cfg, out_path):
    """Diagonal-gradient poster with a rotating circular badge and a full-width
    'highlights' card of pill-style benefit rows (arrow bullets, no icons needed).
    No photo slot -- background + card carry the whole design."""
    pal = _pal(cfg)
    # a 3-stop gradient (accent -> primary -> deep primary) reads much more
    # colourful than fading one color to a darker version of itself, while
    # avoiding the muddy midtone a direct gold-to-navy blend produces
    dark = pal.get("primary_dark", pal["navy"])
    stops = [pe.lighten(pal["gold"], 0.15), pal["primary"], dark]
    canvas_h = H + 250
    bg = pe.diagonal_gradient_multi((W, canvas_h), stops)
    img = bg.convert("RGB")
    d = ImageDraw.Draw(img)

    mirror = cfg.get("mirror", False)

    y = PAD
    # brand name top-right (or top-left when mirrored)
    brand = cfg.get("brand_name", "")
    if brand:
        fnt_b = pe.font("poppins-bold", 26)
        bw = d.textlength(brand, font=fnt_b)
        bx = PAD if mirror else W - PAD - bw
        d.text((bx, y), brand, font=fnt_b, fill=(255, 255, 255))
    y += 60

    # headline (forced white regardless of per-line color, for legibility on gradient)
    headline_w = int((W - 2 * PAD) * 0.62)
    fnt_h = pe.font("poppins-bold", 66)
    widest = max((d.textlength(l["text"], font=fnt_h) for l in cfg["headline_lines"]), default=0)
    size = 66
    while widest > headline_w and size > 28:
        size -= 2
        fnt_h = pe.font("poppins-bold", size)
        widest = max(d.textlength(l["text"], font=fnt_h) for l in cfg["headline_lines"])
    asc, desc = fnt_h.getmetrics()
    hx = W - PAD - headline_w if mirror else PAD
    hy = y
    for l in cfg["headline_lines"]:
        d.text((hx, hy), l["text"], font=fnt_h, fill=(255, 255, 255))
        hy += asc + desc + 4
    y = hy + 8

    # tagline paragraph
    if cfg.get("tagline"):
        y = pe.draw_multiline(d, (hx, y), cfg["tagline"], pe.font("lato-regular", 22),
                               headline_w, (235, 240, 245))
        y += 10

    # rotating circular badge, top-right area (top-left if mirrored)
    badge_text = cfg.get("badge_circle_text", "")
    if badge_text:
        bd_size = 240
        bx = PAD if mirror else W - PAD - bd_size
        by = PAD + 56  # clear of the brand-name text above it
        _stamp_badge(img, (bx + bd_size / 2, by + bd_size / 2), bd_size, badge_text,
                     ("poppins-bold", 27), (255, 255, 255), ring_color=(255, 255, 255))

    y = max(y, PAD + 56 + 240 + 20)

    # full-width highlights card: a photo on one side, "Program Highlights"
    # heading + pill list on the other (matches the original reference layout)
    card_x0, card_y0 = PAD, y
    card_w = W - 2 * PAD
    card_pad = 40
    photo_w = int(card_w * 0.34)
    col_gap = 30
    text_col_w = card_w - photo_w - col_gap - 2 * card_pad

    heading = cfg.get("section_heading", "Program Highlights")
    fnt_sec = pe.font("poppins-bold", 36)
    sec_lines = pe.wrap_text(heading, fnt_sec, text_col_w, d)
    sec_h = len(sec_lines) * 44

    bens = cfg.get("benefits", [])
    pill_h, pill_gap = 58, 14
    pills_h = len(bens) * (pill_h + pill_gap) - pill_gap if bens else 0
    text_content_h = sec_h + 22 + pills_h
    photo_content_h = 320
    card_h = max(text_content_h, photo_content_h) + 2 * card_pad

    card = Image.new("RGBA", (card_w, card_h), (255, 255, 255, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, card_w, card_h], radius=28, fill=(255, 255, 255, 235))

    if mirror:
        text_col_x = card_pad
        photo_x = card_w - card_pad - photo_w
    else:
        photo_x = card_pad
        text_col_x = card_pad + photo_w + col_gap

    # keep the photo box itself landscape-shaped (~1.4:1) rather than
    # stretching it to the card's full portrait-ish height -- most of Josh's
    # people photos are landscape, and squeezing a landscape photo into a
    # tall narrow box crops off its sides. Center the box vertically instead.
    available_h = card_h - 2 * card_pad
    photo_h = min(available_h, int(photo_w / 1.4))
    photo_y = card_pad + (available_h - photo_h) // 2
    hero = pe.load_photo(cfg.get("photos", {}).get("hero"), (photo_w, photo_h), "PHOTO", 4)
    photo_img = pe.rounded_photo(hero, (photo_w, photo_h), 20)
    card.alpha_composite(photo_img, (photo_x, photo_y))

    ty = card_pad
    for ln in sec_lines:
        cd.text((text_col_x, ty), ln, font=fnt_sec, fill=pal["navy"])
        ty += 44
    ty += 22
    fnt_pill = pe.font("poppins-medium", 21)
    for b in bens:
        pe.diagonal_arrow(cd, (text_col_x, ty + pill_h / 2 - 11), 20, pal["primary"], width=4)
        tw = cd.textlength(b, font=fnt_pill)
        px0 = text_col_x + 38
        max_pill_w = text_col_w - 38
        pill_w = min(tw + 40, max_pill_w)
        cd.rounded_rectangle([px0, ty, px0 + pill_w, ty + pill_h], radius=pill_h / 2,
                              fill=pal.get("panel", (246, 247, 249)))
        cd.text((px0 + 20, ty + pill_h / 2 - 13), b, font=fnt_pill, fill=pal["text"])
        ty += pill_h + pill_gap

    pe.paste_with_shadow(img, card, (card_x0, card_y0), 28, blur=20, opacity=60)
    y = card_y0 + card_h + 50

    # footer: icon badge + tagline lines + contact, with a small decorative
    # network-dot cluster in the empty gradient space between them
    footer_lines = cfg.get("footer_tagline_lines", ["Start Your", "Singapore Journey"])
    fb_icon = 64
    fx = PAD
    fy = y + 10
    d.ellipse([fx, fy, fx + fb_icon, fy + fb_icon], outline=(255, 255, 255), width=3)
    ic = pe.icon_char(cfg.get("footer_icon", "graduation-cap"))
    fnt_ic = pe.font("icons", 30)
    ibbox = d.textbbox((0, 0), ic, font=fnt_ic)
    d.text((fx + fb_icon / 2 - (ibbox[2] - ibbox[0]) / 2 - ibbox[0],
             fy + fb_icon / 2 - (ibbox[3] - ibbox[1]) / 2 - ibbox[1]), ic, font=fnt_ic, fill=(255, 255, 255))
    fnt_foot = pe.font("poppins-bold", 26)
    tx = fx + fb_icon + 20
    fty = fy
    for ln in footer_lines:
        d.text((tx, fty), ln, font=fnt_foot, fill=(255, 255, 255))
        fty += 32
    footer_bottom = max(fy + fb_icon, fty)
    footer_text_right = tx + max((d.textlength(ln, font=fnt_foot) for ln in footer_lines), default=0)

    contact_left = W - PAD
    if cfg.get("contact_lines"):
        c = cfg["contact_lines"][0]
        fnt_c = pe.font("lato-bold", 24)
        ctext = c["text"]
        cw = d.textlength(ctext, font=fnt_c)
        cx = W - PAD - cw - 34
        contact_left = cx
        _icon_badge(img, (cx + 16, fy + fb_icon / 2), 32, (255, 255, 255), c.get("icon", "whatsapp"), 16,
                    icon_color=pal["navy"])
        d.text((cx + 34, fy + fb_icon / 2 - 14), ctext, font=fnt_c, fill=(255, 255, 255))

    gap_x0 = footer_text_right + 40
    gap_w = contact_left - 40 - gap_x0
    if gap_w > 80:
        pe.network_dots(d, (gap_x0, fy - 6), (gap_w, fb_icon + 12),
                         (255, 255, 255), count=10, seed=3, dot_r=2, max_line_dist=70)

    y = footer_bottom + 40
    img = img.crop((0, 0, W, y))
    img.save(out_path)
    return out_path


# ---------------------------------------------------------------- TEMPLATE: night_glow
def render_night_glow(cfg, out_path):
    """Dark glowing-gradient 'event card' poster (no photos) -- bold condensed
    headline, an outlined brand pill, a highlight card, and a two-column detail
    strip (description + requirements) framed with corner brackets."""
    pal = _pal(cfg)
    canvas_h = H + 120
    base = Image.new("RGB", (W, canvas_h), (12, 10, 18))
    glow1 = pe.radial_gradient((W, canvas_h), (int(W * 0.25), int(canvas_h * 0.05)),
                                pe.lighten(pal["primary"], 0.15), (12, 10, 18), radius=int(W * 0.95))
    base = Image.blend(base, glow1, 0.9)
    warm = pe.soft_blob((700, 700), pal["gold"] + (110,), blur=160)
    base = base.convert("RGBA")
    base.alpha_composite(warm, (int(W * 0.55), -180))
    accent_blob = pe.soft_blob((520, 520), pal["primary"] + (90,), blur=140)
    base.alpha_composite(accent_blob, (-160, int(canvas_h * 0.55)))
    img = base.convert("RGB")
    d = ImageDraw.Draw(img)

    mirror = cfg.get("mirror", False)
    y = PAD - 20

    fnt_h = pe.font("poppins-bold", 84)
    max_w = W - 2 * PAD
    widest = max((d.textlength(l["text"], font=fnt_h) for l in cfg["headline_lines"]), default=0)
    size = 84
    while widest > max_w and size > 34:
        size -= 2
        fnt_h = pe.font("poppins-bold", size)
        widest = max(d.textlength(l["text"], font=fnt_h) for l in cfg["headline_lines"])
    asc, desc = fnt_h.getmetrics()
    for l in cfg["headline_lines"]:
        d.text((PAD, y), l["text"], font=fnt_h, fill=(255, 255, 255))
        y += asc + desc + 2

    # subtitle + outlined brand pill, inline
    subtitle = cfg.get("subtitle", "")
    brand_pill = cfg.get("brand_pill_text", "")
    fnt_sub = pe.font("poppins-bold", 30)
    x = PAD
    if subtitle:
        d.text((x, y), subtitle, font=fnt_sub, fill=(255, 255, 255))
        x += d.textlength(subtitle, font=fnt_sub) + 24
    if brand_pill:
        fnt_bp = pe.font("poppins-bold", 23)
        bw = d.textlength(brand_pill, font=fnt_bp)
        d.rounded_rectangle([x, y - 6, x + bw + 44, y + 44], radius=22, outline=(255, 255, 255), width=2)
        d.text((x + 22, y + 4), brand_pill, font=fnt_bp, fill=(255, 255, 255))
    y += 74

    # hero photo strip
    photo_h = 300
    hero = pe.load_photo(cfg.get("photos", {}).get("hero"), (W - 2 * PAD, photo_h), "PHOTO", 5)
    photo_img = pe.rounded_photo(hero, (W - 2 * PAD, photo_h), 22)
    pe.paste_with_shadow(img, photo_img, (PAD, y), 22, blur=18, opacity=90)
    y += photo_h + 34

    # highlight/session card
    card_y0 = y
    card_w = W - 2 * PAD
    heading = cfg.get("session_heading", "JOIN THE PROGRAM")
    desc_text = cfg.get("session_description", "")
    fnt_ch = pe.font("poppins-bold", 39)
    fnt_cd = pe.font("lato-regular", 25)
    ch_lines = pe.wrap_text(heading, fnt_ch, card_w - 80, d)
    cd_lines = pe.wrap_text(desc_text, fnt_cd, card_w - 80, d) if desc_text else []
    card_h = 44 + len(ch_lines) * 48 + (18 if cd_lines else 0) + len(cd_lines) * 36 + 40

    card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    cdw = ImageDraw.Draw(card)
    cdw.rounded_rectangle([0, 0, card_w, card_h], radius=26, fill=(255, 255, 255, 28),
                           outline=(255, 255, 255, 90), width=2)
    ty = 40
    for ln in ch_lines:
        cdw.text((40, ty), ln, font=fnt_ch, fill=(255, 255, 255))
        ty += 48
    ty += 14
    for ln in cd_lines:
        cdw.text((40, ty), ln, font=fnt_cd, fill=(225, 225, 232))
        ty += 36
    img.paste(card, (PAD, card_y0), card)
    y = card_y0 + card_h + 46

    # thin divider
    d.line([(PAD, y), (W - PAD, y)], fill=(255, 255, 255, 140), width=2)
    y += 34

    # corner-bracket framed detail block: left description / right requirements
    block_y0 = y
    left_w = int((W - 2 * PAD) * 0.5) - 20
    right_x = PAD + left_w + 40
    right_w = (W - PAD) - right_x

    fnt_bd = pe.font("lato-regular", 25)
    bottom_desc = cfg.get("bottom_description", "")
    ly = block_y0
    if bottom_desc:
        ly = pe.draw_multiline(d, (PAD, ly), bottom_desc, fnt_bd, left_w, (225, 225, 232), line_spacing=1.4)

    reqs = cfg.get("requirements", [])
    req_icons = cfg.get("requirements_icons", ["check"] * len(reqs))
    fnt_req = pe.font("poppins-medium", 26)
    ry = block_y0
    for i, r in enumerate(reqs):
        icon = req_icons[i] if i < len(req_icons) else "check"
        _icon_badge(img, (right_x + 16, ry + 18), 36, pal["gold"], icon, 18, icon_color=(20, 16, 10))
        d.text((right_x + 44, ry + 6), r, font=fnt_req, fill=(255, 255, 255))
        ry += 50

    block_bottom = max(ly, ry) + 20
    pe.corner_brackets(d, (PAD - 14, block_y0 - 14), (W - 2 * PAD + 28, block_bottom - block_y0 + 28),
                        18, (255, 255, 255), width=3)
    y = block_bottom + 40

    # bottom contact row, pipe-separated -- each entry can optionally show a
    # small icon (e.g. a WhatsApp glyph) in front of its text
    contacts = cfg.get("contact_lines", [])
    if contacts:
        d.line([(PAD, y), (W - PAD, y)], fill=(255, 255, 255, 100), width=1)
        y += 26
        fnt_c = pe.font("lato-bold", 26)
        fnt_ic = pe.font("icons", 22)
        sep = "    |    "
        sep_w = d.textlength(sep, font=fnt_c)
        icon_gap = 10

        item_widths = []
        for c in contacts:
            w = d.textlength(c["text"], font=fnt_c)
            if c.get("icon"):
                w += 22 + icon_gap
            item_widths.append(w)
        total_w = sum(item_widths) + sep_w * max(len(contacts) - 1, 0)

        cx = W / 2 - total_w / 2
        cy_text = y
        cy_icon = y + 11 - 10
        for i, c in enumerate(contacts):
            if c.get("icon"):
                _icon_badge(img, (cx + 11, y + 11), 26, (37, 211, 102), c["icon"], 14,
                            icon_color=(255, 255, 255))
                cx += 22 + icon_gap
            d.text((cx, cy_text), c["text"], font=fnt_c, fill=(230, 230, 236))
            cx += d.textlength(c["text"], font=fnt_c)
            if i < len(contacts) - 1:
                d.text((cx, cy_text), sep, font=fnt_c, fill=(230, 230, 236))
                cx += sep_w
        y += 40

    y += 20
    img = img.crop((0, 0, W, y))
    img.save(out_path)
    return out_path


# --------------------------------------------------------- shared helpers for
# the 4 "ticket/stamp" style templates added from Josh's reference designs
def _numbered_checklist(img, xy, w, items, pal, colored=True, numbered=False, font_size=25,
                         circle_d=40, row_gap=54, cols=2, col_gap=40, text_color=(20, 32, 46)):
    """A grid (default 2-col) of check/number-badge + label rows, cycling
    through the active palette's accent colors so each item's badge is a
    different color (matches the multicolor checklist look in the reference
    designs) without breaking when a non-default palette is chosen. Row
    height is computed per-row from how many lines each item's text actually
    wraps to (checked *before* drawing), so a long label never overlaps the
    row below it."""
    d = ImageDraw.Draw(img)
    x0, y0 = xy
    check_colors = _checklist_colors(pal)
    col_w = (w - col_gap * (cols - 1)) // cols
    fnt = pe.font("poppins-medium" if not numbered else "lato-bold", font_size)
    text_w = col_w - circle_d - 16
    asc, desc = fnt.getmetrics()
    line_h = int((asc + desc) * 1.2)
    rows = (len(items) + cols - 1) // cols
    cy = y0
    for row in range(rows):
        row_items = items[row * cols:row * cols + cols]
        n_lines = [len(pe.wrap_text(it, fnt, text_w, d)) for it in row_items]
        row_h = max(circle_d, max(n_lines) * line_h) if n_lines else circle_d
        for c, item in enumerate(row_items):
            i = row * cols + c
            cx = x0 + c * (col_w + col_gap)
            color = check_colors[i % len(check_colors)] if colored else check_colors[0]
            r = circle_d / 2
            badge_cy = cy + row_h / 2
            d.ellipse([cx, badge_cy - r, cx + circle_d, badge_cy + r], fill=color)
            if numbered:
                num = str(i + 1)
                fnt_n = pe.font("lato-bold", int(circle_d * 0.5))
                bbox = d.textbbox((0, 0), num, font=fnt_n)
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                d.text((cx + r - tw / 2 - bbox[0], badge_cy - th / 2 - bbox[1]), num, font=fnt_n, fill=(255, 255, 255))
            else:
                fnt_ic = pe.font("icons", int(circle_d * 0.5))
                ch = pe.icon_char("check")
                bbox = d.textbbox((0, 0), ch, font=fnt_ic)
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                d.text((cx + r - tw / 2 - bbox[0], badge_cy - th / 2 - bbox[1]), ch, font=fnt_ic, fill=(255, 255, 255))
            text_h = n_lines[c] * line_h
            pe.draw_multiline(d, (cx + circle_d + 16, badge_cy - text_h / 2), item, fnt, text_w, text_color)
        cy += row_h + 20
    return cy


def _stamp_badge(img, center, diameter, text, font_spec, text_color, ring_color=None, fill=None, rings=1):
    """A circular badge with 1-3 lines of text, vertically and horizontally
    centered inside the circle regardless of how many lines the text wraps
    to (computed up front, so text never overflows or overlaps itself).
    `font_spec` is either a (font_name, base_size) tuple -- in which case
    the font size auto-shrinks until every wrapped line fits inside the
    circle, so a single long word (e.g. "GUARANTEED", "SINGAPORE") can never
    poke out past the ring -- or a pre-built font object for callers that
    already know their text fits and don't need auto-shrink."""
    d = ImageDraw.Draw(img)
    cx, cy = center
    r = diameter / 2
    if fill:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    if ring_color:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ring_color, width=5)
        if rings > 1:
            d.ellipse([cx - r + 10, cy - r + 10, cx + r - 10, cy + r - 10], outline=ring_color, width=2)

    safe_w = diameter * 0.72
    if isinstance(font_spec, tuple):
        font_name, size = font_spec
        font_obj = pe.font(font_name, size)
        lines = pe.wrap_text(text, font_obj, safe_w, d)
        widest = max((d.textlength(ln, font=font_obj) for ln in lines), default=0)
        while widest > safe_w and size > 11:
            size -= 1
            font_obj = pe.font(font_name, size)
            lines = pe.wrap_text(text, font_obj, safe_w, d)
            widest = max((d.textlength(ln, font=font_obj) for ln in lines), default=0)
    else:
        font_obj = font_spec
        lines = pe.wrap_text(text, font_obj, safe_w, d)

    asc, desc = font_obj.getmetrics()
    line_h = int((asc + desc) * 1.08)
    total_h = len(lines) * line_h
    ty = cy - total_h / 2
    for ln in lines:
        tw = d.textlength(ln, font=font_obj)
        d.text((cx - tw / 2, ty), ln, font=font_obj, fill=text_color)
        ty += line_h


# ---------------------------------------------------------------- TEMPLATE J
def render_stamp_collage(cfg, out_path):
    """Dark diagonal-striped background, a red ribbon banner, big two-tone
    headline, a 3x2 grid of white postage-stamp-style photo cards (each with
    a caption label), a duration pill, a starburst 'no fees' sticker, a round
    'intake open' stamp, an included-benefits checklist, a bold footer
    banner, and a contact bar. Best for a punchy, souvenir-postcard look with
    up to 6 photos to show off. Needs `photos.gallery` (6 {"file","label"}
    items). Recommended palette: `teal_coral` or `green_gold`."""
    pal = _pal(cfg)
    # headline sits directly on the dark striped background (no card behind
    # it), so it needs its own high-contrast palette rather than the normal
    # primary/navy text colors, which are too close to the dark background.
    pal_text = dict(pal)
    pal_text["primary"] = (255, 255, 255)
    pal_text["navy"] = (255, 255, 255)
    bg = pal["primary_dark"]
    stripe_c = tuple(min(255, c + 14) for c in bg)
    canvas_h = H + 260
    img = pe.diagonal_stripes((W, canvas_h), bg, stripe_c, stripe_w=30, gap=60)
    d = ImageDraw.Draw(img)

    y = 18
    if cfg.get("ribbon_text"):
        pe.ribbon_banner(img, (-20, y - 10), cfg["ribbon_text"], pal["primary"], (255, 255, 255),
                          pe.font("poppins-bold", 24), angle=-4)
    y += 72

    y = _headline(img, (PAD, y), cfg["headline_lines"], pal_text, W - 2 * PAD, base_size=68,
                  font_name="poppins-bold", line_gap=4, align="center")
    y += 6

    if cfg.get("duration_text"):
        fnt_dur = pe.font("poppins-bold", 30)
        tw = d.textlength(cfg["duration_text"], font=fnt_dur)
        bw = tw + 60
        d.rounded_rectangle([W / 2 - bw / 2, y, W / 2 + bw / 2, y + 62], radius=31, fill=pal["gold"])
        d.text((W / 2 - tw / 2, y + 14), cfg["duration_text"], font=fnt_dur, fill=pal["primary_dark"])
        y += 74

    # main gallery panel (cream card behind the stamp grid)
    panel_x0, panel_y0 = PAD - 20, y
    panel_w = W - 2 * (PAD - 20)
    gallery = cfg.get("photos", {}).get("gallery", [])[:6]
    cols, rows = 3, 2
    g_gap = 18
    stamp_w = (panel_w - 60 - g_gap * (cols - 1)) // cols
    stamp_photo_h = int(stamp_w * 0.56)
    label_h = 38
    stamp_h = stamp_photo_h + label_h
    panel_h = 26 + rows * stamp_h + (rows - 1) * g_gap + 26
    d.rounded_rectangle([panel_x0, panel_y0, panel_x0 + panel_w, panel_y0 + panel_h],
                         radius=20, fill=(250, 248, 242), outline=pal["gold"], width=3)

    fnt_label = pe.font("poppins-bold", 18)
    gx0 = panel_x0 + 30
    gy0 = panel_y0 + 26
    for i in range(6):
        col, row = i % cols, i // cols
        gx = gx0 + col * (stamp_w + g_gap)
        gy = gy0 + row * (stamp_h + g_gap)
        item = gallery[i] if i < len(gallery) else {}
        item_label = item.get("label", "")
        # if this item has no label, let its photo fill the whole grid slot
        # (photo + would-be-label area) instead of leaving a blank gap under it
        item_photo_h = stamp_photo_h if item_label else stamp_h
        hero = pe.load_photo(item.get("file"), (stamp_w, item_photo_h), "PHOTO", i + 1)
        card = pe.stamp_frame(hero, (stamp_w, item_photo_h), border=14,
                               label=item_label.upper() if item_label else None,
                               font_obj=fnt_label,
                               label_color=pal["primary_dark"])
        img.paste(card, (gx, gy))
    y = panel_y0 + panel_h + 14

    # starburst 'no fees' sticker overlapping the panel's top-left corner
    if cfg.get("badge_text"):
        star_size = 190
        star = pe.starburst((star_size, star_size), pal["primary"])
        img.paste(star, (10, panel_y0 - star_size // 2 + 30), star)
        sd = ImageDraw.Draw(img)
        fnt_star = pe.font("poppins-bold", 22)
        pe.draw_multiline(sd, (10 + star_size // 2 - 60, panel_y0 - star_size // 2 + 30 + star_size // 2 - 34),
                           cfg["badge_text"], fnt_star, 120, (255, 255, 255), align="center")

    # circular 'intake open' stamp sitting fully above the panel's top-right
    # corner (not dipping down into the photo grid below it)
    if cfg.get("stamp_text"):
        stamp_d = 170
        cx = panel_x0 + panel_w - stamp_d // 2 - 6
        cy = panel_y0 - stamp_d // 2 - 14
        _stamp_badge(img, (cx, cy), stamp_d, cfg["stamp_text"], ("poppins-bold", 23),
                     (250, 248, 242), fill=pal["primary"])

    y += 20
    if cfg.get("benefits_heading"):
        fnt_bh = pe.font("poppins-bold", 26)
        tw = d.textlength(cfg["benefits_heading"], font=fnt_bh)
        bw = tw + 70
        d.rounded_rectangle([W / 2 - bw / 2, y, W / 2 + bw / 2, y + 56], radius=28, fill=pal["gold"])
        fnt_ic = pe.font("icons", 20)
        d.text((W / 2 - bw / 2 + 24, y + 16), pe.icon_char("plane"), font=fnt_ic, fill=pal["primary_dark"])
        d.text((W / 2 - tw / 2 + 14, y + 15), cfg["benefits_heading"], font=fnt_bh, fill=pal["primary_dark"])
        y += 68

    bens = cfg.get("benefits", [])[:4]
    y = _numbered_checklist(img, (PAD, y), W - 2 * PAD, bens, pal, colored=True, numbered=False,
                             font_size=25, row_gap=54, text_color=(255, 255, 255))
    y += 20

    if cfg.get("footer_banner_text"):
        d.rectangle([0, y, W, y + 56], fill=pal["primary"])
        fnt_fb = pe.font("poppins-bold", 24)
        tw = d.textlength(cfg["footer_banner_text"], font=fnt_fb)
        d.text((W / 2 - tw / 2, y + 13), cfg["footer_banner_text"], font=fnt_fb, fill=(255, 255, 255))
        y += 56

    contacts = cfg.get("contact_lines", [])
    if contacts:
        bar_h = 96
        d.rectangle([0, y, W, y + bar_h], fill=pal["primary_dark"])
        cta = cfg.get("cta", "CONTACT US TODAY!")
        fnt_cta = pe.font("poppins-bold", 28)
        tw = d.textlength(cta, font=fnt_cta)
        d.rounded_rectangle([PAD, y + 18, PAD + tw + 50, y + 78], radius=10, fill=pal["primary"])
        d.text((PAD + 25, y + 33), cta, font=fnt_cta, fill=(255, 255, 255))
        cx = PAD + tw + 100
        for c in contacts:
            _icon_badge(img, (cx + 28, y + 48), 56, (37, 211, 102), c.get("icon", "whatsapp"), 26)
            d.text((cx + 66, y + 31), c["text"], font=pe.font("poppins-bold", 28), fill=(255, 255, 255))
            cx += 66 + d.textlength(c["text"], font=pe.font("poppins-bold", 28)) + 40
        y += bar_h

    img = img.crop((0, 0, W, min(canvas_h, y + 10)))
    img.save(out_path)
    return out_path


# ---------------------------------------------------------------- TEMPLATE K
def render_magazine_split(cfg, out_path):
    """Cream editorial layout: a navy masthead bar (title + flag + subtitle),
    a big headline, a large hero photo left with a smaller photo + checklist
    stacked to its right, a 3-photo captioned row underneath, an outlined
    'limited slots' box with a round 'apply now' stamp, and a bottom contact
    bar. Best for a clean, newspaper/magazine-style layout. Needs
    `photos.hero`, `photos.secondary[0]`, and `photos.gallery` (3
    {"file","label"} items). Recommended palette: `navy_gold` or `red_navy`."""
    pal = _pal(cfg)
    dark = cfg.get("dark_mode", False)
    bg_color = pal["primary_dark"] if dark else (250, 248, 240)
    pal = dict(pal, bg=bg_color) if dark else pal
    frame_color = _dark_bg_border(pal, dark)
    mast_fill = pal["primary"] if dark else pal["navy"]
    cap_color = (200, 200, 205) if dark else (90, 90, 96)
    text_color = (224, 224, 230) if dark else pal["text"]
    headline_pal = dict(pal, navy=(255, 255, 255), primary=pal["gold"]) if dark else pal
    img = Image.new("RGB", (W, H + 300), bg_color)
    d = ImageDraw.Draw(img)

    # outer double-line frame
    d.rectangle([24, 24, W - 24, H + 300 - 24], outline=frame_color, width=2)
    d.rectangle([30, 30, W - 30, H + 300 - 30], outline=frame_color, width=1)

    # masthead
    mast_y0 = 40
    mast_h = 86
    d.rectangle([46, mast_y0, W - 46, mast_y0 + mast_h], fill=mast_fill)
    title = cfg.get("masthead_title", "THE SINGAPORE OPPORTUNITY")
    fnt_mast = pe.font("poppins-bold", 30)
    while d.textlength(title, font=fnt_mast) > W - 200 and fnt_mast.size > 18:
        fnt_mast = pe.font("poppins-bold", fnt_mast.size - 2)
    tw = d.textlength(title, font=fnt_mast)
    d.text((W / 2 - tw / 2, mast_y0 + 8), title, font=fnt_mast, fill=(255, 255, 255))
    sub = cfg.get("masthead_subtitle", "")
    if sub:
        fnt_subm = pe.font("poppins-medium", 30)
        tws = d.textlength(sub, font=fnt_subm)
        d.text((W / 2 - tws / 2, mast_y0 + mast_h - 38), sub, font=fnt_subm, fill=pal["gold"])
    # small Singapore flag chip top-right of masthead (red/white + crescent
    # + 5 stars, not just a plain red-over-white bar which reads as a
    # different country's flag)
    fw, fh = 46, 30
    fx, fy = W - 46 - fw - 14, mast_y0 + 14
    d.rectangle([fx, fy, fx + fw, fy + fh], fill=(255, 255, 255))
    d.rectangle([fx, fy, fx + fw, fy + fh / 2], fill=(200, 16, 46))
    moon_cx, moon_cy, moon_r = fx + 11, fy + fh / 4, 6
    d.ellipse([moon_cx - moon_r, moon_cy - moon_r, moon_cx + moon_r, moon_cy + moon_r], fill=(255, 255, 255))
    d.ellipse([moon_cx - moon_r + 2.5, moon_cy - moon_r, moon_cx + moon_r + 2.5, moon_cy + moon_r],
              fill=(200, 16, 46))
    for sx, sy in [(23, -3), (28, 1), (26, 6), (20, 6), (18, 1)]:
        d.ellipse([fx + sx, moon_cy + sy - 1, fx + sx + 2, moon_cy + sy + 1], fill=(255, 255, 255))
    y = mast_y0 + mast_h + 24

    y = _headline(img, (60, y), cfg["headline_lines"], headline_pal, W - 120, base_size=66,
                  font_name="poppins-bold", line_gap=2)
    if cfg.get("duration_text"):
        fnt_dur = pe.font("poppins-bold", 22)
        tw = d.textlength(cfg["duration_text"], font=fnt_dur)
        bw = tw + 40
        d.rounded_rectangle([60, y + 4, 60 + bw, y + 4 + 46], radius=23, fill=pal["gold"])
        d.text((60 + 20, y + 16), cfg["duration_text"], font=fnt_dur, fill=pal["primary_dark"])
    y += 58

    # left large photo / right small photo + checklist
    left_w = int((W - 120 - 30) * 0.58)
    right_x = 60 + left_w + 30
    right_w = (W - 60) - right_x
    row_top = y
    left_h = 350
    hero = pe.load_photo(cfg.get("photos", {}).get("hero"), (left_w, left_h), "PHOTO", 0)
    d.rectangle([60 - 4, row_top - 4, 60 + left_w + 4, row_top + left_h + 4], outline=frame_color, width=3)
    img.paste(pe.cover_resize(hero, left_w, left_h), (60, row_top))
    if cfg.get("hero_caption"):
        fnt_cap = pe.font("lato-regular", 18)
        d.text((60, row_top + left_h + 8), cfg["hero_caption"], font=fnt_cap, fill=cap_color)

    small_h = 150
    sec = cfg.get("photos", {}).get("secondary", [None])
    hero2 = pe.load_photo(sec[0] if sec else None, (right_w, small_h), "PHOTO", 1)
    d.rectangle([right_x - 3, row_top - 3, right_x + right_w + 3, row_top + small_h + 3],
                outline=frame_color, width=2)
    img.paste(pe.cover_resize(hero2, right_w, small_h), (right_x, row_top))

    cy = row_top + small_h + 18
    if cfg.get("benefits_heading"):
        fnt_bh = pe.font("poppins-bold", 22)
        tw = d.textlength(cfg["benefits_heading"], font=fnt_bh)
        bw = tw + 50
        d.rounded_rectangle([right_x, cy, right_x + bw, cy + 46], radius=23, fill=pal["primary"])
        fnt_ic = pe.font("icons", 18)
        d.text((right_x + 18, cy + 13), pe.icon_char("star"), font=fnt_ic, fill=(255, 255, 255))
        d.text((right_x + 44, cy + 12), cfg["benefits_heading"], font=fnt_bh, fill=(255, 255, 255))
        cy += 54
    bens = cfg.get("benefits", [])[:4]
    ben_icons = cfg.get("benefits_icons", ["check"] * len(bens))
    check_colors = _checklist_colors(pal)
    for i, b in enumerate(bens):
        icon = ben_icons[i] if i < len(ben_icons) else "check"
        color = check_colors[i % len(check_colors)]
        _icon_badge(img, (right_x + 17, cy + 15), 30, color, icon, 14)
        d.text((right_x + 42, cy + 4), b, font=pe.font("poppins-bold", 19), fill=text_color)
        cy += 38

    y = max(row_top + left_h + 40, cy + 20)

    # 3-photo captioned row
    gallery = cfg.get("photos", {}).get("gallery", [])[:3]
    gcols = 3
    ggap = 24
    gw = (W - 120 - ggap * (gcols - 1)) // gcols
    gh = 170
    any_label = any((gallery[i] if i < len(gallery) else {}).get("label") for i in range(3))
    lbl_h = 46 if any_label else 0
    photo_h_eff = gh + (0 if any_label else 46)
    for i in range(3):
        gx = 60 + i * (gw + ggap)
        item = gallery[i] if i < len(gallery) else {}
        hero_g = pe.load_photo(item.get("file"), (gw, photo_h_eff), "PHOTO", i + 2)
        d.rectangle([gx - 2, y - 2, gx + gw + 2, y + photo_h_eff + 2], outline=frame_color, width=2)
        img.paste(pe.cover_resize(hero_g, gw, photo_h_eff), (gx, y))
        label = item.get("label", "").upper()
        if label and any_label:
            d.rectangle([gx, y + gh, gx + gw, y + gh + lbl_h], fill=mast_fill)
            fnt_lbl = pe.font("poppins-bold", 16)
            lines = pe.wrap_text(label, fnt_lbl, gw - 16, d)
            ly = y + gh + lbl_h / 2 - (len(lines) * 20) / 2
            for ln in lines[:2]:
                lw = d.textlength(ln, font=fnt_lbl)
                d.text((gx + gw / 2 - lw / 2, ly), ln, font=fnt_lbl, fill=pal["gold"])
                ly += 20
    y += photo_h_eff + (lbl_h if any_label else 0) + 30

    # outlined 'limited slots' box with round apply stamp
    box_h = 130
    d.rounded_rectangle([60, y, W - 60, y + box_h], radius=12, outline=pal["gold"], width=2)
    if cfg.get("footer_banner_text"):
        fnt_l1 = pe.font("poppins-bold", 24)
        d.text((90, y + 22), cfg["footer_banner_text"], font=fnt_l1, fill=pal["gold"])
    if cfg.get("cta"):
        fnt_l2 = pe.font("poppins-bold", 26)
        d.text((90, y + 66), cfg["cta"], font=fnt_l2, fill=(255, 255, 255) if sum(pal["bg"]) < 400 else pal["navy"])
    stamp_d = 110
    scx, scy = W - 60 - 40 - stamp_d / 2, y + box_h / 2
    stamp_accent = pal["gold"] if dark else pal["primary"]
    _stamp_badge(img, (scx, scy), stamp_d, cfg.get("stamp_text", "APPLY NOW"), ("poppins-bold", 21),
                 stamp_accent, ring_color=stamp_accent)
    y += box_h + 30

    contacts = cfg.get("contact_lines", [])
    if contacts:
        bar_h = 110
        d.rectangle([24, y, W - 24, y + bar_h], fill=pal["primary"])
        cta2 = cfg.get("cta_short", "ENQUIRE TODAY!")
        fnt_cta = pe.font("poppins-bold", 26)
        tw = d.textlength(cta2, font=fnt_cta)
        d.rounded_rectangle([60, y + 25, 60 + tw + 46, y + 85], radius=10, fill=pal["primary_dark"] if pal["primary_dark"] != pal["primary"] else (0, 0, 0))
        d.text((60 + 23, y + 40), cta2, font=fnt_cta, fill=(255, 255, 255))
        cx = 60 + tw + 46 + 50
        for c in contacts:
            _icon_badge(img, (cx + 26, y + 55), 52, (37, 211, 102), c.get("icon", "whatsapp"), 24)
            d.text((cx + 56, y + 38), c["text"], font=pe.font("poppins-bold", 26), fill=(255, 255, 255))
            cx += 56 + d.textlength(c["text"], font=pe.font("poppins-bold", 26)) + 40
        y += bar_h

    img = img.crop((0, 0, W, min(H + 300, y + 30)))
    img.save(out_path)
    return out_path


# ---------------------------------------------------------------- TEMPLATE L
def render_luggage_tag(cfg, out_path):
    """Dark diagonal-striped background behind a cream 'luggage tag' shaped
    card (rounded card with a punched hole + strap at top). Inside: a red
    ribbon banner, a navy headline box, a big photo + 2 stacked photos, a
    starburst 'guaranteed' sticker, a duration pill, an included-benefits
    checklist with numbered multicolor circles, and a round 'intake open'
    badge. Finishes with a footer banner + contact bar outside the card. The
    card's height is measured from its actual content first, so it never
    leaves dead space or clips content off the bottom. Needs `photos.hero`
    and `photos.secondary` (2 stacked photos). Recommended palette:
    `navy_gold` or `red_navy`."""
    pal = _pal(cfg)
    card_x0 = 40
    card_w = W - 80
    inner_x = card_x0 + 50
    inner_w = card_w - 100
    photo_h_total = 300

    # --- measurement pass: figure out how tall the card's content actually
    # is (only the headline and checklist wrap dynamically -- everything
    # else below them is a fixed height), so the card can be sized exactly.
    scratch = Image.new("RGB", (W, H + 800))
    scratch_d = ImageDraw.Draw(scratch)
    my = _headline(scratch, (inner_x, 90), cfg["headline_lines"], pal, inner_w, base_size=52,
                   font_name="poppins-bold", line_gap=2)
    my += 50 + photo_h_total + 40  # divider gap + photo row
    if cfg.get("duration_text"):
        my += 80
    if cfg.get("benefits_heading"):
        my += 66
    bens = cfg.get("benefits", [])[:4]
    my = _numbered_checklist(scratch, (inner_x, my), inner_w, bens, pal, colored=True, numbered=True,
                              font_size=22, circle_d=36)
    content_bottom = my + 50  # bottom padding inside the card
    if cfg.get("stamp_text"):
        content_bottom += 60  # extra room so the round stamp badge doesn't crowd the edge
    # the scratch measurement started at the same y=90 offset the real card
    # content starts at (card_y0 + 90), so content_bottom already *is* the
    # card height needed from the card's own top edge.
    card_h = content_bottom

    canvas_h = 100 + card_h + 30 + 66 + 100 + 60  # card_y0 + card + gaps + footer + contact bar + margin
    bg = pal["primary_dark"]
    stripe_c = tuple(min(255, c + 16) for c in bg)
    img = pe.diagonal_stripes((W, canvas_h), bg, stripe_c, stripe_w=28, gap=56)
    d = ImageDraw.Draw(img)

    card_y0 = 100
    d.rounded_rectangle([card_x0, card_y0, card_x0 + card_w, card_y0 + card_h], radius=32,
                         fill=(250, 248, 240))

    # punched hole + strap loop, sitting on the card's top edge
    hx, hy = card_x0 + card_w / 2, card_y0
    d.ellipse([hx - 20, hy - 34, hx + 20, hy + 6], fill=bg)
    d.ellipse([hx - 11, hy - 25, hx + 11, hy - 3], fill=(250, 248, 240))

    if cfg.get("ribbon_text"):
        pe.ribbon_banner(img, (30, 24), cfg["ribbon_text"], pal["primary"], (255, 255, 255),
                          pe.font("poppins-bold", 20), angle=-3)

    y = card_y0 + 90
    y = _headline(img, (inner_x, y), cfg["headline_lines"], pal, inner_w, base_size=52,
                  font_name="poppins-bold", line_gap=2)
    y += 20
    d.line([(inner_x, y), (card_x0 + card_w - 50, y)], fill=pal["gold"], width=2)
    y += 30

    photo_left_w = int((inner_w - 24) * 0.6)
    photo_right_x = inner_x + photo_left_w + 24
    photo_right_w = (card_x0 + card_w - 50) - photo_right_x
    hero = pe.load_photo(cfg.get("photos", {}).get("hero"), (photo_left_w, photo_h_total), "PHOTO", 0)
    img.paste(pe.rounded_photo(hero, (photo_left_w, photo_h_total), 16), (inner_x, y))

    sec = cfg.get("photos", {}).get("secondary", [None, None])
    small_h = (photo_h_total - 16) // 2
    for i in range(2):
        p = pe.load_photo(sec[i] if i < len(sec) else None, (photo_right_w, small_h), "PHOTO", i + 1)
        img.paste(pe.rounded_photo(p, (photo_right_w, small_h), 14), (photo_right_x, y + i * (small_h + 16)))

    if cfg.get("badge_text"):
        # sits in the card's top-right corner (mostly above the card's own
        # top edge, mirroring the ribbon banner's top-left placement)
        # instead of overlapping the photo -- it used to sit on the hero
        # photo's bottom-left corner, covering part of the picture.
        star_size = 120
        star = pe.starburst((star_size, star_size), pal["primary"])
        sx = card_x0 + card_w - star_size + 25
        sy = card_y0 - star_size // 2 + 20
        img.paste(star, (sx, sy), star)
        fnt_star = pe.font("poppins-bold", 14)
        _stamp_badge(img, (sx + star_size // 2, sy + star_size // 2), int(star_size * 0.62),
                     cfg["badge_text"], fnt_star, (255, 255, 255))

    y += photo_h_total + 40

    if cfg.get("duration_text"):
        fnt_dur = pe.font("poppins-bold", 30)
        tw = d.textlength(cfg["duration_text"], font=fnt_dur)
        bw = tw + 50
        d.rounded_rectangle([W / 2 - bw / 2, y, W / 2 + bw / 2, y + 54], radius=27, fill=pal["gold"])
        d.text((W / 2 - tw / 2, y + 13), cfg["duration_text"], font=fnt_dur, fill=pal["primary_dark"])
        y += 80

    if cfg.get("benefits_heading"):
        fnt_bh = pe.font("poppins-bold", 28)
        tw = d.textlength(cfg["benefits_heading"], font=fnt_bh)
        bw = tw + 60
        d.rounded_rectangle([inner_x, y, inner_x + bw, y + 48], radius=24, fill=pal["primary"])
        fnt_ic = pe.font("icons", 18)
        d.text((inner_x + 18, y + 14), pe.icon_char("plane"), font=fnt_ic, fill=(255, 255, 255))
        d.text((inner_x + 42, y + 13), cfg["benefits_heading"], font=fnt_bh, fill=(255, 255, 255))
        y += 66

    y = _numbered_checklist(img, (inner_x, y), inner_w, bens, pal, colored=True, numbered=True,
                             font_size=22, circle_d=36)

    if cfg.get("stamp_text"):
        stamp_d = 130
        scx = card_x0 + card_w - 50 - stamp_d / 2
        scy = y + 30
        _stamp_badge(img, (scx, scy), stamp_d, cfg["stamp_text"], ("poppins-bold", 20),
                     (255, 255, 255), fill=pal["primary"])

    y = card_y0 + card_h + 30
    if cfg.get("footer_banner_text"):
        d.rectangle([0, y, W, y + 66], fill=pal["primary"])
        fnt_fb = pe.font("poppins-bold", 24)
        tw = d.textlength(cfg["footer_banner_text"], font=fnt_fb)
        d.text((W / 2 - tw / 2, y + 18), cfg["footer_banner_text"], font=fnt_fb, fill=(255, 255, 255))
        y += 66

    contacts = cfg.get("contact_lines", [])
    if contacts:
        bar_h = 100
        d.rectangle([0, y, W, y + bar_h], fill=pal["primary_dark"])
        cta = cfg.get("cta", "APPLY NOW!")
        fnt_cta = pe.font("poppins-bold", 26)
        tw = d.textlength(cta, font=fnt_cta)
        d.rounded_rectangle([PAD, y + 22, PAD + tw + 46, y + 78], radius=10, fill=pal["primary"])
        d.text((PAD + 23, y + 36), cta, font=fnt_cta, fill=(255, 255, 255))
        cx = PAD + tw + 46 + 40
        for c in contacts:
            _icon_badge(img, (cx + 24, y + 50), 48, (37, 211, 102), c.get("icon", "whatsapp"), 22)
            d.text((cx + 52, y + 36), c["text"], font=pe.font("poppins-bold", 24), fill=(255, 255, 255))
            cx += 52 + d.textlength(c["text"], font=pe.font("poppins-bold", 24)) + 36
        y += bar_h

    img = img.crop((0, 0, W, min(canvas_h, y + 10)))
    img.save(out_path)
    return out_path


# ---------------------------------------------------------------- TEMPLATE M
def render_certificate_award(cfg, out_path):
    """Cream 'personalized award/certificate' layout inside a double gold
    border frame: a red ribbon banner, 'THIS OPPORTUNITY IS AWARDED TO' +
    a large 'You', the headline, a starburst 'guaranteed' sticker, a row of
    4 arch-topped photos, a duration pill, a navy pill heading, a numbered
    multicolor checklist, a round 'intake open' stamp, and a closing contact
    line. Needs `photos.gallery` (4 {"file"} items, no labels needed).
    Recommended palette: `navy_gold` or `burgundy_cream`."""
    pal = _pal(cfg)
    canvas_h = H + 200
    img = Image.new("RGB", (W, canvas_h), pal["bg"])
    d = ImageDraw.Draw(img)

    fm = 26
    d.rounded_rectangle([fm, fm, W - fm, canvas_h - fm], radius=18, outline=pal["gold"], width=3)
    d.rounded_rectangle([fm + 10, fm + 10, W - fm - 10, canvas_h - fm - 10], radius=14, outline=pal["gold"], width=1)
    dot_r = 6
    for cx, cy in [(fm + 10, fm + 10), (W - fm - 10, fm + 10), (fm + 10, canvas_h - fm - 10), (W - fm - 10, canvas_h - fm - 10)]:
        d.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r], fill=pal["gold"])

    y = 50
    if cfg.get("ribbon_text"):
        fnt_rb = pe.font("poppins-bold", 20)
        tw = d.textlength(cfg["ribbon_text"], font=fnt_rb)
        bw = tw + 60
        d.rounded_rectangle([W / 2 - bw / 2, y, W / 2 + bw / 2, y + 42], radius=6, fill=pal["primary"])
        d.text((W / 2 - tw / 2, y + 10), cfg["ribbon_text"], font=fnt_rb, fill=(255, 255, 255))
    y += 80

    awarded_to = cfg.get("awarded_to_label", "THIS OPPORTUNITY IS AWARDED TO")
    fnt_awd = pe.font("poppins-medium", 21)
    tw = d.textlength(awarded_to, font=fnt_awd)
    d.text((W / 2 - tw / 2, y), awarded_to, font=fnt_awd, fill=(120, 108, 80))
    y += 34

    recipient = cfg.get("recipient_name", "You")
    fnt_rec = pe.font("poppins-light", 70)
    tw = d.textlength(recipient, font=fnt_rec)
    d.text((W / 2 - tw / 2, y), recipient, font=fnt_rec, fill=pal["gold"])
    y += 74
    d.line([(W / 2 - 140, y), (W / 2 + 140, y)], fill=(200, 190, 160), width=1)
    y += 30

    y = _headline(img, (fm + 60, y), cfg["headline_lines"], pal, W - 2 * (fm + 60), base_size=60,
                  font_name="poppins-bold", line_gap=2, align="center")
    y += 20

    if cfg.get("badge_text"):
        star_size = 210
        star_x = W - fm - star_size - 14
        star = pe.starburst((star_size, star_size), pal["primary"])
        img.paste(star, (star_x, 40), star)
        # dynamically shrink so long words (e.g. "GUARANTEED") never overflow
        # the star's readable inner area, however big the font starts out
        safe_w = int(star_size * 0.62)
        bsize = 22
        fnt_star = pe.font("poppins-bold", bsize)
        words = cfg["badge_text"].split()
        widest = max((d.textlength(wd, font=fnt_star) for wd in words), default=0)
        while widest > safe_w and bsize > 13:
            bsize -= 1
            fnt_star = pe.font("poppins-bold", bsize)
            widest = max(d.textlength(wd, font=fnt_star) for wd in words)
        pe.draw_multiline(d, (star_x + star_size // 2 - safe_w // 2, 40 + star_size // 2 - 30),
                           cfg["badge_text"], fnt_star, safe_w, (255, 255, 255), align="center")

    # "intake open now" stamp sits top-left, mirroring the starburst badge's
    # top-right position -- clear of the ribbon (centered) and every line
    # element below, instead of sitting low where it used to cross the
    # divider rule.
    if cfg.get("stamp_text"):
        stamp_d = 130
        scx, scy = fm + 34 + stamp_d / 2, 46 + stamp_d / 2
        _stamp_badge(img, (scx, scy), stamp_d, cfg["stamp_text"], ("poppins-bold", 19),
                     pal["primary"], ring_color=pal["primary"])

    gallery = cfg.get("photos", {}).get("gallery", [])[:4]
    gcols = 4
    ggap = 20
    gw = (W - 2 * (fm + 40) - ggap * (gcols - 1)) // gcols
    gh = int(gw * 1.35)
    gx0 = fm + 40
    arch_ratio = 0.5
    for i in range(4):
        gx = gx0 + i * (gw + ggap)
        item = gallery[i] if i < len(gallery) else {}
        hero = pe.load_photo(item.get("file"), (gw, gh), "PHOTO", i)
        arch = pe.arch_photo(hero, (gw, gh), arch_ratio=arch_ratio)
        img.paste(arch, (gx, y), arch)
        pe.arch_outline(d, (gx, y), (gw, gh), arch_ratio, pal["gold"], width=3)
    y += gh + 36

    if cfg.get("duration_text"):
        fnt_dur = pe.font("poppins-bold", 30)
        tw = d.textlength(cfg["duration_text"], font=fnt_dur)
        bw = tw + 50
        d.rounded_rectangle([W / 2 - bw / 2, y, W / 2 + bw / 2, y + 54], radius=27, fill=pal["gold"])
        d.text((W / 2 - tw / 2, y + 13), cfg["duration_text"], font=fnt_dur, fill=pal["primary_dark"])
        y += 78

    if cfg.get("benefits_heading"):
        fnt_bh = pe.font("poppins-bold", 28)
        fnt_ic = pe.font("icons", 18)
        tw = d.textlength(cfg["benefits_heading"], font=fnt_bh)
        icon_ch = pe.icon_char("star")
        iw = d.textlength(icon_ch, font=fnt_ic)
        gap, pad = 12, 30
        content_w = iw + gap + tw
        bw = content_w + 2 * pad
        bx0 = W / 2 - bw / 2
        d.rounded_rectangle([bx0, y, bx0 + bw, y + 50], radius=25, fill=pal["navy"])
        icon_x = bx0 + pad
        d.text((icon_x, y + 15), icon_ch, font=fnt_ic, fill=(255, 255, 255))
        d.text((icon_x + iw + gap, y + 14), cfg["benefits_heading"], font=fnt_bh, fill=(255, 255, 255))
        y += 74

    bens = cfg.get("benefits", [])[:4]
    y = _numbered_checklist(img, (gx0, y), W - 2 * gx0, bens, pal, colored=True, numbered=True,
                             font_size=27, circle_d=44, row_gap=58)
    y += 20

    d.line([(gx0, y + 40), (W - gx0, y + 40)], fill=(210, 200, 175), width=1)
    y += 66

    closing = cfg.get("closing_text", "MESSAGE ME TO CLAIM YOUR SLOT")
    fnt_close = pe.font("poppins-bold", 28)
    tw = d.textlength(closing, font=fnt_close)
    d.text((W / 2 - tw / 2, y), closing, font=fnt_close, fill=pal["navy"])
    y += 46

    contacts = cfg.get("contact_lines", [])
    if contacts:
        total_w = 0
        specs = []
        for c in contacts:
            fnt_c = pe.font("poppins-bold", 30)
            tw = d.textlength(c["text"], font=fnt_c)
            iw = 48 if c.get("icon") else 0
            specs.append((c, fnt_c, tw, iw))
            total_w += tw + iw + 40
        cx = max(gx0, W / 2 - total_w / 2)
        for c, fnt_c, tw, iw in specs:
            if c.get("icon"):
                _icon_badge(img, (cx + 20, y + 20), 40, (37, 211, 102), c["icon"], 18)
                cx += iw
            d.text((cx, y + 2), c["text"], font=fnt_c, fill=pal["navy"])
            cx += tw + 40
        y += 54

    img = img.crop((0, 0, W, min(canvas_h, y + 40)))
    img.save(out_path)
    return out_path


# ---------------------------------------------------------------- TEMPLATE N (neon_edge)
def render_neon_edge(cfg, out_path):
    """Dark poster with a giant glowing vertical headline running up the left
    edge (neon-sign look), a brand row, one big photo, a solid-color stat
    panel, a light closing-statement panel, and a dark contact footer.
    Sized to 1080x1350 (Instagram 4:5 feed post). Needs `photos.hero` and
    `edge_text` (the big vertical glow text). Does not support `mirror`."""
    pal = _pal(cfg)
    w, h = 1080, 1350
    bg_dark = (8, 8, 11)
    img = Image.new("RGB", (w, h), bg_dark)
    d = ImageDraw.Draw(img)

    strip_w = 210
    edge_text = cfg.get("edge_text", "STUDY IN SINGAPORE")
    glow = pe.glow_vertical_text(h - 80, edge_text, fill=(255, 255, 255),
                                  glow_color=pal["gold"] + (150,), glow_blur=14, max_size=118)
    img.paste(glow, (strip_w // 2 - glow.width // 2, (h - glow.height) // 2), glow)

    cx = strip_w + 40
    cw = w - cx - 40

    # brand row: small triangle "mountain" mark + brand name
    tri_y = 46
    d.polygon([(cx, tri_y + 34), (cx + 20, tri_y), (cx + 40, tri_y + 34)], outline=(255, 255, 255), width=4)
    d.polygon([(cx + 16, tri_y + 34), (cx + 32, tri_y + 10), (cx + 48, tri_y + 34)], outline=(255, 255, 255), width=4)
    brand = cfg.get("brand_name", "STUDY SINGAPORE")
    d.text((cx + 64, tri_y + 4), brand, font=pe.font("poppins-bold", 30), fill=(255, 255, 255))

    y = tri_y + 60
    photo_h = 640
    hero = pe.load_photo(cfg.get("photos", {}).get("hero"), (cw, photo_h), "HERO PHOTO", 0)
    photo = pe.rounded_photo(hero, (cw, photo_h), 4)
    img.paste(photo, (cx, y), photo)
    y += photo_h

    # colored stat panel
    panel_h = 180
    d.rectangle([cx, y, cx + cw, y + panel_h], fill=pal["primary"])
    duration = cfg.get("duration_text", "1 YEAR STUDENT PASS")
    fnt_dur = pe.font("poppins-bold", 56)
    dsize = 56
    while d.textlength(duration, font=fnt_dur) > cw - 60 and dsize > 28:
        dsize -= 2
        fnt_dur = pe.font("poppins-bold", dsize)
    d.text((cx + 30, y + 34), duration, font=fnt_dur, fill=(255, 255, 255))
    tagline = cfg.get("tagline", "on our study + paid internship program")
    pe.draw_multiline(d, (cx + 30, y + 34 + dsize + 18), tagline, pe.font("lato-regular", 24), cw - 60, (255, 255, 255))
    y += panel_h

    # light closing-statement panel
    panel2_h = 140
    d.rectangle([cx, y, cx + cw, y + panel2_h], fill=pal["bg"])
    closing = cfg.get("closing_text", "INTAKE CLOSES SOON!")
    fnt_close = pe.font("poppins-bold", 44)
    csize = 44
    while d.textlength(closing, font=fnt_close) > cw - 60 and csize > 24:
        csize -= 2
        fnt_close = pe.font("poppins-bold", csize)
    d.text((cx + 30, y + panel2_h / 2 - csize / 2), closing, font=fnt_close, fill=pal["primary"])
    y += panel2_h + 40

    # benefit chips fill the space between the panels and the footer
    benefits = cfg.get("benefits", [])[:3]
    bicons = cfg.get("benefits_icons", ["check"] * len(benefits))
    bx = cx
    for i, b in enumerate(benefits):
        icon = bicons[i] if i < len(bicons) else "check"
        bw, bh = pe.chip(d, img, (bx, y), b, icon, pal, font_size=20)
        bx += bw + 16

    # footer: lead-in text on the left, contact number right-aligned, same row
    y = h - 66
    d.text((PAD, y + 6), cfg.get("footer_line", "Book your spot now at"), font=pe.font("lato-regular", 22), fill=(210, 210, 210))
    contacts = cfg.get("contact_lines", [])
    specs = []
    total_w = 0
    for c in contacts:
        fnt_c = pe.font("poppins-bold", 30)
        tw = d.textlength(c["text"], font=fnt_c)
        iw = 46 if c.get("icon") else 0
        specs.append((c, fnt_c, tw, iw))
        total_w += tw + iw + 8
    cx2 = w - PAD - total_w
    for c, fnt_c, tw, iw in specs:
        if c.get("icon"):
            _icon_badge(img, (cx2 + 18, y + 16), 38, (37, 211, 102), c["icon"], 17)
            cx2 += iw
        d.text((cx2, y), c["text"], font=fnt_c, fill=(255, 255, 255))
        cx2 += tw + 8

    img.save(out_path)
    return out_path


# ---------------------------------------------------------------- TEMPLATE O (flat_pop)
def render_flat_pop(cfg, out_path):
    """Bold flat-color poster: vivid solid background, a white corner blob +
    black rounded 'sticker' badge, curved repeating brand text along the left
    edge, a big stat headline, one large photo, and a black closing bar.
    Sized to 1080x1350 (Instagram 4:5 feed post). Needs `photos.hero`. Does
    not support `mirror`."""
    pal = _pal(cfg)
    w, h = 1080, 1350
    bg = pal["gold"]
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)

    # white corner blob (clipped quarter-circle in the top-left)
    d.ellipse([-220, -220, 220, 220], fill=(255, 255, 255))

    # black rounded "sticker" badge overlapping the blob
    badge_text = cfg.get("badge_text", "LIMITED SEATS")
    bx0, by0, bx1, by1 = 40, 150, 340, 400
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=60, fill=(15, 15, 15))
    pe.draw_multiline(d, (bx0 + 30, by0 + 44), badge_text, pe.font("poppins-bold", 34),
                       bx1 - bx0 - 60, bg, align="left")

    # straight text inside a ringed circle badge, filling the gap under the
    # black sticker badge (was a curved/spiraling line bleeding off-canvas;
    # now a self-contained round badge like the skill's other stamp badges)
    stamp_text = cfg.get("stamp_text", cfg.get("curve_text", "SINGAPORE"))
    if stamp_text:
        sd = 160
        scx, scy = 40 + sd / 2, 410 + sd / 2
        _stamp_badge(img, (scx, scy), sd, stamp_text, ("poppins-bold", 28),
                     (15, 15, 15), ring_color=(15, 15, 15))

    # eyebrow + big stat headline + tagline, right side of the top section
    tx = 470
    tw_avail = w - tx - PAD
    eyebrow = cfg.get("eyebrow", "UP TO")
    d.text((tx, 60), eyebrow, font=pe.font("poppins-bold", 30), fill=(15, 15, 15))
    y = _headline(img, (tx, 100), cfg["headline_lines"], pal, tw_avail, base_size=88,
                  font_name="poppins-bold", line_gap=0)
    y += 14
    if cfg.get("tagline"):
        y = pe.draw_multiline(d, (tx, y), cfg["tagline"], pe.font("poppins-bold", 36), tw_avail, (15, 15, 15))

    # large photo
    photo_y = 600
    photo_h = h - photo_y - 220
    hero = pe.load_photo(cfg.get("photos", {}).get("hero"), (w, photo_h), "HERO PHOTO", 0)
    img.paste(pe.cover_resize(hero, w, photo_h), (0, photo_y))

    # bottom black closing bar
    bar_y = h - 220
    d.rectangle([0, bar_y, w, h], fill=(15, 15, 15))
    closing_lines = cfg.get("closing_lines", ["ONLY UNTIL", "INTAKE CLOSES!"])
    fnt_cl = pe.font("poppins-bold", 26)
    cy = bar_y + 30
    for line in closing_lines:
        d.text((PAD, cy), line, font=fnt_cl, fill=bg)
        cy += 34

    cta_text = cfg.get("cta", "Book your spot now at")
    d.text((360, bar_y + 40), cta_text, font=pe.font("lato-regular", 22), fill=(230, 230, 230))
    contacts = cfg.get("contact_lines", [])
    cy2 = bar_y + 70
    cx2 = 360
    for c in contacts:
        if c.get("icon"):
            _icon_badge(img, (cx2 + 22, cy2 + 20), 44, bg, c["icon"], 19, icon_color=(15, 15, 15))
            cx2 += 54
        fnt_c = pe.font("poppins-bold", 34)
        d.text((cx2, cy2), c["text"], font=fnt_c, fill=(255, 255, 255))
        cx2 += d.textlength(c["text"], font=fnt_c) + 30

    brand = cfg.get("brand_name", "STUDY SINGAPORE")
    d.polygon([(PAD, h - 40), (PAD + 16, h - 66), (PAD + 32, h - 40)], outline=bg, width=3)
    d.text((PAD + 44, h - 62), brand, font=pe.font("poppins-bold", 22), fill=bg)

    img.save(out_path)
    return out_path


# ---------------------------------------------------------------- TEMPLATE P (dark_chevron)
def render_dark_chevron(cfg, out_path):
    """Dark modern-corporate poster: near-black background, gold double-
    chevron accents (top-left, mirrored bottom-right), a photo in the upper
    right, a short two-line side heading + intro paragraph + a short bulleted
    list (`diploma_points`) on the left, plus-mark and dot-grid accents, a
    big two-tone closing headline below the photo, and a contact row. Sized
    to 1080x1350 (Instagram 4:5 feed post). Needs `photos.hero`; optionally
    add `photos.secondary[0]` to stack a second photo underneath the hero
    photo instead of one full-height photo. Does not support `mirror`."""
    pal = _pal(cfg)
    w, h = 1080, 1350
    bg = pe.darken(pal["primary_dark"], 0.35) if cfg.get("dark_mode", False) else pal["primary_dark"]
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)

    pe.chevrons(d, (50, 100), 2, 46, 66, pal["gold"], direction="right", width=14)

    brand = cfg.get("brand_name", "STUDY SINGAPORE")
    fnt_brand = pe.font("poppins-bold", 44)
    tw = d.textlength(brand, font=fnt_brand)
    d.text((w - PAD - tw, 56), brand, font=fnt_brand, fill=(255, 255, 255))

    # photo dimensions computed up front so the left column can fill down
    # to meet the photo's bottom edge
    photo_x = 400
    photo_w = w - photo_x - PAD
    photo_y = 190
    photo_h = 640
    photo_bottom = photo_y + photo_h

    # left column: 2-line side heading + short paragraph + plus marks + dot grid
    side_lines = cfg.get("side_heading", ["GROW YOUR", "CAREER"])
    fnt_side = pe.font("poppins-bold", 40)
    sy = 195
    for i, line in enumerate(side_lines):
        color = pal["gold"] if i == 0 else (255, 255, 255)
        d.text((PAD, sy), line, font=fnt_side, fill=color)
        sy += 54
    sy += 14
    if cfg.get("tagline"):
        sy = pe.draw_multiline(d, (PAD, sy), cfg["tagline"], pe.font("lato-regular", 24), 320, (210, 210, 214))
    sy += 22

    # short point-form list about the diploma (or whatever cfg supplies)
    diploma_points = cfg.get("diploma_points", [
        "Practical, industry-aligned coursework",
        "Small class sizes with hands-on instructors",
        "Real workplace projects and case studies",
        "Certification recognized by employers",
    ])
    fnt_pt = pe.font("lato-regular", 24)
    for point in diploma_points:
        d.text((PAD, sy + 2), "•", font=pe.font("poppins-bold", 26), fill=pal["gold"])
        sy = pe.draw_multiline(d, (PAD + 28, sy), point, fnt_pt, 320 - 28, (215, 215, 220))
        sy += 18
    sy += 20

    fnt_plus = pe.font("poppins-bold", 40)
    px = PAD
    for _ in range(3):
        d.text((px, sy), "+", font=fnt_plus, fill=pal["gold"])
        px += 52
    sy += 66

    # dot grid fills whatever room is left down to the photo's bottom edge
    dot_gap = 22
    rows_available = max(2, int((photo_bottom - 24 - sy) / dot_gap))
    for row in range(rows_available):
        pe.dot_row(d, (PAD + 4, sy + row * dot_gap), 4, 3, 20, (120, 120, 128))
    secondary_photos = cfg.get("photos", {}).get("secondary", [])
    if secondary_photos:
        # stack the hero photo on top of one secondary photo, split evenly
        # with a small gap between them, instead of one full-height photo
        stack_gap = 16
        half_h = (photo_h - stack_gap) // 2
        hero = pe.load_photo(cfg.get("photos", {}).get("hero"), (photo_w, half_h), "HERO PHOTO", 0)
        img.paste(pe.cover_resize(hero, photo_w, half_h), (photo_x, photo_y))
        hero2 = pe.load_photo(secondary_photos[0], (photo_w, half_h), "PHOTO", 1)
        img.paste(pe.cover_resize(hero2, photo_w, half_h), (photo_x, photo_y + half_h + stack_gap))
    else:
        hero = pe.load_photo(cfg.get("photos", {}).get("hero"), (photo_w, photo_h), "HERO PHOTO", 0)
        img.paste(pe.cover_resize(hero, photo_w, photo_h), (photo_x, photo_y))

    y = photo_y + photo_h + 60
    y = _headline(img, (PAD, y), cfg["headline_lines"], pal, w - 2 * PAD, base_size=76,
                  font_name="poppins-bold", line_gap=4)
    y += 16
    d.rectangle([PAD, y, PAD + 360, y + 5], fill=pal["gold"])
    y += 60

    for row in range(4):
        pe.dot_row(d, (PAD + 4, y + row * 20), 4, 3, 20, (90, 90, 98))

    cta = cfg.get("cta", "MESSAGE US")
    d.text((420, y - 4), cta, font=pe.font("poppins-bold", 24), fill=(160, 160, 168))
    cy = y + 30
    cx2 = 420
    for c in cfg.get("contact_lines", []):
        if c.get("icon"):
            _icon_badge(img, (cx2 + 18, cy + 18), 40, pal["gold"], c["icon"], 18, icon_color=bg)
            cx2 += 48
        fnt_c = pe.font("poppins-bold", 30)
        d.text((cx2, cy), c["text"], font=fnt_c, fill=(255, 255, 255))
        cx2 += d.textlength(c["text"], font=fnt_c) + 30

    pe.chevrons(d, (w - 50, h - 130), 2, 46, 66, pal["gold"], direction="left", width=14)

    img.save(out_path)
    return out_path


def render_studio_split(cfg, out_path):
    """Modern minimalist "agency ad" poster: solid dark background, a small
    sparkle-mark + brand row top-left, a huge 2-4 line bold headline, a short
    body paragraph, a pill-shaped outlined CTA button with an arrow icon, a
    contact/website line, and a tall portrait photo panel on the right with a
    light card notch (holding 3 dots) tucked behind its top-right corner and
    a dot-grid accent overlapping its bottom-left corner. Sized to 1080x1080
    (Instagram square post). Needs `photos.hero` (a tall/portrait-oriented
    photo works best in the narrow photo column); optionally add
    `photos.secondary[0]` to split the photo column into two stacked photos
    (each getting half the height, with a small gap) instead of one
    full-height photo. Does not support `mirror`."""
    pal = _pal(cfg)
    w = h = 1080
    bg = pal["navy"]
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)

    # photo column geometry, computed first so the light notch behind it and
    # the left column's text can both be laid out relative to it
    photo_x = int(w * 0.565)
    photo_w = w - photo_x - 46
    photo_y = 108
    photo_h = h - photo_y - 110

    # light rounded notch card tucked behind the photo's top-right corner,
    # partly bleeding off the top edge, holding a small 3-dot row
    notch_w, notch_h = 200, 300
    nx0, ny0 = w - notch_w - 40, -40
    d.rounded_rectangle([nx0, ny0, nx0 + notch_w, ny0 + notch_h], radius=18, fill=pal["bg"])
    pe.dot_row(d, (nx0 + notch_w / 2 - 34, ny0 + notch_h - 30), 3, 5, 30, pal["navy"])

    # sparkle/asterisk brand mark + brand name, top-left
    sx, sy = 46 + 20, 60 + 20
    spark_r = 18
    spark_color = pal.get("gold", (255, 255, 255))
    for angle in (0, 45, 90, 135):
        rad = math.radians(angle)
        dx, dy = math.cos(rad) * spark_r, math.sin(rad) * spark_r
        d.line([(sx - dx, sy - dy), (sx + dx, sy + dy)], fill=spark_color, width=3)
    brand = cfg.get("brand_name", "STUDY SINGAPORE")
    fnt_brand = pe.font("poppins-medium", 26)
    d.text((sx + spark_r + 20, sy - 16), brand, font=fnt_brand, fill=pal["bg"])

    # headline: 2-4 big bold lines, always rendered in near-white ("bg")
    # regardless of the per-line color hints other templates use, to match
    # this style's monochrome look
    text_col_w = photo_x - 46 - 46
    headline_lines = [{"text": l["text"], "color": "bg"} for l in cfg.get("headline_lines", [])]
    y = _headline(img, (46, 150), headline_lines, pal, text_col_w, base_size=66,
                  font_name="poppins-bold", line_gap=2)
    y += 20

    if cfg.get("body_text"):
        y = pe.draw_multiline(d, (46, y), cfg["body_text"], pe.font("lato-regular", 29),
                               text_col_w, (205, 205, 210), line_spacing=1.4)

    # pill CTA button + website/contact line sit at a fixed position near the
    # bottom of the poster (not directly under the body text), so they land
    # in the same spot regardless of how long the headline/body run
    contact_text = cfg.get("website_text") or (cfg.get("contact_lines", [{}])[0].get("text", "") if cfg.get("contact_lines") else "")
    btn_h = 60
    btn_y = h - 230 if contact_text else h - 190

    cta = cfg.get("cta", "LEARN MORE")
    fnt_cta = pe.font("poppins-bold", 20)
    cta_tw = d.textlength(cta, font=fnt_cta)
    btn_w = 64 + cta_tw + 34
    d.rounded_rectangle([46, btn_y, 46 + btn_w, btn_y + btn_h], radius=btn_h // 2, outline=pal["bg"], width=2)
    _icon_badge(img, (46 + 34, btn_y + btn_h / 2), 40, pal["bg"], "arrow-right", 16, icon_color=bg)
    d.text((46 + 64, btn_y + btn_h / 2 - 12), cta, font=fnt_cta, fill=pal["bg"])

    if contact_text:
        d.text((46, btn_y + btn_h + 24), contact_text, font=pe.font("lato-regular", 26), fill=(190, 190, 196))

    # bottom-left 3-dot row, mirroring the notch's dots
    pe.dot_row(d, (46, h - 60), 3, 5, 30, pal["bg"])

    # tall portrait photo panel on the right -- either one full-height photo,
    # or (if photos.secondary[0] is set) two stacked photos splitting the
    # same column evenly with a small gap between them
    secondary_photos = cfg.get("photos", {}).get("secondary", [])
    if secondary_photos:
        stack_gap = 16
        half_h = (photo_h - stack_gap) // 2
        hero = pe.load_photo(cfg.get("photos", {}).get("hero"), (photo_w, half_h), "HERO PHOTO", 0)
        photo = pe.rounded_photo(hero, (photo_w, half_h), 6)
        img.paste(photo, (photo_x, photo_y), photo)
        hero2 = pe.load_photo(secondary_photos[0], (photo_w, half_h), "PHOTO", 1)
        photo2 = pe.rounded_photo(hero2, (photo_w, half_h), 6)
        img.paste(photo2, (photo_x, photo_y + half_h + stack_gap), photo2)
    else:
        hero = pe.load_photo(cfg.get("photos", {}).get("hero"), (photo_w, photo_h), "HERO PHOTO", 0)
        photo = pe.rounded_photo(hero, (photo_w, photo_h), 6)
        img.paste(photo, (photo_x, photo_y), photo)

    # dot-grid accent overlapping the photo's bottom-left corner
    grid_x0, grid_y0 = photo_x - 26, photo_y + photo_h - 130
    for row in range(6):
        pe.dot_row(d, (grid_x0, grid_y0 + row * 22), 5, 3, 22, pal["bg"])

    img.save(out_path)
    return out_path


# ---------------------------------------------------------------- TEMPLATE Q
def render_boarding_pass(cfg, out_path):
    """A vertical 'mobile boarding pass' ticket card sitting on a solid
    color surface: rounded-top photo strip, a big FROM -> TO route line with
    a dashed flight path + plane icon, a passenger/status row, a perforated
    tear line (dashed rule + circular notches cut into the card edges), a
    2x2 boarding-details grid, a barcode, and a round 'boarding now' stamp
    -- then a closing line + contact row below the card on the surface
    color. Structurally different from the other card/split templates:
    built around an airline-boarding-pass metaphor ("your ticket to
    Singapore") rather than a headline+benefits+CTA stack. Cropped to its
    actual content height (typically well under Instagram's 1350px feed-post
    limit). Needs `photos.hero`. Does not support `mirror`."""
    pal = _pal(cfg)
    w = W
    surface = pal["primary_dark"]
    img = Image.new("RGB", (w, H), surface)
    d = ImageDraw.Draw(img)

    card_x0, card_y0 = 60, 80
    card_x1 = w - 60
    card_w = card_x1 - card_x0
    radius = 32

    photo_h = 400
    # rows below the photo, in order, each entry is the vertical gap added
    # after drawing that row's content
    y = card_y0 + photo_h + 34
    route_y = y
    y += 106
    pax_y = y
    y += 80
    tear_y = y
    y += 40
    grid_y = y
    y += 156 + 26
    bc_y0 = y
    bc_h = 60
    y += bc_h + 22
    card_y1 = y + 30

    # drop shadow + white card body (drawn before the photo/content so they
    # paste on top of it)
    shadow_img, shadow_pad = pe.drop_shadow((card_w, card_y1 - card_y0), radius, blur=30, opacity=110)
    img.paste(shadow_img, (card_x0 - shadow_pad, card_y0 + 16 - shadow_pad), shadow_img)
    d.rounded_rectangle([card_x0, card_y0, card_x1, card_y1], radius=radius, fill=(255, 255, 255))

    # photo strip, rounded top corners only
    hero = pe.load_photo(cfg.get("photos", {}).get("hero"), (card_w, photo_h), "HERO PHOTO", 0)
    photo = pe.cover_resize(hero, card_w, photo_h)
    mask = Image.new("L", (card_w, photo_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, card_w - 1, photo_h + radius], radius=radius,
                                            fill=255, corners=(True, True, False, False))
    photo_rgba = photo.convert("RGBA")
    photo_rgba.putalpha(mask)
    img.paste(photo_rgba, (card_x0, card_y0), photo_rgba)

    # brand pill over the photo, top-left
    brand = cfg.get("brand_name", "")
    if brand:
        fnt_brand = pe.font("poppins-bold", 20)
        bw = d.textlength(brand, font=fnt_brand) + 40
        d.rounded_rectangle([card_x0 + 24, card_y0 + 20, card_x0 + 24 + bw, card_y0 + 20 + 42],
                             radius=21, fill=(255, 255, 255))
        d.text((card_x0 + 44, card_y0 + 31), brand, font=fnt_brand, fill=pal["primary_dark"])

    # FROM -> TO route line
    from_code = cfg.get("from_code", "HOME")
    to_code = cfg.get("to_code", "SIN")
    from_city = cfg.get("from_city", "Your City")
    to_city = cfg.get("to_city", "Singapore")
    fnt_code = pe.font("poppins-bold", 54)
    fnt_city = pe.font("lato-regular", 18)

    d.text((card_x0 + 44, route_y), from_code, font=fnt_code, fill=pal["primary_dark"])
    d.text((card_x0 + 44, route_y + 64), from_city, font=fnt_city, fill=(130, 130, 138))
    to_tw = d.textlength(to_code, font=fnt_code)
    d.text((card_x1 - 44 - to_tw, route_y), to_code, font=fnt_code, fill=pal["primary_dark"])
    to_city_tw = d.textlength(to_city, font=fnt_city)
    d.text((card_x1 - 44 - to_city_tw, route_y + 64), to_city, font=fnt_city, fill=(130, 130, 138))

    from_tw = d.textlength(from_code, font=fnt_code)
    path_x0 = card_x0 + 44 + from_tw + 34
    path_x1 = card_x1 - 44 - to_tw - 34
    path_y = route_y + 26
    if path_x1 > path_x0:
        xx = path_x0
        while xx < path_x1:
            d.line([(xx, path_y), (min(xx + 10, path_x1), path_y)], fill=pal["gold"], width=3)
            xx += 18
        plane_cx = (path_x0 + path_x1) / 2
        fnt_ic = pe.font("icons", 28)
        ch = pe.icon_char("plane")
        bbox = d.textbbox((0, 0), ch, font=fnt_ic)
        tw_ic, th_ic = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text((plane_cx - tw_ic / 2 - bbox[0], path_y - th_ic / 2 - bbox[1] - 2), ch,
               font=fnt_ic, fill=pal["primary"])

    # passenger / status row
    fnt_lbl = pe.font("lato-bold", 14)
    fnt_val = pe.font("poppins-bold", 22)
    col_w = (card_w - 88) / 2
    pax_label = cfg.get("passenger_label", "PASSENGER")
    pax_value = cfg.get("passenger_value", "YOU")
    status_label = cfg.get("status_label", "STATUS")
    status_value = cfg.get("status_value", "CONFIRMED")
    d.text((card_x0 + 44, pax_y), pax_label, font=fnt_lbl, fill=(150, 150, 156))
    d.text((card_x0 + 44, pax_y + 22), pax_value, font=fnt_val, fill=pal["primary_dark"])
    d.text((card_x0 + 44 + col_w, pax_y), status_label, font=fnt_lbl, fill=(150, 150, 156))
    d.text((card_x0 + 44 + col_w, pax_y + 22), status_value, font=fnt_val, fill=pal["primary"])

    # perforated tear line: dashed rule + circular notches cut from the
    # card edges (filled with the surface color so they read as cutouts)
    notch_r = 20
    d.ellipse([card_x0 - notch_r, tear_y - notch_r, card_x0 + notch_r, tear_y + notch_r], fill=surface)
    d.ellipse([card_x1 - notch_r, tear_y - notch_r, card_x1 + notch_r, tear_y + notch_r], fill=surface)
    xx = card_x0 + 34
    while xx < card_x1 - 34:
        d.line([(xx, tear_y), (min(xx + 14, card_x1 - 34), tear_y)], fill=(212, 212, 216), width=3)
        xx += 24

    # 2x2 boarding-details grid
    fields = cfg.get("boarding_fields", [
        {"label": "PROGRAM", "value": "DIPLOMA + INTERNSHIP"},
        {"label": "DURATION", "value": "12 MONTHS"},
        {"label": "INTAKE", "value": "OPEN NOW"},
        {"label": "FEES", "value": "NO AGENCY FEE"},
    ])[:4]
    fw = col_w
    for i, f in enumerate(fields):
        fx = card_x0 + 44 + (i % 2) * fw
        fy = grid_y + (i // 2) * 78
        d.text((fx, fy), f.get("label", ""), font=fnt_lbl, fill=(150, 150, 156))
        pe.draw_multiline(d, (fx, fy + 20), f.get("value", ""), pe.font("poppins-bold", 19),
                           fw - 20, pal["primary_dark"])

    # barcode (deterministic pseudo-random bar widths) + a round stamp badge
    rnd = random.Random(7)
    bar_widths = [2, 2, 3, 5, 2, 4, 3, 2, 5, 2, 3, 2, 4]
    bar_gaps = [3, 4, 6]
    bc_x0 = card_x0 + 44
    bc_x1_limit = card_x0 + 44 + 300
    bx = bc_x0
    i = 0
    while bx < bc_x1_limit:
        bw_ = bar_widths[i % len(bar_widths)]
        d.rectangle([bx, bc_y0, bx + bw_, bc_y0 + bc_h], fill=(30, 30, 34))
        bx += bw_ + bar_gaps[i % len(bar_gaps)]
        i += 1
    fnt_small = pe.font("lato-regular", 13)
    d.text((bc_x0, bc_y0 + bc_h + 6), cfg.get("ticket_code", "SG-2026-INTAKE"),
           font=fnt_small, fill=(150, 150, 156))

    stamp_d = 128
    scx = card_x1 - 44 - stamp_d / 2
    scy = bc_y0 + bc_h / 2
    _stamp_badge(img, (scx, scy), stamp_d, cfg.get("stamp_text", "BOARDING NOW"), ("poppins-bold", 19),
                 pal["primary"], ring_color=pal["primary"])

    # closing CTA + contact row on the surface color, below the card
    y2 = card_y1 + 46
    cta = cfg.get("cta", "Message me to reserve your seat")
    fnt_cta = pe.font("poppins-bold", 28)
    cta_lines = pe.wrap_text(cta, fnt_cta, w - 160, d)
    for ln in cta_lines[:2]:
        tw_cta = d.textlength(ln, font=fnt_cta)
        d.text((w / 2 - tw_cta / 2, y2), ln, font=fnt_cta, fill=(255, 255, 255))
        y2 += 40
    y2 += 14

    contacts = cfg.get("contact_lines", [])
    fnt_c = pe.font("lato-bold", 26)
    total_w = sum(46 + d.textlength(c["text"], font=fnt_c) + 20 for c in contacts)
    cx = w / 2 - total_w / 2
    for c in contacts:
        _icon_badge(img, (cx + 20, y2 + 20), 40, pal["gold"], c.get("icon", "whatsapp"), 18,
                    icon_color=pal["primary_dark"])
        d.text((cx + 46, y2 + 5), c["text"], font=fnt_c, fill=(255, 255, 255))
        cx += 46 + d.textlength(c["text"], font=fnt_c) + 20
    y2 += 60

    img = img.crop((0, 0, w, min(H, y2 + 40)))
    img.save(out_path)
    return out_path


# ---------------------------------------------------------------- TEMPLATE R
def render_movie_poster(cfg, out_path):
    """A cinematic 'blockbuster movie poster' full-bleed layout: the hero
    photo fills the entire 1080x1350 canvas (Instagram 4:5 feed post) with a
    dark gradient rising from the bottom (and a light one at the very top)
    for text legibility, a small tracked "presents" line, a huge centered
    movie-title-style headline, a one-line tagline/logline, a "STARRING: YOU"
    credit line, a small bordered rating badge (doubles as the
    age-requirement line), a tiny tracked movie-credits line listing the
    program benefits, and a solid-color release bar at the very bottom with
    a CTA + contact row. Structurally different from every card/ticket
    template in this skill -- no white card or panel at all, just type set
    directly over a full-bleed photo, like an actual film poster. Needs
    `photos.hero` -- pick a dramatic, high-contrast portrait-leaning photo
    (skyline, dusk, a single strong subject) since the entire canvas is the
    photo; check retention with `check_crop.py` at 1080x1350 before picking.
    Does not support `mirror` or `dark_mode` (already full-bleed dark by
    design)."""
    pal = _pal(cfg)
    # Fixed at 1080x1350 (Instagram's max feed-post portrait ratio, 4:5) --
    # full-bleed, so shrinking the canvas just crops the photo differently
    # (the normal cover-resize crop the user already picks a photo for via
    # check_crop.py), not a loss of any text/content element.
    w, h = W, 1350
    hero = pe.load_photo(cfg.get("photos", {}).get("hero"), (w, h), "HERO PHOTO", 0)
    photo = pe.cover_resize(hero, w, h)
    img = photo.convert("RGBA")

    bottom_grad = pe.vertical_gradient_rgba((w, h), (0, 0, 0, 0), (0, 0, 0, 235), start=0.36)
    img.alpha_composite(bottom_grad)
    top_grad = pe.vertical_gradient_rgba((w, 220), (0, 0, 0, 150), (0, 0, 0, 0), start=0.0)
    img.alpha_composite(top_grad, (0, 0))
    img = img.convert("RGB")
    d = ImageDraw.Draw(img)

    # small tracked "presents" line
    presents = cfg.get("presents_text", "STUDY SINGAPORE PRESENTS")
    fnt_pres = pe.font("lato-bold", 20)
    tracked = "  ".join(list(presents))
    tw = d.textlength(tracked, font=fnt_pres)
    d.text((w / 2 - tw / 2, 60), tracked, font=fnt_pres, fill=(230, 230, 230))

    # big centered movie-title headline
    y = int(h * 0.56)
    y = _headline(img, (PAD, y), cfg["headline_lines"], pal, w - 2 * PAD, base_size=100,
                  font_name="poppins-bold", line_gap=4, align="center")
    y += 10

    # tagline / logline
    if cfg.get("tagline"):
        fnt_tag = pe.font("lato-regular", 22)
        lines = pe.wrap_text(cfg["tagline"], fnt_tag, w - 200, d)
        for ln in lines[:2]:
            tw = d.textlength(ln, font=fnt_tag)
            d.text((w / 2 - tw / 2, y), ln, font=fnt_tag, fill=(225, 225, 228))
            y += 30
        y += 12

    # "starring: you" credit line
    starring = cfg.get("starring_text", "STARRING: YOU")
    fnt_star = pe.font("poppins-bold", 24)
    tw = d.textlength(starring, font=fnt_star)
    d.text((w / 2 - tw / 2, y), starring, font=fnt_star, fill=pal["gold"])
    y += 48

    # small bordered rating badge
    rating = cfg.get("rating_text", "APPROVED · AGES 18-40")
    fnt_rate = pe.font("lato-bold", 16)
    tw = d.textlength(rating, font=fnt_rate)
    box_w, box_h = tw + 40, 40
    d.rectangle([w / 2 - box_w / 2, y, w / 2 + box_w / 2, y + box_h], outline=(255, 255, 255), width=2)
    d.text((w / 2 - tw / 2, y + 11), rating, font=fnt_rate, fill=(255, 255, 255))
    y += box_h + 30

    # tiny tracked movie-credits line (the program benefits)
    credits = cfg.get("credits", [
        "PAID INTERNSHIP", "INTERNATIONAL DIPLOMA", "VISA ASSISTANCE", "NO AGENCY FEES",
    ])
    credits_text = "   •   ".join(credits)
    fnt_cred = pe.font("lato-bold", 15)
    lines = pe.wrap_text(credits_text, fnt_cred, w - 160, d)
    for ln in lines[:2]:
        tw = d.textlength(ln, font=fnt_cred)
        d.text((w / 2 - tw / 2, y), ln, font=fnt_cred, fill=(205, 205, 210))
        y += 24

    # bottom release bar: CTA left, contact right
    bar_h = 110
    bar_y = h - bar_h
    d.rectangle([0, bar_y, w, h], fill=pal["primary"])
    release = cfg.get("release_text", "NOW ENROLLING")
    d.text((PAD, bar_y + 20), release, font=pe.font("lato-bold", 16), fill=(255, 255, 255))
    if cfg.get("cta"):
        d.text((PAD, bar_y + 42), cfg["cta"], font=pe.font("poppins-bold", 26), fill=pal["gold"])
    contacts = cfg.get("contact_lines", [])
    fnt_c = pe.font("lato-bold", 26)
    total_w = sum(46 + d.textlength(c["text"], font=fnt_c) + 30 for c in contacts)
    cx = w - PAD - total_w
    for c in contacts:
        _icon_badge(img, (cx + 18, bar_y + bar_h / 2), 40, (255, 255, 255), c.get("icon", "whatsapp"), 18,
                    icon_color=pal["primary_dark"])
        d.text((cx + 44, bar_y + bar_h / 2 - 15), c["text"], font=fnt_c, fill=(255, 255, 255))
        cx += 46 + d.textlength(c["text"], font=fnt_c) + 30

    img.save(out_path)
    return out_path


# ---------------------------------------------------------------- TEMPLATE S
def render_postcard(cfg, out_path):
    """A 'wish you were here' postcard layout: a thick white print-style
    border frames a large photo, with a postage-stamp graphic (perforated
    edge, plane icon, `stamp_country`/`stamp_denomination`) in the photo's
    top-right corner and a circular postmark (`postmark_text`) in the photo's top-left corner. A big
    retro `headline_lines` sits over a dark band near the photo's bottom
    edge (e.g. "GREETINGS FROM" / "SINGAPORE"). Below the photo, a thin
    vertical divider splits the border area into a left "note" column
    (`note_heading` + `note_text`, plus an optional `ps_text` line under a
    divider and a `who_heading` + `requirements` mini-checklist) and a
    right "mailing address" column (an optional `duration_text` pill, up to
    6 `benefits` as address-style lines, an optional `industries` list, and
    `contact_lines`), like the postcard's addressee block -- both columns
    have enough default content to balance the visual weight of the photo
    above them, so the bottom half doesn't read as empty. A different
    object-metaphor from every other template -- it's meant to read as an
    actual postcard, not a card/ticket/panel. Cropped to its actual content
    height, comfortably within Instagram's 1350px feed-post limit. Needs
    `photos.hero` sized for a ~1020x820 area -- check `check_crop.py` first. Does not support
    `mirror` or `dark_mode`."""
    pal = _pal(cfg)
    w, h = W, H
    img = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(img)

    border = 30
    photo_x0, photo_y0 = border, border
    photo_x1, photo_y1 = w - border, 850
    photo_w, photo_h = photo_x1 - photo_x0, photo_y1 - photo_y0
    hero = pe.load_photo(cfg.get("photos", {}).get("hero"), (photo_w, photo_h), "HERO PHOTO", 0)
    hero_displayed = pe.cover_resize(hero, photo_w, photo_h)
    img.paste(hero_displayed, (photo_x0, photo_y0))

    # postage stamp, top-right corner of the photo, with a perforated edge
    stamp_w, stamp_h = 130, 170
    sx0, sy0 = photo_x1 - 40 - stamp_w, photo_y0 + 30
    sx1, sy1 = sx0 + stamp_w, sy0 + stamp_h
    local_box = (sx0 - photo_x0, sy0 - photo_y0, sx1 - photo_x0, sy1 - photo_y0)
    edge_color = hero_displayed.crop(local_box).resize((1, 1)).getpixel((0, 0))
    d.rectangle([sx0, sy0, sx1, sy1], fill=(255, 255, 255))
    notch_r = 7
    nx = sx0
    while nx <= sx1:
        d.ellipse([nx - notch_r, sy0 - notch_r, nx + notch_r, sy0 + notch_r], fill=edge_color)
        d.ellipse([nx - notch_r, sy1 - notch_r, nx + notch_r, sy1 + notch_r], fill=edge_color)
        nx += notch_r * 2
    ny = sy0
    while ny <= sy1:
        d.ellipse([sx0 - notch_r, ny - notch_r, sx0 + notch_r, ny + notch_r], fill=edge_color)
        d.ellipse([sx1 - notch_r, ny - notch_r, sx1 + notch_r, ny + notch_r], fill=edge_color)
        ny += notch_r * 2
    d.rectangle([sx0 + 10, sy0 + 10, sx1 - 10, sy1 - 10], outline=pal["primary"], width=2)
    fnt_ic = pe.font("icons", 30)
    ch = pe.icon_char("plane")
    bbox = d.textbbox((0, 0), ch, font=fnt_ic)
    tw_ic, th_ic = bbox[2] - bbox[0], bbox[3] - bbox[1]
    icx, icy = (sx0 + sx1) / 2, sy0 + 48
    d.text((icx - tw_ic / 2 - bbox[0], icy - th_ic / 2 - bbox[1]), ch, font=fnt_ic, fill=pal["primary"])
    fnt_sc = pe.font("poppins-bold", 15)
    country = cfg.get("stamp_country", "SINGAPORE")
    tw = d.textlength(country, font=fnt_sc)
    d.text(((sx0 + sx1) / 2 - tw / 2, sy0 + 92), country, font=fnt_sc, fill=pal["primary_dark"])
    fnt_den = pe.font("lato-regular", 13)
    denom = cfg.get("stamp_denomination", "AIRMAIL")
    tw = d.textlength(denom, font=fnt_den)
    d.text(((sx0 + sx1) / 2 - tw / 2, sy0 + 114), denom, font=fnt_den, fill=(120, 120, 128))

    # postmark: ringed circle in the photo's top-left corner -- a separate
    # accent from the stamp, which sits in the opposite (top-right) corner
    pm_d = 108
    pcx, pcy = photo_x0 + 30 + pm_d / 2, photo_y0 + 30 + pm_d / 2
    _stamp_badge(img, (pcx, pcy), pm_d, cfg.get("postmark_text", "APPLY TODAY"), ("poppins-bold", 15),
                 (255, 255, 255), ring_color=(255, 255, 255))

    # retro headline band near the photo's bottom edge
    band_h = 250
    grad = pe.vertical_gradient_rgba((photo_w, band_h), (0, 0, 0, 0), (0, 0, 0, 210), start=0.1)
    img.paste(Image.alpha_composite(
        img.crop((photo_x0, photo_y1 - band_h, photo_x1, photo_y1)).convert("RGBA"), grad).convert("RGB"),
        (photo_x0, photo_y1 - band_h))
    d = ImageDraw.Draw(img)
    _headline(img, (photo_x0 + 30, photo_y1 - band_h + 26), cfg["headline_lines"], pal,
              photo_w - 60, base_size=54, font_name="poppins-bold", line_gap=2, align="center")

    # back-of-postcard area: a thin vertical divider splits a note column
    # from an address-style benefits column. The divider/closer position
    # depends on how tall each column's content turns out to be, so it's
    # drawn after both columns below rather than to a fixed canvas height.
    top = photo_y1 + 34
    mid_x = w // 2

    left_x0, left_w = border + 14, mid_x - border - 34
    note_heading = cfg.get("note_heading", "A quick note...")
    d.text((left_x0, top), note_heading, font=pe.font("poppins-bold", 22), fill=pal["primary_dark"])
    note_text = cfg.get("note_text",
                         "Come study, intern, and earn in Singapore! Message me for the visa process "
                         "and I'll walk you through everything, from your application to your first "
                         "day of class.")
    ly = pe.draw_multiline(d, (left_x0, top + 40), note_text, pe.font("lato-regular", 19), left_w,
                            (70, 70, 76))
    ly += 26
    ps_text = cfg.get("ps_text", "P.S. No agency fees, ever -- you deal with the school directly.")
    if ps_text:
        d.line([(left_x0, ly), (left_x0 + left_w, ly)], fill=(225, 225, 229), width=1)
        ly += 20
        ly = pe.draw_multiline(d, (left_x0, ly), ps_text, pe.font("lato-regular", 18), left_w, (110, 110, 116))
    ly += 26
    who_heading = cfg.get("who_heading", "Who can apply?")
    if who_heading:
        d.text((left_x0, ly), who_heading, font=pe.font("poppins-bold", 18), fill=pal["primary_dark"])
        ly += 30
        for req in cfg.get("requirements", ["Age 18 to 40", "High school graduate", "Valid passport"])[:4]:
            _icon_badge(img, (left_x0 + 10, ly + 10), 22, (235, 235, 238), "check", 11,
                        icon_color=pal["primary_dark"])
            d.text((left_x0 + 26, ly), req, font=pe.font("lato-regular", 17), fill=(80, 80, 86))
            ly += 30

    right_x0, right_w = mid_x + 34, w - border - 14 - (mid_x + 34)
    ry = top
    duration_text = cfg.get("duration_text", "1 YEAR STUDENT PASS")
    if duration_text:
        fnt_dur = pe.font("poppins-bold", 16)
        tw = d.textlength(duration_text, font=fnt_dur)
        d.rounded_rectangle([right_x0, ry, right_x0 + tw + 28, ry + 36], radius=18, fill=pal["gold"])
        d.text((right_x0 + 14, ry + 9), duration_text, font=fnt_dur, fill=pal["primary_dark"])
        ry += 54
    d.text((right_x0, ry), "TO:", font=pe.font("poppins-bold", 16), fill=(150, 150, 156))
    ry += 32
    for b in cfg.get("benefits", [])[:6]:
        _icon_badge(img, (right_x0 + 12, ry + 12), 26, pal["primary"], "check", 12)
        d.text((right_x0 + 32, ry), b, font=pe.font("lato-semibold", 18), fill=pal["primary_dark"])
        ry += 36
    ry += 20
    industries = cfg.get("industries", [])
    if industries:
        d.text((right_x0, ry), "OPEN INDUSTRIES", font=pe.font("poppins-bold", 15), fill=(150, 150, 156))
        ry += 28
        ry = pe.draw_multiline(d, (right_x0, ry), "  •  ".join(industries), pe.font("lato-semibold", 17),
                                right_w, pal["primary_dark"])
        ry += 22
    contacts = cfg.get("contact_lines", [])
    for c in contacts:
        _icon_badge(img, (right_x0 + 13, ry + 13), 28, pal["gold"], c.get("icon", "whatsapp"), 13,
                    icon_color=pal["primary_dark"])
        d.text((right_x0 + 34, ry), c["text"], font=pe.font("poppins-bold", 20), fill=pal["primary_dark"])
        ry += 38

    content_bottom = max(ly, ry)
    d.line([(mid_x, top), (mid_x, content_bottom + 14)], fill=(210, 210, 214), width=2)

    closer = cfg.get("closer_text", "SEND THIS TO YOURSELF — YOUR FUTURE IS WAITING")
    fnt_close = pe.font("lato-bold", 14)
    tw = d.textlength(closer, font=fnt_close)
    closer_y = content_bottom + 40
    d.text((w / 2 - tw / 2, closer_y), closer, font=fnt_close, fill=(160, 160, 166))

    img = img.crop((0, 0, w, min(h, closer_y + 30)))
    img.save(out_path)
    return out_path


# ---------------------------------------------------------------- TEMPLATE T
def render_chat_mockup(cfg, out_path):
    """A phone-screenshot-style mockup of a WhatsApp/DM conversation about
    the program: a colored header bar with a circular avatar photo,
    `contact_name` + `contact_status`, then a scrollback of chat bubbles
    (`messages`, a list of {"from": "them"|"me", "text"} or
    {"from": "me", "photo": true} for an image bubble using
    `photos.secondary[0]`) alternating left/right with a timestamp under
    each, and a bottom message-input-bar mockup with a send button. A UI
    mockup rather than a paper/card/ticket metaphor -- genuinely different
    from every other template, and it doubles as social proof (it reads as
    a real conversation, not an ad). Needs `photos.hero` for the avatar
    (a small circular crop, so any reasonably centered photo works) and
    optionally `photos.secondary[0]` if a message has `"photo": true`.
    Cropped to its actual content height (the bubble list is dynamic),
    typically well under Instagram's 1350px feed-post limit. Does not
    support `mirror` or `dark_mode`."""
    pal = _pal(cfg)
    w = W
    bg = (236, 229, 221)
    img = Image.new("RGB", (w, H), bg)
    d = ImageDraw.Draw(img)

    header_h = 140
    d.rectangle([0, 0, w, header_h], fill=pal["primary"])
    avatar_d = 66
    avatar_cx, avatar_cy = 74, header_h / 2
    hero = cfg.get("photos", {}).get("hero")
    if hero:
        av = pe.load_photo(hero, (avatar_d, avatar_d), "AVATAR", 0)
        av_circ = pe.circle_photo(pe.cover_resize(av, avatar_d, avatar_d), avatar_d)
        img.paste(av_circ, (int(avatar_cx - avatar_d / 2), int(avatar_cy - avatar_d / 2)), av_circ)
    else:
        d.ellipse([avatar_cx - avatar_d / 2, avatar_cy - avatar_d / 2,
                   avatar_cx + avatar_d / 2, avatar_cy + avatar_d / 2], fill=(255, 255, 255))
    name = cfg.get("contact_name", "Study Singapore")
    status = cfg.get("contact_status", "Online")
    d.text((116, avatar_cy - 30), name, font=pe.font("poppins-bold", 26), fill=(255, 255, 255))
    d.text((116, avatar_cy + 4), status, font=pe.font("lato-regular", 18), fill=(230, 230, 230))
    for i, icon in enumerate(["phone", "comments"]):
        cx = w - 60 - i * 70
        _icon_badge(img, (cx, header_h / 2), 40, pal["primary"], icon, 18, icon_color=(255, 255, 255))

    y = header_h + 26
    max_bubble_w = 700
    pad_x, pad_y = 22, 14
    messages = cfg.get("messages", [
        {"from": "them", "text": "Hi! I saw your Singapore internship post -- is it really no agency fees?"},
        {"from": "me", "text": "Yes! 100% no agency fees. Just 6 months study + 6 months paid internship, with an international diploma included."},
        {"from": "them", "text": "Wow that's amazing, how do I start?"},
        {"from": "me", "text": "Message me your name + WhatsApp number and I'll send the application link!"},
    ])
    secondary = cfg.get("photos", {}).get("secondary", [])

    for i, msg in enumerate(messages):
        is_me = msg.get("from") == "me"
        ts = msg.get("time", f"10:0{i % 6} AM")
        if msg.get("photo") and secondary:
            bw, bh = 320, 220
            photo = pe.load_photo(secondary[0], (bw, bh), "PHOTO", i + 1)
            rounded = pe.rounded_photo(photo, (bw, bh), 18)
            bx = w - 40 - bw if is_me else 40
            img.paste(rounded, (bx, y), rounded)
            y += bh + 6
            fnt_ts = pe.font("lato-regular", 14)
            tw = d.textlength(ts, font=fnt_ts)
            tx = w - 40 - tw if is_me else 40
            d.text((tx, y), ts, font=fnt_ts, fill=(140, 140, 146))
            y += 30
            continue

        text = msg.get("text", "")
        fnt_msg = pe.font("lato-regular", 22)
        lines = pe.wrap_text(text, fnt_msg, max_bubble_w - 2 * pad_x, d)
        line_h = 30
        bubble_w = min(max_bubble_w, max((d.textlength(ln, font=fnt_msg) for ln in lines), default=0) + 2 * pad_x)
        bubble_h = len(lines) * line_h + 2 * pad_y
        bx0 = w - 40 - bubble_w if is_me else 40
        bx1 = bx0 + bubble_w
        fill = pal["primary"] if is_me else (255, 255, 255)
        text_color = (255, 255, 255) if is_me else (30, 30, 34)
        d.rounded_rectangle([bx0, y, bx1, y + bubble_h], radius=18, fill=fill)
        ty = y + pad_y
        for ln in lines:
            d.text((bx0 + pad_x, ty), ln, font=fnt_msg, fill=text_color)
            ty += line_h
        y += bubble_h + 6
        fnt_ts = pe.font("lato-regular", 14)
        tw = d.textlength(ts, font=fnt_ts)
        tx = bx1 - tw if is_me else bx0
        d.text((tx, y), ts, font=fnt_ts, fill=(140, 140, 146))
        y += 34

    # bottom message-input-bar mockup
    y += 16
    bar_h = 74
    placeholder = cfg.get("input_placeholder", "Type a message...")
    d.rounded_rectangle([30, y, w - 100, y + bar_h], radius=bar_h / 2, fill=(255, 255, 255),
                         outline=(210, 210, 214), width=2)
    d.text((56, y + bar_h / 2 - 13), placeholder, font=pe.font("lato-regular", 22), fill=(150, 150, 156))
    send_cx, send_cy = w - 60, y + bar_h / 2
    d.ellipse([send_cx - 32, send_cy - 32, send_cx + 32, send_cy + 32], fill=pal["primary"])
    fnt_ic = pe.font("icons", 24)
    ch = pe.icon_char("arrow-right")
    bbox = d.textbbox((0, 0), ch, font=fnt_ic)
    tw_ic, th_ic = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((send_cx - tw_ic / 2 - bbox[0], send_cy - th_ic / 2 - bbox[1]), ch, font=fnt_ic, fill=(255, 255, 255))
    y += bar_h + 30

    img = img.crop((0, 0, w, min(H, y)))
    img.save(out_path)
    return out_path
