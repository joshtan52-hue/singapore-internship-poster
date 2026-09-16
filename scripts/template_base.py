"""
Shared utilities, constants, and helper functions for all poster templates.

This module centralizes palette definitions, common drawing patterns,
and helper functions used across multiple templates.
"""

from typing import Dict, Tuple, List, Any, Optional
from PIL import Image, ImageDraw
import poster_engine as pe

# Canvas dimensions (standard and Instagram-specific)
W, H = 1080, 1620
PAD = 60

# Color palette definitions
PALETTES: Dict[str, Dict[str, Tuple[int, int, int]]] = {
    "red_navy": dict(
        primary=(200, 16, 46),
        primary_dark=(11, 43, 74),
        navy=(11, 43, 74),
        gold=(255, 199, 44),
        bg=(255, 255, 255),
        panel=(246, 247, 249),
        text=(24, 32, 46),
    ),
    "navy_gold": dict(
        primary=(22, 36, 68),
        primary_dark=(12, 20, 42),
        navy=(22, 36, 68),
        gold=(197, 157, 54),
        bg=(250, 248, 240),
        panel=(255, 255, 255),
        text=(24, 32, 46),
    ),
    "green_gold": dict(
        primary=(19, 74, 48),
        primary_dark=(10, 44, 28),
        navy=(19, 74, 48),
        gold=(197, 157, 54),
        bg=(250, 248, 240),
        panel=(255, 255, 255),
        text=(24, 32, 46),
    ),
    "teal_coral": dict(
        primary=(11, 94, 101),
        primary_dark=(6, 56, 61),
        navy=(11, 94, 101),
        gold=(240, 130, 90),
        bg=(247, 250, 250),
        panel=(255, 255, 255),
        text=(20, 34, 36),
    ),
    "burgundy_cream": dict(
        primary=(97, 22, 39),
        primary_dark=(60, 12, 22),
        navy=(97, 22, 39),
        gold=(201, 162, 39),
        bg=(252, 248, 240),
        panel=(255, 255, 255),
        text=(35, 20, 22),
    ),
}

# Color cycling for multicolor badge grids
CHECK_COLORS: List[Tuple[int, int, int]] = [
    (200, 16, 46),
    (197, 157, 54),
    (11, 43, 74),
    (44, 140, 90),
]


def pal(cfg: Dict[str, Any]) -> Dict[str, Tuple[int, int, int]]:
    """Get the palette dictionary for a config.
    
    Args:
        cfg: Poster config dictionary
        
    Returns:
        Palette dict with keys: primary, primary_dark, navy, gold, bg, panel, text
    """
    return PALETTES[cfg.get("palette", "navy_gold")]


def color(cfg: Dict[str, Any], name: str) -> Tuple[int, int, int]:
    """Get a specific color from the config's palette, with fallback.
    
    Args:
        cfg: Poster config dictionary
        name: Color name (e.g. "primary", "gold", "navy")
        
    Returns:
        RGB color tuple, or the palette's primary color as fallback
    """
    p = pal(cfg)
    return p.get(name, p["primary"])


def dark_bg_border(pal_dict: Dict[str, Tuple[int, int, int]], dark: bool) -> Tuple[int, int, int]:
    """Get border/outline color for elements on dark vs light backgrounds.
    
    In light mode, use navy. In dark mode, lighten navy for visibility on dark canvas.
    
    Args:
        pal_dict: Palette dictionary
        dark: Whether the background is dark
        
    Returns:
        RGB color tuple for border outlines
    """
    return pe.lighten(pal_dict["navy"], 0.35) if dark else pal_dict["navy"]


