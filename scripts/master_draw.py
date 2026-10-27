#!/usr/bin/env python3
"""
Master Draw — Create high-quality illustrations from scratch.

Usage:
    python master_draw.py --subject robot --style master_render --output robot.png
    python master_draw.py --subject robot --style master_sketch --output robot.png
    python master_draw.py --list-styles
"""

import sys
import os
import argparse
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

random.seed(42)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drawing_primitives import *


def master_robot_3d(img):
    """Master-level 3D render with all techniques."""
    draw = ImageDraw.Draw(img)
    W, H = img.size
    p = {
        "highlight": (210, 240, 200),
        "light": (130, 190, 100),
        "base": (46, 204, 113),
        "medium": (39, 174, 96),
        "dark": (26, 156, 84),
        "deep": (22, 60, 35),
        "accent": (241, 196, 15),
        "eye": (44, 62, 80),
        "white": (255, 255, 255),
    }

    head_h = int(H * 0.22)
    body_h = int(H * 0.35)
    head_y = int(H * 0.08)
    body_y = head_y + head_h + 8
    body_w = int(W * 0.42)
    body_x = (W - body_w) // 2
    head_w = int(body_w * 0.9)
    head_x = (W - head_w) // 2

    # === BODY ===
    multi_pass_shadow(img, body_x, body_y, body_w, body_h, corner_r=25)
    gradient_mesh(draw, img, body_x, body_y, body_w, body_h,
                  [p["light"], p["base"], p["medium"], p["dark"]], 'vertical')
    draw.rounded_rectangle([body_x, body_y, body_x + body_w, body_y + body_h],
                          radius=25, outline=p["deep"], width=3)
    ambient_occlusion(img, body_x, body_y, body_w, body_h, corner_r=25, intensity=30)
    rim_light(img, body_x, body_y, body_w, body_h, corner_r=25, color=p["highlight"], intensity=60)
    specular_highlight(img, body_x + body_w // 3, body_y + 20, 30, p["white"], 120)

    draw.line([(body_x + body_w // 2, body_y + 15), (body_x + body_w // 2, body_y + body_h - 15)],
              fill=p["dark"] + (100,), width=2)
    draw.line([(body_x + 15, body_y + body_h // 2), (body_x + body_w - 15, body_y + body_h // 2)],
              fill=p["dark"] + (100,), width=2)

    cx, cy = body_x + body_w // 2, body_y + int(body_h * 0.25)
    glow_effect(img, cx, cy, 40, p["accent"], intensity=90, blur=15)
    gradient_circle(draw, img, cx, cy, 22, p["accent"], (200, 160, 10))
    specular_highlight(img, cx - 5, cy - 5, 8, (255, 255, 200), 200)
    draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=p["highlight"])

    # === HEAD ===
    multi_pass_shadow(img, head_x, head_y, head_w, head_h, corner_r=35)
    gradient_mesh(draw, img, head_x, head_y, head_w, head_h,
                  [p["light"], p["medium"], p["dark"]], 'vertical')
    draw.rounded_rectangle([head_x, head_y, head_x + head_w, head_y + head_h],
                          radius=35, outline=p["deep"], width=3)
    ambient_occlusion(img, head_x, head_y, head_w, head_h, corner_r=35, intensity=25)
    rim_light(img, head_x, head_y, head_w, head_h, corner_r=35, color=p["highlight"], intensity=50)
    specular_highlight(img, head_x + head_w // 3, head_y + 15, 25, p["white"], 100)

    ant_x = head_x + head_w // 2
    for i in range(head_y - 40, head_y + 5):
        t = (i - (head_y - 40)) / 45
        color = tuple(int(p["dark"][j] * (1 - t) + p["medium"][j] * t) for j in range(3))
        draw.line([(ant_x - 5, i), (ant_x + 5, i)], fill=color + (255,), width=1)
    gradient_circle(draw, img, ant_x, head_y - 45, 16, (231, 76, 60), (160, 40, 30))
    specular_highlight(img, ant_x - 4, head_y - 49, 6, (255, 150, 150), 180)
    glow_effect(img, ant_x, head_y - 45, 25, (231, 76, 60), intensity=50, blur=10)

    eye_y = head_y + int(head_h * 0.45)
    for ex in [head_x + int(head_w * 0.3), head_x + int(head_w * 0.7)]:
        draw.ellipse([ex - 26, eye_y - 30, ex + 26, eye_y + 30],
                    fill=p["deep"], outline=p["deep"], width=2)
        draw.ellipse([ex - 24, eye_y - 28, ex + 24, eye_y + 28], fill=p["white"])
        gradient_circle(draw, img, ex + 4, eye_y + 2, 14, p["eye"], (20, 30, 50))
        draw.ellipse([ex + 8, eye_y - 2, ex + 20, eye_y + 14], fill=(10, 15, 25))
        specular_highlight(img, ex + 16, eye_y - 6, 5, (255, 255, 255), 220)
        specular_highlight(img, ex + 6, eye_y + 8, 3, (255, 255, 255), 120)
        blush = Image.new('RGBA', img.size, (0, 0, 0, 0))
        bd = ImageDraw.Draw(blush)
        bd.ellipse([ex - 20, eye_y + 22, ex + 20, eye_y + 45], fill=(255, 107, 107, 50))
        blush = blush.filter(ImageFilter.GaussianBlur(radius=8))
        img.paste(blush, (0, 0), blush)

    draw.arc([head_x + 30, eye_y + 25, head_x + head_w - 30, eye_y + 60],
            start=10, end=170, fill=p["deep"], width=3)

    arm_y = body_y + int(body_h * 0.15)
    for side in [-1, 1]:
        if side == -1:
            ax0, ax1 = body_x - 60, body_x
        else:
            ax0, ax1 = body_x + body_w, body_x + body_w + 60
        draw.rounded_rectangle([min(ax0, ax1), arm_y, max(ax0, ax1), arm_y + 24],
                              radius=10, fill=p["medium"], outline=p["deep"], width=2)
        ambient_occlusion(img, min(ax0, ax1), arm_y, abs(ax1 - ax0), 24, corner_r=10, intensity=20)
        hx = body_x - 65 if side == -1 else body_x + body_w + 65
        gradient_circle(draw, img, hx, arm_y + 12, 24, p["base"], p["medium"])
        specular_highlight(img, hx - 5, arm_y + 7, 8, p["white"], 120)
        draw.ellipse([hx - 6, arm_y + 6, hx + 6, arm_y + 18], fill=p["dark"])

    leg_y = body_y + body_h
    for lx in [body_x + 15, body_x + body_w - 50]:
        draw.rounded_rectangle([lx, leg_y, lx + 35, leg_y + int(H * 0.12)],
                              radius=10, fill=p["medium"], outline=p["deep"], width=2)
        ambient_occlusion(img, lx, leg_y, 35, int(H * 0.12), corner_r=10, intensity=20)
        draw.rounded_rectangle([lx - 10, leg_y + int(H * 0.12) - 5, lx + 45, leg_y + int(H * 0.12) + 20],
                              radius=8, fill=p["dark"], outline=p["deep"], width=2)

    for bx, by in [(body_x + 15, body_y + 35), (body_x + body_w - 15, body_y + 35),
                   (body_x + 15, body_y + body_h - 35), (body_x + body_w - 15, body_y + body_h - 35)]:
        gradient_circle(draw, img, bx, by, 7, p["dark"], p["deep"])
        specular_highlight(img, bx - 2, by - 2, 3, p["white"], 150)

    stippling(img, body_x + 5, body_y + body_h // 2, body_w - 10, body_h // 3,
              density=0.02, color=p["deep"])

    return img


def master_robot_sketch(img):
    """Master-level sketch with hatching and line work (fast version)."""
    draw = ImageDraw.Draw(img)
    W, H = img.size

    # Paper texture (fast - use rectangle fill instead of putpixel)
    draw.rectangle([0, 0, W, H], fill=(245, 242, 235))

    p = {
        "highlight": (210, 240, 200),
        "light": (130, 190, 100),
        "base": (46, 204, 113),
        "medium": (39, 174, 96),
        "dark": (26, 156, 84),
        "deep": (22, 60, 35),
        "accent": (241, 196, 15),
        "eye": (44, 62, 80),
        "white": (255, 255, 255),
    }

    head_h = int(H * 0.22)
    body_h = int(H * 0.35)
    head_y = int(H * 0.08)
    body_y = head_y + head_h + 8
    body_w = int(W * 0.42)
    body_x = (W - body_w) // 2
    head_w = int(body_w * 0.9)
    head_x = (W - head_w) // 2

    # Body hatching (single pass, wider spacing)
    hatching(img, body_x + body_w // 2, body_y, body_w // 2, body_h,
             angle=45, spacing=5, opacity=35, color=(70, 70, 70))

    # Body outline
    for _ in range(3):
        off = random.randint(-2, 2)
        draw.rounded_rectangle([body_x + off, body_y + off,
                              body_x + body_w + off, body_y + body_h + off],
                              radius=25, outline=(60, 60, 60), width=1)

    # Head hatching
    hatching(img, head_x + head_w // 2, head_y, head_w // 2, head_h,
             angle=45, spacing=5, opacity=30, color=(70, 70, 70))
    for _ in range(3):
        off = random.randint(-2, 2)
        draw.rounded_rectangle([head_x + off, head_y + off,
                              head_x + head_w + off, head_y + head_h + off],
                              radius=35, outline=(60, 60, 60), width=1)

    # Antenna
    ant_x = head_x + head_w // 2
    for _ in range(2):
        off = random.randint(-1, 1)
        draw.line([(ant_x + off, head_y), (ant_x + off, head_y - 40)], fill=(70, 70, 70), width=2)
    draw.ellipse([ant_x - 14, head_y - 56, ant_x + 14, head_y - 28], outline=(70, 70, 70), width=2)

    # Eyes
    eye_y = head_y + int(head_h * 0.45)
    for ex in [head_x + int(head_w * 0.3), head_x + int(head_w * 0.7)]:
        for _ in range(2):
            off = random.randint(-1, 1)
            draw.ellipse([ex - 24 + off, eye_y - 28 + off, ex + 24 + off, eye_y + 28 + off],
                        outline=(50, 50, 50), width=1)
        hatching(img, ex - 14, eye_y - 14, 28, 28, angle=45, spacing=4, opacity=35, color=(50, 50, 50))
        draw.ellipse([ex + 6, eye_y - 4, ex + 18, eye_y + 10], fill=(40, 40, 40))

    # Smile
    draw.arc([head_x + 30, eye_y + 25, head_x + head_w - 30, eye_y + 60],
            start=10, end=170, fill=(70, 70, 70), width=2)

    # Arms
    arm_y = body_y + int(body_h * 0.15)
    for side in [-1, 1]:
        if side == -1:
            ax0, ax1 = body_x - 60, body_x
        else:
            ax0, ax1 = body_x + body_w, body_x + body_w + 60
        for _ in range(2):
            off = random.randint(-1, 1)
            draw.rounded_rectangle([min(ax0, ax1) + off, arm_y + off,
                                  max(ax0, ax1) + off, arm_y + 24 + off],
                                  radius=10, outline=(60, 60, 60), width=1)
        hx = body_x - 65 if side == -1 else body_x + body_w + 65
        hatching(img, hx - 24, arm_y - 12, 48, 48, angle=45, spacing=5, opacity=30, color=(70, 70, 70))

    # Legs
    leg_y = body_y + body_h
    for lx in [body_x + 15, body_x + body_w - 50]:
        for _ in range(2):
            off = random.randint(-1, 1)
            draw.rounded_rectangle([lx + off, leg_y + off, lx + 35 + off, leg_y + int(H * 0.12) + off],
                                  radius=10, outline=(60, 60, 60), width=1)
        draw.rounded_rectangle([lx - 10, leg_y + int(H * 0.12) - 5, lx + 45, leg_y + int(H * 0.12) + 20],
                              radius=8, outline=(60, 60, 60), width=2)

    return img


STYLES = {
    "master_render": master_robot_3d,
    "master_sketch": master_robot_sketch,
}


def main():
    parser = argparse.ArgumentParser(description="Master Drawing Engine")
    parser.add_argument("--subject", type=str, default="robot", help="Subject to draw")
    parser.add_argument("--style", type=str, default="master_render", help="Art style")
    parser.add_argument("--output", type=str, default="output.png", help="Output file")
    parser.add_argument("--width", type=int, default=512, help="Image width")
    parser.add_argument("--height", type=int, default=640, help="Image height")
    parser.add_argument("--list-styles", action="store_true", help="List available styles")
    args = parser.parse_args()

    if args.list_styles:
        print("Available master styles:")
        for s in STYLES:
            print(f"  - {s}")
        return

    if args.subject != "robot":
        print(f"Unknown subject: {args.subject}")
        sys.exit(1)

    img = create_canvas(args.width, args.height)
    STYLES[args.style](img)
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    img.save(args.output)
    print(f"Saved: {args.output} ({img.size[0]}x{img.size[1]}) — style: {args.style}")


if __name__ == "__main__":
    main()
