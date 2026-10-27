#!/usr/bin/env python3
"""
Master Draw v5 — Pushing code to its absolute limits.

Goal: Match AI-generated quality using pure code (0s and 1s).
Techniques: Bezier contours, anatomical landmarks, multi-layer shading,
texture overlays, paper simulation, high resolution.

Usage:
    python master_draw_v5.py --subject human --output human.png --width 1024 --height 1024
"""

import sys
import os
import argparse
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

random.seed(42)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drawing_primitives import *


# ============================================================
# HIGH-QUALITY BEZIER CONTOUR SYSTEM
# ============================================================

def smooth_contour(points, tension=0.5):
    """Create smooth bezier control points from a set of points."""
    result = []
    n = len(points)
    for i in range(n):
        p0 = points[i]
        p1 = points[(i + 1) % n]
        p2 = points[(i + 2) % n]
        # Calculate tangent
        dx = p2[0] - p0[0]
        dy = p2[1] - p0[1]
        # Control point
        cp = (p1[0] - dx * tension * 0.25, p1[1] - dy * tension * 0.25)
        result.append((p1, cp))
    return result


def fill_smooth_region(draw, points, fill_color, outline_color=None, outline_width=1):
    """Fill a region with smooth bezier-interpolated edges."""
    if len(points) < 3:
        return
    # Use polygon with many interpolated points
    smooth = []
    n = len(points)
    for i in range(n):
        p0 = points[i]
        p1 = points[(i + 1) % n]
        # Add midpoint
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        smooth.append((int(mx), int(my)))
    if len(smooth) >= 3:
        draw.polygon(smooth, fill=fill_color, outline=outline_color)


# ============================================================
# ANATOMICAL LANDMARK SYSTEM
# ============================================================

class AnatomyLandmark:
    """A point on the body with anatomical significance."""
    def __init__(self, name, x, y, depth=0):
        self.name = name
        self.x = x
        self.y = y
        self.depth = depth  # 0=surface, 1=deep


# ============================================================
# MASTER HUMAN v5
# ============================================================

