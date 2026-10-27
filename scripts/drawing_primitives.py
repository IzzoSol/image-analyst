"""Shared drawing primitives for image-analyst scripts."""

import math
import random
from PIL import Image, ImageDraw, ImageFilter


def create_canvas(w, h, bg=(255, 255, 255)):
    return Image.new('RGBA', (w, h), bg + (255,))


def soft_shadow(img, x, y, w, h, radius=10, opacity=50, offset=(5, 5), corner_r=15):
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(
        [x + offset[0], y + offset[1], x + w + offset[0], y + h + offset[1]],
        radius=corner_r, fill=(0, 0, 0, opacity)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=radius))
    img.paste(shadow, (0, 0), shadow)


def gradient_circle(draw, img, cx, cy, r, inner, outer):
    for i in range(r, 0, -1):
        t = i / r
        color = tuple(int(inner[j] * t + outer[j] * (1 - t)) for j in range(3))
        draw.ellipse([cx - i, cy - i, cx + i, cy + i], fill=color + (255,))


def glow_effect(img, cx, cy, r, color, intensity=80, blur=12):
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for i in range(r, 0, -1):
        t = i / r
        alpha = int(intensity * (1 - t) * (1 - t))
        ld.ellipse([cx - i, cy - i, cx + i, cy + i], fill=color + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(radius=blur))
    img.paste(layer, (0, 0), layer)


def hard_shadow(img, x, y, w, h, color=(0, 0, 0, 80), offset=(8, 8), corner_r=0):
    d = ImageDraw.Draw(img)
    if corner_r > 0:
        d.rounded_rectangle([x + offset[0], y + offset[1], x + w + offset[0], y + h + offset[1]],
                           radius=corner_r, fill=color)
    else:
        d.rectangle([x + offset[0], y + offset[1], x + w + offset[0], y + h + offset[1]], fill=color)


def gradient_mesh(draw, img, x, y, w, h, colors, direction='vertical'):
    stops = len(colors)
    for i in range(h if direction == 'vertical' else w):
        t = i / (h if direction == 'vertical' else w)
        seg = min(int(t * (stops - 1)), stops - 2)
        seg_t = t * (stops - 1) - seg
        c1 = colors[seg]
        c2 = colors[seg + 1]
        color = tuple(int(c1[j] * (1 - seg_t) + c2[j] * seg_t) for j in range(3))
        if direction == 'vertical':
            draw.line([(x, y + i), (x + w, y + i)], fill=color + (255,))
        else:
            draw.line([(x + i, y), (x + i, y + h)], fill=color + (255,))


def ambient_occlusion(img, x, y, w, h, corner_r=20, intensity=40):
    ao = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ad = ImageDraw.Draw(ao)
    for i in range(8):
        alpha = int(intensity * (1 - i / 8))
        ad.rounded_rectangle(
            [x + i, y + i, x + w - i, y + h - i],
            radius=max(1, corner_r - i), fill=(0, 0, 0, alpha)
        )
    ao = ao.filter(ImageFilter.GaussianBlur(radius=6))
    img.paste(ao, (0, 0), ao)


