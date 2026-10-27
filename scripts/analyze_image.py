#!/usr/bin/env python3
"""
Image Analyst — Analyze any image file and extract detailed information.

Usage:
    python analyze_image.py <image_path> [--ascii] [--colors N] [--json]

Examples:
    python analyze_image.py photo.jpg
    python analyze_image.py photo.jpg --ascii --width 80
    python analyze_image.py photo.jpg --colors 16 --json
"""

import sys
import os
import json
import argparse
from PIL import Image, ImageStat, ImageFilter
from collections import Counter


def analyze_image(path, num_colors=8, ascii_width=60, show_ascii=False):
    """Analyze an image and return detailed information."""
    if not os.path.exists(path):
        print(f"Error: File not found: {path}")
        return None

    img = Image.open(path)
    rgb = img.convert('RGB')

    # Basic info
    info = {
        "file": os.path.basename(path),
        "path": os.path.abspath(path),
        "size_bytes": os.path.getsize(path),
        "dimensions": {"width": img.width, "height": img.height},
        "aspect_ratio": round(img.width / img.height, 3),
        "mode": img.mode,
        "format": img.format,
    }

    # Content bounding box (non-white/non-black areas)
    min_x, max_x, min_y, max_y = img.width, 0, img.height, 0
    has_content = False
    for x in range(0, img.width, 2):
        for y in range(0, img.height, 2):
            r, g, b = rgb.getpixel((x, y))
            if not (r > 240 and g > 240 and b > 240) and not (r < 15 and g < 15 and b < 15):
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)
                has_content = True

    if has_content:
        info["content_bbox"] = {
            "x": min_x, "y": min_y,
            "width": max_x - min_x, "height": max_y - min_y
        }

    # Color statistics
    stat = ImageStat.Stat(rgb)
    info["color_stats"] = {
        "mean": [round(x) for x in stat.mean],
        "median": [round(x) for x in stat.median],
        "stddev": [round(x) for x in stat.stddev],
    }

    # Dominant colors via quantization
    quantized = img.convert('RGB').quantize(colors=num_colors)
    palette = quantized.getpalette()
    color_counts = quantized.getcolors(maxcolors=10000000)
    color_counts.sort(reverse=True)

    info["dominant_colors"] = []
    for count, idx in color_counts[:num_colors]:
        r, g, b = palette[idx*3:idx*3+3]
        pct = round(count / (img.width * img.height) * 100, 1)
        info["dominant_colors"].append({
            "rgb": [r, g, b],
            "hex": f"#{r:02x}{g:02x}{b:02x}",
            "pixels": count,
            "percent": pct
        })

    # ASCII art
    if show_ascii:
        ascii_img = img.convert('L').resize((ascii_width, int(ascii_width * img.height / img.width * 0.5)))
        chars = " .:-=+*#%@"
        lines = []
        for y in range(ascii_img.height):
            line = ""
            for x in range(ascii_img.width):
                px = ascii_img.getpixel((x, y))
                idx = px * (len(chars) - 1) // 255
                line += chars[idx]
            lines.append(line)
        info["ascii_art"] = "\n".join(lines)

    return info


def print_report(info, show_ascii=False):
    """Print a human-readable report."""
    print("=" * 60)
    print(f"  IMAGE ANALYSIS: {info['file']}")
    print("=" * 60)
    print(f"  Path:        {info['path']}")
    print(f"  Size:        {info['size_bytes']:,} bytes")
    print(f"  Dimensions:  {info['dimensions']['width']} x {info['dimensions']['height']}")
    print(f"  Aspect:      {info['aspect_ratio']}")
    print(f"  Mode:        {info['mode']}")
    print(f"  Format:      {info['format']}")

    if "content_bbox" in info:
        cb = info["content_bbox"]
        print(f"  Content:     {cb['width']} x {cb['height']} (at {cb['x']},{cb['y']})")

    cs = info["color_stats"]
    print(f"  Mean color:  RGB{tuple(cs['mean'])}")
    print(f"  Median:      RGB{tuple(cs['median'])}")
    print(f"  StdDev:      RGB{tuple(cs['stddev'])}")

    print(f"\n  DOMINANT COLORS:")
    for c in info["dominant_colors"]:
        print(f"    {c['hex']}  RGB{tuple(c['rgb'])}  {c['percent']}%  ({c['pixels']:,} px)")

    if show_ascii and "ascii_art" in info:
        print(f"\n  ASCII ART PREVIEW:")
        print(info["ascii_art"])

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Analyze an image file")
    parser.add_argument("image", help="Path to image file")
    parser.add_argument("--colors", type=int, default=8, help="Number of dominant colors (default: 8)")
    parser.add_argument("--ascii", action="store_true", help="Show ASCII art preview")
    parser.add_argument("--width", type=int, default=60, help="ASCII art width (default: 60)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    info = analyze_image(args.image, num_colors=args.colors, ascii_width=args.width, show_ascii=args.ascii)

    if info is None:
        sys.exit(1)

    if args.json:
        print(json.dumps(info, indent=2))
    else:
        print_report(info, show_ascii=args.ascii)


if __name__ == "__main__":
    main()
