#!/usr/bin/env python3
"""Generate the profile logo (brand/logo.svg and brand/logo-512.png).

The mark is the original Vector logo (an inverted triangle with an open
triangle spiralling inside it), redrawn on a pixel grid in the README's
palette: pink -> violet -> cyan gradient, purple drop shadow, dark
dot-grid background. The previous avatar is kept outside the repo as avatar-original.jpg.

Run:  python3 scripts/build_logo.py     (needs Pillow for the PNG)
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "brand"

GRID = 40          # pixel-art resolution of the mark
CELL = 10          # px per grid cell in the 512px logo
SIZE = 512
BG, SHADOW, DOT = "#0f0b1a", "#2e2150", "#251d3b"
GRAD = [(0xFF, 0x4F, 0xD8), (0xB4, 0x6C, 0xFF), (0x3E, 0xF0, 0xFF)]

# Mark geometry, traced from the original logo (units: 540x460 trace space).
TRACE_W, TRACE_H = 540, 460
OUTER = [(45, 45), (485, 45), (265, 425), (45, 45)]
INNER = [(300, 335), (185, 128), (345, 128), (295, 210)]   # open spiral
STROKE = 2  # grid cells


def mark_cells() -> list[tuple[int, int]]:
    """Rasterise the mark onto the pixel grid with no anti-aliasing."""
    scale = (GRID - 4) / TRACE_W
    off_x = 2
    off_y = (GRID - TRACE_H * scale) / 2
    pts = lambda path: [(off_x + x * scale, off_y + y * scale) for x, y in path]
    img = Image.new("1", (GRID, GRID), 0)
    d = ImageDraw.Draw(img)
    for path in (OUTER, INNER):
        p = pts(path)
        d.line(p, fill=1, width=STROKE, joint="curve")
    return [(x, y) for y in range(GRID) for x in range(GRID) if img.getpixel((x, y))]


def placement(cells: list[tuple[int, int]]) -> tuple[int, int, int, int, int, int]:
    """Centre the mark's bounding box, nudged down to the triangle's optical centre."""
    xs, ys = [x for x, _ in cells], [y for _, y in cells]
    w, h = (max(xs) - min(xs) + 1) * CELL, (max(ys) - min(ys) + 1) * CELL
    x0 = (SIZE - w) // 2 - min(xs) * CELL
    y0 = (SIZE - h) // 2 - min(ys) * CELL + h // 12
    return x0, y0, min(xs) * CELL, min(ys) * CELL, w, h


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def grad_at(t: float) -> tuple[int, int, int]:
    return lerp(GRAD[0], GRAD[1], t / 0.55) if t < 0.55 else lerp(GRAD[1], GRAD[2], (t - 0.55) / 0.45)


def runs(cells: list[tuple[int, int]], x0: int, y0: int) -> str:
    """Path data with horizontal runs of cells merged into one rectangle each."""
    rows: dict[int, list[int]] = {}
    for x, y in cells:
        rows.setdefault(y, []).append(x)
    out = []
    for y, xs in sorted(rows.items()):
        xs.sort()
        start = prev = xs[0]
        for x in xs[1:] + [None]:
            if x is not None and x == prev + 1:
                prev = x
                continue
            w = (prev - start + 1) * CELL
            out.append(f"M{x0 + start * CELL} {y0 + y * CELL}h{w}v{CELL}h-{w}z")
            if x is not None:
                start = prev = x
    return "".join(out)


def build_svg(cells: list[tuple[int, int]]) -> str:
    x0, y0, bx, by, w, h = placement(cells)
    g = ["#%02x%02x%02x" % c for c in GRAD]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" width="{SIZE}" height="{SIZE}" '
        f'role="img" aria-label="Vector logo" shape-rendering="crispEdges">'
        f'<title>Vector logo</title>'
        f'<defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="{x0 + bx}" y1="0" x2="{x0 + bx + w}" y2="0">'
        f'<stop offset="0" stop-color="{g[0]}"/><stop offset=".55" stop-color="{g[1]}"/><stop offset="1" stop-color="{g[2]}"/>'
        f'</linearGradient><pattern id="d" x="16" y="16" width="24" height="24" patternUnits="userSpaceOnUse">'
        f'<rect width="2" height="2" fill="{DOT}"/></pattern></defs>'
        f'<rect width="{SIZE}" height="{SIZE}" fill="{BG}"/><rect width="{SIZE}" height="{SIZE}" fill="url(#d)"/>'
        f'<path fill="{SHADOW}" d="{runs(cells, x0 + 7, y0 + 7)}"/><path fill="url(#g)" d="{runs(cells, x0, y0)}"/></svg>\n'
    )


def build_png(cells: list[tuple[int, int]]) -> Image.Image:
    img = Image.new("RGB", (SIZE, SIZE), BG)
    d = ImageDraw.Draw(img)
    for y in range(16, SIZE, 24):
        for x in range(16, SIZE, 24):
            d.rectangle([x, y, x + 1, y + 1], fill=DOT)
    x0, y0, bx, by, w, h = placement(cells)
    for x, y in cells:
        px, py = x0 + x * CELL, y0 + y * CELL
        d.rectangle([px + 7, py + 7, px + 7 + CELL - 1, py + 7 + CELL - 1], fill=SHADOW)
    # Horizontal gradient across the mark's bounding box, same direction as the SVG.
    for x, y in cells:
        px, py = x0 + x * CELL, y0 + y * CELL
        u = (px + CELL / 2 - x0 - bx) / w
        t = u  # left-to-right, same as the README wordmark
        d.rectangle([px, py, px + CELL - 1, py + CELL - 1], fill=grad_at(max(0.0, min(1.0, t))))
    return img


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cells = mark_cells()
    (OUT / "logo.svg").write_text(build_svg(cells), encoding="utf-8")
    build_png(cells).save(OUT / "logo-512.png", optimize=True)
    print(f"wrote logo.svg and logo-512.png ({len(cells)} mark pixels)")


if __name__ == "__main__":
    main()
