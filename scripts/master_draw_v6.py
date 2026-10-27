#!/usr/bin/env python3
"""
Master Draw v6 — Own the code. Everything is 0s and 1s.

We don't call APIs. We don't use external models. We MASTER the code.
Every pixel is computed. Every line is intentional. Every shade is physics.

This is the ultimate code-based drawing system. If it's not 10/10, we iterate.

Usage:
    python master_draw_v6.py --subject human --output human.png --width 800 --height 1200
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
# VARIABLE-WIDTH BEZIER (Artistic strokes)
# ============================================================

def artistic_stroke(draw, points, color, width_start=4, width_end=1, 
                    opacity=200, steps=80):
    """Draw a stroke with variable width (tapers like a real pencil)."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        # Cubic bezier
        x = (1-t)**3 * points[0][0] + 3*(1-t)**2*t * points[1][0] + 3*(1-t)*t**2 * points[2][0] + t**3 * points[3][0]
        y = (1-t)**3 * points[0][1] + 3*(1-t)**2*t * points[1][1] + 3*(1-t)*t**2 * points[2][1] + t**3 * points[3][1]
        pts.append((x, y))
    
    for i in range(len(pts) - 1):
        t = i / (len(pts) - 1)
        w = max(1, int(width_start * (1 - t) + width_end * t))
        # Draw circle at each point for smooth variable width
        x, y = pts[i]
        draw.ellipse([x - w//2, y - w//2, x + w//2, y + w//2], 
                    fill=color + (opacity,))


def tapered_line(draw, p0, p1, width_start, width_end, color, steps=30):
    """Draw a line that tapers from start to end."""
    for i in range(steps):
        t = i / steps
        t2 = (i + 1) / steps
        x0 = p0[0] + (p1[0] - p0[0]) * t
        y0 = p0[1] + (p1[1] - p0[1]) * t
        x1 = p0[0] + (p1[0] - p0[0]) * t2
        y1 = p0[1] + (p1[1] - p0[1]) * t2
        w = max(1, int(width_start * (1 - t) + width_end * t))
        draw.line([(x0, y0), (x1, y1)], fill=color, width=w)


# ============================================================
# ANATOMICAL CONSTRUCTION (Bones → Muscles → Skin → Detail)
# ============================================================

def draw_bone_structure(draw, img, cx, H, head_unit):
    """Draw the skeletal structure (invisible guide)."""
    # This is the foundation - everything builds on this
    pass


def draw_muscle_volume(draw, img, cx, cy, rx, ry, 
                       base_color, shadow_color, highlight_color,
                       light_dir, detail_level=3):
    """Draw a muscle volume with full shading and texture."""
    # Multi-layer shading
    for layer in range(detail_level):
        r_scale = 1.0 - layer * 0.05
        shade_volume(img, cx, cy, int(rx * r_scale), int(ry * r_scale),
                     base_color, light_dir, 
                     ambient=0.15 + layer * 0.05,
                     diffuse=0.5, specular=0.25, shininess=16 - layer * 2)
    
    # Edge definition
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], 
                outline=shadow_color, width=1)


# ============================================================
# MASTER HUMAN v6 (The ultimate)
# ============================================================