def draw_human_v5(img, width, height):
    """Masterful human figure — pushing code to its limits."""
    draw = ImageDraw.Draw(img)
    W, H = width, height
    cx = W // 2
    head_unit = H // 8

    # Colors (skin tones with full range)
    skin = (220, 185, 155)
    skin_light = (245, 215, 185)
    skin_mid = (200, 165, 135)
    skin_shadow = (160, 120, 90)
    skin_deep = (110, 75, 45)
    skin_core = (80, 50, 30)

    light_dir = (-0.35, -0.55, 0.6)

    # === GESTURE (Principle 3) ===
    # Dynamic standing pose with weight shift
    gesture = [
        (cx, int(H * 0.03)),
        (cx + 2, int(H * 0.10)),
        (cx + 6, int(H * 0.28)),
        (cx + 1, int(H * 0.48)),
        (cx - 6, int(H * 0.70)),
        (cx + 12, int(H * 0.95)),
    ]

    # === CONSTRUCTION (Principle 1) ===
    # Head
    head_cy = int(H * 0.07)
    head_r = int(head_unit * 0.42)
    
    # Skull volume (multi-layer)
    for layer in range(3):
        r = head_r - layer * 2
        shade_volume(img, cx, head_cy, r, int(r * 1.15), skin, light_dir,
                     ambient=0.2 + layer * 0.05, diffuse=0.5, specular=0.3, shininess=12)
    
    # Jaw construction
    jaw_top = head_cy + int(head_r * 0.3)
    jaw_bottom = head_cy + int(head_r * 0.9)
    for y in range(jaw_top, jaw_bottom):
        t = (y - jaw_top) / max(1, jaw_bottom - jaw_top)
        w = int(head_r * 0.8 * (1 - t * 0.3))
        for x in range(cx - w, cx + w):
            dx = (x - cx) / max(1, w)
            dist = abs(dx)
            if dist <= 1.0:
                light = max(0, 0.4 + 0.3 * (-dx * 0.2 + 0.6))
                shade = 0.35 + 0.4 * light
                color = tuple(min(255, int(skin[i] * shade)) for i in range(3))
                edge = 1 - dist ** 2
                color = tuple(int(color[i] * edge + skin_shadow[i] * (1 - edge) * 0.4) for i in range(3))
                draw.point((x, y), fill=color + (255,))

    # === ANATOMY (Principle 4) — Facial features ===
    eye_y = head_cy - int(head_r * 0.05)
    eye_spacing = int(head_r * 0.42)
    
    for side in [-1, 1]:
        ex = cx + side * eye_spacing
        
        # Orbital bone (deep)
        draw.ellipse([ex - 13, eye_y - 9, ex + 13, eye_y + 9], fill=skin_deep)
        # Sclera
        draw.ellipse([ex - 11, eye_y - 7, ex + 11, eye_y + 7], fill=(248, 248, 245))
        # Iris
        shade_volume(img, ex + side * 1, eye_y, 5, 5, (48, 68, 38), light_dir, specular=0.5, shininess=10)
        # Pupil
        draw.ellipse([ex + side - 2, eye_y - 3, ex + side + 3, eye_y + 3], fill=(6, 6, 10))
        # Highlights (multiple for realism)
        hl1_x1 = min(ex + side * 4, ex + side * 7)
        hl1_x2 = max(ex + side * 4, ex + side * 7)
        draw.ellipse([hl1_x1, eye_y - 3, hl1_x2, eye_y], fill=(255, 255, 255))
        hl2_x1 = min(ex + side, ex + side + 2)
        hl2_x2 = max(ex + side, ex + side + 2)
        draw.ellipse([hl2_x1, eye_y + 1, hl2_x2, eye_y + 3], fill=(255, 255, 255, 160))
        hl3_x1 = min(ex + side * 2, ex + side * 3)
        hl3_x2 = max(ex + side * 2, ex + side * 3)
        draw.ellipse([hl3_x1, eye_y - 1, hl3_x2, eye_y + 1], fill=(255, 255, 255, 100))

    # Nose (with bridge, tip, nostrils)
    nose_top = eye_y + 8
    nose_bottom = nose_top + int(head_r * 0.55)
    # Bridge
    for y in range(nose_top, nose_bottom):
        t = (y - nose_top) / max(1, nose_bottom - nose_top)
        w = int(3 + t * 4)
        for x in range(cx - w, cx + w):
            dx = (x - cx) / max(1, w)
            light = max(0, 0.4 + 0.3 * (0.5))
            shade = 0.4 + 0.35 * light
            color = tuple(min(255, int(skin[i] * shade)) for i in range(3))
            edge = 1 - abs(dx) ** 1.5
            color = tuple(int(color[i] * edge + skin_shadow[i] * (1 - edge) * 0.3) for i in range(3))
            draw.point((x, y), fill=color + (255,))
    # Nostrils
    draw.ellipse([cx - 7, nose_bottom - 2, cx - 2, nose_bottom + 3], fill=skin_deep)
    draw.ellipse([cx + 2, nose_bottom - 2, cx + 7, nose_bottom + 3], fill=skin_deep)

    # Mouth (lips with volume)
    mouth_y = nose_bottom + 7
    # Upper lip
    for x in range(cx - 14, cx + 15):
        dx = (x - cx) / 14
        y = mouth_y + int(3 * (1 - dx * dx))
        draw.line([(x, y), (x, y + 2)], fill=skin_shadow, width=1)
    # Lower lip
    for x in range(cx - 16, cx + 17):
        dx = (x - cx) / 16
        y = mouth_y + 5 + int(4 * (1 - dx * dx))
        draw.line([(x, y), (x, y + 2)], fill=skin_shadow, width=1)
    # Lip line
    draw.arc([cx - 14, mouth_y - 1, cx + 14, mouth_y + 6], start=190, end=350, fill=skin_deep, width=2)

    # Ears
    for side in [-1, 1]:
        ex = cx + side * (head_r + 2)
        ey = head_cy
        ear_pts = [(ex, ey - 10), (ex + side * 18, ey - 25), (ex + side * 5, ey + 5), (ex, ey + 10)]
        draw.polygon(ear_pts, fill=skin, outline=skin_shadow)
        # Inner ear
        inner = [(ex + side * 2, ey - 5), (ex + side * 12, ey - 20), (ex + side * 4, ey + 2)]
        draw.polygon(inner, fill=skin_shadow)

    # === NECK ===
    neck_top = head_cy + head_r - 5
    neck_bottom = neck_top + int(head_unit * 0.4)
    for y in range(neck_top, neck_bottom):
        t = (y - neck_top) / max(1, neck_bottom - neck_top)
        w = int(head_unit * 0.38 * (1 - t * 0.15))
        for x in range(cx - w, cx + w):
            dx = (x - cx) / max(1, w)
            light = max(0, 0.4 + 0.3 * (0.5 - dx * 0.3))
            shade = 0.4 + 0.35 * light
            color = tuple(min(255, int(skin[i] * shade)) for i in range(3))
            edge = 1 - abs(dx) ** 1.5
            color = tuple(int(color[i] * edge + skin_shadow[i] * (1 - edge) * 0.4) for i in range(3))
            draw.point((x, y), fill=color + (255,))

    # === TORSO ===
    shoulder_y = neck_bottom
    chest_y = shoulder_y + int(head_unit * 0.5)
    waist_y = shoulder_y + int(head_unit * 1.3)
    hip_y = shoulder_y + int(head_unit * 2.3)
    shoulder_w = int(head_unit * 2.5)
    hip_w = int(head_unit * 1.6)
    waist_w = int(head_unit * 1.2)

    # Shoulders
    for side in [-1, 1]:
        sx = cx + side * (shoulder_w // 2)
        shade_volume(img, sx, shoulder_y, int(head_unit * 0.32), int(head_unit * 0.32), skin, light_dir, specular=0.25)

    # Pectoralis
    for side in [-1, 1]:
        px = cx + side * int(shoulder_w * 0.18)
        py = chest_y
        shade_volume(img, px, py, int(head_unit * 0.42), int(head_unit * 0.32), skin, light_dir, specular=0.2)

    # Serratus/obliques
    for side in [-1, 1]:
        for i in range(3):
            ox = cx + side * int(waist_w * 0.45)
            oy = chest_y + i * int((waist_y - chest_y) / 3)
            shade_volume(img, ox, oy, int(head_unit * 0.15), int(head_unit * 0.2), skin, light_dir, ambient=0.3, diffuse=0.4)

    # Abdomen
    ab_top = chest_y + int(head_unit * 0.45)
    ab_bottom = waist_y
    for i in range(4):
        seg_y = ab_top + i * (ab_bottom - ab_top) // 4
        seg_h = (ab_bottom - ab_top) // 4
        shade_volume(img, cx, seg_y + seg_h // 2, int(waist_w * 0.32), int(seg_h * 0.38), skin, light_dir, ambient=0.3, diffuse=0.45)
        # Tendinous intersections (abs lines)
        line_y = seg_y + seg_h
        draw.line([(cx - int(waist_w * 0.25), line_y), (cx + int(waist_w * 0.25), line_y)], fill=skin_shadow + (60,), width=1)

    # === ARMS ===
    upper_arm_len = int(head_unit * 1.0)
    forearm_len = int(head_unit * 1.0)

    for side in [-1, 1]:
        sx = cx + side * (shoulder_w // 2)
        sy = shoulder_y
        
        # Deltoid
        shade_volume(img, sx, sy, int(head_unit * 0.3), int(head_unit * 0.3), skin, light_dir)
        
        # Bicep
        elbow_x = sx + side * int(head_unit * 0.2)
        elbow_y = sy + upper_arm_len
        draw_organic_limb(draw, img, (sx, sy), (elbow_x, elbow_y),
                          int(head_unit * 0.4), int(head_unit * 0.33), skin, skin_shadow, skin_light,
                          bend=side * 4, segments=25)
        
        # Tricep
        draw_organic_limb(draw, img, (sx + side * 6, sy + 5), (elbow_x + side * 6, elbow_y),
                          int(head_unit * 0.28), int(head_unit * 0.22), skin, skin_shadow, skin_light,
                          bend=side * 3, segments=20)
        
        # Forearm
        wrist_x = elbow_x + side * int(head_unit * 0.12)
        wrist_y = elbow_y + forearm_len
        draw_organic_limb(draw, img, (elbow_x, elbow_y), (wrist_x, wrist_y),
                          int(head_unit * 0.3), int(head_unit * 0.25), skin, skin_shadow, skin_light,
                          bend=side * 3, segments=25)
        
        # Hand
        shade_volume(img, wrist_x, wrist_y + 5, int(head_unit * 0.18), int(head_unit * 0.18), skin, light_dir)
        # Fingers
        for f in range(4):
            fx = wrist_x - 8 + f * 5 + side * 2
            draw_organic_limb(draw, img, (fx, wrist_y + 8), (fx + side * 2, wrist_y + 24),
                              3, 2, skin, skin_shadow, skin_light, segments=10)
        # Thumb
        draw_organic_limb(draw, img, (wrist_x + side * 12, wrist_y + 2), (wrist_x + side * 20, wrist_y + 12),
                          4, 2, skin, skin_shadow, skin_light, segments=8)

    # === LEGS ===
    upper_leg_len = int(head_unit * 2.0)
    lower_leg_len = int(head_unit * 1.9)

    for side in [-1, 1]:
        hx = cx + side * int(hip_w * 0.22)
        hy = hip_y
        
        # Glute
        shade_volume(img, hx, hy, int(head_unit * 0.38), int(head_unit * 0.32), skin, light_dir)
        
        # Thigh (quadriceps)
        knee_x = hx + side * int(head_unit * 0.15)
        knee_y = hy + upper_leg_len
        draw_organic_limb(draw, img, (hx, hy), (knee_x, knee_y),
                          int(head_unit * 0.5), int(head_unit * 0.4), skin, skin_shadow, skin_light,
                          bend=side * 3, segments=30)
        
        # Hamstring (back of thigh)
        draw_organic_limb(draw, img, (hx + side * 3, hy + 5), (knee_x + side * 3, knee_y),
                          int(head_unit * 0.35), int(head_unit * 0.28), skin, skin_shadow, skin_light,
                          bend=side * 2, segments=25)
        
        # Calf
        ankle_x = knee_x + side * int(head_unit * 0.1)
        ankle_y = knee_y + lower_leg_len
        draw_organic_limb(draw, img, (knee_x, knee_y), (ankle_x, ankle_y),
                          int(head_unit * 0.35), int(head_unit * 0.25), skin, skin_shadow, skin_light,
                          bend=side * 2, segments=30)
        
        # Foot
        draw_organic_limb(draw, img, (ankle_x, ankle_y), (ankle_x + side * 20, ankle_y + 4),
                          int(head_unit * 0.28), int(head_unit * 0.22), skin, skin_shadow, skin_light,
                          segments=12)
        # Toes
        for t in range(4):
            tx = ankle_x + side * (5 + t * 4)
            draw_organic_limb(draw, img, (tx, ankle_y + 2), (tx + side * 2, ankle_y + 8),
                              4, 2, skin, skin_shadow, skin_light, segments=6)

    # === TEXTURE (Principle 6) ===
    skin_texture(img, cx - shoulder_w//2, shoulder_y, shoulder_w, hip_y - shoulder_y, skin, density=0.015)

    # === LIGHT (Principle 5) — Global ===
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.polygon([(0, 0), (cx - 50, 0), (cx - 50, H), (0, H)], fill=(0, 0, 0, 20))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=50))
    img.paste(shadow, (0, 0), shadow)

    # Paper texture overlay
    paper = Image.new('RGBA', img.size, (0, 0, 0, 0))
    pd = ImageDraw.Draw(paper)
    for _ in range(int(W * H * 0.001)):
        px = random.randint(0, W - 1)
        py = random.randint(0, H - 1)
        pd.point((px, py), fill=(0, 0, 0, random.randint(5, 15)))
    paper = paper.filter(ImageFilter.GaussianBlur(radius=0.5))
    img.paste(paper, (0, 0), paper)

    return img


SUBJECTS = {"human": draw_human_v5}


def main():
    parser = argparse.ArgumentParser(description="Master Draw v5 — Pushing code to its limits")
    parser.add_argument("--subject", type=str, default="human")
    parser.add_argument("--output", type=str, default="output.png")
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--height", type=int, default=768)
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    if args.list:
        print("Available: human")
        return

    img = create_canvas(args.width, args.height, (248, 245, 238))
    draw_human_v5(img, args.width, args.height)
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    img.save(args.output)
    print(f"Saved: {args.output} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
