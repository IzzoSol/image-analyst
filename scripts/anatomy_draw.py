#!/usr/bin/env python3
"""
Anatomy Draw — Draw human figures and animals with proper anatomy.

Based on classical drawing fundamentals:
- 8-head proportion system for humans
- Proper joint placement and range of motion
- Muscle group awareness
- Gesture and flow lines
- Anatomical shading

Usage:
    python anatomy_draw.py --subject human --pose standing --output human.png
    python anatomy_draw.py --subject human --pose dynamic --output human2.png
    python anatomy_draw.py --subject cat --pose sitting --output cat.png
    python anatomy_draw.py --list-subjects
"""

import sys
import os
import argparse
import math
import random
from PIL import Image, ImageDraw, ImageFilter

random.seed(42)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drawing_primitives import *

# ============================================================
# ANATOMY CONSTANTS (By The Book)
# ============================================================

# Human proportions (8 heads tall)
HUMAN = {
    "head": 1.0,        # 1 head unit
    "neck": 0.5,
    "torso": 2.5,       # shoulders to hips
    "upper_arm": 1.0,   # shoulder to elbow
    "lower_arm": 1.0,   # elbow to wrist
    "hand": 0.75,
    "upper_leg": 2.0,   # hip to knee
    "lower_leg": 2.0,   # knee to ankle
    "foot": 0.5,
    # Total: 8 heads (1+0.5+2.5+1+1+0.75+2+2+0.5 = 11.25? No, let me recalculate)
    # Actually: head(1) + neck(0.5) + torso(2.5) + upper_leg(2) + lower_leg(2) = 8
    # Arms: shoulder to elbow(1) + elbow to wrist(1) + hand(0.75) = 2.75 (attached to torso)
}

# Cat proportions (different)
CAT = {
    "head": 1.0,
    "neck": 0.3,
    "body": 2.5,        # chest to hips
    "front_leg": 1.5,   # shoulder to paw
    "back_leg": 1.8,    # hip to paw
    "tail": 2.0,
    "ear": 0.4,
}

# ============================================================
# HUMAN FIGURE DRAWING
# ============================================================

def draw_human_standing(img, style="master"):
    """Draw a standing human figure with proper anatomy."""
    draw = ImageDraw.Draw(img)
    W, H = img.size
    cx = W // 2  # center x
    head_unit = H // 8  # 1 head = 1/8 of height

    # Key points (using 8-head system)
    head_top = int(H * 0.05)
    head_bottom = head_top + head_unit
    neck_top = head_bottom
    neck_bottom = neck_top + int(head_unit * 0.5)
    shoulder_y = neck_bottom
    chest_y = shoulder_y + int(head_unit * 0.75)
    waist_y = shoulder_y + int(head_unit * 1.5)
    hip_y = shoulder_y + int(head_unit * 2.5)
    knee_y = hip_y + int(head_unit * 2.0)
    ankle_y = knee_y + int(head_unit * 2.0)
    foot_y = ankle_y + int(head_unit * 0.5)

    shoulder_w = int(head_unit * 2.5)
    hip_w = int(head_unit * 1.8)
    waist_w = int(head_unit * 1.4)

    # === HEAD ===
    head_r = head_unit // 2
    head_cx = cx
    head_cy = (head_top + head_bottom) // 2
    # Head shape (oval)
    draw.ellipse([head_cx - head_r, head_top, head_cx + head_r, head_bottom],
                fill=(235, 200, 170), outline=(180, 140, 110), width=2)
    # Jaw
    draw.ellipse([head_cx - int(head_r*0.7), head_cy, head_cx + int(head_r*0.7), head_bottom + 5],
                fill=(235, 200, 170))

    # Eyes (at midline of head)
    eye_y = head_cy
    eye_spacing = head_r // 2
    for ex in [head_cx - eye_spacing, head_cx + eye_spacing]:
        draw.ellipse([ex - 8, eye_y - 4, ex + 8, eye_y + 4], fill=(255, 255, 255), outline=(100, 80, 60), width=1)
        draw.ellipse([ex - 4, eye_y - 3, ex + 4, eye_y + 3], fill=(60, 40, 20))
        draw.ellipse([ex + 1, eye_y - 2, ex + 3, eye_y], fill=(255, 255, 255))

    # Nose
    draw.line([(head_cx, eye_y + 5), (head_cx - 3, eye_y + 15)], fill=(180, 140, 110), width=2)
    draw.line([(head_cx, eye_y + 5), (head_cx + 3, eye_y + 15)], fill=(180, 140, 110), width=2)

    # Mouth
    draw.arc([head_cx - 10, eye_y + 18, head_cx + 10, eye_y + 30], start=0, end=180, fill=(180, 100, 80), width=2)

    # Neck
    neck_w = int(head_unit * 0.4)
    draw.rectangle([cx - neck_w//2, neck_top, cx + neck_w//2, neck_bottom], fill=(235, 200, 170))

    # === TORSO ===
    # Shoulders
    draw.ellipse([cx - shoulder_w//2 - 10, shoulder_y - 5, cx - shoulder_w//2 + 10, shoulder_y + 5], fill=(235, 200, 170))
    draw.ellipse([cx + shoulder_w//2 - 10, shoulder_y - 5, cx + shoulder_w//2 + 10, shoulder_y + 5], fill=(235, 200, 170))

    # Torso shape (trapezoid: wide shoulders, narrow waist, wider hips)
    torso_points = [
        (cx - shoulder_w//2, shoulder_y),
        (cx + shoulder_w//2, shoulder_y),
        (cx + waist_w//2, waist_y),
        (cx + hip_w//2, hip_y),
        (cx - hip_w//2, hip_y),
        (cx - waist_w//2, waist_y),
    ]
    draw.polygon(torso_points, fill=(220, 180, 150), outline=(180, 140, 110))

    # Chest muscles (pectoralis)
    draw.ellipse([cx - shoulder_w//3, shoulder_y + 5, cx - 5, chest_y + 10], fill=(225, 185, 155), outline=(190, 150, 120), width=1)
    draw.ellipse([cx + 5, shoulder_y + 5, cx + shoulder_w//3, chest_y + 10], fill=(225, 185, 155), outline=(190, 150, 120), width=1)

    # Abs (rectus abdominis)
    for i in range(3):
        ay = waist_y + i * (hip_y - waist_y) // 3
        draw.line([(cx - waist_w//4, ay), (cx + waist_w//4, ay)], fill=(190, 150, 120), width=1)

    # === ARMS ===
    arm_len = int(head_unit * 2.0)  # shoulder to wrist
    upper_arm_len = int(head_unit * 1.0)
    lower_arm_len = int(head_unit * 1.0)

    for side in [-1, 1]:
        sx = cx + side * (shoulder_w // 2)
        # Upper arm
        ex = sx + side * int(head_unit * 0.3)  # slight outward
        ey = shoulder_y + upper_arm_len
        draw.line([(sx, shoulder_y), (ex, ey)], fill=(220, 180, 150), width=12)
        # Forearm
        wx = ex + side * int(head_unit * 0.2)
        wy = ey + lower_arm_len
        draw.line([(ex, ey), (wx, wy)], fill=(220, 180, 150), width=10)
        # Hand
        draw.ellipse([wx - 12, wy - 8, wx + 12, wy + 12], fill=(235, 200, 170), outline=(180, 140, 110), width=1)
        # Fingers
        for f in range(4):
            fx = wx - 8 + f * 5
            draw.line([(fx, wy + 5), (fx, wy + 18)], fill=(235, 200, 170), width=3)

    # === LEGS ===
    leg_len = int(head_unit * 4.0)
    upper_leg_len = int(head_unit * 2.0)
    lower_leg_len = int(head_unit * 2.0)

    for side in [-1, 1]:
        hx = cx + side * (hip_w // 3)
        # Thigh
        kx = hx + side * int(head_unit * 0.2)
        ky = hip_y + upper_leg_len
        draw.line([(hx, hip_y), (kx, ky)], fill=(220, 180, 150), width=14)
        # Calf
        ax = kx + side * int(head_unit * 0.1)
        ay = ky + lower_leg_len
        draw.line([(kx, ky), (ax, ay)], fill=(220, 180, 150), width=12)
        # Foot
        foot_x0 = min(ax - 5, ax + 25 * side)
        foot_x1 = max(ax - 5, ax + 25 * side)
        draw.ellipse([foot_x0, ay - 5, foot_x1, ay + 10], fill=(235, 200, 170), outline=(180, 140, 110), width=1)

    # === SHADING ===
    # Add shadows
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    # Left side shadow
    sd.polygon([(0, 0), (cx - 20, 0), (cx - 20, H), (0, H)], fill=(0, 0, 0, 15))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=20))
    img.paste(shadow, (0, 0), shadow)

    return img


def draw_cat_sitting(img):
    """Draw a sitting cat with proper anatomy."""
    draw = ImageDraw.Draw(img)
    W, H = img.size
    cx = W // 2
    head_unit = H // 6

    # Cat proportions: head is larger relative to body
    head_r = int(head_unit * 0.8)
    body_w = int(head_unit * 2.5)
    body_h = int(head_unit * 2.0)

    # === HEAD ===
    head_cx = cx
    head_cy = int(H * 0.25)
    # Cat head (slightly oval)
    draw.ellipse([head_cx - head_r, head_cy - int(head_r*0.8), head_cx + head_r, head_cy + int(head_r*0.8)],
                fill=(200, 180, 150), outline=(150, 120, 90), width=2)

    # Ears (triangular)
    ear_h = int(head_r * 0.8)
    # Left ear
    draw.polygon([(head_cx - head_r + 5, head_cy - int(head_r*0.6)),
                  (head_cx - head_r - 10, head_cy - int(head_r*0.6) - ear_h),
                  (head_cx - head_r + 25, head_cy - int(head_r*0.6) - ear_h // 2)],
                 fill=(200, 180, 150), outline=(150, 120, 90))
    # Right ear
    draw.polygon([(head_cx + head_r - 5, head_cy - int(head_r*0.6)),
                  (head_cx + head_r + 10, head_cy - int(head_r*0.6) - ear_h),
                  (head_cx + head_r - 25, head_cy - int(head_r*0.6) - ear_h // 2)],
                 fill=(200, 180, 150), outline=(150, 120, 90))
    # Inner ears
    draw.polygon([(head_cx - head_r + 8, head_cy - int(head_r*0.6) - 5),
                  (head_cx - head_r - 2, head_cy - int(head_r*0.6) - ear_h + 5),
                  (head_cx - head_r + 20, head_cy - int(head_r*0.6) - ear_h // 2)],
                 fill=(220, 170, 160))
    draw.polygon([(head_cx + head_r - 8, head_cy - int(head_r*0.6) - 5),
                  (head_cx + head_r + 2, head_cy - int(head_r*0.6) - ear_h + 5),
                  (head_cx + head_r - 20, head_cy - int(head_r*0.6) - ear_h // 2)],
                 fill=(220, 170, 160))

    # Eyes (cat eyes - almond shaped)
    eye_y = head_cy - 5
    for ex in [head_cx - head_r // 3, head_cx + head_r // 3]:
        draw.ellipse([ex - 12, eye_y - 8, ex + 12, eye_y + 8], fill=(120, 180, 80), outline=(80, 120, 50), width=1)
        # Slit pupil
        draw.ellipse([ex - 3, eye_y - 7, ex + 3, eye_y + 7], fill=(20, 20, 20))
        # Highlight
        draw.ellipse([ex + 4, eye_y - 5, ex + 8, eye_y - 1], fill=(255, 255, 255))

    # Nose (small triangle)
    nose_y = head_cy + int(head_r * 0.2)
    draw.polygon([(head_cx, nose_y), (head_cx - 5, nose_y + 6), (head_cx + 5, nose_y + 6)],
                fill=(200, 120, 100))

    # Mouth
    draw.line([(head_cx, nose_y + 6), (head_cx, nose_y + 12)], fill=(150, 100, 80), width=1)
    draw.arc([head_cx - 8, nose_y + 8, head_cx, nose_y + 18], start=0, end=180, fill=(150, 100, 80), width=1)
    draw.arc([head_cx, nose_y + 8, head_cx + 8, nose_y + 18], start=0, end=180, fill=(150, 100, 80), width=1)

    # Whiskers
    for side in [-1, 1]:
        for i in range(3):
            wy = nose_y + 2 + i * 4
            draw.line([(head_cx + side * 5, wy), (head_cx + side * (head_r + 20), wy + random.randint(-3, 3))],
                     fill=(150, 120, 90), width=1)

    # === BODY ===
    body_cx = cx
    body_cy = head_cy + int(head_r * 1.2) + body_h // 2
    body_x = body_cx - body_w // 2
    body_y = body_cy - body_h // 2

    # Body (oval, sitting)
    draw.ellipse([body_x, body_y, body_x + body_w, body_y + body_h],
                fill=(200, 180, 150), outline=(150, 120, 90), width=2)

    # === FRONT LEGS ===
    leg_w = int(head_unit * 0.4)
    for side in [-1, 1]:
        lx = body_cx + side * (body_w // 4)
        # Upper leg
        draw.rounded_rectangle([lx - leg_w//2, body_y + body_h // 3, lx + leg_w//2, body_y + body_h],
                              radius=leg_w//2, fill=(200, 180, 150), outline=(150, 120, 90), width=1)
        # Paw
        draw.ellipse([lx - leg_w, body_y + body_h - 5, lx + leg_w, body_y + body_h + 10],
                    fill=(200, 180, 150), outline=(150, 120, 90), width=1)
        # Toes
        for t in range(3):
            tx = lx - leg_w // 2 + t * (leg_w // 2)
            draw.ellipse([tx - 3, body_y + body_h + 5, tx + 3, body_y + body_h + 12],
                        fill=(200, 180, 150), outline=(150, 120, 90), width=1)

    # === TAIL ===
    tail_points = []
    tx = body_x + body_w
    ty = body_cy
    for i in range(20):
        angle = math.radians(-30 + i * 3)
        tail_points.append((tx + i * 8, ty + int(math.sin(angle) * 20)))
    for i in range(len(tail_points) - 1):
        draw.line([tail_points[i], tail_points[i+1]], fill=(200, 180, 150), width=6)

    # === SHADING ===
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([body_x + 10, body_y + body_h - 5, body_x + body_w - 10, body_y + body_h + 15],
              fill=(0, 0, 0, 40))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=8))
    img.paste(shadow, (0, 0), shadow)

    return img


SUBJECTS = {
    "human": draw_human_standing,
    "cat": draw_cat_sitting,
}


def main():
    parser = argparse.ArgumentParser(description="Anatomy Drawing Engine")
    parser.add_argument("--subject", type=str, default="human", help="Subject to draw")
    parser.add_argument("--output", type=str, default="output.png", help="Output file")
    parser.add_argument("--width", type=int, default=512, help="Image width")
    parser.add_argument("--height", type=int, default=768, help="Image height")
    parser.add_argument("--list-subjects", action="store_true", help="List available subjects")
    args = parser.parse_args()

    if args.list_subjects:
        print("Available subjects:")
        for s in SUBJECTS:
            print(f"  - {s}")
        return

    if args.subject not in SUBJECTS:
        print(f"Unknown subject: {args.subject}")
        sys.exit(1)

    img = create_canvas(args.width, args.height, (245, 242, 235))
    SUBJECTS[args.subject](img)
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    img.save(args.output)
    print(f"Saved: {args.output} ({img.size[0]}x{img.size[1]}) — subject: {args.subject}")


if __name__ == "__main__":
    main()
