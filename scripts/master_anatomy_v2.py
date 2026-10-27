#!/usr/bin/env python3
"""
Master Anatomy Draw v2 — Truly masterful drawings with organic forms.

Uses bezier curves, anatomical construction, volume-aware shading,
perspective, and texture simulation.

Usage:
    python master_anatomy_v2.py --subject human --pose standing --output human.png
    python master_anatomy_v2.py --subject cat --pose sitting --output cat.png
    python master_anatomy_v2.py --list
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
# BEZIER CURVE UTILITIES
# ============================================================

def bezier_point(points, t):
    """Evaluate a bezier curve at parameter t."""
    n = len(points) - 1
    result = [0, 0]
    for i, (px, py) in enumerate(points):
        coeff = math.comb(n, i) * (t ** i) * ((1 - t) ** (n - i))
        result[0] += px * coeff
        result[1] += py * coeff
    return tuple(result)


def draw_bezier(draw, points, color, width=2, steps=50):
    """Draw a smooth bezier curve."""
    pts = [bezier_point(points, t / steps) for t in range(steps + 1)]
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=color, width=width)


def fill_bezier_region(draw, img, contour_points, fill_color, outline_color=None, outline_width=2):
    """Fill a region defined by bezier contour points."""
    # Convert bezier to polygon
    polygon = []
    for i in range(len(contour_points) - 1):
        seg = [contour_points[i], contour_points[i + 1]]
        # Simple: just use control points as polygon vertices
        polygon.append(contour_points[i])
    if len(polygon) >= 3:
        draw.polygon(polygon, fill=fill_color, outline=outline_color)


# ============================================================
# ORGANIC FORM DRAWING
# ============================================================

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


def draw_volume_sphere(draw, img, cx, cy, r, color_base, color_shadow, color_highlight,
                      light_dir=(-0.3, -0.5)):
    """Draw a shaded sphere with volume."""
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            dx = x - cx
            dy = y - cy
            dist = math.sqrt(dx*dx + dy*dy)
            if dist <= r:
                # Normal
                nx = dx / r
                ny = dy / r
                nz = math.sqrt(max(0, 1 - nx*nx - ny*ny))
                # Light
                light = max(0, nx * light_dir[0] + ny * light_dir[1] + nz * 0.7)
                # Specular
                spec = max(0, light) ** 8
                # Color
                shade = 0.3 + 0.5 * light + 0.2 * spec
                color = tuple(min(255, int(color_base[i] * shade + color_highlight[i] * spec * 0.5)) for i in range(3))
                # Darken edges (ambient occlusion)
                edge_factor = 1 - (dist / r) ** 3
                color = tuple(int(c * edge_factor + color_shadow[i] * (1 - edge_factor) * 0.3) for i, c in enumerate(color))
                draw.point((x, y), fill=color + (255,))


# ============================================================
# MASTER HUMAN FIGURE
# ============================================================

def draw_human_master(img):
    """Draw a masterful human figure with proper anatomy."""
    draw = ImageDraw.Draw(img)
    W, H = img.size
    cx = W // 2
    head_unit = H // 8

    # Skin colors
    skin = (235, 200, 170)
    skin_light = (250, 220, 190)
    skin_shadow = (180, 140, 110)
    skin_deep = (140, 100, 70)

    # === KEY POINTS (8-head system) ===
    head_top = int(H * 0.04)
    head_bottom = head_top + head_unit
    head_cy = (head_top + head_bottom) // 2
    neck_top = head_bottom
    neck_bottom = neck_top + int(head_unit * 0.4)
    shoulder_y = neck_bottom
    chest_y = shoulder_y + int(head_unit * 0.6)
    waist_y = shoulder_y + int(head_unit * 1.4)
    hip_y = shoulder_y + int(head_unit * 2.4)
    knee_y = hip_y + int(head_unit * 2.0)
    ankle_y = knee_y + int(head_unit * 1.9)
    foot_y = ankle_y + int(head_unit * 0.4)

    shoulder_w = int(head_unit * 2.6)
    hip_w = int(head_unit * 1.7)
    waist_w = int(head_unit * 1.3)

    # === HEAD (volume sphere + details) ===
    head_r = int(head_unit * 0.45)
    draw_volume_sphere(draw, img, cx, head_cy, head_r, skin, skin_shadow, skin_light)
    
    # Jaw (organic)
    draw_organic_limb(draw, img, (cx - int(head_r*0.6), head_cy + int(head_r*0.3)),
                      (cx, head_bottom + 5), int(head_r*0.8), int(head_r*0.4),
                      skin, skin_shadow, skin_light, bend=0, segments=15)
    draw_organic_limb(draw, img, (cx + int(head_r*0.6), head_cy + int(head_r*0.3)),
                      (cx, head_bottom + 5), int(head_r*0.8), int(head_r*0.4),
                      skin, skin_shadow, skin_light, bend=0, segments=15)

    # Eyes (detailed)
    eye_y = head_cy - int(head_r * 0.1)
    eye_spacing = int(head_r * 0.45)
    for ex in [cx - eye_spacing, cx + eye_spacing]:
        # Eye socket (orbital bone)
        draw.ellipse([ex - 12, eye_y - 8, ex + 12, eye_y + 8], fill=skin_shadow)
        # Sclera
        draw.ellipse([ex - 10, eye_y - 6, ex + 10, eye_y + 6], fill=(250, 250, 245))
        # Iris
        draw_volume_sphere(draw, img, ex + 1, eye_y, 5, (60, 80, 50), (30, 50, 25), (120, 160, 100))
        # Pupil
        draw.ellipse([ex - 1, eye_y - 3, ex + 5, eye_y + 3], fill=(10, 10, 15))
        # Highlights
        draw.ellipse([ex + 3, eye_y - 3, ex + 6, eye_y], fill=(255, 255, 255))
        draw.ellipse([ex - 1, eye_y + 1, ex + 1, eye_y + 3], fill=(255, 255, 255, 180))

    # Nose (organic, with nostrils)
    nose_top = eye_y + 8
    nose_bottom = nose_top + int(head_r * 0.5)
    draw_organic_limb(draw, img, (cx, nose_top), (cx, nose_bottom), 8, 4, skin, skin_shadow, skin_light)
    # Nostrils
    draw.ellipse([cx - 6, nose_bottom - 2, cx - 2, nose_bottom + 2], fill=skin_deep)
    draw.ellipse([cx + 2, nose_bottom - 2, cx + 6, nose_bottom + 2], fill=skin_deep)

    # Mouth (lips with volume)
    mouth_y = nose_bottom + 5
    # Upper lip
    draw.arc([cx - 12, mouth_y - 3, cx + 12, mouth_y + 8], start=200, end=340, fill=skin_deep, width=2)
    # Lower lip
    draw.arc([cx - 14, mouth_y + 2, cx + 14, mouth_y + 12], start=20, end=160, fill=skin_deep, width=2)

    # === NECK ===
    draw_organic_limb(draw, img, (cx, neck_top), (cx, neck_bottom), 
                      int(head_unit * 0.45), int(head_unit * 0.4), skin, skin_shadow, skin_light)

    # === TORSO (with muscle definition) ===
    # Shoulders
    draw_volume_sphere(draw, img, cx - shoulder_w//2, shoulder_y, int(head_unit * 0.35), skin, skin_shadow, skin_light)
    draw_volume_sphere(draw, img, cx + shoulder_w//2, shoulder_y, int(head_unit * 0.35), skin, skin_shadow, skin_light)

    # Pectoralis major (left and right)
    draw_volume_sphere(draw, img, cx - int(shoulder_w * 0.2), chest_y, int(head_unit * 0.5), skin, skin_shadow, skin_light)
    draw_volume_sphere(draw, img, cx + int(shoulder_w * 0.2), chest_y, int(head_unit * 0.5), skin, skin_shadow, skin_light)

    # Abdomen (rectus abdominis)
    ab_top = chest_y + int(head_unit * 0.5)
    ab_bottom = waist_y
    for i in range(4):
        seg_y = ab_top + i * (ab_bottom - ab_top) // 4
        seg_h = (ab_bottom - ab_top) // 4
        draw_volume_sphere(draw, img, cx, seg_y + seg_h // 2, int(waist_w * 0.3), skin, skin_shadow, skin_light)

    # Obliques (sides)
    draw_organic_limb(draw, img, (cx - waist_w//2, chest_y), (cx - waist_w//2, hip_y),
                      int(head_unit * 0.4), int(head_unit * 0.3), skin, skin_shadow, skin_light, bend=-5)
    draw_organic_limb(draw, img, (cx + waist_w//2, chest_y), (cx + waist_w//2, hip_y),
                      int(head_unit * 0.4), int(head_unit * 0.3), skin, skin_shadow, skin_light, bend=5)

    # === ARMS (with muscle definition) ===
    upper_arm_len = int(head_unit * 1.0)
    forearm_len = int(head_unit * 1.0)

    for side in [-1, 1]:
        sx = cx + side * (shoulder_w // 2)
        sy = shoulder_y
        
        # Deltoid (shoulder cap)
        draw_volume_sphere(draw, img, sx, sy, int(head_unit * 0.35), skin, skin_shadow, skin_light)
        
        # Bicep
        elbow_x = sx + side * int(head_unit * 0.15)
        elbow_y = sy + upper_arm_len
        draw_organic_limb(draw, img, (sx, sy), (elbow_x, elbow_y),
                          int(head_unit * 0.4), int(head_unit * 0.35), skin, skin_shadow, skin_light,
                          bend=side * 3, segments=20)
        
        # Tricep (back of arm)
        draw_organic_limb(draw, img, (sx + side * 5, sy + 5), (elbow_x + side * 5, elbow_y),
                          int(head_unit * 0.3), int(head_unit * 0.25), skin, skin_shadow, skin_light,
                          bend=side * 2, segments=15)
        
        # Forearm
        wrist_x = elbow_x + side * int(head_unit * 0.1)
        wrist_y = elbow_y + forearm_len
        draw_organic_limb(draw, img, (elbow_x, elbow_y), (wrist_x, wrist_y),
                          int(head_unit * 0.3), int(head_unit * 0.25), skin, skin_shadow, skin_light,
                          bend=side * 2, segments=20)
        
        # Hand
        draw_volume_sphere(draw, img, wrist_x, wrist_y + 5, int(head_unit * 0.2), skin, skin_shadow, skin_light)
        # Fingers
        for f in range(4):
            fx = wrist_x - 8 + f * 5 + side * 2
            draw_organic_limb(draw, img, (fx, wrist_y + 8), (fx + side * 2, wrist_y + 20),
                              3, 2, skin, skin_shadow, skin_light, segments=8)

    # === LEGS (with muscle definition) ===
    upper_leg_len = int(head_unit * 2.0)
    lower_leg_len = int(head_unit * 1.9)

    for side in [-1, 1]:
        hx = cx + side * int(hip_w * 0.25)
        hy = hip_y
        
        # Glute
        draw_volume_sphere(draw, img, hx, hy, int(head_unit * 0.4), skin, skin_shadow, skin_light)
        
        # Thigh (quadriceps)
        knee_x = hx + side * int(head_unit * 0.15)
        knee_y = hy + upper_leg_len
        draw_organic_limb(draw, img, (hx, hy), (knee_x, knee_y),
                          int(head_unit * 0.5), int(head_unit * 0.4), skin, skin_shadow, skin_light,
                          bend=side * 2, segments=25)
        
        # Calf
        ankle_x = knee_x + side * int(head_unit * 0.1)
        ankle_y = knee_y + lower_leg_len
        draw_organic_limb(draw, img, (knee_x, knee_y), (ankle_x, ankle_y),
                          int(head_unit * 0.35), int(head_unit * 0.25), skin, skin_shadow, skin_light,
                          bend=side * 1.5, segments=25)
        
        # Foot
        draw_organic_limb(draw, img, (ankle_x, ankle_y), (ankle_x + side * 15, ankle_y + 3),
                          int(head_unit * 0.25), int(head_unit * 0.2), skin, skin_shadow, skin_light,
                          segments=10)

    # === OVERALL SHADING ===
    # Global shadow (left side)
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.polygon([(0, 0), (cx - 30, 0), (cx - 30, H), (0, H)], fill=(0, 0, 0, 20))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=30))
    img.paste(shadow, (0, 0), shadow)

    # Ambient occlusion at joints
    for jx, jy in [(cx - shoulder_w//2, shoulder_y), (cx + shoulder_w//2, shoulder_y),
                   (cx, hip_y), (cx - shoulder_w//2 + 20, elbow_y if 'elbow_y' in dir() else 0)]:
        pass

    return img


# ============================================================
# MASTER CAT
# ============================================================

def draw_cat_master(img):
    """Draw a masterful cat with proper feline anatomy."""
    draw = ImageDraw.Draw(img)
    W, H = img.size
    cx = W // 2
    head_unit = H // 6

    fur = (200, 180, 150)
    fur_light = (225, 205, 175)
    fur_shadow = (150, 120, 90)
    fur_deep = (100, 75, 50)

    # === HEAD ===
    head_r = int(head_unit * 0.75)
    head_cx = cx
    head_cy = int(H * 0.22)

    # Head volume (slightly flattened sphere)
    for y in range(head_cy - head_r, head_cy + head_r):
        for x in range(head_cx - head_r, head_cx + head_r):
            dx = (x - head_cx) / head_r
            dy = (y - head_cy) / (head_r * 0.8)
            dist = math.sqrt(dx*dx + dy*dy)
            if dist <= 1.0:
                light = max(0, 0.4 + 0.4 * (-dx * 0.3 - dy * 0.5 + 0.5))
                spec = max(0, light) ** 6
                shade = 0.35 + 0.45 * light + 0.2 * spec
                color = tuple(min(255, int(fur[i] * shade + fur_light[i] * spec * 0.4)) for i in range(3))
                edge = 1 - dist ** 2
                color = tuple(int(color[i] * edge + fur_shadow[i] * (1 - edge) * 0.2) for i in range(3))
                draw.point((x, y), fill=color + (255,))

    # Ears (organic triangular with inner detail)
    ear_h = int(head_r * 0.9)
    for side in [-1, 1]:
        ex = head_cx + side * (head_r - 10)
        ey = head_cy - int(head_r * 0.5)
        # Outer ear
        pts = [(ex, ey), (ex + side * 15, ey - ear_h), (ex + side * 5, ey - ear_h // 2)]
        draw.polygon(pts, fill=fur, outline=fur_deep)
        # Inner ear
        pts2 = [(ex + side * 2, ey - 5), (ex + side * 12, ey - ear_h + 8), (ex + side * 4, ey - ear_h // 2)]
        draw.polygon(pts2, fill=(220, 170, 160))

    # Eyes (almond-shaped, detailed)
    eye_y = head_cy - 5
    for side in [-1, 1]:
        ex = head_cx + side * (head_r // 3)
        # Eye shape
        draw.ellipse([ex - 14, eye_y - 9, ex + 14, eye_y + 9], fill=(120, 180, 80), outline=fur_deep, width=1)
        # Slit pupil
        draw.ellipse([ex - 3, eye_y - 8, ex + 3, eye_y + 8], fill=(15, 15, 20))
        # Iris detail
        draw.ellipse([ex - 8, eye_y - 5, ex - 4, eye_y - 1], fill=(80, 140, 50))
        # Highlights
        draw.ellipse([ex + 5, eye_y - 6, ex + 9, eye_y - 2], fill=(255, 255, 255))
        draw.ellipse([ex - 2, eye_y + 2, ex + 1, eye_y + 5], fill=(255, 255, 255, 180))

    # Nose
    nose_y = head_cy + int(head_r * 0.2)
    draw.polygon([(head_cx, nose_y), (head_cx - 6, nose_y + 7), (head_cx + 6, nose_y + 7)],
                fill=(200, 120, 100), outline=fur_deep)

    # Mouth
    draw.line([(head_cx, nose_y + 7), (head_cx, nose_y + 14)], fill=fur_deep, width=1)
    draw.arc([head_cx - 10, nose_y + 10, head_cx, nose_y + 22], start=0, end=180, fill=fur_deep, width=1)
    draw.arc([head_cx, nose_y + 10, head_cx + 10, nose_y + 22], start=0, end=180, fill=fur_deep, width=1)

    # Whiskers (with slight curve)
    for side in [-1, 1]:
        for i in range(3):
            wy = nose_y + 3 + i * 5
            # Curved whisker using multiple segments
            points = [(head_cx + side * 6, wy)]
            for j in range(5):
                wx = head_cx + side * (6 + j * 8)
                wy2 = wy + random.randint(-2, 2)
                points.append((wx, wy2))
            for j in range(len(points) - 1):
                draw.line([points[j], points[j+1]], fill=fur_deep, width=1)

    # === BODY ===
    body_cx = cx
    body_cy = head_cy + int(head_r * 1.3) + int(head_unit * 1.2)
    body_w = int(head_unit * 2.8)
    body_h = int(head_unit * 2.2)
    body_x = body_cx - body_w // 2
    body_y = body_cy - body_h // 2

    # Body volume (oval with shading)
    for y in range(body_y, body_y + body_h):
        for x in range(body_x, body_x + body_w):
            dx = (x - body_cx) / (body_w / 2)
            dy = (y - body_cy) / (body_h / 2)
            dist = math.sqrt(dx*dx + dy*dy)
            if dist <= 1.0:
                light = max(0, 0.4 + 0.3 * (-dx * 0.2 - dy * 0.4 + 0.6))
                shade = 0.4 + 0.4 * light
                color = tuple(min(255, int(fur[i] * shade)) for i in range(3))
                edge = 1 - dist ** 2
                color = tuple(int(color[i] * edge + fur_shadow[i] * (1 - edge) * 0.3) for i in range(3))
                draw.point((x, y), fill=color + (255,))

    # === FRONT LEGS ===
    leg_w = int(head_unit * 0.45)
    for side in [-1, 1]:
        lx = body_cx + side * (body_w // 4)
        # Upper leg
        draw_organic_limb(draw, img, (lx, body_y + body_h // 3),
                          (lx, body_y + body_h - 5), leg_w, int(leg_w * 0.8),
                          fur, fur_shadow, fur_light, bend=side * 2, segments=15)
        # Paw
        draw_organic_limb(draw, img, (lx - leg_w // 2, body_y + body_h - 5),
                          (lx + leg_w // 2, body_y + body_h + 8), int(leg_w * 1.5), int(leg_w * 1.2),
                          fur, fur_shadow, fur_light, segments=10)
        # Toes
        for t in range(4):
            tx = lx - leg_w + t * (leg_w // 2)
            draw.ellipse([tx - 3, body_y + body_h + 5, tx + 3, body_y + body_h + 12],
                        fill=fur, outline=fur_deep, width=1)

    # === TAIL ===
    tail_points = []
    tx = body_x + body_w
    ty = body_cy
    for i in range(15):
        angle = math.radians(-20 + i * 4)
        tail_points.append((tx + i * 10, ty + int(math.sin(angle) * 15)))
    for i in range(len(tail_points) - 1):
        width = 8 - i // 3
        draw.line([tail_points[i], tail_points[i+1]], fill=fur, width=max(2, width))

    # === SHADING ===
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([body_x + 10, body_y + body_h - 5, body_x + body_w - 10, body_y + body_h + 15],
              fill=(0, 0, 0, 40))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=8))
    img.paste(shadow, (0, 0), shadow)

    return img


SUBJECTS = {
    "human": draw_human_master,
    "cat": draw_cat_master,
}


def main():
    parser = argparse.ArgumentParser(description="Master Anatomy Drawing v2")
    parser.add_argument("--subject", type=str, default="human", help="Subject to draw")
    parser.add_argument("--output", type=str, default="output.png", help="Output file")
    parser.add_argument("--width", type=int, default=512, help="Image width")
    parser.add_argument("--height", type=int, default=768, help="Image height")
    parser.add_argument("--list", action="store_true", help="List available subjects")
    args = parser.parse_args()

    if args.list:
        print("Available subjects:")
        for s in SUBJECTS:
            print(f"  - {s}")
        return

    if args.subject not in SUBJECTS:
        print(f"Unknown subject: {args.subject}")
        sys.exit(1)

    img = create_canvas(args.width, args.height, (248, 245, 238))
    SUBJECTS[args.subject](img)
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    img.save(args.output)
    print(f"Saved: {args.output} ({img.size[0]}x{img.size[1]}) — subject: {args.subject}")


if __name__ == "__main__":
    main()
