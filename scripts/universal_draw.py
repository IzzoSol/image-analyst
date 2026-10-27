#!/usr/bin/env python3
"""
Universal Drawing Engine — Draw any subject in any style.

Usage:
    python universal_draw.py --subject robot --style 3d_render --output robot.png
    python universal_draw.py --subject robot --style pixel_art --output robot_px.png --size 64
    python universal_draw.py --subject robot --style sketch --output robot_sketch.png
    python universal_draw.py --subject robot --style watercolor --output robot_wc.png
    python universal_draw.py --subject robot --style flat_vector --output robot_fv.png
    python universal_draw.py --subject robot --style chibi --output robot_chibi.png
    python universal_draw.py --list-styles

Supported styles:
    pixel_art, 3d_render, sketch, watercolor, flat_vector, chibi, comic, realistic
"""

import sys
import os
import argparse
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math


# ============================================================
# COLOR PALETTES
# ============================================================

PALETTES = {
    "robot_green": {
        "highlight": (198, 220, 179),
        "light": (130, 174, 95),
        "base": (46, 204, 113),
        "medium": (39, 174, 96),
        "dark": (26, 156, 84),
        "deep": (22, 31, 19),
        "accent": (241, 196, 15),
        "eye": (44, 62, 80),
        "white": (255, 255, 255),
    },
    "gameboy": [(15, 56, 15), (48, 98, 48), (139, 172, 15), (155, 188, 15)],
    "pico8": [(0,0,0),(29,43,83),(126,37,83),(0,135,81),(171,82,54),(95,87,79),
              (194,195,199),(255,241,232),(255,0,77),(255,163,0),(255,236,39),
              (0,228,54),(41,173,255),(131,118,156),(255,119,168),(255,204,170)],
}


# ============================================================
# DRAWING PRIMITIVES
# ============================================================

def create_canvas(w, h, bg=(255, 255, 255)):
    return Image.new('RGBA', (w, h), bg + (255,))


def soft_shadow(img, x, y, w, h, radius=10, opacity=50, offset=(5, 5), corner_r=15):
    """Draw a soft drop shadow."""
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(
        [x + offset[0], y + offset[1], x + w + offset[0], y + h + offset[1]],
        radius=corner_r, fill=(0, 0, 0, opacity)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=radius))
    img.paste(shadow, (0, 0), shadow)


def gradient_circle(draw, img, cx, cy, r, inner, outer):
    """Radial gradient circle."""
    for i in range(r, 0, -1):
        t = i / r
        color = tuple(int(inner[j] * t + outer[j] * (1 - t)) for j in range(3))
        draw.ellipse([cx - i, cy - i, cx + i, cy + i], fill=color + (255,))


def glow_effect(img, cx, cy, r, color, intensity=80, blur=12):
    """Draw a glow around a point."""
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for i in range(r, 0, -1):
        t = i / r
        alpha = int(intensity * (1 - t) * (1 - t))
        ld.ellipse([cx - i, cy - i, cx + i, cy + i], fill=color + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(radius=blur))
    img.paste(layer, (0, 0), layer)


def hard_shadow(img, x, y, w, h, color=(0, 0, 0, 80), offset=(8, 8), corner_r=0):
    """Draw a hard-edged shadow (flat vector style)."""
    d = ImageDraw.Draw(img)
    if corner_r > 0:
        d.rounded_rectangle([x + offset[0], y + offset[1], x + w + offset[0], y + h + offset[1]],
                           radius=corner_r, fill=color)
    else:
        d.rectangle([x + offset[0], y + offset[1], x + w + offset[0], y + h + offset[1]], fill=color)


# ============================================================
# STYLE RENDERERS
# ============================================================