def icon_badge(
    img: Image.Image,
    center: Tuple[int, int],
    diameter: int,
    bg_color: Tuple[int, int, int],
    icon_name: str,
    icon_size: int,
    icon_color: Tuple[int, int, int] = (255, 255, 255),
) -> None:
    """Draw a circular icon badge with a background color.
    
    Args:
        img: PIL Image to draw on
        center: (x, y) center coordinates of the badge
        diameter: Badge diameter in pixels
        bg_color: Background RGB color
        icon_name: FontAwesome icon name (e.g. "check", "briefcase", "phone")
        icon_size: Font size for the icon
        icon_color: RGB color for the icon glyph
    """
    d = ImageDraw.Draw(img)
    r = diameter / 2
    d.ellipse([center[0] - r, center[1] - r, center[0] + r, center[1] + r], fill=bg_color)
    fnt = pe.font("icons", icon_size)
    ch = pe.icon_char(icon_name)
    bbox = d.textbbox((0, 0), ch, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(
        (center[0] - tw / 2 - bbox[0], center[1] - th / 2 - bbox[1]),
        ch,
        font=fnt,
        fill=icon_color,
    )


def feature_row(
    img: Image.Image,
    xy: Tuple[int, int],
    w: int,
    icon_name: str,
    title: str,
    subtitle: str,
    pal_dict: Dict[str, Tuple[int, int, int]],
    icon_bg: Optional[Tuple[int, int, int]] = None,
    title_size: int = 24,
    sub_size: int = 18,
) -> int:
    """Draw a feature row with icon, title, and optional subtitle.
    
    Args:
        img: PIL Image to draw on
        xy: Top-left (x, y) coordinates
        w: Available width for text
        icon_name: FontAwesome icon name
        title: Title text
        subtitle: Optional subtitle text
        pal_dict: Palette dictionary
        icon_bg: Optional custom icon background color (defaults to primary)
        title_size: Font size for title
        sub_size: Font size for subtitle
        
    Returns:
        Y coordinate of the bottom of the row
    """
    d = ImageDraw.Draw(img)
    x, y = xy
    icon_bg = icon_bg or pal_dict["primary"]
    icon_badge(img, (x + 28, y + 28), 56, icon_bg, icon_name, 26)
    tf = pe.font("poppins-bold", title_size)
    sf = pe.font("lato-regular", sub_size)
    d.text((x + 72, y + 4), title, font=tf, fill=pal_dict["text"])
    if subtitle:
        pe.draw_multiline(
            d, (x + 72, y + 4 + title_size + 6), subtitle, sf, w - 72, (110, 110, 118)
        )
    return y + 68


def headline(
    img: Image.Image,
    xy: Tuple[int, int],
    lines_cfg: List[Dict[str, str]],
    pal_dict: Dict[str, Tuple[int, int, int]],
    max_width: int,
    base_size: int = 64,
    font_name: str = "poppins-bold",
    line_gap: int = 6,
    align: str = "left",
) -> int:
    """Draw a multi-line headline with auto-shrinking to fit.
    
    Args:
        img: PIL Image to draw on
        xy: Top-left (x, y) coordinates
        lines_cfg: List of {"text": str, "color": str (optional)} dicts
        pal_dict: Palette dictionary
        max_width: Maximum line width in pixels
        base_size: Starting font size
        font_name: Font name (e.g. "poppins-bold")
        line_gap: Vertical gap between lines
        align: Text alignment ("left", "center", or "right")
        
    Returns:
        Y coordinate of the bottom of the headline
    """
    d = ImageDraw.Draw(img)
    x, y = xy
    size = base_size
    fnt = pe.font(font_name, size)
    # Shrink to fit widest line
    widest = max(d.textlength(l["text"], font=fnt) for l in lines_cfg)
    while widest > max_width and size > 24:
        size -= 2
        fnt = pe.font(font_name, size)
        widest = max(d.textlength(l["text"], font=fnt) for l in lines_cfg)
    asc, desc = fnt.getmetrics()
    for l in lines_cfg:
        color_name = l.get("color", "primary")
        text_color = pal_dict.get(color_name, pal_dict["primary"])
        tw = d.textlength(l["text"], font=fnt)
        lx = x if align == "left" else x + (max_width - tw) / 2 if align == "center" else x + max_width - tw
        d.text((lx, y), l["text"], font=fnt, fill=text_color)
        y += asc + desc + line_gap
    return y


def contact_bar(
    img: Image.Image,
    y0: int,
    h: int,
    cfg: Dict[str, Any],
    pal_dict: Dict[str, Tuple[int, int, int]],
    bg: Optional[Tuple[int, int, int]] = None,
) -> None:
    """Draw a colored contact/CTA bar at the bottom of a poster.
    
    Args:
        img: PIL Image to draw on
        y0: Top Y coordinate of the bar
        h: Bar height
        cfg: Poster config (contains contact_lines, cta)
        pal_dict: Palette dictionary
        bg: Background color (defaults to primary)
    """
    bg = bg or pal_dict["primary"]
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
        icon_badge(img, (x + 20, y0 + h / 2), 44, (255, 255, 255), c["icon"], 22, icon_color=bg)
        d.text((x + 48, y0 + h / 2 - 16), c["text"], font=fnt_c, fill=(255, 255, 255))
        x += 48 + d.textlength(c["text"], font=fnt_c) + 40


def numbered_checklist(
    img: Image.Image,
    xy: Tuple[int, int],
    w: int,
    items: List[str],
    colored: bool = True,
    numbered: bool = False,
    font_size: int = 25,
    circle_d: int = 40,
    row_gap: int = 54,
    cols: int = 2,
    col_gap: int = 40,
    text_color: Tuple[int, int, int] = (20, 32, 46),
) -> int:
    """Draw a grid of check/number-badge + label rows.
    
    Cycles through CHECK_COLORS so each item's badge is a different accent color.
    Row height is computed per-row from text wrapping, so tall labels never overlap.
    
    Args:
        img: PIL Image to draw on
        xy: Top-left (x, y) coordinates
        w: Available width
        items: List of label strings
        colored: Whether to cycle through colors (True) or use single color (False)
        numbered: Whether to show numbers (True) or checkmarks (False)
        font_size: Font size for labels
        circle_d: Diameter of the badge circle
        row_gap: Vertical gap between rows
        cols: Number of columns
        col_gap: Horizontal gap between columns
        text_color: RGB color for label text
        
    Returns:
        Y coordinate of the bottom of the checklist
    """
    d = ImageDraw.Draw(img)
    x0, y0 = xy
    col_w = (w - col_gap * (cols - 1)) // cols
    fnt = pe.font("poppins-medium" if not numbered else "lato-bold", font_size)
    text_w = col_w - circle_d - 16
    asc, desc = fnt.getmetrics()
    line_h = int((asc + desc) * 1.2)
    rows = (len(items) + cols - 1) // cols
    cy = y0
    for row in range(rows):
        row_items = items[row * cols : row * cols + cols]
        n_lines = [len(pe.wrap_text(it, fnt, text_w, d)) for it in row_items]
        row_h = max(circle_d, max(n_lines) * line_h) if n_lines else circle_d
        for c, item in enumerate(row_items):
            i = row * cols + c
            cx = x0 + c * (col_w + col_gap)
            color = CHECK_COLORS[i % len(CHECK_COLORS)] if colored else CHECK_COLORS[0]
            r = circle_d / 2
            badge_cy = cy + row_h / 2
            d.ellipse([cx, badge_cy - r, cx + circle_d, badge_cy + r], fill=color)
            if numbered:
                num = str(i + 1)
                fnt_n = pe.font("lato-bold", int(circle_d * 0.5))
                bbox = d.textbbox((0, 0), num, font=fnt_n)
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                d.text(
                    (cx + r - tw / 2 - bbox[0], badge_cy - th / 2 - bbox[1]),
                    num,
                    font=fnt_n,
                    fill=(255, 255, 255),
                )
            else:
                fnt_ic = pe.font("icons", int(circle_d * 0.5))
                ch = pe.icon_char("check")
                bbox = d.textbbox((0, 0), ch, font=fnt_ic)
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                d.text(
                    (cx + r - tw / 2 - bbox[0], badge_cy - th / 2 - bbox[1]),
                    ch,
                    font=fnt_ic,
                    fill=(255, 255, 255),
                )
            text_h = n_lines[c] * line_h
            pe.draw_multiline(d, (cx + circle_d + 16, badge_cy - text_h / 2), item, fnt, text_w, text_color)
        cy += row_h + 20
    return cy


def stamp_badge(
    img: Image.Image,
    center: Tuple[int, int],
    diameter: int,
    text: str,
    font_spec,
    text_color: Tuple[int, int, int],
    ring_color: Optional[Tuple[int, int, int]] = None,
    fill: Optional[Tuple[int, int, int]] = None,
    rings: int = 1,
) -> None:
    """Draw a circular badge with text centered inside, optionally with rings.
    
    Args:
        img: PIL Image to draw on
        center: (x, y) center coordinates
        diameter: Badge diameter
        text: Text to display (auto-wraps and shrinks to fit)
        font_spec: Either (font_name, size) tuple or a pre-built font object
        text_color: RGB color for text
        ring_color: Optional RGB color for the ring outline
        fill: Optional RGB background fill color
        rings: Number of concentric rings to draw (1 or 2)
    """
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
