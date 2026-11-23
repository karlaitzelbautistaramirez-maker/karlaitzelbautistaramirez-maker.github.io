"""Optimización de imágenes (Módulo 1.3 - SEO de imágenes).

Convierte las imágenes fuente de /assets-src (PNG/JPG) a WebP optimizado en
/src/static/img, genera variantes responsivas (-640w) para imágenes anchas,
la imagen Open Graph (JPG 1200x630) y los favicons.

Uso:  python scripts/optimize_images.py
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets-src"
OUT = ROOT / "src" / "static" / "img"
QUALITY = 80


def kb(n: int) -> str:
    return f"{n / 1024:.1f} KB"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    total_in = total_out = 0
    for src in sorted(SRC.glob("*")):
        if src.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            continue
        img = Image.open(src)
        img = img.convert("RGBA") if img.mode in ("RGBA", "LA", "P") else img.convert("RGB")
        dest = OUT / f"{src.stem}.webp"
        img.save(dest, "WEBP", quality=QUALITY, method=6)
        size_in, size_out = src.stat().st_size, dest.stat().st_size
        total_in += size_in
        total_out += size_out
        print(f"{src.name:50s} {kb(size_in):>10s} -> {kb(size_out):>9s}  ({img.width}x{img.height})")
        if img.width > 800:  # variante responsiva para móviles
            small = img.resize((640, round(img.height * 640 / img.width)), Image.LANCZOS)
            small.save(OUT / f"{src.stem}-640w.webp", "WEBP", quality=QUALITY, method=6)

    # Imagen para redes sociales (Open Graph / Twitter Card)
    hero = Image.open(SRC / "hero-enchiladas-de-huejutla.png").convert("RGB")
    ratio = 1200 / 630
    w, h = hero.size
    if w / h > ratio:
        nw = round(h * ratio)
        hero = hero.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    hero.resize((1200, 630), Image.LANCZOS).save(OUT / "og-eke-enchiladas-de-huejutla.jpg", "JPEG", quality=82, optimize=True)

    # Favicons a partir del tazón del logotipo
    logo = Image.open(SRC / "logo-eke-comida-tradicional-huasteca.png").convert("RGBA")
    bg = Image.new("RGBA", logo.size, (249, 237, 221, 255))
    logo = Image.alpha_composite(bg, logo).convert("RGB")
    bowl = logo.crop((0, 0, logo.height + 6, logo.height))
    for size, name in [(32, "favicon-32.png"), (180, "apple-touch-icon.png"), (512, "icon-512.png")]:
        bowl.resize((size, size), Image.LANCZOS).save(OUT / name, optimize=True)

    saved = 100 - (total_out * 100 / total_in) if total_in else 0
    print(f"\nTotal: {kb(total_in)} -> {kb(total_out)}  (ahorro {saved:.0f}%)")


if __name__ == "__main__":
    main()
