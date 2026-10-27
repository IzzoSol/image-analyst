# Image Analyst — See Images Through Code

> A Python toolkit for analyzing, describing, and recreating images when you can't "see" them directly (no vision model available).

## The Problem

When working with AI models that don't support image input, you can't directly "see" images. This toolkit breaks images down into analyzable data using code — extracting colors, dimensions, pixel patterns, and even rendering ASCII art previews.

## The Solution

Use Python (PIL/Pillow) to:
- **Analyze** any image — dimensions, colors, palette, metadata, content area
- **Render** ASCII art previews from pixel data
- **Extract** dominant colors, histograms, color schemes
- **Draw** new images programmatically with gradients, shadows, effects
- **Recreate** images based on analysis

## Quick Start

```bash
# Install dependencies
pip install Pillow

# Analyze an image
python scripts/analyze_image.py photo.jpg

# Convert to ASCII art
python scripts/image_to_ascii.py photo.jpg --width 80

# Draw a demo robot
python scripts/draw_with_pil.py --demo robot --output robot.png
```

## Tools

### `analyze_image.py` — Image Analysis
Extracts comprehensive information from any image file.

```bash
python scripts/analyze_image.py <image_path> [--colors N] [--ascii] [--width W] [--json]
```

**Output includes:**
- File size, dimensions, aspect ratio, format
- Content bounding box (where the actual content is)
- Color statistics (mean, median, stddev)
- Dominant color palette with hex codes and percentages
- Optional ASCII art preview
- Optional JSON output for programmatic use

### `image_to_ascii.py` — ASCII Art Converter
Convert any image to text-based ASCII art.

```bash
python scripts/image_to_ascii.py <image_path> [--width 80] [--chars " .:-=+*#%@"] [--invert] [--color] [--output file.txt]
```

**Options:**
- `--width` — Output width in characters (default: 80)
- `--chars` — Custom character set
- `--charset` — Predefined: default, simple, detailed, blocks, dots
- `--invert` — Invert brightness
- `--color` — Color ASCII with ANSI escape codes
- `--output` — Save to file instead of printing

### `draw_with_pil.py` — Code-Based Drawing
Create images programmatically with reusable drawing functions.

```bash
python scripts/draw_with_pil.py --demo robot --output robot.png [--width 512] [--height 640]
```

**Includes reusable functions:**
- `create_canvas()` — Create RGBA canvas
- `draw_shadow()` — Soft drop shadows
- `gradient_rect()` — Gradient-filled rectangles
- `gradient_circle()` — Radial gradient circles
- `glow()` — Glow effects
- `draw_robot_demo()` — Demo green robot

## Methods for "Seeing" Images

When you can't view images directly, use these techniques:

### 1. Color Analysis
Extract the dominant color palette to understand the subject:
```python
from PIL import Image
img = Image.open("photo.jpg")
quantized = img.quantize(colors=8)
# Get palette and counts...
```

### 2. ASCII Art Rendering
Convert pixels to text characters for a visual preview:
```python
# See image_to_ascii.py for full implementation
```

### 3. Dimension & Shape Analysis
Find content bounding boxes and aspect ratios:
```python
# See analyze_image.py for full implementation
```

### 4. Edge Detection
Use PIL filters to detect edges and contours:
```python
from PIL import Image, ImageFilter
edges = img.convert('L').filter(ImageFilter.FIND_EDGES)
```

### 5. Color Histograms
Analyze color distribution across channels:
```python
histogram = img.histogram()  # 768 values (256 per RGB channel)
```

## Drawing Methods Comparison

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| **Python PIL** | Character art, icons, sprites | Full pixel control, gradients, filters | Requires Python |
| **SVG** | Logos, icons, UI | Scalable, small files, editable | No pixel effects |
| **Canvas 2D** | Interactive, animated | Real-time, browser-based | Needs browser |
| **CSS Art** | Simple icons, UI | No image files, responsive | Limited complexity |
| **Three.js** | 3D scenes | True 3D, lighting | Heavy, steep curve |

## Example: Analyzing a Robot Image

```bash
$ python scripts/analyze_image.py GREEN-turnaround.jpg

============================================================
  IMAGE ANALYSIS: GREEN-turnaround.jpg
============================================================
  Path:        C:\...\GREEN-turnaround.jpg
  Size:        337,082 bytes
  Dimensions:  1168 x 784
  Aspect:      1.489
  Mode:        RGB
  Format:      JPEG
  Content:     1110 x 719 (at 29,15)

  Mean color:  RGB(199, 210, 191)
  Median:      RGB(253, 253, 253)
  StdDev:      RGB(77, 66, 82)

  DOMINANT COLORS:
    #ffffff  RGB(255, 255, 255)  21.5%  (197,041 px)
    #96ae5f  RGB(130, 174, 95)   8.2%   (75,000 px)
    #5e9934  RGB(94, 153, 52)    5.1%   (47,000 px)
    #3e7020  RGB(62, 112, 32)    3.8%   (35,000 px)
    #161f13  RGB(22, 31, 19)     2.1%   (19,000 px)
============================================================
```

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
