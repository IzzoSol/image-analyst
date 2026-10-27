#!/usr/bin/env python3
"""
Image to ASCII — Convert any image to ASCII art.

Usage:
    python image_to_ascii.py <image_path> [--width 80] [--chars " .:-=+*#%@"] [--invert] [--color]

Examples:
    python image_to_ascii.py photo.jpg
    python image_to_ascii.py photo.jpg --width 120
    python image_to_ascii.py photo.jpg --invert --chars " .oO@"
"""

import sys
import os
import argparse
from PIL import Image


CHAR_SETS = {
    "default": " .:-=+*#%@",
    "simple": " .oO@",
    "detailed": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    "blocks": " ░▒▓█",
    "dots": " ·•●",
}


def image_to_ascii(path, width=80, chars=None, invert=False, color=False):
    """Convert an image to ASCII art."""
    if not os.path.exists(path):
        print(f"Error: File not found: {path}")
        return None

    img = Image.open(path)
    aspect = img.height / img.width
    height = int(width * aspect * 0.5)  # Adjust for char aspect ratio

    if color:
        # Color ASCII (using ANSI escape codes)
        img_rgb = img.convert('RGB').resize((width, height))
        lines = []
        for y in range(height):
            line = ""
            for x in range(width):
                r, g, b = img_rgb.getpixel((x, y))
                # Use block character with color
                brightness = (r + g + b) / 3
                if brightness < 40:
                    char = " "
                elif brightness < 80:
                    char = "░"
                elif brightness < 120:
                    char = "▒"
                elif brightness < 160:
                    char = "▓"
                else:
                    char = "█"
                line += f"\033[38;2;{r};{g};{b}m{char}\033[0m"
            lines.append(line)
        return "\n".join(lines)
    else:
        # Grayscale ASCII
        gray = img.convert('L').resize((width, height))
        if chars is None:
            chars = CHAR_SETS["default"]
        if invert:
            chars = chars[::-1]
        lines = []
        for y in range(height):
            line = ""
            for x in range(width):
                px = gray.getpixel((x, y))
                idx = px * (len(chars) - 1) // 255
                line += chars[idx]
            lines.append(line)
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Convert image to ASCII art")
    parser.add_argument("image", help="Path to image file")
    parser.add_argument("--width", type=int, default=80, help="Output width in chars (default: 80)")
    parser.add_argument("--chars", type=str, default=None, help="Character set to use")
    parser.add_argument("--charset", type=str, choices=list(CHAR_SETS.keys()), default="default",
                        help="Predefined character set")
    parser.add_argument("--invert", action="store_true", help="Invert brightness")
    parser.add_argument("--color", action="store_true", help="Color ASCII (ANSI)")
    parser.add_argument("--output", type=str, default=None, help="Save to file instead of printing")
    args = parser.parse_args()

    chars = args.chars if args.chars else CHAR_SETS[args.charset]
    result = image_to_ascii(args.image, width=args.width, chars=chars, invert=args.invert, color=args.color)

    if result is None:
        sys.exit(1)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"Saved ASCII art to: {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
