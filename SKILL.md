---
name: image-analyst
description: Analyze, describe, and recreate images using code (Python PIL/Pillow). Draw anatomy-accurate humans, animals, robots in 8 styles. Use when you can't view images directly, or need to extract colors, dimensions, pixel data, ASCII art, or draw illustrations programmatically. Model-agnostic — works with any AI model.
license: MIT
metadata:
  author: turtle
  version: "2.0"
compatibility: Requires Python 3.10+ with Pillow (PIL) installed. Optional: numpy for advanced analysis.
---

# Image Analyst — See Images Through Code

When you can't "see" an image (no vision model available), use code to break it down into analyzable data. This skill provides tools and methods for:

1. **Image Analysis** — Extract dimensions, colors, palette, metadata
2. **ASCII Art Rendering** — Convert any image to text-based preview
3. **Color Extraction** — Get dominant colors, histograms, color schemes
4. **Code-Based Drawing** — Create images with Python PIL, SVG, Canvas 2D, CSS
5. **Multi-Style Rendering** — Draw in 6 different art styles
6. **Image Recreation** — Recreate or modify images based on analysis

## Quick Start

### Analyze an image file

```bash
python scripts/analyze_image.py "path/to/image.jpg"
python scripts/analyze_image.py "path/to/image.jpg" --ascii --width 80 --colors 16
```

### Draw an image in any style

```bash
python scripts/universal_draw.py --subject robot --style 3d_render --output robot.png
python scripts/universal_draw.py --subject robot --style pixel_art --output robot_px.png --width 64 --height 64
python scripts/universal_draw.py --subject robot --style sketch --output robot_sketch.png
python scripts/universal_draw.py --subject robot --style watercolor --output robot_wc.png
python scripts/universal_draw.py --subject robot --style flat_vector --output robot_fv.png
python scripts/universal_draw.py --subject robot --style chibi --output robot_chibi.png
python scripts/universal_draw.py --list-styles
```

### Convert image to ASCII

```bash
python scripts/image_to_ascii.py "path/to/image.jpg" --width 80
python scripts/image_to_ascii.py "path/to/image.jpg" --color --width 60
```

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
- **Chibi proportions**: Head = 1/2 to 1/3 of body. Oversized eyes.
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

## Art Styles (6 Supported)

### 1. 3D Render (Pixar-like)
- **Lighting**: 3-point (key, fill, rim) + ambient
- **Shading**: Smooth gradients, specular highlights
- **Materials**: Plastic (smooth), metal (reflective)
- **Colors**: Saturated, vibrant
- **Effects**: Depth of field, ambient occlusion
- **Code**: Python PIL with gradient circles and Gaussian blur

### 2. Pixel Art
- **Resolution**: 16×16, 32×32, 64×64, or 128×128
- **Palette**: Limited (4-16 colors)
- **Technique**: Nearest-neighbor scaling, no anti-aliasing
- **Shading**: Hard edges, dithering for gradients
- **Outline**: 1-pixel dark outline
- **Code**: Python PIL with cell-based grid rendering

### 3. Sketch/Pencil
- **Lines**: Varied weight, hatching, cross-hatching
- **Shading**: Graphite gradients, smudging
- **Colors**: Monochrome or limited color
- **Texture**: Paper grain, pencil marks
- **Code**: SVG paths with varying stroke-width

### 4. Watercolor
- **Edges**: Soft, bleeding boundaries
- **Colors**: Transparent layers, wet-on-wet blending
- **Texture**: Paper texture, granulation
- **Technique**: Light washes first, dark details last
- **Code**: Python PIL with alpha compositing and blur

### 5. Flat Vector/Illustration
- **Shapes**: Clean geometric forms
- **Colors**: Bold, flat (no gradients)
- **Outlines**: Thick, consistent stroke
- **Shadows**: Hard-edged, offset shapes
- **Code**: SVG with solid fills

### 6. Chibi/Cute
- **Proportions**: Head = 1/2 to 1/3 of body
- **Eyes**: Large, expressive, sparkly
- **Colors**: Pastel, soft
- **Details**: Simplified, rounded
- **Expression**: Exaggerated emotions
- **Code**: Python PIL with large circles and soft colors

