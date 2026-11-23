"""Pruebas automáticas del sitio generado (se ejecutan en el pipeline CI).

Verifica sobre /dist:
  * SEO on-page: <title> (10-70 car.), meta description (50-170 car.), un solo <h1>,
    jerarquía de encabezados sin saltos, canonical, Open Graph, lang.
  * Imágenes: atributos alt y title obligatorios, width/height, formato WebP.
  * Enlaces internos sin rotos (href/src) y URLs amigables (minúsculas, sin espacios).
  * JSON-LD válido.
  * sitemap.xml bien formado, cada URL existe; robots.txt apunta al sitemap.

Uso:  python scripts/test_site.py        (código de salida 1 si hay errores)
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
sys.stdout.reconfigure(encoding="utf-8")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.in_title = "", False
        self.meta: dict[str, str] = {}
        self.links: list[str] = []
        self.imgs: list[dict] = []
        self.headings: list[int] = []
        self.canonical = ""
        self.lang = ""
        self.jsonld: list[str] = []
        self._in_jsonld = False
        self._buf = ""

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "html":
            self.lang = d.get("lang", "")
        elif tag == "title":
            self.in_title = True
        elif tag == "meta":
            key = d.get("name") or d.get("property")
            if key:
                self.meta[key] = d.get("content", "")
        elif tag == "link" and d.get("rel") == "canonical":
            self.canonical = d.get("href", "")
        elif tag == "img":
            self.imgs.append(d)
        elif tag in ("a", "link", "script", "img", "iframe", "source"):
            pass
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        for attr in ("href", "src"):
            if attr in d and tag in ("a", "link", "script", "img"):
                self.links.append(d[attr])
        if tag == "script" and d.get("type") == "application/ld+json":
            self._in_jsonld, self._buf = True, ""

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "script" and self._in_jsonld:
            self.jsonld.append(self._buf)
            self._in_jsonld = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self._in_jsonld:
            self._buf += data


def resolve(base_path: str, href: str) -> Path | None:
    """Convierte un enlace interno en ruta de archivo dentro de /dist."""
    if href.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:", "javascript:")) or href.startswith("//"):
        return None
    path = unquote(urlparse(href).path)
    if not path:
        return None
    if base_path and path.startswith(base_path):
        path = path[len(base_path):] or "/"
    target = DIST / path.lstrip("/")
    if path.endswith("/"):
        target = target / "index.html"
    return target


def main() -> int:
    if not DIST.exists():
        print("ERROR: no existe /dist. Ejecuta primero: python scripts/build.py")
        return 1
    errors: list[str] = []
    warnings: list[str] = []
    pages = sorted(DIST.rglob("*.html"))
    base_path = ""
    first = (DIST / "index.html").read_text(encoding="utf-8")
    m = re.search(r'data-base="([^"]*)"', first)
    if m:
        base_path = m.group(1)

    for f in pages:
        rel = "/" + f.relative_to(DIST).as_posix()
        p = Page()
        p.feed(f.read_text(encoding="utf-8"))
        err = lambda msg: errors.append(f"{rel}: {msg}")

        if not p.lang:
            err("falta atributo lang en <html>")
        t = p.title.strip()
        if not 10 <= len(t) <= 70:
            err(f"<title> de {len(t)} caracteres (recomendado 10-70): {t!r}")
        d = p.meta.get("description", "")
        if not 50 <= len(d) <= 170:
            err(f"meta description de {len(d)} caracteres (recomendado 50-170)")
        if p.headings.count(1) != 1:
            err(f"debe tener exactamente un <h1> (tiene {p.headings.count(1)})")
        for prev, cur in zip(p.headings, p.headings[1:]):
            if cur > prev + 1:
                warnings.append(f"{rel}: salto de encabezado h{prev} -> h{cur}")
                break
        if not p.canonical:
            err("falta <link rel=canonical>")
        for k in ("og:title", "og:description", "og:image", "twitter:card"):
            if k not in p.meta:
                err(f"falta meta {k}")
        for im in p.imgs:
            src = im.get("src", "")
            if not im.get("alt"):
                err(f"imagen sin alt: {src}")
            if not im.get("title"):
                err(f"imagen sin title: {src}")
            if not (im.get("width") and im.get("height")):
                err(f"imagen sin width/height: {src}")
            if not src.endswith((".webp", ".svg")):
                err(f"imagen no está en WebP: {src}")
        for href in p.links:
            target = resolve(base_path, href)
            if target is not None and not target.exists():
                err(f"enlace interno roto: {href}")
            path = urlparse(href).path
            if target is not None and (path != path.lower() or " " in path):
                err(f"URL no amigable: {href}")
        for block in p.jsonld:
            try:
                json.loads(block)
            except json.JSONDecodeError as e:
                err(f"JSON-LD inválido: {e}")

    # sitemap.xml
    sm = DIST / "sitemap.xml"
    try:
        tree = ET.parse(sm)
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [e.text for e in tree.getroot().findall("s:url/s:loc", ns)]
        if not locs:
            errors.append("sitemap.xml: sin URLs")
        for loc in locs:
            target = resolve(base_path, urlparse(loc).path)
            if target is None or not target.exists():
                errors.append(f"sitemap.xml: URL sin página: {loc}")
    except (ET.ParseError, FileNotFoundError) as e:
        errors.append(f"sitemap.xml inválido: {e}")
        locs = []

    robots = (DIST / "robots.txt").read_text(encoding="utf-8") if (DIST / "robots.txt").exists() else ""
    if "Sitemap:" not in robots:
        errors.append("robots.txt no declara el Sitemap")

    print(f"Páginas revisadas: {len(pages)} · URLs en sitemap: {len(locs)}")
    for w in warnings:
        print("  AVISO ", w)
    for e in errors:
        print("  ERROR ", e)
    if errors:
        print(f"\nFALLÓ: {len(errors)} error(es)")
        return 1
    print("\nOK: todas las pruebas pasaron")
    return 0


if __name__ == "__main__":
    sys.exit(main())
