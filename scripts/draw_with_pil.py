#!/usr/bin/env python3
"""
Draw with PIL — Template for creating images programmatically.

Usage:
    python draw_with_pil.py --output "my-image.png" --width 512 --height 512
    python draw_with_pil.py --demo robot --output "robot.png"

This script provides reusable drawing functions for common shapes, effects, and styles.
"""

import sys
import os
import argparse
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def create_canvas(width=512, height=512, bg_color=(255, 255, 255, 255)):
    """Create a new RGBA canvas."""
    return Image.new('RGBA', (width, height), bg_color)


def draw_shadow(draw, img, x, y, w, h, radius=8, opacity=60, offset=(4, 4)):
    """Draw a soft shadow behind a shape."""
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(
        [x + offset[0], y + offset[1], x + w + offset[0], y + h + offset[1]],
        radius=radius, fill=(0, 0, 0, opacity)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=radius))
    img.paste(shadow, (0, 0), shadow)


def gradient_rect(draw, img, x, y, w, h, color_start, color_end, direction='vertical'):
    """Draw a gradient-filled rectangle."""
    for i in range(w if direction == 'horizontal' else h):
        t = i / (w if direction == 'horizontal' else h)
        color = tuple(int(color_start[j] * (1 - t) + color_end[j] * t) for j in range(3))
        if direction == 'vertical':
            draw.line([(x, y + i), (x + w, y + i)], fill=color + (255,))
        else:
            draw.line([(x + i, y), (x + i, y + h)], fill=color + (255,))


def gradient_circle(draw, img, cx, cy, r, color_inner, color_outer):
    """Draw a radial gradient circle."""
    for i in range(r, 0, -1):
        t = i / r
        color = tuple(int(color_inner[j] * t + color_outer[j] * (1 - t)) for j in range(3))
        draw.ellipse([cx - i, cy - i, cx + i, cy + i], fill=color + (255,))


def glow(draw, img, cx, cy, r, color, intensity=80, blur=15):
    """Draw a glow effect around a point."""
    glow_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    for i in range(r, 0, -1):
        t = i / r
        alpha = int(intensity * (1 - t))
        gd.ellipse([cx - i, cy - i, cx + i, cy + i], fill=color + (alpha,))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=blur))
    img.paste(glow_layer, (0, 0), glow_layer)


def draw_robot_demo(img, style="classic"):
    """Draw a demo green robot."""
    draw = ImageDraw.Draw(img)
    W, H = img.size

    if style == "classic":
        # Body
        body_x, body_y, body_w, body_h = W//4, H//3, W//2, H//2
        draw_shadow(draw, img, body_x, body_y, body_w, body_h, radius=15)
        draw.rounded_rectangle([body_x, body_y, body_x + body_w, body_y + body_h],
                              radius=30, fill=(46, 204, 113), outline=(26, 156, 84), width=3)

        # Body highlight
        hl = Image.new('RGBA', img.size, (0, 0, 0, 0))
        hld = ImageDraw.Draw(hl)
        hld.rounded_rectangle([body_x + 15, body_y + 10, body_x + 60, body_y + body_h - 10],
                             radius=20, fill=(88, 214, 141, 100))
        img.paste(hl, (0, 0), hl)

        # Chest light
        cx, cy = body_x + body_w//2, body_y + 50
        glow(draw, img, cx, cy, 30, (241, 196, 15), intensity=60, blur=10)
        gradient_circle(draw, img, cx, cy, 18, (241, 196, 15), (212, 172, 13))
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(249, 231, 159))

        # Head
        head_x, head_y, head_w, head_h = W//4 + 10, H//6, W//2 - 20, H//4
        draw_shadow(draw, img, head_x, head_y, head_w, head_h, radius=20)
        draw.rounded_rectangle([head_x, head_y, head_x + head_w, head_y + head_h],
                              radius=40, fill=(39, 174, 96), outline=(26, 156, 84), width=3)

        # Antenna
        ant_x = head_x + head_w//2
        draw.rectangle([ant_x - 5, head_y - 30, ant_x + 5, head_y + 5], fill=(26, 156, 84))
        gradient_circle(draw, img, ant_x, head_y - 35, 12, (231, 76, 60), (192, 57, 43))

        # Eyes
        eye_y = head_y + head_h//2 - 5
        for ex in [head_x + head_w//3, head_x + 2*head_w//3]:
            draw.ellipse([ex - 22, eye_y - 25, ex + 22, eye_y + 25],
                        fill=(255, 255, 255), outline=(26, 156, 84), width=2)
            draw.ellipse([ex + 2, eye_y - 3, ex + 20, eye_y + 15], fill=(44, 62, 80))
            draw.ellipse([ex + 12, eye_y - 8, ex + 18, eye_y - 2], fill=(255, 255, 255))

        # Smile
        draw.arc([head_x + 40, eye_y + 20, head_x + head_w - 40, eye_y + 60],
                start=10, end=170, fill=(26, 156, 84), width=3)

        # Arms
        arm_y = body_y + 30
        for side in [-1, 1]:
            ax = body_x - 50 if side == -1 else body_x + body_w
            draw.rounded_rectangle([ax, arm_y, ax + 50 * side, arm_y + 20],
                                  radius=10, fill=(39, 174, 96), outline=(26, 156, 84), width=2)
            hx = body_x - 55 if side == -1 else body_x + body_w + 55
            gradient_circle(draw, img, hx, arm_y + 10, 20, (46, 204, 113), (39, 174, 96))

        # Legs
        leg_y = body_y + body_h
        for lx in [body_x + 20, body_x + body_w - 55]:
            draw.rounded_rectangle([lx, leg_y, lx + 35, leg_y + 60],
                                  radius=10, fill=(39, 174, 96), outline=(26, 156, 84), width=2)
            draw.rounded_rectangle([lx - 10, leg_y + 55, lx + 45, leg_y + 75],
                                  radius=8, fill=(26, 156, 84))

    return img


def main():
    parser = argparse.ArgumentParser(description="Draw with PIL")
    parser.add_argument("--output", type=str, default="output.png", help="Output file path")
    parser.add_argument("--width", type=int, default=512, help="Image width")
    parser.add_argument("--height", type=int, default=640, help="Image height")
    parser.add_argument("--demo", type=str, choices=["robot"], default="robot",
                        help="Demo to draw")
    parser.add_argument("--bg", type=str, default="240,248,240", help="Background color (r,g,b)")
    args = parser.parse_args()

    bg = tuple(int(x) for x in args.bg.split(','))
    img = create_canvas(args.width, args.height, bg + (255,))

    if args.demo == "robot":
        draw_robot_demo(img)

    img.save(args.output)
    print(f"Saved: {args.output} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