def draw_human_v6(img, W, H):
    """The ultimate code-based human figure."""
    draw = ImageDraw.Draw(img)
    cx = W // 2
    head_unit = H // 8

    # Colors
    skin = (220, 185, 155)
    skin_light = (248, 218, 188)
    skin_mid = (200, 165, 135)
    skin_shadow = (160, 120, 90)
    skin_deep = (110, 75, 45)
    skin_core = (75, 45, 25)

    light_dir = (-0.35, -0.5, 0.6)

    # === GESTURE ===
    gesture = [
        (cx, int(H * 0.03)),
        (cx + 3, int(H * 0.10)),
        (cx + 8, int(H * 0.28)),
        (cx + 2, int(H * 0.48)),
        (cx - 6, int(H * 0.70)),
        (cx + 12, int(H * 0.95)),
    ]

    # === HEAD ===
    head_cy = int(H * 0.07)
    head_r = int(head_unit * 0.42)
    
    # Skull (multi-layer volume)
    for layer in range(4):
        r = head_r - layer * 2
        ry = int(r * 1.15)
        shade_volume(img, cx, head_cy, r, ry, skin, light_dir,
                     ambient=0.18 + layer * 0.04, diffuse=0.5, specular=0.25, shininess=14)
    
    # Jaw
    jaw_top = head_cy + int(head_r * 0.2)
    jaw_bottom = head_cy + int(head_r * 0.9)
    for y in range(jaw_top, jaw_bottom):
        t = (y - jaw_top) / max(1, jaw_bottom - jaw_top)
        w = int(head_r * 0.75 * (1 - t * 0.25))
        for x in range(cx - w, cx + w):
            dx = (x - cx) / max(1, w)
            dist = abs(dx)
            if dist <= 1.0:
                light = max(0, 0.4 + 0.3 * (0.5 - dx * 0.2))
                shade = 0.35 + 0.4 * light
                color = tuple(min(255, int(skin[i] * shade)) for i in range(3))
                edge = 1 - dist ** 1.8
                color = tuple(int(color[i] * edge + skin_shadow[i] * (1 - edge) * 0.35) for i in range(3))
                draw.point((x, y), fill=color + (255,))

    # === FACIAL FEATURES ===
    eye_y = head_cy - int(head_r * 0.05)
    eye_spacing = int(head_r * 0.42)
    
    for side in [-1, 1]:
        ex = cx + side * eye_spacing
        
        # Orbital bone
        draw.ellipse([ex - 14, eye_y - 9, ex + 14, eye_y + 9], fill=skin_deep)
        # Sclera
        draw.ellipse([ex - 12, eye_y - 7, ex + 12, eye_y + 7], fill=(248, 248, 245))
        # Iris
        shade_volume(img, ex + side, eye_y, 6, 6, (45, 65, 35), light_dir, specular=0.5, shininess=10)
        # Pupil
        draw.ellipse([ex + side - 2, eye_y - 3, ex + side + 3, eye_y + 3], fill=(6, 6, 10))
        # Highlights
        hx = ex + side * 4
        draw.ellipse([hx, eye_y - 3, hx + 3, eye_y], fill=(255, 255, 255))
        draw.ellipse([ex + side, eye_y + 1, ex + side + 2, eye_y + 3], fill=(255, 255, 255, 160))

    # Nose
    nose_top = eye_y + 8
    nose_bottom = nose_top + int(head_r * 0.55)
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
    draw.ellipse([cx - 7, nose_bottom - 2, cx - 2, nose_bottom + 3], fill=skin_deep)
    draw.ellipse([cx + 2, nose_bottom - 2, cx + 7, nose_bottom + 3], fill=skin_deep)

    # Mouth
    mouth_y = nose_bottom + 7
    for x in range(cx - 14, cx + 15):
        dx = (x - cx) / 14
        y = mouth_y + int(3 * (1 - dx * dx))
        draw.line([(x, y), (x, y + 2)], fill=skin_shadow, width=1)
    for x in range(cx - 16, cx + 17):
        dx = (x - cx) / 16
        y = mouth_y + 5 + int(4 * (1 - dx * dx))
        draw.line([(x, y), (x, y + 2)], fill=skin_shadow, width=1)
    draw.arc([cx - 14, mouth_y - 1, cx + 14, mouth_y + 6], start=190, end=350, fill=skin_deep, width=2)

    # Ears
    for side in [-1, 1]:
        ex = cx + side * (head_r + 2)
        ey = head_cy
        ear_pts = [(ex, ey - 10), (ex + side * 18, ey - 25), (ex + side * 5, ey + 5), (ex, ey + 10)]
        draw.polygon(ear_pts, fill=skin, outline=skin_shadow)
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
        draw_muscle_volume(draw, img, sx, shoulder_y, int(head_unit * 0.32), int(head_unit * 0.32),
                           skin, skin_shadow, skin_light, light_dir, detail_level=3)

    # Pectoralis
    for side in [-1, 1]:
        px = cx + side * int(shoulder_w * 0.18)
        py = chest_y
        draw_muscle_volume(draw, img, px, py, int(head_unit * 0.42), int(head_unit * 0.32),
                           skin, skin_shadow, skin_light, light_dir, detail_level=3)

    # Serratus
    for side in [-1, 1]:
        for i in range(3):
            ox = cx + side * int(waist_w * 0.45)
            oy = chest_y + i * int((waist_y - chest_y) / 3)
            draw_muscle_volume(draw, img, ox, oy, int(head_unit * 0.15), int(head_unit * 0.2),
                               skin, skin_shadow, skin_light, light_dir, detail_level=2)

    # Abdomen
    ab_top = chest_y + int(head_unit * 0.45)
    ab_bottom = waist_y
    for i in range(4):
        seg_y = ab_top + i * (ab_bottom - ab_top) // 4
        seg_h = (ab_bottom - ab_top) // 4
        draw_muscle_volume(draw, img, cx, seg_y + seg_h // 2, int(waist_w * 0.32), int(seg_h * 0.38),
                           skin, skin_shadow, skin_light, light_dir, detail_level=3)
        line_y = seg_y + seg_h
        draw.line([(cx - int(waist_w * 0.25), line_y), (cx + int(waist_w * 0.25), line_y)], 
                  fill=skin_shadow + (60,), width=1)

    # === ARMS ===
    upper_arm_len = int(head_unit * 1.0)
    forearm_len = int(head_unit * 1.0)

    for side in [-1, 1]:
        sx = cx + side * (shoulder_w // 2)
        sy = shoulder_y
        
        # Deltoid
        draw_muscle_volume(draw, img, sx, sy, int(head_unit * 0.3), int(head_unit * 0.3),
                           skin, skin_shadow, skin_light, light_dir, detail_level=3)
        
        # Bicep
        elbow_x = sx + side * int(head_unit * 0.2)
        elbow_y = sy + upper_arm_len
        draw_organic_limb(draw, img, (sx, sy), (elbow_x, elbow_y),
                          int(head_unit * 0.4), int(head_unit * 0.33), skin, skin_shadow, skin_light,
                          bend=side * 4, segments=30)
        
        # Tricep
        draw_organic_limb(draw, img, (sx + side * 6, sy + 5), (elbow_x + side * 6, elbow_y),
                          int(head_unit * 0.28), int(head_unit * 0.22), skin, skin_shadow, skin_light,
                          bend=side * 3, segments=25)
        
        # Forearm
        wrist_x = elbow_x + side * int(head_unit * 0.12)
        wrist_y = elbow_y + forearm_len
        draw_organic_limb(draw, img, (elbow_x, elbow_y), (wrist_x, wrist_y),
                          int(head_unit * 0.3), int(head_unit * 0.25), skin, skin_shadow, skin_light,
                          bend=side * 3, segments=30)
        
        # Hand
        draw_muscle_volume(draw, img, wrist_x, wrist_y + 5, int(head_unit * 0.18), int(head_unit * 0.18),
                           skin, skin_shadow, skin_light, light_dir, detail_level=2)
        for f in range(4):
            fx = wrist_x - 8 + f * 5 + side * 2
            draw_organic_limb(draw, img, (fx, wrist_y + 8), (fx + side * 2, wrist_y + 24),
                              3, 2, skin, skin_shadow, skin_light, segments=12)
        draw_organic_limb(draw, img, (wrist_x + side * 12, wrist_y + 2), (wrist_x + side * 20, wrist_y + 12),
                          4, 2, skin, skin_shadow, skin_light, segments=10)

    # === LEGS ===
    upper_leg_len = int(head_unit * 2.0)
    lower_leg_len = int(head_unit * 1.9)

    for side in [-1, 1]:
        hx = cx + side * int(hip_w * 0.22)
        hy = hip_y
        
        # Glute
        draw_muscle_volume(draw, img, hx, hy, int(head_unit * 0.38), int(head_unit * 0.32),
                           skin, skin_shadow, skin_light, light_dir, detail_level=3)
        
        # Thigh
        knee_x = hx + side * int(head_unit * 0.15)
        knee_y = hy + upper_leg_len
        draw_organic_limb(draw, img, (hx, hy), (knee_x, knee_y),
                          int(head_unit * 0.5), int(head_unit * 0.4), skin, skin_shadow, skin_light,
                          bend=side * 3, segments=35)
        
        # Hamstring
        draw_organic_limb(draw, img, (hx + side * 3, hy + 5), (knee_x + side * 3, knee_y),
                          int(head_unit * 0.35), int(head_unit * 0.28), skin, skin_shadow, skin_light,
                          bend=side * 2, segments=30)
        
        # Calf
        ankle_x = knee_x + side * int(head_unit * 0.1)
        ankle_y = knee_y + lower_leg_len
        draw_organic_limb(draw, img, (knee_x, knee_y), (ankle_x, ankle_y),
                          int(head_unit * 0.35), int(head_unit * 0.25), skin, skin_shadow, skin_light,
                          bend=side * 2, segments=35)
        
        # Foot
        draw_organic_limb(draw, img, (ankle_x, ankle_y), (ankle_x + side * 20, ankle_y + 4),
                          int(head_unit * 0.28), int(head_unit * 0.22), skin, skin_shadow, skin_light,
                          segments=15)
        for t in range(4):
            tx = ankle_x + side * (5 + t * 4)
            draw_organic_limb(draw, img, (tx, ankle_y + 2), (tx + side * 2, ankle_y + 8),
                              4, 2, skin, skin_shadow, skin_light, segments=8)

    # === TEXTURE (Principle 6) ===
    skin_texture(img, cx - shoulder_w//2, shoulder_y, shoulder_w, hip_y - shoulder_y, skin, density=0.012)

    # === LIGHT (Principle 5) — Global ===
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.polygon([(0, 0), (cx - 50, 0), (cx - 50, H), (0, H)], fill=(0, 0, 0, 20))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=50))
    img.paste(shadow, (0, 0), shadow)

    # Paper texture
    paper = Image.new('RGBA', img.size, (0, 0, 0, 0))
    pd = ImageDraw.Draw(paper)
    for _ in range(int(W * H * 0.002)):
        px = random.randint(0, W - 1)
        py = random.randint(0, H - 1)
        pd.point((px, py), fill=(0, 0, 0, random.randint(3, 12)))
    paper = paper.filter(ImageFilter.GaussianBlur(radius=0.5))
    img.paste(paper, (0, 0), paper)

    return img


def main():
    parser = argparse.ArgumentParser(description="Master Draw v6 — Own the code")
    parser.add_argument("--subject", type=str, default="human")
    parser.add_argument("--output", type=str, default="output.png")
    parser.add_argument("--width", type=int, default=600)
    parser.add_argument("--height", type=int, default=900)
    args = parser.parse_args()

    img = create_canvas(args.width, args.height, (248, 245, 238))
    draw_human_v6(img, args.width, args.height)
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    img.save(args.output)
    print(f"Saved: {args.output} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
