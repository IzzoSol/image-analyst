---
name: image-analyst
description: Analyze, describe, and recreate images using code (Python PIL/Pillow, SVG, Canvas 2D). Use when you can't view images directly (no vision model), or when you need to extract colors, dimensions, pixel data, ASCII art, or draw illustrations programmatically. Includes tools for image analysis, color extraction, ASCII rendering, and code-based drawing.
license: MIT
metadata:
  author: turtle
  version: "1.0"
compatibility: Requires Python 3.10+ with Pillow (PIL) installed. Optional: numpy for advanced analysis.
---

# Image Analyst — See Images Through Code

When you can't "see" an image (no vision model available), use code to break it down into analyzable data. This skill provides tools and methods for:

1. **Image Analysis** — Extract dimensions, colors, palette, metadata
2. **ASCII Art Rendering** — Convert any image to text-based preview
3. **Color Extraction** — Get dominant colors, histograms, color schemes
4. **Code-Based Drawing** — Create images with Python PIL, SVG, Canvas 2D, CSS
5. **Image Recreation** — Recreate or modify images based on analysis

## Quick Start

### Analyze an image file

```bash
python scripts/analyze_image.py "path/to/image.jpg"
```

### Draw an image with code

```bash
python scripts/draw_with_pil.py --output "my-robot.png"
```

### Convert image to ASCII

```bash
python scripts/image_to_ascii.py "path/to/image.jpg" --width 80
```

## Tools & Methods

### 1. Python PIL (Pillow) — Primary Drawing Tool

**Best for:** Character art, icons, sprites, illustrations with precise pixel control.

```python
from PIL import Image, ImageDraw, ImageFilter

# Create canvas
img = Image.new('RGBA', (512, 512), (255, 255, 255, 255))
draw = ImageDraw.Draw(img)

# Draw shapes
draw.ellipse([100, 100, 200, 200], fill=(46, 204, 113), outline=(26, 156, 84), width=3)
draw.rounded_rectangle([50, 50, 250, 250], radius=20, fill=(39, 174, 96))

# Gradients (manual)
for i in range(100):
    color = (int(46 * (1 - i/100) + 26 * (i/100)), int(204 * (1 - i/100) + 156 * (i/100)), int(113 * (1 - i/100) + 84 * (i/100)))
    draw.line([(100 + i, 100), (100 + i, 200)], fill=color)

# Shadows & glow
shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
sd.ellipse([105, 105, 205, 205], fill=(0, 0, 0, 60))
shadow = shadow.filter(ImageFilter.GaussianBlur(radius=8))
img.paste(shadow, (0, 0), shadow)

# Save
img.save("output.png")
```

**Key capabilities:**
- Shapes: ellipse, rectangle, polygon, line, arc, pieslice, chord
- Rounded rectangles, bezier curves
- Image filters: blur, sharpen, edge enhance, emboss
- Color manipulation: convert, quantize, point operations
- Text rendering with TrueType fonts
- Alpha compositing and layering

### 2. SVG — Vector Graphics

**Best for:** Logos, icons, UI elements, scalable illustrations.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">
  <!-- Gradients -->
  <defs>
    <radialGradient id="body" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#2ecc71"/>
      <stop offset="100%" stop-color="#1a9c54"/>
    </radialGradient>
  </defs>
  
  <!-- Shapes -->
  <circle cx="200" cy="200" r="100" fill="url(#body)" stroke="#1a9c54" stroke-width="3"/>
  <rect x="150" y="150" width="100" height="100" rx="20" fill="#27ae60"/>
  
  <!-- Paths (bezier curves) -->
  <path d="M 100 200 Q 200 100 300 200" stroke="#1a9c54" stroke-width="3" fill="none"/>
  
  <!-- Text -->
  <text x="200" y="350" text-anchor="middle" font-size="24" fill="#27ae60">Robot</text>
</svg>
```

### 3. Canvas 2D — Browser Rendering

**Best for:** Interactive art, animations, real-time visualizations.

```html
<canvas id="canvas" width="512" height="512"></canvas>
<script>
const ctx = document.getElementById('canvas').getContext('2d');

// Gradients
const grad = ctx.createRadialGradient(256, 256, 0, 256, 256, 200);
grad.addColorStop(0, '#2ecc71');
grad.addColorStop(1, '#1a9c54');
ctx.fillStyle = grad;
ctx.fillRect(0, 0, 512, 512);

// Shapes with shadows
ctx.shadowColor = 'rgba(0,0,0,0.3)';
ctx.shadowBlur = 10;
ctx.shadowOffsetX = 5;
ctx.shadowOffsetY = 5;
ctx.fillStyle = '#27ae60';
ctx.beginPath();
ctx.arc(256, 256, 100, 0, Math.PI * 2);
ctx.fill();

// Animation loop
function animate() {
  ctx.clearRect(0, 0, 512, 512);
  // redraw...
  requestAnimationFrame(animate);
}
animate();
</script>
```

### 4. CSS Art — Pure CSS

**Best for:** Simple icons, decorative elements, animated UI components.

```css
.robot {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, #2ecc71, #1a9c54);
  border-radius: 30px;
  position: relative;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.robot::before {
  content: '';
  position: absolute;
  top: 40px;
  left: 40px;
  width: 40px;
  height: 40px;
  background: white;
  border-radius: 50%;
  box-shadow: 80px 0 0 white;
}

.robot::after {
  content: '';
  position: absolute;
  top: 100px;
  left: 50px;
  width: 100px;
  height: 4px;
  background: #1a9c54;
  border-radius: 2px;
}
```

## Image Analysis Techniques

### Extract Dominant Colors

```python
from PIL import Image
from collections import Counter

img = Image.open("photo.jpg")
# Quantize to N colors
quantized = img.quantize(colors=8)
palette = quantized.getpalette()

# Get color counts
colors = quantized.getcolors(maxcolors=1000000)
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
height = int(width * aspect * 0.5)  # Adjust for char aspect ratio
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

### Extract Image Metadata

```python
from PIL import Image

img = Image.open("photo.jpg")
print(f"Size: {img.size}")
print(f"Mode: {img.mode}")
print(f"Format: {img.format}")
print(f"Info: {img.info}")

# EXIF data
exif = img._getexif()
if exif:
    for tag, value in exif.items():
        print(f"{tag}: {value}")
```

### Edge Detection

```python
from PIL import Image, ImageFilter

img = Image.open("photo.jpg").convert('L')
edges = img.filter(ImageFilter.FIND_EDGES)
edges.save("edges.png")

# Or use contour
contour = img.filter(ImageFilter.CONTOUR)
contour.save("contour.png")
```

### Color Histogram

```python
from PIL import Image

img = Image.open("photo.jpg").convert('RGB')
# Get histogram for each channel
r_hist = img.histogram()[0:256]
g_hist = img.histogram()[256:512]
b_hist = img.histogram()[512:768]

# Find peak colors
for channel, hist in [("R", r_hist), ("G", g_hist), ("B", b_hist)]:
    peak = max(range(256), key=lambda i: hist[i])
    print(f"{channel} channel peak: {peak} (count: {hist[peak]})")
```

## Drawing Best Practices

1. **Use RGBA mode** for transparency and layering
2. **Draw shadows first**, then main shapes, then highlights
3. **Use Gaussian blur** for soft shadows and glows
4. **Layer with paste()** for compositing effects
5. **Quantize colors** for consistent palettes
6. **Use anti-aliasing** — PIL's default drawing is already anti-aliased
7. **Save as PNG** for lossless quality with transparency
8. **Use `ImageFilter`** for post-processing (blur, sharpen, edge detect)

## Common Pitfalls

- Forgetting to convert to RGBA before compositing
- Not accounting for character aspect ratio in ASCII art (chars are ~2x taller than wide)
- Using JPEG for images with transparency (use PNG instead)
- Not using `ImageFilter.GaussianBlur` for soft effects
- Drawing in the wrong order (shadows should be behind main shapes)

## Workflow

1. **Analyze** the source image (colors, dimensions, content area)
2. **Plan** the drawing (sketch the structure, identify key shapes)
3. **Draw** base shapes (body, head, etc.)
4. **Add details** (eyes, mouth, accessories)
5. **Apply effects** (shadows, highlights, glows)
6. **Post-process** (blur, sharpen, adjust)
7. **Save** and verify

## Related Skills

- `pixel-art` — Pixel art techniques and sprite creation
- `digital-painting` — Digital painting techniques
- `illustration` — Illustration principles
- `character-art` — Character design
- `color-theory` — Color theory and palette creation
- `svg` — SVG graphics
- `canvas-developer` — Canvas 2D rendering

---
*:23*:
