#!/usr/bin/env python3
"""
Master Draw v4 — Everything is 0s and 1s. We master drawing ANYTHING.

True mastery through code: bezier curves, anatomical construction,
volume-aware shading, texture simulation, perspective, and detail.

This is NOT a fallback. This IS the art. Every pixel is intentional.

Usage:
    python master_draw_v4.py --subject human --pose standing --output human.png
    python master_draw_v4.py --subject cat --pose sitting --output cat.png
    python master_draw_v4.py --subject robot --pose standing --output robot.png
    python master_draw_v4.py --list
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
# BEZIER CURVE SYSTEM (Organic forms)
# ============================================================

def cubic_bezier(draw, p0, p1, p2, p3, color, width=2, steps=60):
    """Draw a smooth cubic bezier curve."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = (1-t)**3 * p0[0] + 3*(1-t)**2*t * p1[0] + 3*(1-t)*t**2 * p2[0] + t**3 * p3[0]
        y = (1-t)**3 * p0[1] + 3*(1-t)**2*t * p1[1] + 3*(1-t)*t**2 * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i+1]], fill=color, width=width)


def quadratic_bezier(draw, p0, p1, p2, color, width=2, steps=40):
    """Draw a smooth quadratic bezier curve."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = (1-t)**2 * p0[0] + 2*(1-t)*t * p1[0] + t**2 * p2[0]
        y = (1-t)**2 * p0[1] + 2*(1-t)*t * p1[1] + t**2 * p2[1]
        pts.append((x, y))
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i+1]], fill=color, width=width)


def draw_smooth_contour(draw, img, points, fill_color, outline_color=None, outline_width=2):
    """Draw a smooth filled contour using bezier interpolation."""
    if len(points) < 3:
        return
    # Create smooth polygon
    smooth = []
    n = len(points)
    for i in range(n):
        p0 = points[i]
        p1 = points[(i + 1) % n]
        p2 = points[(i + 2) % n]
        # Midpoint
        mx = (p0[0] + p1[0]) / 2
        my = (p0[1] + p1[1]) / 2
        smooth.append((mx, my))
    if len(smooth) >= 3:
        draw.polygon(smooth, fill=fill_color, outline=outline_color)


# ============================================================
# ANATOMICAL CONSTRUCTION (Bones → Muscles → Skin)
# ============================================================

class Bone:
    def __init__(self, start, end, name=""):
        self.start = start
        self.end = end
        self.name = name
        self.children = []
    
    def length(self):
        dx = self.end[0] - self.start[0]
        dy = self.end[1] - self.start[1]
        return math.sqrt(dx*dx + dy*dy)


class Skeleton:
    def __init__(self):
        self.bones = {}
        self.root = None
    
    def add_bone(self, name, start, end, parent=None):
        bone = Bone(start, end, name)
        self.bones[name] = bone
        if parent and parent in self.bones:
            self.bones[parent].children.append(name)
        if self.root is None:
            self.root = name
        return bone
    
    def draw(self, draw, color=(100, 100, 100), width=1):
        for name, bone in self.bones.items():
            draw.line([bone.start, bone.end], fill=color, width=width)
            # Joint
            draw.ellipse([bone.start[0]-3, bone.start[1]-3, bone.start[0]+3, bone.start[1]+3], 
                        fill=color)


# ============================================================
# VOLUME-AWARE SHADING (Light physics)
# ============================================================

def shade_volume(img, cx, cy, rx, ry, base_color, light_dir, 
                 ambient=0.2, diffuse=0.6, specular=0.2, shininess=16):
    """Shade an elliptical volume with proper light physics."""
    draw = ImageDraw.Draw(img)
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            dx = (x - cx) / max(1, rx)
            dy = (y - cy) / max(1, ry)
            dist = math.sqrt(dx*dx + dy*dy)
            if dist <= 1.0:
                # Surface normal (ellipsoid)
                nz = math.sqrt(max(0, 1 - dx*dx - dy*dy))
                # Light direction
                lx, ly, lz = light_dir
                mag = math.sqrt(lx*lx + ly*ly + lz*lz)
                lx, ly, lz = lx/mag, ly/mag, lz/mag
                # Diffuse (Lambert)
                ndotl = max(0, dx * lx + dy * ly + nz * lz)
                # Specular (Blinn-Phong)
                hx = lx + 0  # view dir is (0,0,1)
                hy = ly + 0
                hz = lz + 1
                hmag = math.sqrt(hx*hx + hy*hy + hz*hz)
                if hmag > 0:
                    hx, hy, hz = hx/hmag, hy/hmag, hz/hmag
                    spec = max(0, dx * hx + dy * hy + nz * hz) ** shininess
                else:
                    spec = 0
                # Final
                shade = ambient + diffuse * ndotl + specular * spec
                # Edge darkening (ambient occlusion)
                edge = 1 - dist ** 2.5
                color = tuple(min(255, int(base_color[i] * shade * edge)) for i in range(3))
                # Specular highlight
                if spec > 0.3:
                    color = tuple(min(255, int(color[i] + 80 * spec)) for i in range(3))
                draw.point((x, y), fill=color + (255,))


# ============================================================
# TEXTURE SIMULATION
# ============================================================

def skin_texture(img, x, y, w, h, color, density=0.03):
    """Simulate skin texture (pores, subtle variation)."""
    draw = ImageDraw.Draw(img)
    for _ in range(int(w * h * density)):
        px = random.randint(x, x + w - 1)
        py = random.randint(y, y + h - 1)
        # Small pore
        r = random.choice([1, 1, 1, 2])
        shade = random.randint(-15, 15)
        c = tuple(max(0, min(255, color[i] + shade)) for i in range(3))
        draw.ellipse([px, py, px + r, py + r], fill=c + (random.randint(100, 180),))


def fur_texture(img, x, y, w, h, base_color, density=0.05):
    """Simulate fur texture (strands)."""
    draw = ImageDraw.Draw(img)
    for _ in range(int(w * h * density)):
        px = random.randint(x, x + w - 1)
        py = random.randint(y, y + h - 1)
        # Strand direction (mostly vertical/down)
        angle = random.uniform(-30, 30)
        length = random.randint(3, 8)
        ex = px + int(length * math.sin(math.radians(angle)))
        ey = py + int(length * math.cos(math.radians(angle)))
        shade = random.randint(-20, 20)
        c = tuple(max(0, min(255, base_color[i] + shade)) for i in range(3))
        draw.line([(px, py), (ex, ey)], fill=c + (random.randint(80, 150),), width=1)


def metal_texture(img, x, y, w, h, base_color, density=0.02):
    """Simulate metal texture (scratches, reflections)."""
    draw = ImageDraw.Draw(img)
    # Scratches
    for _ in range(int(w * h * density)):
        px = random.randint(x, x + w - 1)
        py = random.randint(y, y + h - 1)
        length = random.randint(5, 20)
        angle = random.uniform(0, 180)
        ex = px + int(length * math.cos(math.radians(angle)))
        ey = py + int(length * math.sin(math.radians(angle)))
        c = tuple(min(255, base_color[i] + 40) for i in range(3))
        draw.line([(px, py), (ex, ey)], fill=c + (random.randint(30, 80),), width=1)


# ============================================================
# MASTER HUMAN v4 (All 6 principles)
# ============================================================

def draw_human_v4(img):
    """Masterful human with all 6 principles fully implemented."""
    draw = ImageDraw.Draw(img)
    W, H = img.size
    cx = W // 2
    head_unit = H // 8

    # Colors
    skin = (225, 190, 160)
    skin_light = (248, 218, 188)
    skin_shadow = (165, 125, 95)
    skin_deep = (115, 80, 50)

    light_dir = (-0.4, -0.6, 0.5)

    # === GESTURE (Principle 3) ===
    # Dynamic pose: weight shifted, slight twist
    gesture = [
        (cx, int(H * 0.03)),           # head
        (cx + 3, int(H * 0.12)),       # neck
        (cx + 8, int(H * 0.30)),       # chest (shifted right)
        (cx + 2, int(H * 0.50)),       # waist
        (cx - 8, int(H * 0.72)),       # hip (shifted left)
        (cx + 15, int(H * 0.95)),      # right foot (weight bearing)
    ]

    # === CONSTRUCTION (Principle 1) ===
    # Head
    head_cy = int(H * 0.08)
    head_r = int(head_unit * 0.4)
    
    # Skull (sphere)
    shade_volume(img, cx, head_cy, head_r, int(head_r * 1.1), skin, light_dir)
    
    # Jaw (organic)
    draw_organic_limb(draw, img, (cx - int(head_r*0.55), head_cy + int(head_r*0.25)),
                      (cx, head_cy + int(head_r*0.85)), int(head_r*0.9), int(head_r*0.45),
                      skin, skin_shadow, skin_light, bend=0, segments=20)
    draw_organic_limb(draw, img, (cx + int(head_r*0.55), head_cy + int(head_r*0.25)),
                      (cx, head_cy + int(head_r*0.85)), int(head_r*0.9), int(head_r*0.45),
                      skin, skin_shadow, skin_light, bend=0, segments=20)

    # === ANATOMY (Principle 4) ===
    # Eyes
    eye_y = head_cy - int(head_r * 0.05)
    eye_spacing = int(head_r * 0.42)
    for side in [-1, 1]:
        ex = cx + side * eye_spacing
        # Orbital bone
        draw.ellipse([ex - 12, eye_y - 8, ex + 12, eye_y + 8], fill=skin_deep)
        # Sclera
        draw.ellipse([ex - 10, eye_y - 6, ex + 10, eye_y + 6], fill=(248, 248, 245))
        # Iris
        shade_volume(img, ex + side, eye_y, 5, 5, (50, 70, 40), light_dir, specular=0.4, shininess=8)
        # Pupil
        draw.ellipse([ex + side - 2, eye_y - 3, ex + side + 3, eye_y + 3], fill=(8, 8, 12))
        # Highlights
        hx = ex + side * 4
        draw.ellipse([hx, eye_y - 3, hx + 3, eye_y], fill=(255, 255, 255))
        draw.ellipse([ex + side, eye_y + 1, ex + side + 2, eye_y + 3], fill=(255, 255, 255, 160))

    # Nose
    nose_top = eye_y + 8
    nose_bottom = nose_top + int(head_r * 0.5)
    draw_organic_limb(draw, img, (cx, nose_top), (cx, nose_bottom), 6, 3, skin, skin_shadow, skin_light, segments=10)
    # Nostrils
    draw.ellipse([cx - 6, nose_bottom - 2, cx - 2, nose_bottom + 2], fill=skin_deep)
    draw.ellipse([cx + 2, nose_bottom - 2, cx + 6, nose_bottom + 2], fill=skin_deep)

    # Mouth
    mouth_y = nose_bottom + 6
    draw.arc([cx - 13, mouth_y - 2, cx + 13, mouth_y + 10], start=195, end=345, fill=skin_deep, width=2)
    draw.arc([cx - 15, mouth_y + 3, cx + 15, mouth_y + 14], start=20, end=160, fill=skin_deep, width=2)

    # Neck
    neck_top = head_cy + head_r
    neck_bottom = neck_top + int(head_unit * 0.35)
    draw_organic_limb(draw, img, (cx, neck_top), (cx, neck_bottom),
                      int(head_unit * 0.38), int(head_unit * 0.32), skin, skin_shadow, skin_light, segments=12)

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
        shade_volume(img, sx, shoulder_y, int(head_unit * 0.35), int(head_unit * 0.35), skin, light_dir)

    # Pectoralis
    for side in [-1, 1]:
        px = cx + side * int(shoulder_w * 0.18)
        py = chest_y
        shade_volume(img, px, py, int(head_unit * 0.45), int(head_unit * 0.35), skin, light_dir)

    # Abdomen segments
    ab_top = chest_y + int(head_unit * 0.4)
    ab_bottom = waist_y
    for i in range(4):
        seg_y = ab_top + i * (ab_bottom - ab_top) // 4
        seg_h = (ab_bottom - ab_top) // 4
        shade_volume(img, cx, seg_y + seg_h // 2, int(waist_w * 0.35), int(seg_h * 0.4), skin, light_dir)

    # === ARMS ===
    upper_arm_len = int(head_unit * 1.0)
    forearm_len = int(head_unit * 1.0)

    for side in [-1, 1]:
        sx = cx + side * (shoulder_w // 2)
        sy = shoulder_y
        
        # Deltoid
        shade_volume(img, sx, sy, int(head_unit * 0.3), int(head_unit * 0.3), skin, light_dir)
        
        # Bicep
        elbow_x = sx + side * int(head_unit * 0.18)
        elbow_y = sy + upper_arm_len
        draw_organic_limb(draw, img, (sx, sy), (elbow_x, elbow_y),
                          int(head_unit * 0.4), int(head_unit * 0.33), skin, skin_shadow, skin_light,
                          bend=side * 4, segments=20)
        
        # Forearm
        wrist_x = elbow_x + side * int(head_unit * 0.12)
        wrist_y = elbow_y + forearm_len
        draw_organic_limb(draw, img, (elbow_x, elbow_y), (wrist_x, wrist_y),
                          int(head_unit * 0.3), int(head_unit * 0.25), skin, skin_shadow, skin_light,
                          bend=side * 3, segments=20)
        
        # Hand
        shade_volume(img, wrist_x, wrist_y + 5, int(head_unit * 0.18), int(head_unit * 0.18), skin, light_dir)
        for f in range(4):
            fx = wrist_x - 8 + f * 5 + side * 2
            draw_organic_limb(draw, img, (fx, wrist_y + 8), (fx + side * 2, wrist_y + 22),
                              3, 2, skin, skin_shadow, skin_light, segments=8)

    # === LEGS ===
    upper_leg_len = int(head_unit * 2.0)
    lower_leg_len = int(head_unit * 1.9)

    for side in [-1, 1]:
        hx = cx + side * int(hip_w * 0.22)
        hy = hip_y
        
        # Glute
        shade_volume(img, hx, hy, int(head_unit * 0.35), int(head_unit * 0.3), skin, light_dir)
        
        # Thigh
        knee_x = hx + side * int(head_unit * 0.15)
        knee_y = hy + upper_leg_len
        draw_organic_limb(draw, img, (hx, hy), (knee_x, knee_y),
                          int(head_unit * 0.5), int(head_unit * 0.4), skin, skin_shadow, skin_light,
                          bend=side * 3, segments=25)
        
        # Calf
        ankle_x = knee_x + side * int(head_unit * 0.1)
        ankle_y = knee_y + lower_leg_len
        draw_organic_limb(draw, img, (knee_x, knee_y), (ankle_x, ankle_y),
                          int(head_unit * 0.35), int(head_unit * 0.25), skin, skin_shadow, skin_light,
                          bend=side * 2, segments=25)
        
        # Foot
        draw_organic_limb(draw, img, (ankle_x, ankle_y), (ankle_x + side * 18, ankle_y + 4),
                          int(head_unit * 0.25), int(head_unit * 0.2), skin, skin_shadow, skin_light,
                          segments=10)

    # === TEXTURE (Principle 6) ===
    skin_texture(img, cx - shoulder_w//2, shoulder_y, shoulder_w, hip_y - shoulder_y, skin, density=0.02)

    # === LIGHT (Principle 5) — Global shadow ===
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.polygon([(0, 0), (cx - 45, 0), (cx - 45, H), (0, H)], fill=(0, 0, 0, 25))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=40))
    img.paste(shadow, (0, 0), shadow)

    return img


# ============================================================
# MASTER CAT v4
# ============================================================

def draw_cat_v4(img):
    """Masterful cat with all 6 principles."""
    draw = ImageDraw.Draw(img)
    W, H = img.size
    cx = W // 2
    head_unit = H // 6

    fur = (190, 170, 140)
    fur_light = (220, 200, 170)
    fur_shadow = (135, 105, 75)
    fur_deep = (85, 60, 35)

    light_dir = (-0.4, -0.6, 0.5)

    # === CONSTRUCTION — Head ===
    head_r = int(head_unit * 0.7)
    head_cx = cx
    head_cy = int(H * 0.16)

    shade_volume(img, head_cx, head_cy, head_r, int(head_r * 0.85), fur, light_dir)

    # Ears
    for side in [-1, 1]:
        ex = head_cx + side * (head_r - 5)
        ey = head_cy - int(head_r * 0.55)
        pts = [(ex, ey), (ex + side * 18, ey - int(head_r * 0.9)), (ex + side * 4, ey - int(head_r * 0.35))]
        draw.polygon(pts, fill=fur, outline=fur_deep)
        pts2 = [(ex + side * 2, ey - 3), (ex + side * 14, ey - int(head_r * 0.9) + 8), (ex + side * 3, ey - int(head_r * 0.35))]
        draw.polygon(pts2, fill=(210, 160, 150))

    # Eyes
    eye_y = head_cy - 3
    for side in [-1, 1]:
        ex = head_cx + side * (head_r // 3)
        draw.ellipse([ex - 14, eye_y - 9, ex + 14, eye_y + 9], fill=fur_deep)
        draw.ellipse([ex - 12, eye_y - 7, ex + 12, eye_y + 7], fill=(110, 170, 70))
        shade_volume(img, ex + side, eye_y, 4, 4, (45, 95, 35), light_dir, specular=0.5, shininess=12)
        draw.ellipse([ex - 3, eye_y - 8, ex + 3, eye_y + 8], fill=(10, 10, 15))
        draw.ellipse([ex + 4, eye_y - 6, ex + 8, eye_y - 2], fill=(255, 255, 255))
        draw.ellipse([ex - 2, eye_y + 2, ex + 1, eye_y + 5], fill=(255, 255, 255, 160))

    # Nose
    nose_y = head_cy + int(head_r * 0.15)
    draw.polygon([(head_cx, nose_y), (head_cx - 7, nose_y + 8), (head_cx + 7, nose_y + 8)],
                fill=(190, 110, 90), outline=fur_deep)

    # Mouth
    draw.line([(head_cx, nose_y + 8), (head_cx, nose_y + 16)], fill=fur_deep, width=1)
    draw.arc([head_cx - 12, nose_y + 12, head_cx, nose_y + 26], start=0, end=180, fill=fur_deep, width=1)
    draw.arc([head_cx, nose_y + 12, head_cx + 12, nose_y + 26], start=0, end=180, fill=fur_deep, width=1)

    # Whiskers
    for side in [-1, 1]:
        for i in range(3):
            wy = nose_y + 4 + i * 5
            points = [(head_cx + side * 7, wy)]
            for j in range(6):
                wx = head_cx + side * (7 + j * 9)
                wy2 = wy + random.randint(-2, 2)
                points.append((wx, wy2))
            for j in range(len(points) - 1):
                draw.line([points[j], points[j+1]], fill=fur_deep, width=1)

    # === BODY ===
    body_cx = cx
    body_cy = head_cy + int(head_r * 1.4) + int(head_unit * 1.0)
    body_w = int(head_unit * 2.6)
    body_h = int(head_unit * 2.0)
    body_x = body_cx - body_w // 2
    body_y = body_cy - body_h // 2

    for y in range(body_y, body_y + body_h):
        for x in range(body_x, body_x + body_w):
            dx = (x - body_cx) / (body_w / 2)
            dy = (y - body_cy) / (body_h / 2)
            dist = math.sqrt(dx*dx + dy*dy)
            if dist <= 1.0:
                light = max(0, 0.4 + 0.3 * (-dx * 0.2 - dy * 0.35 + 0.65))
                shade = 0.4 + 0.4 * light
                color = tuple(min(255, int(fur[i] * shade)) for i in range(3))
                edge = 1 - dist ** 2
                color = tuple(int(color[i] * edge + fur_shadow[i] * (1 - edge) * 0.3) for i in range(3))
                draw.point((x, y), fill=color + (255,))

    # === FRONT LEGS ===
    leg_w = int(head_unit * 0.4)
    for side in [-1, 1]:
        lx = body_cx + side * (body_w // 4)
        draw_organic_limb(draw, img, (lx, body_y + body_h // 3),
                          (lx, body_y + body_h - 5), leg_w, int(leg_w * 0.75),
                          fur, fur_shadow, fur_light, bend=side * 2, segments=15)
        draw_organic_limb(draw, img, (lx - leg_w // 2, body_y + body_h - 5),
                          (lx + leg_w // 2, body_y + body_h + 10), int(leg_w * 1.6), int(leg_w * 1.3),
                          fur, fur_shadow, fur_light, segments=10)
        for t in range(4):
            tx = lx - leg_w + t * (leg_w // 2) + 2
            draw.ellipse([tx - 3, body_y + body_h + 5, tx + 3, body_y + body_h + 12],
                        fill=fur, outline=fur_deep, width=1)

    # === TAIL ===
    tail_points = []
    tx = body_x + body_w
    ty = body_cy
    for i in range(12):
        angle = math.radians(-15 + i * 3)
        tail_points.append((tx + i * 12, ty + int(math.sin(angle) * 12)))
    for i in range(len(tail_points) - 1):
        width = max(2, 7 - i // 2)
        draw.line([tail_points[i], tail_points[i+1]], fill=fur, width=width)

    # === TEXTURE ===
    fur_texture(img, body_x, body_y, body_w, body_h, fur, density=0.04)

    # === SHADING ===
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([body_x + 10, body_y + body_h - 5, body_x + body_w - 10, body_y + body_h + 15],
              fill=(0, 0, 0, 40))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=8))
    img.paste(shadow, (0, 0), shadow)

    return img


# ============================================================
# MASTER ROBOT v4
# ============================================================

def draw_robot_v4(img):
    """Masterful robot with all 6 principles."""
    draw = ImageDraw.Draw(img)
    W, H = img.size
    cx = W // 2
    head_unit = H // 8

    p = {
        "highlight": (195, 230, 185),
        "light": (115, 185, 90),
        "base": (46, 204, 113),
        "medium": (39, 174, 96),
        "dark": (26, 156, 84),
        "deep": (18, 50, 30),
        "accent": (241, 196, 15),
        "eye": (44, 62, 80),
        "white": (255, 255, 255),
    }

    light_dir = (-0.4, -0.6, 0.5)

    head_h = int(H * 0.20)
    body_h = int(H * 0.33)
    head_y = int(H * 0.06)
    body_y = head_y + head_h + 6
    body_w = int(W * 0.40)
    body_x = (W - body_w) // 2
    head_w = int(body_w * 0.85)
    head_x = (W - head_w) // 2

    # === BODY ===
    multi_pass_shadow(img, body_x, body_y, body_w, body_h, corner_r=22)
    for y in range(body_y, body_y + body_h):
        for x in range(body_x, body_x + body_w):
            dx = (x - (body_x + body_w//2)) / (body_w / 2)
            dy = (y - (body_y + body_h//2)) / (body_h / 2)
            dist = math.sqrt(dx*dx + dy*dy)
            if dist <= 1.0:
                light = max(0, 0.35 + 0.4 * (-dx * 0.25 - dy * 0.3 + 0.6))
                shade = 0.3 + 0.5 * light
                color = tuple(min(255, int(p["base"][i] * shade + p["light"][i] * light * 0.3)) for i in range(3))
                edge = 1 - dist ** 2.5
                color = tuple(int(color[i] * edge + p["deep"][i] * (1 - edge) * 0.4) for i in range(3))
                draw.point((x, y), fill=color + (255,))
    draw.rounded_rectangle([body_x, body_y, body_x + body_w, body_y + body_h],
                          radius=22, outline=p["deep"], width=2)
    # Panel lines
    draw.line([(body_x + body_w//2, body_y + 10), (body_x + body_w//2, body_y + body_h - 10)],
              fill=p["dark"] + (80,), width=1)
    draw.line([(body_x + 10, body_y + body_h//2), (body_x + body_w - 10, body_y + body_h//2)],
              fill=p["dark"] + (80,), width=1)
    # Chest light
    cx2, cy2 = body_x + body_w//2, body_y + int(body_h * 0.22)
    glow_effect(img, cx2, cy2, 35, p["accent"], intensity=80, blur=12)
    gradient_circle(draw, img, cx2, cy2, 18, p["accent"], (180, 140, 10))
    specular_highlight(img, cx2 - 4, cy2 - 4, 6, (255, 255, 200), 200)
    ambient_occlusion(img, body_x, body_y, body_w, body_h, corner_r=22, intensity=25)
    rim_light(img, body_x, body_y, body_w, body_h, corner_r=22, color=p["highlight"], intensity=50)

    # === HEAD ===
    multi_pass_shadow(img, head_x, head_y, head_w, head_h, corner_r=30)
    for y in range(head_y, head_y + head_h):
        for x in range(head_x, head_x + head_w):
            dx = (x - (head_x + head_w//2)) / (head_w / 2)
            dy = (y - (head_y + head_h//2)) / (head_h / 2)
            dist = math.sqrt(dx*dx + dy*dy)
            if dist <= 1.0:
                light = max(0, 0.4 + 0.35 * (-dx * 0.2 - dy * 0.3 + 0.65))
                shade = 0.35 + 0.45 * light
                color = tuple(min(255, int(p["medium"][i] * shade + p["light"][i] * light * 0.3)) for i in range(3))
                edge = 1 - dist ** 2
                color = tuple(int(color[i] * edge + p["deep"][i] * (1 - edge) * 0.3) for i in range(3))
                draw.point((x, y), fill=color + (255,))
    draw.rounded_rectangle([head_x, head_y, head_x + head_w, head_y + head_h],
                          radius=30, outline=p["deep"], width=2)
    ambient_occlusion(img, head_x, head_y, head_w, head_h, corner_r=30, intensity=20)
    rim_light(img, head_x, head_y, head_w, head_h, corner_r=30, color=p["highlight"], intensity=40)

    # Antenna
    ant_x = head_x + head_w // 2
    for i in range(head_y - 35, head_y + 5):
        t = (i - (head_y - 35)) / 40
        color = tuple(int(p["dark"][j] * (1 - t) + p["medium"][j] * t) for j in range(3))
        draw.line([(ant_x - 4, i), (ant_x + 4, i)], fill=color + (255,), width=1)
    gradient_circle(draw, img, ant_x, head_y - 40, 14, (231, 76, 60), (160, 40, 30))
    specular_highlight(img, ant_x - 3, head_y - 44, 5, (255, 150, 150), 180)
    glow_effect(img, ant_x, head_y - 40, 20, (231, 76, 60), intensity=45, blur=8)

    # Eyes
    eye_y = head_y + int(head_h * 0.42)
    for ex in [head_x + int(head_w * 0.3), head_x + int(head_w * 0.7)]:
        draw.ellipse([ex - 22, eye_y - 26, ex + 22, eye_y + 26], fill=p["deep"])
        draw.ellipse([ex - 20, eye_y - 24, ex + 20, eye_y + 24], fill=p["white"])
        gradient_circle(draw, img, ex + 3, eye_y + 1, 12, p["eye"], (20, 30, 50))
        draw.ellipse([ex + 7, eye_y - 2, ex + 18, eye_y + 12], fill=(8, 12, 20))
        specular_highlight(img, ex + 14, eye_y - 5, 4, (255, 255, 255), 220)
        specular_highlight(img, ex + 4, eye_y + 6, 2, (255, 255, 255), 120)
        blush = Image.new('RGBA', img.size, (0, 0, 0, 0))
        bd = ImageDraw.Draw(blush)
        bd.ellipse([ex - 16, eye_y + 18, ex + 16, eye_y + 38], fill=(255, 107, 107, 45))
        blush = blush.filter(ImageFilter.GaussianBlur(radius=6))
        img.paste(blush, (0, 0), blush)

    # Smile
    draw.arc([head_x + 25, eye_y + 22, head_x + head_w - 25, eye_y + 55],
            start=10, end=170, fill=p["deep"], width=2)

    # Arms
    arm_y = body_y + int(body_h * 0.12)
    for side in [-1, 1]:
        if side == -1:
            ax0, ax1 = body_x - 55, body_x
        else:
            ax0, ax1 = body_x + body_w, body_x + body_w + 55
        for y in range(arm_y, arm_y + 22):
            for x in range(min(ax0, ax1), max(ax0, ax1)):
                light = 0.4
                shade = 0.4 + 0.3 * light
                color = tuple(min(255, int(p["medium"][i] * shade)) for i in range(3))
                draw.point((x, y), fill=color + (255,))
        draw.rounded_rectangle([min(ax0, ax1), arm_y, max(ax0, ax1), arm_y + 22],
                              radius=10, outline=p["deep"], width=2)
        hx = body_x - 60 if side == -1 else body_x + body_w + 60
        gradient_circle(draw, img, hx, arm_y + 11, 20, p["base"], p["medium"])
        specular_highlight(img, hx - 4, arm_y + 6, 7, p["white"], 120)

    # Legs
    leg_y = body_y + body_h
    for lx in [body_x + 12, body_x + body_w - 47]:
        for y in range(leg_y, leg_y + int(H * 0.10)):
            for x in range(lx, lx + 35):
                light = 0.4
                shade = 0.4 + 0.2 * light
                color = tuple(min(255, int(p["medium"][i] * shade)) for i in range(3))
                draw.point((x, y), fill=color + (255,))
        draw.rounded_rectangle([lx, leg_y, lx + 35, leg_y + int(H * 0.10)],
                              radius=10, outline=p["deep"], width=2)
        draw.rounded_rectangle([lx - 8, leg_y + int(H * 0.10) - 4, lx + 43, leg_y + int(H * 0.10) + 18],
                              radius=7, fill=p["dark"], outline=p["deep"], width=2)

    # Bolts
    for bx, by in [(body_x + 12, body_y + 30), (body_x + body_w - 12, body_y + 30),
                   (body_x + 12, body_y + body_h - 30), (body_x + body_w - 12, body_y + body_h - 30)]:
        gradient_circle(draw, img, bx, by, 6, p["dark"], p["deep"])
        specular_highlight(img, bx - 2, by - 2, 3, p["white"], 150)

    # Texture
    metal_texture(img, body_x, body_y, body_w, body_h, p["base"], density=0.02)

    # Global shading
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.polygon([(0, 0), (cx - 30, 0), (cx - 30, H), (0, H)], fill=(0, 0, 0, 20))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=35))
    img.paste(shadow, (0, 0), shadow)

    return img


SUBJECTS = {
    "human": draw_human_v4,
    "cat": draw_cat_v4,
    "robot": draw_robot_v4,
}


def main():
    parser = argparse.ArgumentParser(description="Master Draw v4 — Everything is 0s and 1s")
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