def draw_robot_pixel_art(img):
    """Draw a robot in pixel art style."""
    draw = ImageDraw.Draw(img)
    p = PALETTES["robot_green"]
    W, H = img.size

    # Work on a small grid then scale up
    grid_w, grid_h = 16, 20
    cell = min(W // grid_w, H // grid_h)
    off_x = (W - grid_w * cell) // 2
    off_y = (H - grid_h * cell) // 2

    # Pixel art robot on 16x20 grid
    # Color codes: 0=transparent, 1=highlight, 2=light, 3=base, 4=medium, 5=dark, 6=deep, 7=accent, 8=eye, 9=white
    colors = {
        0: None,
        1: p["highlight"],
        2: p["light"],
        3: p["base"],
        4: p["medium"],
        5: p["dark"],
        6: p["deep"],
        7: p["accent"],
        8: p["eye"],
        9: (255, 255, 255),
        10: (231, 76, 60),
    }

    grid = [
        "     3333     ",
        "    333333    ",
        "   33    33   ",
        "   33 88 33   ",
        "   33 88 33   ",
        "   33    33   ",
        "    333333    ",
        "     3333     ",
        "    444444    ",
        "   44444444   ",
        "  44  77  44  ",
        "  44  77  44  ",
        "  4444444444  ",
        "   44444444   ",
        "  55        55 ",
        "  55        55 ",
        "  55        55 ",
        "  66        66 ",
        " 6666      6666",
        "66666      6666",
    ]

    for gy, row in enumerate(grid):
        for gx, ch in enumerate(row):
            if ch == " ":
                continue
            ci = int(ch)
            color = colors.get(ci)
            if color is None:
                continue
            x = off_x + gx * cell
            y = off_y + gy * cell
            draw.rectangle([x, y, x + cell - 1, y + cell - 1], fill=color + (255,))

    # Outline
    for gy, row in enumerate(grid):
        for gx, ch in enumerate(row):
            if ch == " ":
                continue
            # Check neighbors for outline
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = gx + dx, gy + dy
                if 0 <= ny < len(grid) and 0 <= nx < len(grid[ny]):
                    if grid[ny][nx] == " ":
                        x = off_x + gx * cell
                        y = off_y + gy * cell
                        # Draw outline on this edge
                        if dx == -1:
                            draw.line([(x, y), (x, y + cell - 1)], fill=p["deep"] + (255,), width=1)
                        elif dx == 1:
                            draw.line([(x + cell - 1, y), (x + cell - 1, y + cell - 1)], fill=p["deep"] + (255,), width=1)
                        elif dy == -1:
                            draw.line([(x, y), (x + cell - 1, y)], fill=p["deep"] + (255,), width=1)
                        elif dy == 1:
                            draw.line([(x, y + cell - 1), (x + cell - 1, y + cell - 1)], fill=p["deep"] + (255,), width=1)

    return img


def draw_robot_3d_render(img):
    """Draw a robot in 3D render style (Pixar-like)."""
    draw = ImageDraw.Draw(img)
    p = PALETTES["robot_green"]
    W, H = img.size

    # Proportions: head = 1/4 of height
    head_h = H // 4
    body_h = H // 2
    head_y = H // 8
    body_y = head_y + head_h + 10

    # Body
    body_w = W // 2
    body_x = (W - body_w) // 2
    soft_shadow(img, body_x, body_y, body_w, body_h, radius=15, opacity=60)
    draw.rounded_rectangle([body_x, body_y, body_x + body_w, body_y + body_h],
                          radius=30, fill=p["base"], outline=p["dark"], width=3)
    # Highlight
    hl = Image.new('RGBA', img.size, (0, 0, 0, 0))
    hld = ImageDraw.Draw(hl)
    hld.rounded_rectangle([body_x + 15, body_y + 10, body_x + 50, body_y + body_h - 10],
                         radius=20, fill=p["light"] + (100,))
    img.paste(hl, (0, 0), hl)

    # Chest light
    cx, cy = body_x + body_w // 2, body_y + 50
    glow_effect(img, cx, cy, 35, p["accent"], intensity=70, blur=12)
    gradient_circle(draw, img, cx, cy, 20, p["accent"], (212, 172, 13))
    draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=p["highlight"])

    # Head
    head_w = body_w - 20
    head_x = (W - head_w) // 2
    soft_shadow(img, head_x, head_y, head_w, head_h, radius=20, opacity=50)
    draw.rounded_rectangle([head_x, head_y, head_x + head_w, head_y + head_h],
                          radius=40, fill=p["medium"], outline=p["dark"], width=3)
    hl2 = Image.new('RGBA', img.size, (0, 0, 0, 0))
    hld2 = ImageDraw.Draw(hl2)
    hld2.rounded_rectangle([head_x + 15, head_y + 10, head_x + 50, head_y + head_h - 10],
                          radius=20, fill=p["light"] + (100,))
    img.paste(hl2, (0, 0), hl2)

    # Antenna
    ant_x = head_x + head_w // 2
    draw.rectangle([ant_x - 6, head_y - 35, ant_x + 6, head_y + 5], fill=p["dark"])
    gradient_circle(draw, img, ant_x, head_y - 40, 14, (231, 76, 60), (192, 57, 43))
    glow_effect(img, ant_x, head_y - 40, 20, (231, 76, 60), intensity=40, blur=8)

    # Eyes
    eye_y = head_y + head_h // 2 - 5
    for ex in [head_x + head_w // 3, head_x + 2 * head_w // 3]:
        draw.ellipse([ex - 24, eye_y - 28, ex + 24, eye_y + 28],
                    fill=p["white"], outline=p["dark"], width=2)
        draw.ellipse([ex + 2, eye_y - 4, ex + 22, eye_y + 16], fill=p["eye"])
        draw.ellipse([ex + 14, eye_y - 10, ex + 20, eye_y - 4], fill=p["white"])
        # Cheek blush
        blush = Image.new('RGBA', img.size, (0, 0, 0, 0))
        bd = ImageDraw.Draw(blush)
        bd.ellipse([ex - 18, eye_y + 20, ex + 18, eye_y + 40], fill=(255, 107, 107, 60))
        blush = blush.filter(ImageFilter.GaussianBlur(radius=6))
        img.paste(blush, (0, 0), blush)

    # Smile
    draw.arc([head_x + 40, eye_y + 25, head_x + head_w - 40, eye_y + 65],
            start=10, end=170, fill=p["dark"], width=3)

    # Arms
    arm_y = body_y + 30
    for side in [-1, 1]:
        if side == -1:
            ax0, ax1 = body_x - 55, body_x
        else:
            ax0, ax1 = body_x + body_w, body_x + body_w + 55
        draw.rounded_rectangle([min(ax0, ax1), arm_y, max(ax0, ax1), arm_y + 22],
                              radius=10, fill=p["medium"], outline=p["dark"], width=2)
        hx = body_x - 60 if side == -1 else body_x + body_w + 60
        gradient_circle(draw, img, hx, arm_y + 11, 22, p["base"], p["medium"])

    # Legs
    leg_y = body_y + body_h
    for lx in [body_x + 20, body_x + body_w - 55]:
        draw.rounded_rectangle([lx, leg_y, lx + 35, leg_y + 65],
                              radius=10, fill=p["medium"], outline=p["dark"], width=2)
        draw.rounded_rectangle([lx - 10, leg_y + 60, lx + 45, leg_y + 80],
                              radius=8, fill=p["dark"])

    # Bolts
    for bx, by in [(body_x + 15, body_y + 40), (body_x + body_w - 15, body_y + 40),
                   (body_x + 15, body_y + body_h - 40), (body_x + body_w - 15, body_y + body_h - 40)]:
        draw.ellipse([bx - 6, by - 6, bx + 6, by + 6], fill=p["dark"], outline=p["deep"], width=2)
        draw.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=p["medium"])

    return img


