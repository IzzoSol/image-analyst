# Universal Drawing System — Draw Anything, Any Style, Any Model

> A code-based drawing system that works regardless of AI model capabilities.
> Implements drawing fundamentals "by the book" and supports multiple art styles.

## The 7 Fundamentals of Drawing (By The Book)

### 1. Perspective
- **1-Point**: Single vanishing point. Objects recede to one point on horizon.
- **2-Point**: Two vanishing points. Most common for buildings/boxes.
- **3-Point**: Three vanishing points. Dramatic angles, looking up/down.
- **Key rule**: Parallel lines converge to vanishing points. The horizon line is at eye level.

### 2. Construction
- Build complex forms from simple primitives (sphere, cube, cylinder, cone)
- Start with largest shapes, add detail progressively
- Use center lines and cross-contours to establish 3D form
- **Rule**: Never draw detail before establishing the overall form

### 3. Gesture
- Capture the "flow" and energy of a pose in 30 seconds
- Use curved lines, not straight ones, for living subjects
- Exaggerate the action line for dynamic poses
- **Rule**: Gesture comes first, structure second

### 4. Anatomy
- **Human proportions**: Head = 1/8 of body height. Eyes at midline of head.
- **Robot proportions**: Head = 1/4 to 1/3 of body. Eyes dominate face.
- **Joints**: Elbows, knees, shoulders have limited range of motion
- **Key**: Study the subject before drawing it

### 5. Color & Light Theory
- **Hue**: Position on color wheel (red, orange, yellow, green, blue, purple)
- **Saturation**: Vividness (0% = gray, 100% = pure color)
- **Value**: Lightness/darkness (0% = black, 100% = white)
- **Lighting**: Key light (main), fill light (softens shadows), rim light (edges)
- **Shadows**: Form shadow (on object), cast shadow (on surface), ambient occlusion (crevices)

### 6. Composition
- **Rule of Thirds**: Place key elements at 1/3 intersections
- **Leading Lines**: Guide the eye through the image
- **Negative Space**: Empty areas that define the subject
- **Visual Weight**: Larger/darker elements feel heavier
- **Focal Point**: Where the eye goes first

### 7. Design
- **Silhouette**: The shape should be recognizable as a black outline
- **Contrast**: Light vs dark, big vs small, simple vs complex
- **Rhythm**: Repeating elements create visual flow
- **Unity**: Everything should feel like it belongs together
- **Variety**: Enough difference to stay interesting

## Art Styles

### 1. Pixel Art
- **Resolution**: 16×16, 32×32, 64×64, or 128×128
- **Palette**: Limited (4-16 colors)
- **Technique**: Nearest-neighbor scaling, no anti-aliasing
- **Shading**: Hard edges, dithering for gradients
- **Outline**: 1-pixel black outline (optional)
- **Tools**: Python PIL with `Image.NEAREST` resize

### 2. 3D Render (Pixar-like)
- **Lighting**: 3-point (key, fill, rim) + ambient
- **Shading**: Smooth gradients, specular highlights
- **Materials**: Plastic (smooth), metal (reflective), fabric (matte)
- **Colors**: Saturated, vibrant
- **Effects**: Depth of field, ambient occlusion, subsurface scattering
- **Tools**: Python PIL with gradient circles and Gaussian blur

### 3. Sketch/Pencil
- **Lines**: Varied weight, hatching, cross-hatching
- **Shading**: Graphite gradients, smudging
- **Colors**: Monochrome or limited color
- **Texture**: Paper grain, pencil marks
- **Tools**: SVG paths with varying stroke-width

### 4. Watercolor
- **Edges**: Soft, bleeding boundaries
- **Colors**: Transparent layers, wet-on-wet blending
- **Texture**: Paper texture, granulation
- **Technique**: Light washes first, dark details last
- **Tools**: Python PIL with alpha compositing and blur

### 5. Flat Vector/Illustration
- **Shapes**: Clean geometric forms
- **Colors**: Bold, flat (no gradients)
- **Outlines**: Thick, consistent stroke
- **Shadows**: Hard-edged, offset shapes
- **Tools**: SVG with solid fills

### 6. Chibi/Cute
- **Proportions**: Head = 1/2 to 1/3 of body
- **Eyes**: Large, expressive, sparkly
- **Colors**: Pastel, soft
- **Details**: Simplified, rounded
- **Expression**: Exaggerated emotions
- **Tools**: Python PIL with large circles and soft colors

### 7. Comic/Anime
- **Lines**: Bold, dynamic, speed lines
- **Shading**: Cel-shaded (hard edges), screen tones
- **Colors**: Vibrant, high contrast
- **Eyes**: Large, detailed
- **Effects**: Action lines, impact frames
- **Tools**: SVG with bold strokes

### 8. Realistic/Detailed
- **Precision**: Accurate proportions and anatomy
- **Shading**: Smooth gradients, subsurface scattering
- **Texture**: Skin pores, fabric weave, metal scratches
- **Lighting**: Photographic quality
- **Colors**: Natural, muted
- **Tools**: Python PIL with high-resolution gradients

## Universal Drawing Engine

The drawing engine uses a **style parameter** to switch between rendering techniques:

```python
from universal_draw import draw_subject

# Draw a robot in any style
img = draw_subject("robot", style="pixel_art", width=64, height=64)
img = draw_subject("robot", style="3d_render", width=512, height=512)
img = draw_subject("robot", style="sketch", width=800, height=600)
img = draw_subject("robot", style="watercolor", width=512, height=512)
img = draw_subject("robot", style="flat_vector", width=512, height=512)
img = draw_subject("robot", style="chibi", width=256, height=256)
img = draw_subject("robot", style="comic", width=512, height=512)
img = draw_subject("robot", style="realistic", width=1024, height=1024)
```

## Model-Agnostic Approach

This system works **no matter what AI model** you're using because:

1. **Pure Python** — No API calls, no external services
2. **Deterministic** — Same input always produces same output
3. **Self-contained** — Only requires Pillow (PIL)
4. **Readable** — Code is the documentation
5. **Extensible** — Add new styles by adding new renderers
6. **Portable** — Runs on any platform with Python

The AI model's job is to:
1. Understand what to draw (subject, pose, details)
2. Choose the style
3. Generate the Python code
4. Execute it

The drawing engine's job is to:
1. Render the subject in the chosen style
2. Apply fundamentals (proportion, lighting, composition)
3. Output a clean image file

## Color Palettes by Style

### Pixel Art Palettes
- **Game Boy**: 4 greens (#0f380f, #306230, #8bac0f, #9bbc0f)
- **NES**: 54 colors (limited but vibrant)
- **PICO-8**: 16 colors (specific palette)
- **Commodore 64**: 16 colors

### 3D Render Palettes
- Use full RGB range
- Saturated colors with proper shading
- 3-5 color variations per material (highlight, base, shadow, deep shadow)

### Watercolor Palettes
- Muted, desaturated colors
- Transparent layers create new colors
- Warm/cool temperature shifts

### Flat Vector Palettes
- Bold, flat colors
- High contrast
- Limited palette (3-5 colors)

## Lighting Setups

### 3-Point Lighting (Standard)
```
Key Light: 45° above, 45° to the side (main illumination)
Fill Light: Opposite side, lower intensity (softens shadows)
Rim Light: Behind subject (creates edge separation)
```

### Dramatic Lighting
```
Key Light: Low angle, strong (creates long shadows)
Fill Light: Minimal (high contrast)
Rim Light: Strong (silhouette edges)
```

### Soft Lighting
```
Key Light: Diffused, large source (soft shadows)
Fill Light: Strong (minimal shadows)
Rim Light: Subtle (gentle edge)
```

## Proportion Guides

### Human (8 heads tall)
```
Head: 1 unit
Neck to shoulders: 0.5 units
Torso: 2.5 units
Legs: 4 units
Total: 8 units
```

### Robot (4-5 heads tall)
```
Head: 1 unit (large, expressive)
Neck: 0.25 units
Torso: 1.5 units
Arms: 1.5 units (shoulder to fingertips)
Legs: 1.5 units (hip to foot)
Total: 4.5-5 units
```

### Chibi (3 heads tall)
```
Head: 1.5 units (oversized)
Body: 1 unit (small)
Legs: 0.5 units (stubby)
Total: 3 units
```

## Quick Reference: Drawing Checklist

Before finishing any drawing, verify:
- [ ] Silhouette is recognizable
- [ ] Proportions are correct for the style
- [ ] Lighting is consistent (single light source)
- [ ] Shadows fall in the right direction
- [ ] Colors harmonize (use color wheel)
- [ ] Composition has a clear focal point
- [ ] Details are appropriate for the resolution
- [ ] Edges are consistent (hard or soft, not mixed randomly)
- [ ] The image reads well at thumbnail size
- [ ] No unnecessary elements (every stroke has a purpose)

---
*:23*:
