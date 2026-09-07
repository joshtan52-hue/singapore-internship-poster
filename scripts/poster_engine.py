"""
Core drawing engine for Singapore Study + Paid Internship posters.
Pure Pillow (no browser/network needed) so it runs anywhere.
"""
import os
import math
import textwrap
import colorsys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts")

FONT_FILES = {
    "poppins-bold": "Poppins-Bold.ttf",
    "poppins-regular": "Poppins-Regular.ttf",
    "poppins-medium": "Poppins-Medium.ttf",
    "poppins-light": "Poppins-Light.ttf",
    "lato-black": "Lato-Black.ttf",
    "lato-bold": "Lato-Bold.ttf",
    "lato-semibold": "Lato-Semibold.ttf",
    "lato-regular": "Lato-Regular.ttf",
    "icons": "fontawesome-webfont.ttf",
}

# FontAwesome 4 codepoints used as bullet / contact icons
ICONS = {
    "graduation-cap": "\uf19d",
    "briefcase": "\uf0b1",
    "dollar": "\uf155",
    "percent": "\uf295",
    "check": "\uf00c",
    "check-circle": "\uf058",
    "phone": "\uf095",
    "whatsapp": "\uf232",
    "plane": "\uf072",
    "globe": "\uf0ac",
    "handshake": "\uf2b5",
    "comments": "\uf0e6",
    "id-card": "\uf2c2",
    "calendar": "\uf133",
    "clock": "\uf017",
    "map-marker": "\uf041",
    "users": "\uf0c0",
    "star": "\uf005",
    "envelope": "\uf0e0",
    "book": "\uf02d",
    "money": "\uf0d6",
    "passport": "\uf2c2",
    "language": "\uf1ab",
    "home": "\uf015",
    "arrow-right": "\uf061",
}

_font_cache = {}

def font(name, size):
    key = (name, size)
    if key not in _font_cache:
        path = os.path.join(FONT_DIR, FONT_FILES[name])
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def icon_char(name):
    return ICONS.get(name, "")


# ---------- generic drawing helpers ----------

def rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def vertical_gradient(size, top_color, bottom_color):
    w, h = size
    base = Image.new("RGB", (1, h), color=0)
    px = base.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        px[0, y] = tuple(int(top_color[i] + (bottom_color[i] - top_color[i]) * t) for i in range(3))
    return base.resize((w, h))


def diagonal_gradient(size, top_color, bottom_color):
    w, h = size
    base = Image.new("RGB", (w, h))
    px = base.load()
    maxd = w + h
    for y in range(h):
        for x in range(0, w, 4):
            t = (x + y) / maxd
            c = tuple(int(top_color[i] + (bottom_color[i] - top_color[i]) * t) for i in range(3))
            for dx in range(4):
                if x + dx < w:
                    px[x + dx, y] = c
    return base


def diagonal_gradient_multi(size, colors):
    """Diagonal gradient through an ordered list of 2+ colors. Passing 3+ stops
    (rather than blending two colors directly) avoids the muddy/desaturated
    midtone you get when the two end colors are near-complementary (e.g. a
    warm gold fading straight into a deep navy) -- the gradient instead
    passes through each color's own saturated hue."""
    w, h = size
    base = Image.new("RGB", (w, h))
    px = base.load()
    n = len(colors) - 1
    maxd = w + h
    for y in range(h):
        for x in range(0, w, 4):
            t = (x + y) / maxd
            seg = min(int(t * n), n - 1)
            local_t = t * n - seg
            c0, c1 = colors[seg], colors[seg + 1]
            c = tuple(int(c0[i] + (c1[i] - c0[i]) * local_t) for i in range(3))
            for dx in range(4):
                if x + dx < w:
                    px[x + dx, y] = c
    return base


