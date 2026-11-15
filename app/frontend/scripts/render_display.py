"""Renders the display words (Brunson) to PNG so every device shows the brand type without loading the font.

Run from app/frontend:  python3 scripts/render_display.py   (needs Pillow with raqm; fonts in design/fonts/)
Writes src/assets/display/<name>.png and prints the height (in em) the images must have in CSS (--display-h).

All images share one vertical window [baseline - TOP*cap, baseline + BOTTOM*cap], so words placed side by side keep
the same baseline, and an <img> with height = H em looks like the old text at that font-size.
Decision (jaime, 2026-11-15): Brunson is used as images for a closed exhibition; the .ttf is not shipped.
"""
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = {"clean": ROOT / "design/fonts/Brunson.ttf", "rough": ROOT / "design/fonts/Brunson-Rough.ttf"}
OUT = ROOT / "src/assets/display"
SIZE = 320          # px of font-size used to render (sharp up to ~150 px CSS at 3x screens for the logo)
TOP, BOTTOM = 1.12, 0.10   # vertical window around the caps, in cap heights (rough edges stick out a little)

COLORS = {"green-light": "#6BB383", "green": "#297847", "cream": "#F0EDE4", "dark": "#1E3626"}
WORDS = [  # (file name, text, font, colour)
    ("regiones", "REGIONES", "clean", "green-light"),
    ("filtros", "FILTROS", "clean", "green-light"),
    ("tus-parcelas", "TUS PARCELAS", "clean", "green-light"),
    ("informe", "INFORME DE TUS PARCELAS", "clean", "green-light"),
    ("logo-agro", "AGRO", "rough", "green"),
    ("logo-ckham-cream", "CKHAM", "clean", "cream"),
    ("logo-ckham-dark", "CKHAM", "clean", "dark"),
]


def cap_height(path: Path) -> float:
    f = TTFont(path)
    cap = getattr(f["OS/2"], "sCapHeight", 0) or 0
    if not cap:  # old fonts: measure the H
        glyf, cmap = f["glyf"], f.getBestCmap()
        g = glyf[cmap[ord("H")]]
        cap = g.yMax
    return cap / f["head"].unitsPerEm


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cap = max(cap_height(p) for p in FONTS.values()) * SIZE
    top, bottom = round(TOP * cap), round(BOTTOM * cap)
    for name, text, font, colour in WORDS:
        f = ImageFont.truetype(str(FONTS[font]), SIZE, layout_engine=ImageFont.Layout.RAQM)
        x0, y0, x1, y1 = f.getbbox(text, anchor="ls")
        if y0 < -top or y1 > bottom:
            raise SystemExit(f"{name}: ink {y0}..{y1} outside window -{top}..{bottom}; raise TOP/BOTTOM")
        pad = round(0.02 * SIZE)
        w, h = (x1 - min(x0, 0)) + 2 * pad, top + bottom
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(img).text((pad - min(x0, 0), top), text, font=f, fill=COLORS[colour], anchor="ls")
        img.save(OUT / f"{name}.png", optimize=True)
        print(f"{name}.png {w}x{h}")
    print(f"--display-h: {(top + bottom) / SIZE:.4f}em   (baseline at {top / (top + bottom):.4f} of the height)")


if __name__ == "__main__":
    main()
