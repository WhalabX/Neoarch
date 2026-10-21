#!/usr/bin/env python3
"""Generate the placeholder portrait used for sponsors without a photo.

The About -> Community tab renders a sponsor portrait from
``assets/icons/app/sponsor-<slug>.png``. When a sponsor has no portrait on
file we fall back to a generated monogram so the card never shows an empty
badge.

Usage:

    python scripts/generate_sponsor_avatar.py Ferreol
    python scripts/generate_sponsor_avatar.py "Ferreol" "ArchCanary"

Each name produces ``assets/icons/app/sponsor-<slug>.png`` — a 192x192
circular monogram in the app accent colours, well under 50 KB.

Needs Pillow (``pip install Pillow``) — a build-time helper only, the app
itself never imports it.
"""

import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

SIZE = 192
SUPERSAMPLE = 4
ACCENT_TOP = (0, 212, 193)      # Colors.ACCENT_HOVER
ACCENT_BOTTOM = (0, 150, 136)   # between ACCENT_PRESSED and ACCENT
FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
)


def slugify(name):
    """``Ferreol`` -> ``ferreol`` (matches the sponsor ``handle``)."""
    return re.sub(r"[^a-z0-9]+", "", name.strip().lower())


def load_font(size):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def make_avatar(name, out_path):
    """Draw a circular monogram badge and write it as a PNG."""
    big = SIZE * SUPERSAMPLE
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))

    # Vertical gradient inside the circle.
    grad = Image.new("RGBA", (big, big))
    grad_px = grad.load()
    for y in range(big):
        t = y / max(big - 1, 1)
        colour = tuple(
            int(round(ACCENT_TOP[i] + (ACCENT_BOTTOM[i] - ACCENT_TOP[i]) * t))
            for i in range(3)
        ) + (255,)
        for x in range(big):
            grad_px[x, y] = colour

    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, big - 1, big - 1), fill=255)
    img.paste(grad, (0, 0), mask)

    draw = ImageDraw.Draw(img)
    # Soft inner ring for a bit of depth.
    draw.ellipse((2, 2, big - 3, big - 3), outline=(255, 255, 255, 40),
                 width=SUPERSAMPLE * 2)

    initial = (name.strip() or "?")[0].upper()
    font = load_font(int(big * 0.46))
    box = draw.textbbox((0, 0), initial, font=font)
    text_w = box[2] - box[0]
    text_h = box[3] - box[1]
    draw.text(
        ((big - text_w) / 2 - box[0], (big - text_h) / 2 - box[1]),
        initial, font=font, fill=(255, 255, 255, 255),
    )

    img = img.resize((SIZE, SIZE), Image.LANCZOS)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG", optimize=True)
    return out_path


def main(argv):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(root, "assets", "icons", "app")
    names = argv or ["Ferreol"]
    for name in names:
        path = os.path.join(out_dir, f"sponsor-{slugify(name)}.png")
        make_avatar(name, path)
        size_kb = os.path.getsize(path) / 1024
        print(f"wrote {path} ({size_kb:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