def cover_resize(img, target_w, target_h, anchor_x=0.5, anchor_y=0.5):
    """Resize+crop image to exactly fill target box (like CSS background-size:cover).
    anchor_x/anchor_y (0-1) control which part of the image the crop keeps when
    something has to be cut -- 0.5/0.5 is the old centered-crop default. Use a
    lower anchor_y (e.g. 0.1-0.2) to keep the top of a tall subject (a statue's
    head, a building's roofline) in frame when the crop has to cut height."""
    src_w, src_h = img.size
    src_ratio = src_w / src_h
    tgt_ratio = target_w / target_h
    if src_ratio > tgt_ratio:
        new_h = target_h
        new_w = int(new_h * src_ratio)
    else:
        new_w = target_w
        new_h = int(new_w / src_ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = int((new_w - target_w) * anchor_x)
    top = int((new_h - target_h) * anchor_y)
    left = max(0, min(left, new_w - target_w))
    top = max(0, min(top, new_h - target_h))
    return img.crop((left, top, left + target_w, top + target_h))


def contain_resize(img, target_w, target_h, bg_color=(10, 10, 14)):
    """Resize image to fit entirely inside the target box with no cropping
    (like CSS background-size:contain) -- the whole photo stays visible.
    Scaled to the limiting dimension and centered on a solid-color canvas,
    so any leftover space becomes letterbox/pillarbox bars rather than a crop."""
    src_w, src_h = img.size
    scale = min(target_w / src_w, target_h / src_h)
    new_w, new_h = max(1, int(src_w * scale)), max(1, int(src_h * scale))
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new("RGB", (target_w, target_h), bg_color)
    canvas.paste(resized, ((target_w - new_w) // 2, (target_h - new_h) // 2))
    return canvas


def rounded_photo(img, size, radius):
    img = cover_resize(img, *size).convert("RGB")
    mask = Image.new("L", size, 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle([0, 0, size[0], size[1]], radius=radius, fill=255)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def circle_photo(img, diameter):
    img = cover_resize(img, diameter, diameter).convert("RGB")
    mask = Image.new("L", (diameter, diameter), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.ellipse([0, 0, diameter, diameter], fill=255)
    out = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def drop_shadow(size, radius, blur=18, opacity=90, offset=(0, 8)):
    w, h = size
    pad = blur * 3
    radius = max(0, min(radius, min(w, h) // 2 - 1))
    canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([pad + offset[0], pad + offset[1], pad + w + offset[0], pad + h + offset[1]],
                         radius=radius, fill=(0, 0, 0, opacity))
    canvas = canvas.filter(ImageFilter.GaussianBlur(blur))
    return canvas, pad


def paste_with_shadow(base, layer_rgba, xy, radius, blur=18, opacity=90, offset=(0, 8)):
    w, h = layer_rgba.size
    shadow, pad = drop_shadow((w, h), radius, blur, opacity, offset)
    base.paste(shadow, (xy[0] - pad, xy[1] - pad), shadow)
    base.paste(layer_rgba, xy, layer_rgba)


def wrap_text(text, fnt, max_width, draw):
    words = text.split()
    lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_multiline(draw, xy, text, fnt, max_width, fill, line_spacing=1.25, align="left"):
    lines = wrap_text(text, fnt, max_width, draw)
    x, y = xy
    asc, desc = fnt.getmetrics()
    line_h = int((asc + desc) * line_spacing)
    for i, ln in enumerate(lines):
        lw = draw.textlength(ln, font=fnt)
        lx = x
        if align == "center":
            lx = x + (max_width - lw) / 2
        elif align == "right":
            lx = x + (max_width - lw)
        draw.text((lx, y + i * line_h), ln, font=fnt, fill=fill)
    return y + len(lines) * line_h


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def placeholder_photo(size, label, seed=0):
    """Plain gradient placeholder when the user hasn't supplied a real photo yet.
    Deliberately has no text on it -- photo areas stay photo-only, never labeled."""
    palette = [((70, 110, 165), (25, 45, 80)), ((90, 150, 120), (20, 60, 45)),
               ((190, 150, 80), (110, 80, 30))]
    top, bottom = palette[seed % len(palette)]
    return diagonal_gradient(size, top, bottom).convert("RGB")


def load_photo(path, size, label, seed=0):
    if path and os.path.exists(path):
        try:
            return Image.open(path).convert("RGB")
        except Exception:
            pass
    return placeholder_photo(size, label, seed)


# ---------- photo crop-retention check ----------
# Pure geometry, not a perceptual judgment call -- given a source photo's
# size and the target box it'll be cropped (cover_resize) into, compute what
# fraction of the source survives. A tall portrait photo forced into a short
# wide strip (e.g. photo_overlay's ~1080x550 hero band) can lose the majority
# of the image -- one photo measured at 736x1308 into that band kept only
# ~29% of itself, slicing through both the top of a building and a bridge
# below it. This is exactly the "match photo orientation to slot" guidance
# in SKILL.md turned into a number you can check instead of eyeballing.

def crop_retention(src_size, target_size):
    """Fraction (0-1) of a source image's relevant dimension that survives a
    cover_resize crop into target_size. 1.0 means the aspect ratios already
    match (no crop needed beyond scaling); lower means more of the photo
    gets cut off. As a rule of thumb, treat anything below ~0.6 as a sign to
    pick a differently-shaped photo for that slot."""
    src_w, src_h = src_size
    tgt_w, tgt_h = target_size
    src_ratio = src_w / src_h
    tgt_ratio = tgt_w / tgt_h
    return min(src_ratio, tgt_ratio) / max(src_ratio, tgt_ratio)


def photo_size(path):
    with Image.open(path) as im:
        return im.size

# ---------- palette / photo color-harmony check ----------
# Objective (not eyeballed) check for whether a palette's primary/accent
# color visually clashes with a photo's dominant tone -- e.g. a saturated
# red badge sitting next to an orange/pink sunset photo. Both colors being
# "warm" isn't itself the problem; the problem is a saturated palette color
# landing very close in hue to an already-saturated, similarly-warm photo,
# which reads as competing rather than complementary. Run this before
# finalizing any photo-heavy poster config (see scripts/check_palette.py).

def _rgb_to_hsv(rgb):
    r, g, b = [c / 255 for c in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h * 360, s, v


def photo_avg_hsv(path, n_bins=24):
    """Dominant hue/saturation of a photo via a saturation-weighted hue
    histogram (downsampled for speed). Two things a plain average gets
    wrong: (1) a flat RGB average washes out a small vivid sunset glow
    sitting under a large area of pale sky/water/pavement, and (2) even a
    saturation-weighted *circular mean* breaks on a photo with two distinct
    dominant hues on opposite sides of the wheel (e.g. a blue sky above an
    orange sunset glow) -- averaging "blue" and "orange" hue vectors lands
    on a meaningless purple midpoint that matches neither.  Binning hues
    into buckets and picking the single bucket with the most saturation*value
    weight avoids both problems and matches what a person would point to as
    "the" color of the photo."""
    img = Image.open(path).convert("RGB").resize((60, 60))
    pixels = list(img.getdata())
    bin_weight = [0.0] * n_bins
    bin_sat = [0.0] * n_bins
    for r, g, b in pixels:
        h, s, v = _rgb_to_hsv((r, g, b))
        w = s * v
        idx = int(h / 360 * n_bins) % n_bins
        bin_weight[idx] += w
        bin_sat[idx] += s * w
    best = max(range(n_bins), key=lambda i: bin_weight[i])
    total_w = bin_weight[best]
    if total_w < 1e-6:
        return 0.0, 0.0, 0.0
    dominant_hue = (best + 0.5) * (360 / n_bins)
    dominant_sat = bin_sat[best] / total_w
    return dominant_hue, dominant_sat, 0.0


def hue_distance(h1, h2):
    d = abs(h1 - h2) % 360
    return min(d, 360 - d)


def check_palette_clash(photo_path, palette_primary_rgb, hue_threshold=40, sat_threshold=0.35):
    """Returns (clash, photo_hsv, palette_hsv). `clash` is True when the
    palette's primary color and the photo's average tone are both fairly
    saturated AND close in hue -- the pattern that produced the red_navy /
    orange-sunset clash on an earlier poster. Desaturated (grayish/neutral)
    photos or palette colors never flag a clash, since a muted tone doesn't
    compete with anything."""
    ph, ps, pv = photo_avg_hsv(photo_path)
    lh, ls, lv = _rgb_to_hsv(palette_primary_rgb)
    if ps < sat_threshold or ls < sat_threshold:
        return False, (ph, ps, pv), (lh, ls, lv)
    return hue_distance(ph, lh) < hue_threshold, (ph, ps, pv), (lh, ls, lv)


def palette_photo_swatch(photo_paths, palette, out_path, chip_size=160):
    """Build a quick side-by-side reference strip: the palette's color chips
    (primary, gold, navy, bg) next to a thumbnail of each candidate photo.
    Numeric hue-matching (see check_palette_clash above) is a useful signal
    but proved unreliable on its own -- a photo with two very different
    dominant regions (e.g. blue sky above an orange sunset glow) can trip a
    hue-distance check in either direction depending on which region has
    more weighted pixels, even when a human would call the combination
    fine. This swatch exists so the actual choice gets a quick visual check
    (view the saved PNG) rather than trusting a single auto-pass/fail
    number."""
    keys = [k for k in ("primary", "gold", "navy", "bg") if k in palette]
    n_chips = len(keys)
    n_photos = len(photo_paths)
    w = chip_size * (n_chips + n_photos)
    h = chip_size + 30
    img = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(img)
    x = 0
    fnt = font("lato-regular", 14)
    for k in keys:
        d.rectangle([x, 0, x + chip_size, chip_size], fill=palette[k])
        d.text((x + 6, chip_size + 6), k, font=fnt, fill=(20, 20, 20))
        x += chip_size
    for p in photo_paths:
        thumb = load_photo(p, (chip_size, chip_size), "PHOTO", 0)
        thumb = cover_resize(thumb, chip_size, chip_size)
        img.paste(thumb, (x, 0))
        d.text((x + 6, chip_size + 6), os.path.basename(p)[:18], font=fnt, fill=(20, 20, 20))
        x += chip_size
    img.save(out_path)
    return out_path

# ---------- torn-paper effect ----------

def _torn_edge_points(length, amplitude, step, seed):
    import random
    rnd = random.Random(seed)
    pts = []
    x = 0
    while x <= length:
        pts.append((x, rnd.uniform(-amplitude, amplitude)))
        x += step
    pts.append((length, rnd.uniform(-amplitude, amplitude)))
    return pts


def torn_mask(size, edge="bottom", amplitude=16, step=34, seed=0):
    """White rectangle mask with one edge replaced by a jagged 'torn paper' line."""
    w, h = size
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    if edge == "bottom":
        pts = _torn_edge_points(w, amplitude, step, seed)
        poly = [(0, 0), (w, 0), (w, h)] + [(x, h - amplitude - dy) for x, dy in reversed(pts)] + [(0, h)]
    elif edge == "top":
        pts = _torn_edge_points(w, amplitude, step, seed)
        poly = [(x, amplitude + dy) for x, dy in pts] + [(w, h), (0, h)]
    else:
        pts = _torn_edge_points(h, amplitude, step, seed)
        poly = [(0, 0), (w, 0), (w, h), (0, h)]
    d.polygon(poly, fill=255)
    return mask


def torn_photo(img, size, edge="bottom", amplitude=16, seed=0):
    img = cover_resize(img, *size).convert("RGB")
    mask = torn_mask(size, edge=edge, amplitude=amplitude, seed=seed)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def chevrons(draw, xy, count, size, gap, color, direction="right", width=6):
    x, y = xy
    for i in range(count):
        cx = x + i * gap if direction == "right" else x - i * gap
        if direction == "right":
            pts = [(cx, y - size), (cx + size, y), (cx, y + size)]
        else:
            pts = [(cx, y - size), (cx - size, y), (cx, y + size)]
        draw.line(pts, fill=color, width=width, joint="curve")


def dot_row(draw, xy, count, radius, gap, color):
    x, y = xy
    for i in range(count):
        cx = x + i * gap
        draw.ellipse([cx - radius, y - radius, cx + radius, y + radius], outline=color, width=3)

def vertical_gradient_rgba(size, top_rgba, bottom_rgba, start=0.0):
    """RGBA gradient, transparent-ish at top fading to solid at bottom.
    `start` (0-1) is where the fade begins (area above stays top_rgba)."""
    w, h = size
    grad = Image.new("RGBA", size)
    px = grad.load()
    start_px = int(h * start)
    for y in range(h):
        if y < start_px:
            c = top_rgba
        else:
            t = (y - start_px) / max(h - start_px - 1, 1)
            c = tuple(int(top_rgba[i] + (bottom_rgba[i] - top_rgba[i]) * t) for i in range(4))
        for x in range(0, w, 8):
            for dx in range(8):
                if x + dx < w:
                    px[x + dx, y] = c
    return grad


def chip(draw, img, xy, text, icon_name, pal, fill=None, text_color=None, font_size=20, icon_size=16, pad_x=18):
    """A small rounded pill with an icon + short text, used for compact benefit chips."""
    fill = fill or (255, 255, 255, 235)
    text_color = text_color or pal.get("navy", (20, 20, 20))
    x, y = xy
    fnt = font("poppins-medium", font_size)
    tw = draw.textlength(text, font=fnt)
    h = font_size + 26
    w = pad_x + icon_size + 10 + tw + pad_x
    d2 = ImageDraw.Draw(img, "RGBA") if img.mode == "RGBA" else draw
    d2.rounded_rectangle([x, y, x + w, y + h], radius=h / 2, fill=fill)
    fnt_ic = font("icons", icon_size + 2)
    d2.text((x + pad_x, y + h / 2 - (icon_size + 2) / 2 - 1), icon_char(icon_name), font=fnt_ic, fill=text_color)
    d2.text((x + pad_x + icon_size + 10, y + h / 2 - font_size / 2 - 2), text, font=fnt, fill=text_color)
    return w, h



# ---------- helpers for gradient_highlights / night_glow templates ----------

def lighten(color, amt):
    """Blend a color toward white by `amt` (0-1)."""
    return tuple(int(c + (255 - c) * amt) for c in color)


def darken(color, amt):
    """Blend a color toward black by `amt` (0-1)."""
    return tuple(int(c * (1 - amt)) for c in color)


def radial_gradient(size, center, inner_color, outer_color, radius=None):
    w, h = size
    if radius is None:
        radius = max(w, h)
    img = Image.new("RGB", size)
    px = img.load()
    cx, cy = center
    for y in range(h):
        for x in range(0, w, 4):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            t = min(d / radius, 1.0)
            c = tuple(int(inner_color[i] + (outer_color[i] - inner_color[i]) * t) for i in range(3))
            for dx in range(4):
                if x + dx < w:
                    px[x + dx, y] = c
    return img


def soft_blob(size, color_rgba, blur=40):
    """A soft blurred circle, used for glow/bubble decorative accents. The
    circle is drawn well inside its canvas (padded by ~1.5x the blur radius)
    so the blur fully fades to transparent before reaching the canvas edge --
    without this margin, GaussianBlur leaves a hard rectangular seam where
    the image gets pasted onto a background."""
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    margin = blur * 1.5
    d.ellipse([margin, margin, size[0] - margin, size[1] - margin], fill=color_rgba)
    return img.filter(ImageFilter.GaussianBlur(blur))


def circular_text(size, text, radius, font_obj, fill, start_deg=-140, letter_spacing=2):
    """Render `text` along a circular arc onto a transparent image of `size`.
    Angles measured clockwise from 12 o'clock. Characters read left-to-right
    walking clockwise starting at `start_deg`."""
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    cx, cy = size[0] / 2, size[1] / 2
    meas = ImageDraw.Draw(img)
    circumference = 2 * math.pi * radius
    angle = start_deg
    for ch in text:
        w = meas.textlength(ch, font=font_obj)
        ch_arc = (w + letter_spacing) / circumference * 360
        mid_angle = angle + ch_arc / 2
        theta = math.radians(mid_angle)
        x = cx + radius * math.sin(theta)
        y = cy - radius * math.cos(theta)
        pad = 12
        char_img = Image.new("RGBA", (int(w) + pad * 2, font_obj.size + pad * 2), (0, 0, 0, 0))
        cd = ImageDraw.Draw(char_img)
        cd.text((pad, pad), ch, font=font_obj, fill=fill)
        rotated = char_img.rotate(-mid_angle, resample=Image.BICUBIC, expand=True)
        img.paste(rotated, (int(x - rotated.width / 2), int(y - rotated.height / 2)), rotated)
        angle += ch_arc
    return img


def corner_brackets(draw, xy, size, length, color, width=3):
    """Four L-shaped corner ticks around a rectangular region (viewfinder-style frame)."""
    x0, y0 = xy
    x1, y1 = x0 + size[0], y0 + size[1]
    draw.line([(x0, y0 + length), (x0, y0), (x0 + length, y0)], fill=color, width=width)
    draw.line([(x1 - length, y0), (x1, y0), (x1, y0 + length)], fill=color, width=width)
    draw.line([(x0, y1 - length), (x0, y1), (x0 + length, y1)], fill=color, width=width)
    draw.line([(x1 - length, y1), (x1, y1), (x1, y1 - length)], fill=color, width=width)


def network_dots(draw, xy, size, color, count=14, seed=0, dot_r=3, max_line_dist=95):
    """A small decorative dot-and-line 'network' cluster, for corner accents."""
    import random
    rnd = random.Random(seed)
    x0, y0 = xy
    w, h = size
    pts = [(x0 + rnd.uniform(0, w), y0 + rnd.uniform(0, h)) for _ in range(count)]
    for i, (px, py) in enumerate(pts):
        for (qx, qy) in pts[i + 1:]:
            d = ((px - qx) ** 2 + (py - qy) ** 2) ** 0.5
            if d < max_line_dist:
                draw.line([(px, py), (qx, qy)], fill=color, width=1)
    for (px, py) in pts:
        draw.ellipse([px - dot_r, py - dot_r, px + dot_r, py + dot_r], fill=color)


def diagonal_arrow(draw, xy, size, color, width=4):
    """A small ↘-style diagonal arrow glyph (used as a bullet instead of a FontAwesome icon)."""
    x, y = xy
    draw.line([(x, y), (x + size, y + size)], fill=color, width=width)
    draw.line([(x + size, y + size - size * 0.45), (x + size, y + size)], fill=color, width=width)


def diagonal_stripes(size, bg_color, stripe_color, stripe_w=26, gap=54):
    """Subtle diagonal-stripe texture background (bg with faint diagonal bands
    drawn across it), used behind the 'ticket/stamp' style templates."""
    w, h = size
    img = Image.new("RGBA", (w, h), bg_color + (255,) if len(bg_color) == 3 else bg_color)
    d = ImageDraw.Draw(img)
    period = stripe_w + gap
    span = w + h
    n = span // period + 2
    for i in range(-2, n):
        x0 = i * period - h
        d.line([(x0, h), (x0 + h, 0)], fill=stripe_color, width=stripe_w)
    return img.convert("RGB")


def ribbon_banner(img, xy, text, fill, text_color, font_obj, angle=-5, pad_x=26, pad_y=14):
    """A short banner of text rotated slightly (a 'torn ticket stub' ribbon look),
    composited onto img at xy (top-left of the banner's bounding box)."""
    meas = Image.new("RGB", (1, 1))
    md = ImageDraw.Draw(meas)
    tw = md.textlength(text, font=font_obj)
    asc, desc = font_obj.getmetrics()
    bw, bh = int(tw + pad_x * 2), int(asc + desc + pad_y * 2)
    banner = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    bd = ImageDraw.Draw(banner)
    bd.rectangle([0, 0, bw, bh], fill=fill)
    bd.text((pad_x, pad_y), text, font=font_obj, fill=text_color)
    rotated = banner.rotate(angle, resample=Image.BICUBIC, expand=True)
    img.paste(rotated, xy, rotated)
    return rotated.size


def starburst(size, color, points=12, inner_ratio=0.72):
    """A spiky starburst/sticker badge shape (alternating inner/outer radius
    polygon) -- used for 'NO AGENCY FEES' / 'GUARANTEED' sticker-style badges."""
    w, h = size
    cx, cy = w / 2, h / 2
    r_out = min(w, h) / 2
    r_in = r_out * inner_ratio
    pts = []
    n = points * 2
    for i in range(n):
        ang = math.pi * 2 * i / n - math.pi / 2
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon(pts, fill=color)
    return img


def stamp_frame(photo_img, size, border=16, label=None, font_obj=None, label_color=(20, 40, 40)):
    """Composite a photo onto a white 'postage stamp' card: thick white border,
    small perforation dots along the inner edge, and an optional caption label
    printed in the bottom margin (like a photo souvenir stamp)."""
    w, h = size
    label_h = 46 if label else 0
    card = Image.new("RGB", (w, h + label_h), (255, 255, 255))
    photo = cover_resize(photo_img, w - border * 2, h - border * 2)
    card.paste(photo, (border, border))
    d = ImageDraw.Draw(card)
    # perforation dots tracing the border seam
    dot_r = 3
    step = 14
    seam = border - 7
    for x in range(seam, w - seam, step):
        d.ellipse([x - dot_r, seam - dot_r, x + dot_r, seam + dot_r], fill=(225, 225, 225))
        d.ellipse([x - dot_r, h - seam - dot_r, x + dot_r, h - seam + dot_r], fill=(225, 225, 225))
    for y in range(seam, h - seam, step):
        d.ellipse([seam - dot_r, y - dot_r, seam + dot_r, y + dot_r], fill=(225, 225, 225))
        d.ellipse([w - seam - dot_r, y - dot_r, w - seam + dot_r, y + dot_r], fill=(225, 225, 225))
    if label and font_obj:
        tw = d.textlength(label, font=font_obj)
        d.text(((w - tw) / 2, h + label_h / 2 - 12), label, font=font_obj, fill=label_color)
    return card


def arch_photo(photo_img, size, arch_ratio=0.55):
    """A photo cropped to fill a rounded-arch shape (flat sides + bottom,
    rounded/domed top) -- like a museum placard or church-window photo frame."""
    w, h = size
    photo = cover_resize(photo_img, w, h).convert("RGB")
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    arch_h = int(w * arch_ratio / 2)
    md.rectangle([0, arch_h, w, h], fill=255)
    md.pieslice([0, 0, w, arch_h * 2], 180, 360, fill=255)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(photo, (0, 0), mask)
    return out


def arch_outline(draw, xy, size, arch_ratio, color, width=2):
    """Outline that traces the exact same boundary as `arch_photo`'s mask
    (flat sides, sharp bottom corners, a domed/arched top) -- draw this
    around an arch_photo so the border hugs the photo with no gap, instead
    of a generic rounded-rectangle whose corner radius won't match the
    arch's actual curve."""
    x, y = xy
    w, h = size
    arch_h = int(w * arch_ratio / 2)
    draw.line([(x, y + arch_h), (x, y + h)], fill=color, width=width)
    draw.line([(x + w, y + arch_h), (x + w, y + h)], fill=color, width=width)
    draw.line([(x, y + h), (x + w, y + h)], fill=color, width=width)
    draw.arc([x, y, x + w, y + arch_h * 2], 180, 360, fill=color, width=width)


def luggage_tag_shape(size, fill, radius=28):
    """A rounded-rect card with a small punched hole near the top-center and a
    short strap loop above it, used as the base card for the 'luggage tag'
    style poster -- returns an RGBA image with the card + hole cut transparent."""
    w, h = size
    hole_r = 14
    hole_cy = 46
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, hole_cy + hole_r + 14, w, h], radius=radius, fill=fill)
    cx = w / 2
    d.ellipse([cx - hole_r - 6, hole_cy - hole_r - 6, cx + hole_r + 6, hole_cy + hole_r + 6], fill=fill)
    # punch the hole transparent
    d.ellipse([cx - hole_r, hole_cy - hole_r, cx + hole_r, hole_cy + hole_r], fill=(0, 0, 0, 0))
    return card, (int(cx), hole_cy)
    draw.line([(x + size - size * 0.45, y + size), (x + size, y + size)], fill=color, width=width)


def glow_vertical_text(strip_h, text, fill=(255, 255, 255), glow_color=(255, 255, 255, 160),
                        glow_blur=16, font_name="poppins-bold", max_size=140, min_size=28, pad=24):
    """Big bold text with a soft neon-style glow behind it, rotated 90° to run
    bottom-to-top -- used for a glowing vertical sidebar strip of text.
    `strip_h` is the available height (post-rotation) the text must fit into;
    font size auto-shrinks until the (pre-rotation) text width fits."""
    tmp = Image.new("RGB", (1, 1))
    td = ImageDraw.Draw(tmp)
    fsize = max_size
    fnt = font(font_name, fsize)
    tw = td.textlength(text, font=fnt)
    while tw > strip_h - pad * 2 and fsize > min_size:
        fsize -= 2
        fnt = font(font_name, fsize)
        tw = td.textlength(text, font=fnt)
    asc, desc = fnt.getmetrics()
    th = asc + desc
    canvas = Image.new("RGBA", (int(tw) + pad * 2, th + pad * 2), (0, 0, 0, 0))
    glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text((pad, pad), text, font=fnt, fill=glow_color)
    glow = glow.filter(ImageFilter.GaussianBlur(glow_blur))
    sharp = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sharp)
    sd.text((pad, pad), text, font=fnt, fill=fill)
    combined = Image.alpha_composite(glow, sharp)
    rotated = combined.rotate(90, expand=True, resample=Image.BICUBIC)
    return rotated