def specular_highlight(img, cx, cy, r, color=(255, 255, 255), intensity=180):
    hl = Image.new('RGBA', img.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(hl)
    for i in range(r, 0, -1):
        t = i / r
        alpha = int(intensity * (1 - t) * (1 - t))
        hd.ellipse([cx - i, cy - i, cx + i, cy + i], fill=color + (alpha,))
    hl = hl.filter(ImageFilter.GaussianBlur(radius=2))
    img.paste(hl, (0, 0), hl)


def rim_light(img, x, y, w, h, corner_r=20, color=(255, 255, 255), intensity=80):
    rim = Image.new('RGBA', img.size, (0, 0, 0, 0))
    rd = ImageDraw.Draw(rim)
    for i in range(3):
        alpha = int(intensity * (1 - i / 3))
        rd.rounded_rectangle(
            [x - 2 + i, y - 2 + i, x + w + 2 - i, y + h + 2 - i],
            radius=corner_r + 2, fill=(0, 0, 0, 0), outline=color + (alpha,), width=2
        )
    rim = rim.filter(ImageFilter.GaussianBlur(radius=3))
    img.paste(rim, (0, 0), rim)


def hatching(img, x, y, w, h, angle=45, spacing=4, opacity=60, color=(80, 80, 80)):
    mask = Image.new('L', img.size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([x, y, x + w, y + h], radius=5, fill=255)
    rad = math.radians(angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    diag = int(math.sqrt(w*w + h*h)) + 20
    temp = Image.new('RGBA', img.size, (0, 0, 0, 0))
    td = ImageDraw.Draw(temp)
    for i in range(-diag, diag, spacing):
        x1 = x + w//2 + i * cos_a - diag * sin_a
        y1 = y + h//2 + i * sin_a - diag * cos_a
        x2 = x + w//2 + i * cos_a + diag * sin_a
        y2 = y + h//2 + i * sin_a + diag * cos_a
        td.line([(x1, y1), (x2, y2)], fill=color + (opacity,), width=1)
    temp.putalpha(mask)
    img.paste(temp, (0, 0), temp)


def stippling(img, x, y, w, h, density=0.3, color=(80, 80, 80)):
    draw = ImageDraw.Draw(img)
    for _ in range(int(w * h * density)):
        px = random.randint(x, x + w - 1)
        py = random.randint(y, y + h - 1)
        size = random.choice([1, 1, 1, 2])
        draw.ellipse([px, py, px + size, py + size], fill=color + (random.randint(40, 120),))


def multi_pass_shadow(img, x, y, w, h, corner_r=20, passes=3):
    for i in range(passes, 0, -1):
        shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        spread = i * 3
        opacity = 20 + i * 10
        sd.rounded_rectangle(
            [x + 4 + i, y + 4 + i, x + w + 4 + i, y + h + 4 + i],
            radius=corner_r + i, fill=(0, 0, 0, opacity)
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=4 + i * 2))
        img.paste(shadow, (0, 0), shadow)


def draw_organic_limb(draw, img, start, end, width_start, width_end, 
                      color_base, color_shadow, color_highlight, 
                      bend=0, segments=20):
    """Draw a limb with organic tapering and shading."""
    sx, sy = start
    ex, ey = end
    
    # Calculate perpendicular direction
    dx = ex - sx
    dy = ey - sy
    length = math.sqrt(dx*dx + dy*dy)
    if length == 0:
        return
    nx = -dy / length
    ny = dx / length
    
    # Build outline points
    left_points = []
    right_points = []
    
    for i in range(segments + 1):
        t = i / segments
        # Position along limb
        px = sx + dx * t
        py = sy + dy * t
        # Bend
        px += bend * math.sin(t * math.pi) * nx
        py += bend * math.sin(t * math.pi) * ny
        # Width
        w = width_start * (1 - t) + width_end * t
        left_points.append((px + nx * w / 2, py + ny * w / 2))
        right_points.append((px - nx * w / 2, py - ny * w / 2))
    
    # Fill
    polygon = left_points + right_points[::-1]
    draw.polygon(polygon, fill=color_base)
    
    # Shading gradient (shadow on one side)
    for i in range(len(left_points) - 1):
        t = i / (len(left_points) - 1)
        w = width_start * (1 - t) + width_end * t
        # Shadow side
        shadow_color = tuple(int(color_base[j] * 0.7 + color_shadow[j] * 0.3) for j in range(3))
        draw.line([left_points[i], left_points[i+1]], fill=shadow_color + (180,), width=2)
    
    # Highlight
    for i in range(len(right_points) - 1):
        t = i / (len(right_points) - 1)
        hl_color = tuple(int(color_base[j] * 0.85 + color_highlight[j] * 0.15) for j in range(3))
        draw.line([right_points[i], right_points[i+1]], fill=hl_color + (120,), width=1)


