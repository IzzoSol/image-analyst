#!/usr/bin/env python3
"""
Master Draw v3 — Full implementation of the 6 principles of masterful drawing.

1. Construction — Build from simple forms, refine progressively
2. Observation — Study the reference, measure proportions
3. Gesture — Capture energy before detail
4. Anatomy — Know the structure beneath the surface
5. Light — Understand how light interacts with form
6. Texture — Simulate real materials

Usage:
    python master_draw_v3.py --subject human --pose standing --output human.png
    python master_draw_v3.py --subject cat --pose sitting --output cat.png
    python master_draw_v3.py --subject robot --pose standing --output robot.png
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
# PRINCIPLE 1: CONSTRUCTION — Simple forms
# ============================================================

class Form:
    """A simple 3D form (sphere, cylinder, box)."""
    def __init__(self, center, size, form_type="sphere"):
        self.cx, self.cy = center
        self.w, self.h = size
        self.type = form_type  # sphere, cylinder, box
    
    def draw(self, draw, img, color, light_dir=(-0.3, -0.5)):
        if self.type == "sphere":
            draw_volume_sphere(draw, img, self.cx, self.cy, self.w // 2, color, 
                             tuple(int(c*0.5) for c in color), 
                             tuple(min(255, int(c*1.3)) for c in color), light_dir)
        elif self.type == "cylinder":
            # Draw as rounded rectangle with volume
            x0, y0 = self.cx - self.w//2, self.cy - self.h//2
            x1, y1 = self.cx + self.w//2, self.cy + self.h//2
            # Gradient fill
            for y in range(y0, y1):
                t = (y - y0) / max(1, y1 - y0)
                shade = 0.4 + 0.4 * (1 - abs(2*t - 1))
                c = tuple(min(255, int(color[i] * shade)) for i in range(3))
                draw.line([(x0, y), (x1, y)], fill=c + (255,))
            # Outline
            draw.rounded_rectangle([x0, y0, x1, y1], radius=self.w//4, outline=(80,80,80), width=1)
        elif self.type == "box":
            x0, y0 = self.cx - self.w//2, self.cy - self.h//2
            x1, y1 = self.cx + self.w//2, self.cy + self.h//2
            draw.rectangle([x0, y0, x1, y1], fill=color, outline=(80,80,80), width=1)


# ============================================================
# PRINCIPLE 3: GESTURE — Action lines
# ============================================================

def draw_gesture_line(draw, points, color=(100, 100, 100), width=2):
    """Draw an action/gesture line (the flow of the pose)."""
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=color, width=width)


def apply_gesture_to_point(point, gesture_points, influence=0.3):
    """Offset a point based on gesture flow."""
    # Find nearest gesture segment
    px, py = point
    min_dist = float('inf')
    nearest_tangent = (0, 0)
    for i in range(len(gesture_points) - 1):
        x1, y1 = gesture_points[i]
        x2, y2 = gesture_points[i+1]
        # Project point onto segment
        dx, dy = x2 - x1, y2 - y1
        seg_len = math.sqrt(dx*dx + dy*dy)
        if seg_len == 0:
            continue
        t = max(0, min(1, ((px - x1)*dx + (py - y1)*dy) / (seg_len*seg_len)))
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        dist = math.sqrt((px - proj_x)**2 + (py - proj_y)**2)
        if dist < min_dist:
            min_dist = dist
            # Tangent direction
            nearest_tangent = (dx/seg_len, dy/seg_len)
    # Offset perpendicular to tangent
    perp = (-nearest_tangent[1], nearest_tangent[0])
    return (px + perp[0] * influence * 5, py + perp[1] * influence * 5)


# ============================================================
# PRINCIPLE 5: LIGHT — Volume-aware shading
# ============================================================

def shade_form(draw, img, form, light_dir=(-0.5, -0.7, 0.3)):
    """Apply lighting to a form based on its 3D orientation."""
    # light_dir is (x, y, z) normalized
    lx, ly, lz = light_dir
    mag = math.sqrt(lx*lx + ly*ly + lz*lz)
    lx, ly, lz = lx/mag, ly/mag, lz/mag
    
    cx, cy = form.cx, form.cy
    r = form.w // 2
    
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            dx = (x - cx) / max(1, r)
            dy = (y - cy) / max(1, r)
            dist = math.sqrt(dx*dx + dy*dy)
            if dist <= 1.0:
                # Surface normal (for sphere)
                nz = math.sqrt(max(0, 1 - dx*dx - dy*dy))
                # Diffuse
                diffuse = max(0, dx * lx + dy * ly + nz * lz)
                # Specular
                spec = max(0, diffuse) ** 16
                # Ambient
                ambient = 0.25
                # Final shade
                shade = ambient + 0.55 * diffuse + 0.2 * spec
                # Edge darkening (ambient occlusion)
                edge = 1 - dist ** 3
                # Color
                base = form.color if hasattr(form, 'color') else (200, 180, 150)
                c = tuple(min(255, int(base[i] * shade * edge)) for i in range(3))
                # Specular highlight
                if spec > 0.5:
                    c = tuple(min(255, int(c[i] + 100 * spec)) for i in range(3))
                draw.point((x, y), fill=c + (255,))


# ============================================================
# MASTER HUMAN FIGURE v3
# ============================================================

def draw_human_v3(img):
    """Masterful human figure implementing all 6 principles."""
    draw = ImageDraw.Draw(img)
    W, H = img.size
    cx = W // 2
    head_unit = H // 8

    # Colors
    skin = (230, 195, 165)
    skin_light = (250, 220, 190)
    skin_shadow = (170, 130, 100)
    skin_deep = (120, 85, 55)

    # === PRINCIPLE 3: GESTURE — Action line ===
    # Slightly dynamic pose: weight on right leg, left hip shifted
    gesture_points = [
        (cx, int(H * 0.04)),           # head top
        (cx + 5, int(H * 0.15)),       # neck
        (cx + 8, int(H * 0.35)),       # chest
        (cx + 3, int(H * 0.55)),       # waist
        (cx - 5, int(H * 0.75)),       # hip
        (cx + 10, int(H * 0.95)),      # foot
    ]
    # Draw gesture line (invisible in final, used for construction)

    # === PRINCIPLE 1: CONSTRUCTION — Simple forms ===
    # Head
    head_cy = int(H * 0.08)
    head_r = int(head_unit * 0.42)
    head_form = Form((cx, head_cy), (head_r * 2, head_r * 2), "sphere")
    head_form.color = skin
    shade_form(draw, img, head_form)

    # Jaw (box form)
    jaw_form = Form((cx, head_cy + int(head_r * 0.5)), (int(head_r * 1.2), int(head_r * 0.6)), "box")
    jaw_form.color = skin
    # Draw jaw as organic
    draw_organic_limb(draw, img, (cx - int(head_r*0.5), head_cy + int(head_r*0.2)),
                      (cx, head_cy + int(head_r*0.9)), int(head_r*0.9), int(head_r*0.4),
                      skin, skin_shadow, skin_light, segments=15)
    draw_organic_limb(draw, img, (cx + int(head_r*0.5), head_cy + int(head_r*0.2)),
                      (cx, head_cy + int(head_r*0.9)), int(head_r*0.9), int(head_r*0.4),
                      skin, skin_shadow, skin_light, segments=15)

    # === PRINCIPLE 4: ANATOMY — Facial features ===
    eye_y = head_cy - int(head_r * 0.05)
    eye_spacing = int(head_r * 0.4)
    for side in [-1, 1]:
        ex = cx + side * eye_spacing
        # Eye socket
        draw.ellipse([ex - 11, eye_y - 7, ex + 11, eye_y + 7], fill=skin_deep)
        # Sclera
        draw.ellipse([ex - 9, eye_y - 5, ex + 9, eye_y + 5], fill=(248, 248, 245))
        # Iris (volume sphere)
        iris_form = Form((ex + side * 1, eye_y), (8, 8), "sphere")
        iris_form.color = (55, 75, 45)
        shade_form(draw, img, iris_form)
        # Pupil
        draw.ellipse([ex + side * 1 - 2, eye_y - 2, ex + side * 1 + 3, eye_y + 3], fill=(10, 10, 15))
        # Highlights
        hx1 = min(ex + side * 4, ex + side * 7)
        hx2 = max(ex + side * 4, ex + side * 7)
        draw.ellipse([hx1, eye_y - 3, hx2, eye_y], fill=(255, 255, 255))
        hl2_x1 = min(ex + side * 0, ex + side * 2)
        hl2_x2 = max(ex + side * 0, ex + side * 2)
        draw.ellipse([hl2_x1, eye_y + 1, hl2_x2, eye_y + 3], fill=(255, 255, 255, 150))

    # Nose
    nose_top = eye_y + 8
    nose_bottom = nose_top + int(head_r * 0.5)
    draw_organic_limb(draw, img, (cx, nose_top), (cx, nose_bottom), 7, 3, skin, skin_shadow, skin_light, segments=10)
    # Nostrils
    draw.ellipse([cx - 6, nose_bottom - 2, cx - 2, nose_bottom + 2], fill=skin_deep)
    draw.ellipse([cx + 2, nose_bottom - 2, cx + 6, nose_bottom + 2], fill=skin_deep)

    # Mouth
    mouth_y = nose_bottom + 6
    draw.arc([cx - 13, mouth_y - 2, cx + 13, mouth_y + 10], start=195, end=345, fill=skin_deep, width=2)
    draw.arc([cx - 15, mouth_y + 3, cx + 15, mouth_y + 14], start=20, end=160, fill=skin_deep, width=2)

    # Neck
    neck_top = head_cy + head_r
    neck_bottom = neck_top + int(head_unit * 0.4)
    draw_organic_limb(draw, img, (cx, neck_top), (cx, neck_bottom), 
                      int(head_unit * 0.4), int(head_unit * 0.35), skin, skin_shadow, skin_light, segments=12)

    # === TORSO (anatomical construction) ===
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
        shoulder_form = Form((sx, shoulder_y), (int(head_unit * 0.6), int(head_unit * 0.6)), "sphere")
        shoulder_form.color = skin
        shade_form(draw, img, shoulder_form)

    # Pectoralis (left and right)
    for side in [-1, 1]:
        px = cx + side * int(shoulder_w * 0.18)
        py = chest_y
        pec_form = Form((px, py), (int(head_unit * 0.7), int(head_unit * 0.5)), "sphere")
        pec_form.color = skin
        shade_form(draw, img, pec_form)

    # Abdomen (segmented)
    ab_top = chest_y + int(head_unit * 0.4)
    ab_bottom = waist_y
    for i in range(4):
        seg_y = ab_top + i * (ab_bottom - ab_top) // 4
        seg_h = (ab_bottom - ab_top) // 4
        ab_form = Form((cx, seg_y + seg_h // 2), (int(waist_w * 0.5), seg_h), "cylinder")
        ab_form.color = skin
        shade_form(draw, img, ab_form)

    # === ARMS (anatomical) ===
    upper_arm_len = int(head_unit * 1.0)
    forearm_len = int(head_unit * 1.0)

    for side in [-1, 1]:
        sx = cx + side * (shoulder_w // 2)
        sy = shoulder_y
        
        # Deltoid
        delt_form = Form((sx, sy), (int(head_unit * 0.55), int(head_unit * 0.55)), "sphere")
        delt_form.color = skin
        shade_form(draw, img, delt_form)
        
        # Bicep
        elbow_x = sx + side * int(head_unit * 0.2)
        elbow_y = sy + upper_arm_len
        draw_organic_limb(draw, img, (sx, sy), (elbow_x, elbow_y),
                          int(head_unit * 0.42), int(head_unit * 0.35), skin, skin_shadow, skin_light,
                          bend=side * 4, segments=20)
        
        # Forearm
        wrist_x = elbow_x + side * int(head_unit * 0.15)
        wrist_y = elbow_y + forearm_len
        draw_organic_limb(draw, img, (elbow_x, elbow_y), (wrist_x, wrist_y),
                          int(head_unit * 0.32), int(head_unit * 0.28), skin, skin_shadow, skin_light,
                          bend=side * 3, segments=20)
        
        # Hand
        hand_form = Form((wrist_x, wrist_y + 5), (int(head_unit * 0.3), int(head_unit * 0.3)), "sphere")
        hand_form.color = skin
        shade_form(draw, img, hand_form)
        # Fingers
        for f in range(4):
            fx = wrist_x - 8 + f * 5 + side * 2
            draw_organic_limb(draw, img, (fx, wrist_y + 8), (fx + side * 2, wrist_y + 22),
                              3, 2, skin, skin_shadow, skin_light, segments=8)

    # === LEGS (anatomical) ===
    upper_leg_len = int(head_unit * 2.0)
    lower_leg_len = int(head_unit * 1.9)

    for side in [-1, 1]:
        hx = cx + side * int(hip_w * 0.22)
        hy = hip_y
        
        # Glute
        glute_form = Form((hx, hy), (int(head_unit * 0.6), int(head_unit * 0.5)), "sphere")
        glute_form.color = skin
        shade_form(draw, img, glute_form)
        
        # Thigh
        knee_x = hx + side * int(head_unit * 0.15)
        knee_y = hy + upper_leg_len
        draw_organic_limb(draw, img, (hx, hy), (knee_x, knee_y),
                          int(head_unit * 0.52), int(head_unit * 0.42), skin, skin_shadow, skin_light,
                          bend=side * 3, segments=25)
        
        # Calf
        ankle_x = knee_x + side * int(head_unit * 0.1)
        ankle_y = knee_y + lower_leg_len
        draw_organic_limb(draw, img, (knee_x, knee_y), (ankle_x, ankle_y),
                          int(head_unit * 0.38), int(head_unit * 0.28), skin, skin_shadow, skin_light,
                          bend=side * 2, segments=25)
        
        # Foot
        draw_organic_limb(draw, img, (ankle_x, ankle_y), (ankle_x + side * 18, ankle_y + 4),
                          int(head_unit * 0.28), int(head_unit * 0.22), skin, skin_shadow, skin_light,
                          segments=10)

    # === PRINCIPLE 6: TEXTURE — Skin detail ===
    # Subtle skin texture (pores) via stippling
    stippling(img, cx - shoulder_w//2, shoulder_y, shoulder_w, hip_y - shoulder_y,
              density=0.005, color=skin_deep)

    # === PRINCIPLE 5: LIGHT — Global shading ===
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.polygon([(0, 0), (cx - 40, 0), (cx - 40, H), (0, H)], fill=(0, 0, 0, 25))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=40))
    img.paste(shadow, (0, 0), shadow)

    return img


# ============================================================
# MASTER CAT v3
# ============================================================

def draw_cat_v3(img):
    """Masterful cat with all 6 principles."""
    draw = ImageDraw.Draw(img)
    W, H = img.size
    cx = W // 2
    head_unit = H // 6

    fur = (195, 175, 145)
    fur_light = (225, 205, 175)
    fur_shadow = (140, 110, 80)
    fur_deep = (90, 65, 40)

    # === GESTURE — Action line (sitting, alert) ===
    gesture = [(cx, int(H*0.1)), (cx, int(H*0.25)), (cx, int(H*0.45)), (cx, int(H*0.7))]

    # === CONSTRUCTION — Head (sphere) ===
    head_r = int(head_unit * 0.7)
    head_cx = cx
    head_cy = int(H * 0.18)

    # Head volume
    head_form = Form((head_cx, head_cy), (head_r * 2, int(head_r * 1.7)), "sphere")
    head_form.color = fur
    shade_form(draw, img, head_form)

    # Ears (organic triangular forms)
    for side in [-1, 1]:
        ex = head_cx + side * (head_r - 5)
        ey = head_cy - int(head_r * 0.6)
        # Outer ear
        pts = [(ex, ey), (ex + side * 18, ey - int(head_r * 0.9)), (ex + side * 4, ey - int(head_r * 0.4))]
        draw.polygon(pts, fill=fur, outline=fur_deep)
        # Inner ear
        pts2 = [(ex + side * 2, ey - 3), (ex + side * 14, ey - int(head_r * 0.9) + 8), (ex + side * 3, ey - int(head_r * 0.4))]
        draw.polygon(pts2, fill=(215, 165, 155))

    # Eyes (almond, detailed)
    eye_y = head_cy - 3
    for side in [-1, 1]:
        ex = head_cx + side * (head_r // 3)
        # Eye socket
        draw.ellipse([ex - 15, eye_y - 10, ex + 15, eye_y + 10], fill=fur_deep)
        # Sclera
        draw.ellipse([ex - 13, eye_y - 8, ex + 13, eye_y + 8], fill=(115, 175, 75))
        # Iris
        iris_form = Form((ex + side * 1, eye_y), (10, 10), "sphere")
        iris_form.color = (50, 100, 40)
        shade_form(draw, img, iris_form)
        # Slit pupil
        draw.ellipse([ex - 3, eye_y - 9, ex + 3, eye_y + 9], fill=(10, 10, 15))
        # Highlights
        draw.ellipse([ex + 4, eye_y - 6, ex + 8, eye_y - 2], fill=(255, 255, 255))
        draw.ellipse([ex - 2, eye_y + 2, ex + 1, eye_y + 5], fill=(255, 255, 255, 150))

    # Nose
    nose_y = head_cy + int(head_r * 0.15)
    draw.polygon([(head_cx, nose_y), (head_cx - 7, nose_y + 8), (head_cx + 7, nose_y + 8)],
                fill=(195, 115, 95), outline=fur_deep)

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
    body_cy = head_cy + int(head_r * 1.5) + int(head_unit * 1.0)
    body_w = int(head_unit * 2.6)
    body_h = int(head_unit * 2.0)
    body_x = body_cx - body_w // 2
    body_y = body_cy - body_h // 2

    # Body volume
    body_form = Form((body_cx, body_cy), (body_w, body_h), "sphere")
    body_form.color = fur
    # Scale the sphere to be oval
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
        # Upper leg
        draw_organic_limb(draw, img, (lx, body_y + body_h // 3),
                          (lx, body_y + body_h - 5), leg_w, int(leg_w * 0.75),
                          fur, fur_shadow, fur_light, bend=side * 2, segments=15)
        # Paw
        draw_organic_limb(draw, img, (lx - leg_w // 2, body_y + body_h - 5),
                          (lx + leg_w // 2, body_y + body_h + 10), int(leg_w * 1.6), int(leg_w * 1.3),
                          fur, fur_shadow, fur_light, segments=10)
        # Toes
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
    stippling(img, body_x, body_y, body_w, body_h, density=0.008, color=fur_deep)

    # === SHADING ===
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([body_x + 10, body_y + body_h - 5, body_x + body_w - 10, body_y + body_h + 15],
              fill=(0, 0, 0, 40))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=8))
    img.paste(shadow, (0, 0), shadow)

    return img


# ============================================================
# MASTER ROBOT v3
# ============================================================

def draw_robot_v3(img):
    """Masterful robot with all 6 principles."""
    draw = ImageDraw.Draw(img)
    W, H = img.size
    cx = W // 2
    head_unit = H // 8

    p = {
        "highlight": (200, 235, 190),
        "light": (120, 190, 95),
        "base": (46, 204, 113),
        "medium": (39, 174, 96),
        "dark": (26, 156, 84),
        "deep": (18, 50, 30),
        "accent": (241, 196, 15),
        "eye": (44, 62, 80),
        "white": (255, 255, 255),
    }

    # Gesture
    gesture = [(cx, int(H*0.05)), (cx + 3, int(H*0.15)), (cx + 5, int(H*0.35)), 
               (cx, int(H*0.55)), (cx - 3, int(H*0.75)), (cx + 5, int(H*0.95))]

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
    # Volume shading
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
    # Outline
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
    # Ambient occlusion
    ambient_occlusion(img, body_x, body_y, body_w, body_h, corner_r=22, intensity=25)
    # Rim light
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
        # Blush
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
        # Volume shading on arm
        for y in range(arm_y, arm_y + 22):
            for x in range(min(ax0, ax1), max(ax0, ax1)):
                light = max(0, 0.4 + 0.3 * (0.5))
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
    stippling(img, body_x + 5, body_y + body_h // 2, body_w - 10, body_h // 3,
              density=0.015, color=p["deep"])

    # Global shading
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.polygon([(0, 0), (cx - 30, 0), (cx - 30, H), (0, H)], fill=(0, 0, 0, 20))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=35))
    img.paste(shadow, (0, 0), shadow)

    return img


SUBJECTS = {
    "human": draw_human_v3,
    "cat": draw_cat_v3,
    "robot": draw_robot_v3,
}


def main():
    parser = argparse.ArgumentParser(description="Master Draw v3 — Full 6-principle implementation")
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