def draw_robot_sketch(img):
    """Draw a robot in pencil sketch style."""
    draw = ImageDraw.Draw(img)
    p = PALETTES["robot_green"]
    W, H = img.size

    # Light gray background (paper)
    for y in range(H):
        for x in range(W):
            img.putpixel((x, y), (245, 240, 230, 255))

    # Sketch lines with varying weight
    import random
    random.seed(42)

    # Body outline (rough, sketchy)
    body_x, body_y, body_w, body_h = W//4, H//3, W//2, H//2

    # Multiple overlapping lines for sketch effect
    for _ in range(3):
        offset = random.randint(-3, 3)
        draw.rounded_rectangle([body_x + offset, body_y + offset,
                              body_x + body_w + offset, body_y + body_h + offset],
                              radius=30, outline=(80, 80, 80), width=1)

    # Hatching for shading
    for i in range(0, body_h, 4):
        x_start = body_x + 10
        x_end = body_x + body_w - 10
        y = body_y + i
        if i % 8 == 0:
            draw.line([(x_start, y), (x_end, y)], fill=(120, 120, 120), width=1)

    # Head
    head_x, head_y, head_w, head_h = W//4 + 10, H//6, W//2 - 20, H//4
    for _ in range(3):
        offset = random.randint(-3, 3)
        draw.rounded_rectangle([head_x + offset, head_y + offset,
                              head_x + head_w + offset, head_y + head_h + offset],
                              radius=40, outline=(80, 80, 80), width=1)

    # Eyes (sketched circles)
    eye_y = head_y + head_h // 2
    for ex in [head_x + head_w // 3, head_x + 2 * head_w // 3]:
        draw.ellipse([ex - 22, eye_y - 25, ex + 22, eye_y + 25], outline=(60, 60, 60), width=2)
        draw.ellipse([ex + 2, eye_y - 4, ex + 22, eye_y + 16], outline=(40, 40, 40), width=1)

    # Antenna
    ant_x = head_x + head_w // 2
    draw.line([(ant_x, head_y), (ant_x, head_y - 30)], fill=(80, 80, 80), width=2)
    draw.ellipse([ant_x - 12, head_y - 42, ant_x + 12, head_y - 18], outline=(80, 80, 80), width=2)

    # Smile
    draw.arc([head_x + 40, eye_y + 25, head_x + head_w - 40, eye_y + 60],
            start=10, end=170, fill=(80, 80, 80), width=2)

    return img


def draw_robot_flat_vector(img):
    """Draw a robot in flat vector style (bold shapes, no gradients)."""
    draw = ImageDraw.Draw(img)
    p = PALETTES["robot_green"]
    W, H = img.size

    # White background
    draw.rectangle([0, 0, W, H], fill=(255, 255, 255))

    body_x, body_y, body_w, body_h = W//4, H//3, W//2, H//2
    head_x, head_y, head_w, head_h = W//4 + 10, H//6, W//2 - 20, H//4

    # Hard shadow
    hard_shadow(img, body_x, body_y, body_w, body_h, color=(0, 0, 0, 60), offset=(8, 8), corner_r=30)
    hard_shadow(img, head_x, head_y, head_w, head_h, color=(0, 0, 0, 60), offset=(8, 8), corner_r=40)

    # Body (flat color)
    draw.rounded_rectangle([body_x, body_y, body_x + body_w, body_y + body_h],
                          radius=30, fill=p["base"], outline=p["deep"], width=3)

    # Head (flat color)
    draw.rounded_rectangle([head_x, head_y, head_x + head_w, head_y + head_h],
                          radius=40, fill=p["medium"], outline=p["deep"], width=3)

    # Antenna
    ant_x = head_x + head_w // 2
    draw.rectangle([ant_x - 6, head_y - 35, ant_x + 6, head_y + 5], fill=p["dark"])
    draw.ellipse([ant_x - 14, head_y - 49, ant_x + 14, head_y - 21], fill=(231, 76, 60), outline=p["deep"], width=2)

    # Chest light (flat)
    cx, cy = body_x + body_w // 2, body_y + 50
    draw.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=p["accent"], outline=p["deep"], width=2)
    draw.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=(249, 231, 159))

    # Eyes (flat)
    eye_y = head_y + head_h // 2 - 5
    for ex in [head_x + head_w // 3, head_x + 2 * head_w // 3]:
        draw.ellipse([ex - 24, eye_y - 28, ex + 24, eye_y + 28], fill=(255, 255, 255), outline=p["deep"], width=3)
        draw.ellipse([ex + 2, eye_y - 4, ex + 22, eye_y + 16], fill=p["eye"])

    # Smile
    draw.arc([head_x + 40, eye_y + 25, head_x + head_w - 40, eye_y + 65],
            start=10, end=170, fill=p["deep"], width=3)

    # Arms
    arm_y = body_y + 30
    for side in [-1, 1]:
        if side == -1:
            ax0, ax1 = body_x - 55, body_x
        else:
            ax0, ax1 = body_x + body_w, body_x + body_w + 55
        draw.rounded_rectangle([min(ax0, ax1), arm_y, max(ax0, ax1), arm_y + 22],
                              radius=10, fill=p["medium"], outline=p["deep"], width=2)
        hx = body_x - 60 if side == -1 else body_x + body_w + 60
        draw.ellipse([hx - 22, arm_y - 11, hx + 22, arm_y + 33], fill=p["base"], outline=p["deep"], width=2)

    # Legs
    leg_y = body_y + body_h
    for lx in [body_x + 20, body_x + body_w - 55]:
        draw.rounded_rectangle([lx, leg_y, lx + 35, leg_y + 65],
                              radius=10, fill=p["medium"], outline=p["deep"], width=2)
        draw.rounded_rectangle([lx - 10, leg_y + 60, lx + 45, leg_y + 80],
                              radius=8, fill=p["dark"])

    return img


def draw_robot_chibi(img):
    """Draw a robot in chibi style (big head, small body)."""
    draw = ImageDraw.Draw(img)
    p = PALETTES["robot_green"]
    W, H = img.size

    # Background
    draw.rectangle([0, 0, W, H], fill=(240, 248, 240))

    # Chibi proportions: head = 1/2 of height
    head_size = min(W, H) // 2
    head_x = (W - head_size) // 2
    head_y = H // 8
    body_y = head_y + head_size + 5
    body_h = H // 4

    # Body (small)
    body_w = head_size // 2
    body_x = (W - body_w) // 2
    soft_shadow(img, body_x, body_y, body_w, body_h, radius=10, opacity=40, corner_r=15)
    draw.rounded_rectangle([body_x, body_y, body_x + body_w, body_y + body_h],
                          radius=15, fill=p["base"], outline=p["dark"], width=2)

    # Head (big)
    soft_shadow(img, head_x, head_y, head_size, head_size, radius=15, opacity=40, corner_r=head_size//2)
    draw.ellipse([head_x, head_y, head_x + head_size, head_y + head_size],
                fill=p["medium"], outline=p["dark"], width=3)
    # Highlight
    hl = Image.new('RGBA', img.size, (0, 0, 0, 0))
    hld = ImageDraw.Draw(hl)
    hld.ellipse([head_x + 10, head_y + 10, head_x + head_size//3, head_y + head_size//2],
               fill=p["light"] + (100,))
    img.paste(hl, (0, 0), hl)

    # Antenna (small)
    ant_x = head_x + head_size // 2
    draw.line([(ant_x, head_y), (ant_x, head_y - 20)], fill=p["dark"], width=3)
    draw.ellipse([ant_x - 10, head_y - 30, ant_x + 10, head_y - 10], fill=(231, 76, 60), outline=p["deep"], width=2)

    # Eyes (big, sparkly)
    eye_y = head_y + head_size // 2 - 10
    eye_size = head_size // 4
    for ex in [head_x + head_size // 3, head_x + 2 * head_size // 3]:
        draw.ellipse([ex - eye_size, eye_y - eye_size, ex + eye_size, eye_y + eye_size],
                    fill=(255, 255, 255), outline=p["dark"], width=2)
        # Big pupil
        draw.ellipse([ex - eye_size//2, eye_y - eye_size//2, ex + eye_size//2, eye_y + eye_size//2],
                    fill=p["eye"])
        # Sparkle
        draw.ellipse([ex + eye_size//4, eye_y - eye_size//2, ex + eye_size//2, eye_y - eye_size//4],
                    fill=(255, 255, 255))
        draw.ellipse([ex - eye_size//4, eye_y + eye_size//4, ex, eye_y + eye_size//2],
                    fill=(255, 255, 255, 180))

    # Blush
    for ex in [head_x + head_size // 5, head_x + 4 * head_size // 5]:
        blush = Image.new('RGBA', img.size, (0, 0, 0, 0))
        bd = ImageDraw.Draw(blush)
        bd.ellipse([ex - 15, eye_y + 20, ex + 15, eye_y + 40], fill=(255, 107, 107, 80))
        blush = blush.filter(ImageFilter.GaussianBlur(radius=5))
        img.paste(blush, (0, 0), blush)

    # Smile (big, cute)
    draw.arc([head_x + head_size//4, eye_y + 15, head_x + 3*head_size//4, eye_y + 50],
            start=10, end=170, fill=p["dark"], width=3)

    # Tiny arms
    arm_y = body_y + 10
    for side in [-1, 1]:
        ax = body_x - 20 if side == -1 else body_x + body_w
        draw.rounded_rectangle([min(ax, ax + 20*side), arm_y, max(ax, ax + 20*side), arm_y + 12],
                              radius=6, fill=p["medium"], outline=p["dark"], width=1)

    # Tiny legs
    leg_y = body_y + body_h
    for lx in [body_x + 5, body_x + body_w - 25]:
        draw.rounded_rectangle([lx, leg_y, lx + 20, leg_y + 25],
                              radius=8, fill=p["medium"], outline=p["dark"], width=1)

    return img


def draw_robot_watercolor(img):
    """Draw a robot in watercolor style (soft, bleeding edges)."""
    draw = ImageDraw.Draw(img)
    p = PALETTES["robot_green"]
    W, H = img.size

    # Paper texture
    for y in range(H):
        for x in range(W):
            v = 248 + (x * 7 + y * 13) % 8
            img.putpixel((x, y), (v, v - 2, v - 5, 255))

    body_x, body_y, body_w, body_h = W//4, H//3, W//2, H//2
    head_x, head_y, head_w, head_h = W//4 + 10, H//6, W//2 - 20, H//4

    # Watercolor: multiple semi-transparent layers
    for layer in range(3):
        offset = layer * 3
        alpha = 40 + layer * 20
        layer_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer_img)
        # Body wash
        ld.rounded_rectangle([body_x - offset, body_y - offset,
                            body_x + body_w + offset, body_y + body_h + offset],
                           radius=30 + offset, fill=p["base"] + (alpha,))
        # Head wash
        ld.rounded_rectangle([head_x - offset, head_y - offset,
                            head_x + head_w + offset, head_y + head_h + offset],
                           radius=40 + offset, fill=p["medium"] + (alpha,))
        layer_img = layer_img.filter(ImageFilter.GaussianBlur(radius=8 + layer * 3))
        img.paste(layer_img, (0, 0), layer_img)

    # Details (darker, sharper)
    detail = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(detail)
    # Eyes
    eye_y = head_y + head_h // 2 - 5
    for ex in [head_x + head_w // 3, head_x + 2 * head_w // 3]:
        dd.ellipse([ex - 20, eye_y - 22, ex + 20, eye_y + 22], fill=p["eye"] + (180,))
    # Smile
    dd.arc([head_x + 40, eye_y + 25, head_x + head_w - 40, eye_y + 60],
          start=10, end=170, fill=p["deep"] + (150,), width=2)
    detail = detail.filter(ImageFilter.GaussianBlur(radius=2))
    img.paste(detail, (0, 0), detail)

    # Antenna
    ant_x = head_x + head_w // 2
    draw.line([(ant_x, head_y), (ant_x, head_y - 30)], fill=p["dark"] + (150,), width=2)
    draw.ellipse([ant_x - 12, head_y - 42, ant_x + 12, head_y - 18], fill=(231, 76, 60, 150))

    return img


STYLES = {
    "3d_render": draw_robot_3d_render,
    "pixel_art": draw_robot_pixel_art,
    "sketch": draw_robot_sketch,
    "flat_vector": draw_robot_flat_vector,
    "chibi": draw_robot_chibi,
    "watercolor": draw_robot_watercolor,
}


def draw_subject(subject, style, width=512, height=512):
    """Draw a subject in the specified style."""
    if subject != "robot":
        raise ValueError(f"Unknown subject: {subject}. Currently supports: robot")
    if style not in STYLES:
        raise ValueError(f"Unknown style: {style}. Available: {list(STYLES.keys())}")

    img = create_canvas(width, height)
    STYLES[style](img)
    return img


def main():
    parser = argparse.ArgumentParser(description="Universal Drawing Engine")
    parser.add_argument("--subject", type=str, default="robot", help="Subject to draw")
    parser.add_argument("--style", type=str, default="3d_render", help="Art style")
    parser.add_argument("--output", type=str, default="output.png", help="Output file")
    parser.add_argument("--width", type=int, default=512, help="Image width")
    parser.add_argument("--height", type=int, default=512, help="Image height")
    parser.add_argument("--list-styles", action="store_true", help="List available styles")
    args = parser.parse_args()

    if args.list_styles:
        print("Available styles:")
        for s in STYLES:
            print(f"  - {s}")
        print(f"\nAvailable subjects: robot")
        return

    img = draw_subject(args.subject, args.style, args.width, args.height)
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    img.save(args.output)
    print(f"Saved: {args.output} ({img.size[0]}x{img.size[1]}) — style: {args.style}")


if __name__ == "__main__":
    main()