## Drawing Methods Comparison

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| **Python PIL** | Character art, icons, sprites | Full pixel control, gradients, filters | Requires Python |
| **SVG** | Logos, icons, UI | Scalable, small files, editable | No pixel effects |
| **Canvas 2D** | Interactive, animated | Real-time, browser-based | Needs browser |
| **CSS Art** | Simple icons, UI | No image files, responsive | Limited complexity |
| **Three.js** | 3D scenes | True 3D, lighting | Heavy, steep curve |

## Image Analysis Techniques

### Extract Dominant Colors

```python
from PIL import Image
img = Image.open("photo.jpg")
quantized = img.quantize(colors=8)
palette = quantized.getpalette()
colors = quantized.getcolors(maxcolors=10000000)
colors.sort(reverse=True)
for count, idx in colors[:8]:
    r, g, b = palette[idx*3:idx*3+3]
    print(f"RGB({r},{g},{b}): {count} pixels")
```

### Generate ASCII Art

```python
from PIL import Image
img = Image.open("photo.jpg").convert('L')
width = 80
aspect = img.height / img.width
height = int(width * aspect * 0.5)
img = img.resize((width, height))
chars = " .:-=+*#%@"
for y in range(height):
    line = ""
    for x in range(width):
        px = img.getpixel((x, y))
        idx = px * (len(chars) - 1) // 255
        line += chars[idx]
    print(line)
```

### Edge Detection

```python
from PIL import Image, ImageFilter
img = Image.open("photo.jpg").convert('L')
edges = img.filter(ImageFilter.FIND_EDGES)
edges.save("edges.png")
```

## Model-Agnostic Approach

This system works **no matter what AI model** you're using because:

1. **Pure Python** — No API calls, no external services, no model dependencies
2. **Deterministic** — Same input always produces same output
3. **Self-contained** — Only requires Pillow (PIL)
4. **Readable** — Code is the documentation
5. **Extensible** — Add new styles by adding new renderers
6. **Portable** — Runs on any platform with Python

The AI model's job is to:
1. Understand what to draw (subject, pose, details)
2. Choose the style
3. Generate or call the Python code
4. Execute it

The drawing engine's job is to:
1. Render the subject in the chosen style
2. Apply fundamentals (proportion, lighting, composition)
3. Output a clean image file

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

## Tools

### `analyze_image.py` — Image Analysis
```bash
python scripts/analyze_image.py <image_path> [--colors N] [--ascii] [--width W] [--json]
```

### `image_to_ascii.py` — ASCII Art Converter
```bash
python scripts/image_to_ascii.py <image_path> [--width 80] [--chars "..."] [--invert] [--color] [--output file.txt]
```

### `universal_draw.py` — Multi-Style Drawing Engine
```bash
python scripts/universal_draw.py --subject robot --style 3d_render --output robot.png [--width 512] [--height 512]
python scripts/universal_draw.py --list-styles
```

### `anatomy_draw.py` — Anatomy Drawing Engine
```bash
python scripts/anatomy_draw.py --subject human --output human.png [--width 400] [--height 600]
python scripts/anatomy_draw.py --subject cat --output cat.png [--width 512] [--height 512]
python scripts/anatomy_draw.py --list-subjects
```

**Subjects:**
- `human` — Standing human with 8-head proportions, pectorals, abs, limbs, joints
- `cat` — Sitting cat with proper feline anatomy, ears, eyes, whiskers, tail

**Anatomy Systems:**
- **Human**: 8-head proportion system, shoulder/hip width ratios, limb segmentation
- **Cat**: Feline proportions, triangular ears, almond eyes, digitigrade legs

---

## Requirements

- Python 3.10+
- Pillow (PIL) 9.0+
- Optional: numpy for advanced analysis

## License

MIT — Use freely, modify, distribute.

## Author

Created by TURTLE (SHADDAI council) — UI/UX & Creative agent.

---
*:23*:
