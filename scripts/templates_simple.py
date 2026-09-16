"""
Simple poster templates: bold_impact, clean_split, elegant_pills.

These three templates share a similar visual grammar (white background, 
colored header bar, boxed info sections) and are best suited for 
structured benefit/requirement layouts.
"""

from typing import Dict, Any
from PIL import Image, ImageDraw
import poster_engine as pe
import template_base as tb


def render_bold_impact(cfg: Dict[str, Any], out_path: str) -> str:
    """Render bold_impact template.
    
    A4-proportioned poster with a colored ribbon, optional badge, 
    hero photo, 2x2 benefit grid, and two-column info boxes.
    
    Args:
        cfg: Poster configuration dictionary
        out_path: Output PNG file path
        
    Returns:
        Path to the saved poster PNG
    """
    pal = tb.pal(cfg)
    # A4 proportions (1:1.4142) instead of standard 1:1.5
    H = round(tb.W * 297 / 210)
    img = Image.new("RGB", (tb.W, H), pal["bg"])
    d = ImageDraw.Draw(img)

    # Top ribbon
    ribbon_h = 64
    d.rectangle([0, 0, tb.W, ribbon_h], fill=pal["primary"])
    fnt = pe.font("poppins-bold", 26)
    eyebrow = cfg.get("eyebrow", "KICKSTART YOUR GLOBAL CAREER!")
    d.text((tb.PAD, ribbon_h / 2 - 15), eyebrow, font=fnt, fill=(255, 255, 255))

    mirror = cfg.get("mirror", False)

    # Badge: fixed position (top-right or top-left when mirrored)
    if cfg.get("badge_text"):
        if mirror:
            bx0, by0, bx1, by1 = tb.PAD, ribbon_h + 18, tb.PAD + 220, ribbon_h + 130
        else:
            bx0, by0, bx1, by1 = tb.W - 260, ribbon_h + 18, tb.W - 40, ribbon_h + 130
        d.rounded_rectangle([bx0, by0, bx1, by1], radius=16, outline=pal["gold"], width=4, fill=pal["navy"])
        stars = pe.icon_char("star") * 5
        d.text((bx0 + 20, by0 + 10), stars, font=pe.font("icons", 16), fill=pal["gold"])
        pe.draw_multiline(
            d,
            (bx0 + 16, by0 + 36),
            cfg["badge_text"],
            pe.font("poppins-bold", 20),
            bx1 - bx0 - 32,
            (255, 210, 60),
            align="center",
        )

    # Headline (starts right under ribbon, not pushed down by badge)
    y = ribbon_h + 36
    if mirror and cfg.get("badge_text"):
        y = max(y, by1 + 24)
    headline_w = tb.W - 2 * tb.PAD
    if cfg.get("badge_text") and not mirror:
        headline_w = min(headline_w, (tb.W - 260) - tb.PAD - 20)
    y = tb.headline(img, (tb.PAD, y), cfg["headline_lines"], pal, headline_w, base_size=76)
    y += 10
    if cfg.get("tagline"):
        y = pe.draw_multiline(d, (tb.PAD, y), cfg["tagline"], pe.font("lato-bold", 24), tb.W - 2 * tb.PAD, pal["text"])
        y += 8
    if cfg.get("badge_text"):
        y = max(y, by1 + 24)

    # Hero photo
    photo_h = 330
    hero = pe.load_photo(cfg.get("photos", {}).get("hero"), (tb.W - 2 * tb.PAD, photo_h), "HERO PHOTO", 0)
    photo = pe.rounded_photo(hero, (tb.W - 2 * tb.PAD, photo_h), 24)
    img.paste(photo, (tb.PAD, y), photo)
    y += photo_h + 26

    # Feature icon row (up to 4 benefits)
    feats = cfg.get("benefits", [])[:4]
    ficons = cfg.get("benefits_icons", ["check", "briefcase", "dollar", "globe"])
    col_w = (tb.W - 2 * tb.PAD) // 2
    row_h = 88
    for i, feat in enumerate(feats):
        cx = tb.PAD + (i % 2) * col_w
        cy = y + (i // 2) * row_h
        icon = ficons[i] if i < len(ficons) else "check"
        tb.feature_row(img, (cx, cy), col_w - 20, icon, feat, "", pal, icon_bg=pal["primary"])
    y += row_h * ((len(feats) + 1) // 2) + 14

    # Two-column info boxes
    box_w = (tb.W - 2 * tb.PAD - 30) // 2
    row_line_h = 44
    box_h = row_line_h * max(
        len(cfg.get("requirements", [])), len(cfg.get("benefits_extra", cfg.get("requirements", [])))
    ) + 84
    box_h = max(box_h, 300)

    def _req_box(x0: int) -> None:
        d.rounded_rectangle([x0, y, x0 + box_w, y + box_h], radius=14, outline=pal["primary"], width=3)
        d.rectangle([x0, y, x0 + box_w, y + 54], fill=pal["primary"])
        d.text((x0 + 20, y + 12), "PROGRAM REQUIREMENTS", font=pe.font("poppins-bold", 22), fill=(255, 255, 255))
        ry = y + 70
        req_icons = cfg.get("requirements_icons", ["calendar", "graduation-cap", "passport", "language"])
        for i, req in enumerate(cfg.get("requirements", [])):
            icon = req_icons[i] if i < len(req_icons) else "check"
            tb.icon_badge(img, (x0 + 40, ry + 18), 40, pal["gold"], icon, 18, icon_color=pal["navy"])
            d.text((x0 + 72, ry + 4), req, font=pe.font("lato-bold", 20), fill=pal["text"])
            ry += row_line_h

    def _incl_box(x0: int) -> None:
        d.rounded_rectangle([x0, y, x0 + box_w, y + box_h], radius=14, outline=pal["primary"], width=3)
        d.rectangle([x0, y, x0 + box_w, y + 54], fill=pal["primary"])
        d.text((x0 + 20, y + 12), "WHAT'S INCLUDED", font=pe.font("poppins-bold", 22), fill=(255, 255, 255))
        ry = y + 70
        incl = cfg.get("benefits_extra", cfg.get("benefits", []))
        incl_icons = cfg.get("benefits_extra_icons", cfg.get("benefits_icons", ["check"] * len(incl)))
        for i, b in enumerate(incl):
            icon = incl_icons[i] if i < len(incl_icons) else "check"
            tb.icon_badge(img, (x0 + 40, ry + 18), 40, pal["gold"], icon, 18, icon_color=pal["navy"])
            d.text((x0 + 72, ry + 4), b, font=pe.font("lato-bold", 20), fill=pal["text"])
            ry += row_line_h

    x2 = tb.PAD + box_w + 30
    if mirror:
        _incl_box(tb.PAD)
        _req_box(x2)
    else:
        _req_box(tb.PAD)
        _incl_box(x2)
    y += box_h + 22

    # Bottom contact bar
    bar_h = 150
    y_bar = max(y + 20, H - bar_h)
    tb.contact_bar(img, y_bar, H - y_bar, cfg, pal, bg=pal["primary"])

    img.save(out_path)
    return out_path


def render_clean_split(cfg: Dict[str, Any], out_path: str) -> str:
    """Render clean_split template.
    
    Light or dark mode poster with optional dark mode support, 
    hero photo with shadow, and 2x2 requirement/benefits grid.
    
    Args:
        cfg: Poster configuration dictionary
        out_path: Output PNG file path
        
    Returns:
        Path to the saved poster PNG
    """
    pal = tb.pal(cfg)
    dark = cfg.get("dark_mode", False)
    bg_color = pal["primary_dark"] if dark else pal["bg"]
    panel_color = pe.lighten(pal["primary_dark"], 0.18) if dark else pal["panel"]
    text_color = (224, 224, 230) if dark else pal["text"]
    tagline_color = (195, 195, 202) if dark else (90, 90, 96)
    accent_fill = pal["primary"] if dark else pal["navy"]
    headline_pal = dict(pal, navy=(255, 255, 255), primary=pal["gold"]) if dark else pal
    img = Image.new("RGB", (tb.W, tb.H), bg_color)
    d = ImageDraw.Draw(img)

    mirror = cfg.get("mirror", False)
    y = tb.PAD - 10
    if cfg.get("eyebrow"):
        fnt = pe.font("poppins-bold", 20)
        txt = cfg["eyebrow"]
        tw = d.textlength(txt, font=fnt)
        ex0 = tb.W - tb.PAD - (tw + 40) if mirror else tb.PAD
        d.rounded_rectangle([ex0, y, ex0 + tw + 40, y + 44], radius=22, fill=pal["gold"])
        d.text((ex0 + 20, y + 10), txt, font=fnt, fill=(255, 255, 255))
    if cfg.get("badge_text"):
        bw, bh = 220, 90
        bx0, by0 = (tb.PAD, y - 6) if mirror else (tb.W - tb.PAD - bw, y - 6)
        d.rounded_rectangle([bx0, by0, bx0 + bw, by0 + bh], radius=14, fill=accent_fill)
        pe.draw_multiline(
            d, (bx0 + 16, by0 + 18), cfg["badge_text"], pe.font("poppins-bold", 20), bw - 32, pal["gold"], align="center"
        )
    y += 70

    y = tb.headline(img, (tb.PAD, y), cfg["headline_lines"], headline_pal, tb.W - 2 * tb.PAD, base_size=66)
    y += 6
    if cfg.get("tagline"):
        y = pe.draw_multiline(d, (tb.PAD, y), cfg["tagline"], pe.font("lato-regular", 22), tb.W - 2 * tb.PAD, tagline_color)
        y += 20

    if cfg.get("discount_text"):
        fnt = pe.font("poppins-bold", 26)
        tw = d.textlength(cfg["discount_text"], font=fnt)
        pill_w = tw + 100
        d.rounded_rectangle([tb.PAD, y, tb.PAD + pill_w, y + 64], radius=32, fill=pal["gold"])
        tb.icon_badge(img, (tb.PAD + 32, y + 32), 40, (255, 255, 255), "percent", 18, icon_color=pal["gold"])
        d.text((tb.PAD + 60, y + 18), cfg["discount_text"], font=fnt, fill=(255, 255, 255))
        y += 84

    # Hero photo with shadow
    photo_h = 400
    hero = pe.load_photo(cfg.get("photos", {}).get("hero"), (tb.W - 2 * tb.PAD, photo_h), "HERO PHOTO", 1)
    photo = pe.rounded_photo(hero, (tb.W - 2 * tb.PAD, photo_h), 24)
    pe.paste_with_shadow(img, photo, (tb.PAD, y), 24, blur=16, opacity=60)
    y += photo_h + 36

    # Requirements + benefits boxes (2x2 grid)
    box_w = (tb.W - 2 * tb.PAD - 24) // 2
    reqs = cfg.get("requirements", [])[:4]
    bens = cfg.get("benefits", [])[:4]
    req_icons = cfg.get("requirements_icons", ["calendar", "graduation-cap", "passport", "language"])
    ben_icons = cfg.get("benefits_icons", ["book", "briefcase", "check-circle", "globe"])
    box_h = 240

    box_border = pe.lighten(panel_color, 0.15) if dark else (225, 225, 230)
    title_color = (255, 255, 255) if dark else pal["navy"]

    def info_box(x0: int, title: str, items: list, icons: list) -> None:
        d.rounded_rectangle(
            [x0, y, x0 + box_w, y + box_h], radius=16, fill=panel_color, outline=box_border, width=2
        )
        d.text((x0 + 22, y + 18), title, font=pe.font("poppins-bold", 20), fill=title_color)
        iy = y + 62
        for i, item in enumerate(items):
            ic = icons[i] if i < len(icons) else "check"
            tb.icon_badge(img, (x0 + 40, iy + 15), 32, accent_fill, ic, 14)
            pe.draw_multiline(d, (x0 + 64, iy + 4), item, pe.font("lato-semibold", 17), box_w - 84, text_color)
            iy += 42

    if mirror:
        info_box(tb.PAD, "BENEFITS", bens, ben_icons)
        info_box(tb.PAD + box_w + 24, "REQUIREMENTS", reqs, req_icons)
    else:
        info_box(tb.PAD, "REQUIREMENTS", reqs, req_icons)
        info_box(tb.PAD + box_w + 24, "BENEFITS", bens, ben_icons)
    y += box_h + 30

    # Bottom bar: CTA left + contact right
    bar_h = 100
    img = img.crop((0, 0, tb.W, y + bar_h))
    d = ImageDraw.Draw(img)
    d.rectangle([0, y, tb.W, y + bar_h], fill=accent_fill)
    if cfg.get("cta"):
        d.text((tb.PAD, y + 28), cfg["cta"], font=pe.font("poppins-bold", 26), fill=pal["gold"])
    cx = tb.W - tb.PAD
    contacts = cfg.get("contact_lines", [])
    total_w = 0
    fnt_c = pe.font("lato-bold", 26)
    for c in contacts:
        total_w += 46 + d.textlength(c["text"], font=fnt_c) + 30
    cx = tb.W - tb.PAD - total_w
    for c in contacts:
        tb.icon_badge(img, (cx + 18, y + bar_h / 2), 40, pal["gold"], c["icon"], 18, icon_color=pal["navy"])
        d.text((cx + 44, y + bar_h / 2 - 15), c["text"], font=fnt_c, fill=(255, 255, 255))
        cx += 46 + d.textlength(c["text"], font=fnt_c) + 30

    img.save(out_path)
    return out_path


def render_elegant_pills(cfg: Dict[str, Any], out_path: str) -> str:
    """Render elegant_pills template.
    
    Left text column with benefit pills, right column with stacked photos.
    Framed with a gold border.
    
    Args:
        cfg: Poster configuration dictionary
        out_path: Output PNG file path
        
    Returns:
        Path to the saved poster PNG
    """
    pal = tb.pal(cfg)
    img = Image.new("RGB", (tb.W, tb.H), pal["bg"])
    d = ImageDraw.Draw(img)

    border = 22
    d.rounded_rectangle([border, border, tb.W - border, tb.H - border], radius=28, outline=pal["gold"], width=4)

    inner_pad = border + 44
    mirror = cfg.get("mirror", False)

    text_w = int((tb.W - 2 * inner_pad) * 0.5)
    photo_w = tb.W - inner_pad - (inner_pad + text_w + 30)
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
    y = tb.headline(img, (inner_pad_eff, y), cfg["headline_lines"], pal, headline_w, base_size=52)
    y += 6
    if cfg.get("tagline"):
        y = pe.draw_multiline(d, (inner_pad_eff, y), cfg["tagline"], pe.font("lato-bold", 20), headline_w, pal["navy"])
        y += 26

    # Benefit pills
    top_y = inner_pad + (60 if cfg.get("eyebrow") else 0)
    pill_y = max(y, top_y)
    bens = cfg.get("benefits", [])
    ben_icons = cfg.get("benefits_icons", ["check"] * len(bens))
    pill_h = 62
    pill_gap = 16
    text_bottom = pill_y + len(bens) * (pill_h + pill_gap) - pill_gap if bens else pill_y

    # Right column: stacked photos
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
        d.rounded_rectangle([inner_pad_eff, py, inner_pad_eff + headline_w, py + pill_h], radius=pill_h // 2, fill=pal["navy"])
        tb.icon_badge(img, (inner_pad_eff + pill_h / 2, py + pill_h / 2), pill_h - 16, pal["gold"], icon, 20, icon_color=pal["navy"])
        d.text((inner_pad_eff + pill_h + 6, py + pill_h / 2 - 13), b, font=pe.font("poppins-medium", 22), fill=(255, 255, 255))
    content_bottom = max(pill_y + len(bens) * (pill_h + pill_gap), top_y + total_h)

    # Bottom contact bar
    bar_h = 110
    bar_y = content_bottom + 40
    img = img.crop((0, 0, tb.W, bar_y + bar_h + border))
    d = ImageDraw.Draw(img)
    d.rectangle([border, bar_y, tb.W - border, bar_y + bar_h], fill=pal["navy"])
    # Redraw border so it closes at the bottom
    d.rounded_rectangle([border, border, tb.W - border, bar_y + bar_h + border - 1], radius=28, outline=pal["gold"], width=4)
    d.rectangle([border, bar_y, tb.W - border, bar_y + bar_h], fill=pal["navy"])
    contacts = cfg.get("contact_lines", [])
    if contacts:
        c = contacts[0]
        tb.icon_badge(img, (inner_pad + 26, bar_y + bar_h / 2), 52, pal["gold"], c["icon"], 24, icon_color=pal["navy"])
        label = cfg.get("contact_label", "FOR MORE INFORMATION, WHATSAPP ME AT:")
        d.text((inner_pad + 66, bar_y + 20), label, font=pe.font("lato-regular", 16), fill=(230, 230, 235))
        d.text((inner_pad + 66, bar_y + 42), c["text"], font=pe.font("poppins-bold", 30), fill=(255, 255, 255))

    img.save(out_path)
    return out_path
