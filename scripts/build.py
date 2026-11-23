"""Generador estático de la tienda Eke (sin dependencias externas).

Lee la configuración (data/site.json), el catálogo (data/products.json),
las páginas (src/pages/*.html) y las entradas del blog (src/blog/*.html) y
produce el sitio listo para publicar en /dist, incluyendo:

  * Páginas con SEO on-page (title, meta description, canonical, Open Graph,
    Twitter Card, JSON-LD Schema.org, breadcrumbs).
  * Páginas de producto y categoría con URLs amigables (/producto/<slug>/).
  * sitemap.xml dinámico (con extensión de imágenes) y robots.txt.
  * Catálogo para el carrito (assets/js/catalog.js) y manifest PWA.

Variables de entorno opcionales (las usa el pipeline de CI/CD):
  SITE_URL   URL pública, p. ej. https://usuario.github.io
  BASE_PATH  Subcarpeta de publicación, p. ej. /eke (vacío si es raíz)

Uso:  python scripts/build.py
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
SRC = ROOT / "src"

SITE = json.loads((ROOT / "data" / "site.json").read_text(encoding="utf-8"))
CATALOG = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))
PRODUCTS = CATALOG["products"]
CATEGORIES = {c["slug"]: c for c in CATALOG["categories"]}

SITE_URL = os.environ.get("SITE_URL", SITE["site_url"]).rstrip("/")
BASE = os.environ.get("BASE_PATH", "").rstrip("/")
if BASE and not BASE.startswith("/"):
    BASE = "/" + BASE
BUILD_DATE = date.today().isoformat()
BUILD_ID = os.environ.get("GITHUB_SHA", datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"))[:12]

SITEMAP: list[dict] = []
sys.stdout.reconfigure(encoding="utf-8")


# --------------------------------------------------------------------------- utilidades
def u(path: str) -> str:
    """URL relativa al sitio, respetando BASE_PATH."""
    return f"{BASE}{path}"


def absu(path: str) -> str:
    return f"{SITE_URL}{BASE}{path}"


def a(value) -> str:
    return escape(str(value), quote=True)


def money(n: float) -> str:
    return f"${n:,.2f} MXN"


def img(name: str, alt: str, width: int, height: int, cls: str = "", lazy: bool = True,
        title: str | None = None, srcset: str = "", sizes: str = "") -> str:
    """<img> optimizado: WebP, alt + title obligatorios, dimensiones explícitas (evita CLS)."""
    ext = "" if "." in name else ".webp"
    attrs = [
        f'src="{u("/assets/img/" + name + ext)}"',
        f'alt="{a(alt)}"',
        f'title="{a(title or alt)}"',
        f'width="{width}"', f'height="{height}"',
        'decoding="async"',
        'loading="lazy"' if lazy else 'fetchpriority="high"',
    ]
    if srcset:
        attrs.append(f'srcset="{srcset}"')
    if sizes:
        attrs.append(f'sizes="{sizes}"')
    if cls:
        attrs.append(f'class="{cls}"')
    return f"<img {' '.join(attrs)}>"


def icon(name: str, cls: str = "icon") -> str:
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="#i-{name}"></use></svg>'


def jsonld(data) -> str:
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"


def parse_front_matter(text: str) -> tuple[dict, str]:
    meta: dict = {}
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        for line in fm.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        return meta, body.strip()
    return meta, text


def write(path: str, html: str) -> None:
    out = DIST / path.lstrip("/")
    if path.endswith("/"):
        out = out / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


# --------------------------------------------------------------------------- iconos SVG
ICONS = {
    "truck": '<path d="M3 6h11v9H3zM14 9h4l3 3v3h-7z"/><circle cx="7" cy="17" r="1.8"/><circle cx="17" cy="17" r="1.8"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/>',
    "heart": '<path d="M12 20s-7-4.4-9-9.2C1.8 7.6 4 4.5 7.2 4.5c2 0 3.6 1.1 4.8 2.8 1.2-1.7 2.8-2.8 4.8-2.8 3.2 0 5.4 3.1 4.2 6.3C19 15.6 12 20 12 20z"/>',
    "cart": '<path d="M2 3h3l2.4 11.2a2 2 0 0 0 2 1.6h7.9a2 2 0 0 0 2-1.5L21 7H6"/><circle cx="10" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/>',
    "leaf": '<path d="M5 19c0-8 5-14 15-14 0 10-6 15-14 15"/><path d="M5 19c3-4 6-7 10-9"/>',
    "pin": '<path d="M12 21s-7-6.2-7-12a7 7 0 0 1 14 0c0 5.8-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "menu": '<path d="M3 6h18M3 12h18M3 18h18"/>',
    "close": '<path d="M6 6l12 12M18 6 6 18"/>',
    "whatsapp": '<path d="M4 20l1.3-4A8.5 8.5 0 1 1 8.6 19z"/><path d="M9 9.5c.3 2 2.2 4 4.5 4.6l1.2-1.1 1.8.9c-.2 1-1.1 1.7-2.1 1.6-3.5-.4-6.6-3.5-6.9-7 0-1 .7-1.9 1.6-2.1l.9 1.8z"/>',
    "facebook": '<path d="M15 3h-2.5A3.5 3.5 0 0 0 9 6.5V10H6.5v3.5H9V21h3.5v-7.5H15l.5-3.5h-3V7a1 1 0 0 1 1-1H15z"/>',
    "instagram": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".8"/>',
    "tiktok": '<path d="M14 3v11.5a3.5 3.5 0 1 1-3.5-3.5"/><path d="M14 3c.5 2.8 2.3 4.5 5 4.8"/>',
    "youtube": '<rect x="2.5" y="5.5" width="19" height="13" rx="4"/><path d="m10 9 5 3-5 3z"/>',
    "video": '<rect x="2.5" y="6" width="13" height="12" rx="2"/><path d="m15.5 10 6-3.5v11l-6-3.5"/>',
    "share": '<circle cx="18" cy="5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="19" r="2.5"/><path d="m8.2 10.8 7.6-4.5M8.2 13.2l7.6 4.5"/>',
    "x": '<path d="M4 4l16 16M20 4 4 20"/>',
    "linkedin": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 10v7M8 7v.01M12 17v-4a2 2 0 0 1 4 0v4M12 10v7"/>',
    "check": '<path d="m5 12 5 5 9-10"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "shield": '<path d="M12 3 4 6v6c0 4.5 3.4 8 8 9 4.6-1 8-4.5 8-9V6z"/><path d="m9 12 2 2 4-4"/>',
    "help": '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.7.3-1 .9-1 1.7M12 17v.01"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
    "minus": '<path d="M5 12h14"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "trash": '<path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13"/>',
    "activity": '<path d="M3 12h4l3-8 4 16 3-8h4"/>',
}


def svg_sprite() -> str:
    symbols = "".join(
        f'<symbol id="i-{k}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" '
        f'stroke-linecap="round" stroke-linejoin="round">{v}</symbol>'
        for k, v in ICONS.items()
    )
    return f'<svg width="0" height="0" style="position:absolute" aria-hidden="true">{symbols}</svg>'


# --------------------------------------------------------------------------- navegación
NAV = [
    ("Inicio", "/"),
    ("Nuestro Menú", "/menu/"),
    ("Paquetes", "/menu/paquetes/"),
    ("Salsas y Complementos", "/menu/salsas-y-complementos/"),
    ("Tradición de Huejutla", "/tradicion-de-huejutla/"),
    ("Blog", "/blog/"),
    ("Nosotros", "/nosotros/"),
]


def nav_html(current: str) -> str:
    # El elemento activo es el de prefijo más largo que coincide con la ruta actual
    match = max((p for _, p in NAV if current == p or (p != "/" and current.startswith(p))),
                key=len, default="")
    items = []
    for label, path in NAV:
        cur = ' aria-current="page"' if path == match else ""
        if path == "/menu/":
            sub = "".join(
                f'<li><a href="{u("/menu/" + c["slug"] + "/")}">{escape(c["name"])}</a></li>'
                for c in CATALOG["categories"]
            )
            items.append(
                f'<li class="has-sub"><a href="{u(path)}"{cur}>{label}</a>'
                f'<button class="sub-toggle" aria-expanded="false" aria-label="Abrir submenú de {label}">{icon("chevron")}</button>'
                f'<ul class="submenu">{sub}<li><a href="{u("/menu/")}">Ver todo el menú</a></li></ul></li>'
            )
        else:
            items.append(f'<li><a href="{u(path)}"{cur}>{label}</a></li>')
    return "".join(items)


def social_links(cls: str = "social") -> str:
    labels = {"facebook": "Facebook", "instagram": "Instagram", "tiktok": "TikTok", "youtube": "YouTube"}
    return f'<ul class="{cls}">' + "".join(
        f'<li><a href="{a(url)}" target="_blank" rel="noopener" aria-label="Eke en {labels[k]}" '
        f'data-track="social_click" data-network="{k}">{icon(k)}</a></li>'
        for k, url in SITE["social"].items()
    ) + "</ul>"


# --------------------------------------------------------------------------- layout
def analytics_head() -> str:
    ga = SITE["analytics"]["ga4_measurement_id"].strip()
    out = []
    gsc = SITE["analytics"]["gsc_verification"].strip()
    if gsc:
        out.append(f'<meta name="google-site-verification" content="{a(gsc)}">')
    if ga:
        out.append(
            f'<script async src="https://www.googletagmanager.com/gtag/js?id={a(ga)}"></script>'
            "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
            f"gtag('js',new Date());gtag('config','{a(ga)}');</script>"
        )
    else:
        out.append("<!-- Google Analytics 4: agrega tu ID G-XXXXXXX en data/site.json -> analytics.ga4_measurement_id -->")
    return "\n".join(out)


def breadcrumbs(trail: list[tuple[str, str]]) -> tuple[str, dict]:
    items = [("Inicio", "/")] + trail
    html = '<nav class="breadcrumb container" aria-label="Ruta de navegación"><ol>' + "".join(
        f'<li><a href="{u(p)}">{escape(n)}</a></li>' if i < len(items) - 1
        else f'<li aria-current="page">{escape(n)}</li>'
        for i, (n, p) in enumerate(items)
    ) + "</ol></nav>"
    schema = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": absu(p)}
            for i, (n, p) in enumerate(items)
        ],
    }
    return html, schema


def layout(*, path: str, title: str, description: str, body: str, schemas: list | None = None,
           noindex: bool = False, og_image: str = "og-eke-enchiladas-de-huejutla.jpg",
           og_type: str = "website", trail: list | None = None, priority: str = "0.5",
           changefreq: str = "monthly", images: list | None = None, page_class: str = "") -> None:
    schemas = list(schemas or [])
    crumb_html = ""
    if trail:
        crumb_html, crumb_schema = breadcrumbs(trail)
        schemas.append(crumb_schema)
    if "Eke" in title:
        full_title = title
    elif len(title) <= 50:
        full_title = f"{title} | Eke Huejutla"
    elif len(title) <= 64:
        full_title = f"{title} | Eke"
    else:
        full_title = title
    canonical = absu(path)
    og_url = absu("/assets/img/" + og_image)
    robots = "noindex, follow" if noindex else "index, follow, max-image-preview:large"
    ship = SITE["shipping"][-1]

    html = f"""<!doctype html>
<html lang="{SITE['lang']}" data-base="{a(BASE)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(full_title)}</title>
<meta name="description" content="{a(description)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{a(canonical)}">
<meta name="theme-color" content="#6e1a1a">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{a(SITE['name'])}">
<meta property="og:locale" content="{SITE['locale']}">
<meta property="og:title" content="{a(full_title)}">
<meta property="og:description" content="{a(description)}">
<meta property="og:url" content="{a(canonical)}">
<meta property="og:image" content="{a(og_url)}">
<meta property="og:image:alt" content="{a(title)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{a(full_title)}">
<meta name="twitter:description" content="{a(description)}">
<meta name="twitter:image" content="{a(og_url)}">
<link rel="icon" type="image/png" sizes="32x32" href="{u('/assets/img/favicon-32.png')}">
<link rel="apple-touch-icon" href="{u('/assets/img/apple-touch-icon.png')}">
<link rel="manifest" href="{u('/manifest.webmanifest')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bree+Serif&family=Kaushan+Script&family=Nunito+Sans:opsz,wght@6..12,400;6..12,600;6..12,700;6..12,800&display=swap">
<link rel="stylesheet" href="{u('/assets/css/styles.css')}?v={BUILD_ID}">
{analytics_head()}
{''.join(jsonld(s) for s in schemas)}
</head>
<body class="{page_class}">
{svg_sprite()}
<a class="skip-link" href="#contenido">Saltar al contenido</a>
<div class="topbar">
  <div class="container topbar-in">
    <p class="topbar-msg">{icon('truck')} <span>Envíos a todo México</span><span class="sep" aria-hidden="true">|</span><span class="hide-sm">Enchiladas de Huejutla auténticas, ahora en línea</span></p>
    <ul class="topbar-links">
      <li><a href="{u('/ayuda/')}">Ayuda</a></li>
      <li><a href="{u('/seguimiento/')}">Seguimiento de pedido</a></li>
    </ul>
  </div>
</div>
<header class="site-header">
  {img('bordado-huasteco-izquierdo', 'Bordado huasteco de flores rojas', 100, 95, 'flor flor-izq', lazy=False, title='Bordado huasteco')}
  <div class="container header-in">
    <a class="logo" href="{u('/')}" aria-label="Eke, Comida Tradicional Huasteca - Inicio">
      {img('logo-eke-comida-tradicional-huasteca', 'Logotipo de Eke, Comida Tradicional Huasteca', 293, 94, lazy=False, title='Eke Comida Tradicional Huasteca')}
    </a>
    <form class="search" role="search" action="{u('/menu/')}" method="get">
      <label class="sr-only" for="q">Buscar productos</label>
      {icon('search')}
      <input id="q" name="q" type="search" placeholder="Buscar productos (enchiladas, salsas, paquetes...)" autocomplete="off">
    </form>
    <div class="header-actions">
      <a class="hact account" href="{u('/cuenta/')}">{icon('user', 'icon icon-lg')}<span class="hide-md"><span data-account-name>Iniciar sesión</span><small data-account-sub>Crear cuenta</small></span></a>
      <a class="hact" href="{u('/favoritos/')}" aria-label="Favoritos">{icon('heart', 'icon icon-lg')}<span class="hide-md">Favoritos</span></a>
      <a class="hact cart-link" href="{u('/carrito/')}" aria-label="Carrito de compras">
        <span class="cart-icon">{icon('cart', 'icon icon-xl')}<span class="badge" data-cart-count>0</span></span>
        <strong data-cart-total>$0.00 MXN</strong>
      </a>
      <button class="menu-toggle" aria-expanded="false" aria-controls="main-nav" aria-label="Abrir menú">{icon('menu', 'icon icon-lg')}</button>
    </div>
  </div>
  {img('bordado-huasteco-derecho', 'Bordado huasteco de flores rojas', 74, 95, 'flor flor-der', lazy=False, title='Bordado huasteco')}
</header>
<nav class="main-nav" id="main-nav" aria-label="Principal">
  <ul class="container">{nav_html(path)}</ul>
</nav>
<main id="contenido">
{crumb_html}
{body}
</main>
<footer class="site-footer">
  <div class="textile" role="presentation"></div>
  <div class="container footer-grid">
    <section>
      {img('logo-eke-comida-tradicional-huasteca', 'Logotipo de Eke', 220, 71, 'footer-logo', title='Eke Comida Tradicional Huasteca')}
      <p>Enchiladas de Huejutla hechas en casa con receta tradicional de la Huasteca Hidalguense. Pedidos en línea con entrega local y envíos a todo México.</p>
      {social_links()}
    </section>
    <section>
      <h2 class="footer-title">Tienda</h2>
      <ul>
        <li><a href="{u('/menu/enchiladas/')}">Enchiladas</a></li>
        <li><a href="{u('/menu/paquetes/')}">Paquetes</a></li>
        <li><a href="{u('/menu/salsas-y-complementos/')}">Salsas y Complementos</a></li>
        <li><a href="{u('/carrito/')}">Carrito</a></li>
        <li><a href="{u('/blog/')}">Blog</a></li>
      </ul>
    </section>
    <section>
      <h2 class="footer-title">Atención al cliente</h2>
      <ul>
        <li><a href="{u('/ayuda/')}">Mesa de ayuda</a></li>
        <li><a href="{u('/seguimiento/')}">Seguimiento de pedido o ticket</a></li>
        <li><a href="{u('/catalogo-de-servicios/')}">Catálogo de servicios</a></li>
        <li><a href="{u('/estado/')}">Estado del sitio</a></li>
        <li><a href="{u('/aviso-de-privacidad/')}">Aviso de privacidad</a></li>
      </ul>
    </section>
    <section>
      <h2 class="footer-title">Contacto</h2>
      <ul class="contact-list">
        <li>{icon('pin')} {escape(SITE['address']['city'])}, {escape(SITE['address']['region'])}</li>
        <li>{icon('phone')} <a href="tel:{SITE['phone'].replace(' ', '')}">{escape(SITE['phone'])}</a></li>
        <li>{icon('whatsapp')} <a href="https://wa.me/{SITE['whatsapp']}" target="_blank" rel="noopener" data-track="whatsapp_click">WhatsApp</a></li>
        <li>{icon('mail')} <a href="mailto:{SITE['email']}">{escape(SITE['email'])}</a></li>
        <li>{icon('video')} <a href="{u('/nosotros/')}#videollamada">Agenda una videollamada</a></li>
        <li>{icon('clock')} Lunes a domingo, 8:00 a 16:00 h</li>
      </ul>
    </section>
  </div>
  <div class="footer-bottom container">
    <p>Pagos con tarjeta, PayPal, transferencia SPEI o efectivo. Envío nacional gratis desde {money(ship['free_from'])}.</p>
    <p>&copy; {date.today().year} {escape(SITE['name'])}. Proyecto académico, Gestiones Tecnológicas Empresariales (ISC), IT Huejutla.</p>
  </div>
</footer>
<div class="toast" role="status" aria-live="polite" hidden></div>
<script src="{u('/assets/js/catalog.js')}?v={BUILD_ID}"></script>
<script src="{u('/assets/js/app.js')}?v={BUILD_ID}" defer></script>
</body>
</html>
"""
    write(path, html)
    if not noindex:
        SITEMAP.append({"path": path, "priority": priority, "changefreq": changefreq, "images": images or []})


# --------------------------------------------------------------------------- componentes
def product_card(p: dict, heading: str = "h3", lazy: bool = True) -> str:
    badge = f'<span class="tag">{escape(p["badge"])}</span>' if p.get("badge") else ""
    url = u(f"/producto/{p['slug']}/")
    return f"""<article class="card product" data-product="{p['slug']}" data-name="{a(p['name'].lower())}" data-category="{p['category']}" data-price="{p['price']}">
  <a class="card-media" href="{url}" tabindex="-1" aria-hidden="true">
    {img(p['image'], p['image_alt'], 263, 126, lazy=lazy, title=p['name'])}
  </a>
  {badge}
  <button class="fav" data-fav="{p['slug']}" aria-pressed="false" aria-label="Agregar {a(p['name'])} a favoritos">{icon('heart')}</button>
  <div class="card-body">
    <{heading} class="card-title"><a href="{url}">{escape(p['name'])}</a></{heading}>
    <p class="card-desc">{escape(p['short'])}</p>
    <p class="stock" data-stock-for="{p['slug']}"></p>
    <p class="price">{money(p['price'])}</p>
    <button class="btn btn-wine" data-add-to-cart="{p['slug']}">{icon('cart')} Agregar al carrito</button>
  </div>
</article>"""


def product_grid(items: list[dict], heading: str = "h3") -> str:
    return '<div class="grid products">' + "".join(product_card(p, heading) for p in items) + "</div>"


def latest_posts(n: int = 3, heading: str = "h3") -> str:
    cards = []
    for post in BLOG_POSTS[:n]:
        cards.append(f"""<article class="card post-card">
  <a class="card-media" href="{u('/blog/' + post['slug'] + '/')}" tabindex="-1" aria-hidden="true">{img(post['image'], post['image_alt'], 263, 126)}</a>
  <div class="card-body">
    <p class="meta"><time datetime="{post['date']}">{format_date(post['date'])}</time></p>
    <{heading} class="card-title"><a href="{u('/blog/' + post['slug'] + '/')}">{escape(post['title'])}</a></{heading}>
    <p class="card-desc">{escape(post['description'])}</p>
  </div>
</article>""")
    return '<div class="grid posts">' + "".join(cards) + "</div>"


MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
          "septiembre", "octubre", "noviembre", "diciembre"]


def format_date(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day} de {MONTHS[d.month - 1]} de {d.year}"


def share_buttons(path: str, title: str) -> str:
    url = absu(path)
    from urllib.parse import quote
    q, t = quote(url, safe=""), quote(title, safe="")
    links = [
        ("facebook", "Facebook", f"https://www.facebook.com/sharer/sharer.php?u={q}"),
        ("x", "X", f"https://twitter.com/intent/tweet?url={q}&text={t}"),
        ("whatsapp", "WhatsApp", f"https://api.whatsapp.com/send?text={t}%20{q}"),
        ("linkedin", "LinkedIn", f"https://www.linkedin.com/sharing/share-offsite/?url={q}"),
    ]
    btns = "".join(
        f'<a class="share-btn share-{k}" href="{h}" target="_blank" rel="noopener" data-share="{k}" aria-label="Compartir en {n}">{icon(k)}<span>{n}</span></a>'
        for k, n, h in links
    )
    return (f'<div class="share" data-share-url="{a(url)}" data-share-title="{a(title)}"><p class="share-label">{icon("share")} Compartir:</p>{btns}'
            f'<button class="share-btn share-native" data-share="native" hidden>{icon("share")}<span>Más</span></button></div>')


def video_meta() -> dict:
    """Duración real del video generado por make_video.py (si existe)."""
    v = SITE["video"]
    f = SRC / "static" / "video" / f"{v.get('file', '')}.json"
    return json.loads(f.read_text(encoding="utf-8")) if v.get("file") and f.exists() else {}


def video_block() -> str:
    v = SITE["video"]
    if v.get("file") and (SRC / "static" / "video" / f"{v['file']}.mp4").exists():
        base = u("/assets/video/" + v["file"])
        return f"""<figure class="video">
  <video controls preload="none" playsinline width="1280" height="720" poster="{u('/assets/img/video-poster-eke.webp')}" title="{a(v['title'])}" data-video-title="{a(v['title'])}">
    <source src="{base}.mp4" type="video/mp4">
    <track kind="captions" src="{base}.vtt" srclang="es" label="Español" default>
    Tu navegador no puede reproducir este video. <a href="{base}.mp4">Descárgalo aquí</a>.
  </video>
  <figcaption>{escape(v['title'])}. Activa el sonido para escuchar la narración.</figcaption>
</figure>"""
    poster =img("hero-enchiladas-de-huejutla", "Vista previa del video: enchiladas de Huejutla recién servidas", 1016, 390, "video-poster", title=v["title"])
    if v["youtube_id"]:
        return f"""<figure class="video" data-youtube="{a(v['youtube_id'])}">
  <button class="video-facade" aria-label="Reproducir video: {a(v['title'])}">{poster}<span class="play">{icon('youtube', 'icon icon-xl')}</span></button>
  <figcaption>{escape(v['title'])}</figcaption>
</figure>"""
    return f"""<figure class="video">
  <div class="video-facade is-pending">{poster}<span class="play">{icon('video', 'icon icon-xl')}</span></div>
  <figcaption>{escape(v['title'])}. <em>Video en producción: se publicará en nuestro canal de YouTube.</em></figcaption>
</figure>"""


def video_schema() -> list:
    v = SITE["video"]
    meta = video_meta()
    if meta:
        return [{
            "@context": "https://schema.org", "@type": "VideoObject",
            "name": v["title"], "description": v["description"],
            "thumbnailUrl": [absu("/assets/img/video-poster-eke.webp")],
            "uploadDate": v["upload_date"], "duration": meta["iso_duration"],
            "contentUrl": absu(f"/assets/video/{v['file']}.mp4"),
            "inLanguage": "es-MX",
        }]
    if not v["youtube_id"]:
        return []
    return [{
        "@context": "https://schema.org", "@type": "VideoObject",
        "name": v["title"], "description": v["description"],
        "thumbnailUrl": [f"https://i.ytimg.com/vi/{v['youtube_id']}/hqdefault.jpg", absu("/assets/img/og-eke-enchiladas-de-huejutla.jpg")],
        "uploadDate": v["upload_date"], "duration": v["duration"],
        "embedUrl": f"https://www.youtube-nocookie.com/embed/{v['youtube_id']}",
        "contentUrl": f"https://www.youtube.com/watch?v={v['youtube_id']}",
    }]


def shipping_table() -> str:
    rows = "".join(
        f"<tr><td>{escape(s['label'])}</td><td>{'Gratis' if s['cost'] == 0 else money(s['cost'])}"
        f"{' (gratis desde ' + money(s['free_from']) + ')' if s.get('free_from') else ''}</td></tr>"
        for s in SITE["shipping"]
    )
    return f'<table class="table"><thead><tr><th scope="col">Modalidad</th><th scope="col">Costo</th></tr></thead><tbody>{rows}</tbody></table>'


def org_schema() -> dict:
    s = SITE
    return {
        "@context": "https://schema.org", "@type": "Restaurant",
        "@id": absu("/#negocio"),
        "name": s["name"], "url": absu("/"),
        "logo": absu("/assets/img/logo-eke-comida-tradicional-huasteca.webp"),
        "image": absu("/assets/img/og-eke-enchiladas-de-huejutla.jpg"),
        "description": s["default_description"],
        "servesCuisine": ["Mexicana", "Huasteca"],
        "priceRange": "$$", "telephone": s["phone"], "email": s["email"],
        "address": {"@type": "PostalAddress", "streetAddress": s["address"]["street"],
                    "addressLocality": s["address"]["city"], "addressRegion": s["address"]["region"],
                    "postalCode": s["address"]["postal_code"], "addressCountry": s["address"]["country"]},
        "geo": {"@type": "GeoCoordinates", "latitude": s["geo"]["lat"], "longitude": s["geo"]["lng"]},
        "openingHours": s["opening_hours"],
        "hasMenu": absu("/menu/"),
        "sameAs": list(s["social"].values()),
    }


# --------------------------------------------------------------------------- bloques reemplazables en páginas
def featured() -> str:
    return product_grid([p for p in PRODUCTS if p.get("featured")][:4])


BLOCKS = {
    "featured_products": featured,
    "all_products": lambda: product_grid(PRODUCTS),
    "latest_posts": lambda: latest_posts(3),
    "video": video_block,
    "shipping_table": shipping_table,
    "social_links": lambda: social_links("social social-lg"),
    "category_links": lambda: "".join(
        f'<a class="chip" href="{u("/menu/" + c["slug"] + "/")}">{escape(c["name"])}</a>' for c in CATALOG["categories"]
    ),
}


def render_tokens(body: str) -> str:
    body = re.sub(r"\{\{block:(\w+)\}\}", lambda m: BLOCKS[m.group(1)](), body)
    body = re.sub(r"\{\{icon:([\w-]+)(?:\s+([\w -]+))?\}\}", lambda m: icon(m.group(1), m.group(2) or "icon"), body)
    body = re.sub(
        r"\{\{img:([\w-]+)\|([^|]+)\|(\d+)\|(\d+)(?:\|([\w -]*))?(?:\|(eager))?\}\}",
        lambda m: img(m.group(1), m.group(2), int(m.group(3)), int(m.group(4)), m.group(5) or "", lazy=not m.group(6)),
        body,
    )
    body = re.sub(r"\{\{url:([^}]*)\}\}", lambda m: u(m.group(1)), body)

    def site_value(m):
        val = SITE
        for key in m.group(1).split("."):
            val = val[key]
        return escape(str(val))

    return re.sub(r"\{\{site\.([\w.]+)\}\}", site_value, body)


# --------------------------------------------------------------------------- generadores
def build_pages() -> None:
    for f in sorted((SRC / "pages").glob("*.html")):
        meta, body = parse_front_matter(f.read_text(encoding="utf-8"))
        path = meta["path"]
        schemas = []
        if meta.get("schema") == "home":
            schemas += [org_schema(), {
                "@context": "https://schema.org", "@type": "WebSite", "name": SITE["name"], "url": absu("/"),
                "potentialAction": {"@type": "SearchAction",
                                    "target": absu("/menu/") + "?q={search_term_string}",
                                    "query-input": "required name=search_term_string"},
            }]
        if meta.get("schema") == "video":
            schemas += video_schema()
        if meta.get("schema") == "faq":
            faqs = re.findall(r'<details class="faq">\s*<summary>(.*?)</summary>\s*<div>(.*?)</div>', body, re.S)
            schemas.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": re.sub("<[^>]+>", "", q).strip(),
                 "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"\s+", " ", re.sub("<[^>]+>", "", ans)).strip()}}
                for q, ans in faqs]})
        if meta.get("schema") == "about":
            schemas.append(org_schema())
        trail = [(meta["crumb"], path)] if meta.get("crumb") and path != "/" else None
        layout(path=path, title=meta["title"], description=meta["description"], body=render_tokens(body),
               schemas=schemas, noindex=meta.get("noindex") == "true", trail=trail,
               priority=meta.get("priority", "0.5"), changefreq=meta.get("changefreq", "monthly"),
               page_class=meta.get("class", ""), images=[i for i in meta.get("images", "").split(",") if i])


def build_catalog_pages() -> None:
    chips = lambda active: '<div class="chips">' + f'<a class="chip{" is-active" if active == "" else ""}" href="{u("/menu/")}">Todo</a>' + "".join(
        f'<a class="chip{" is-active" if active == c["slug"] else ""}" href="{u("/menu/" + c["slug"] + "/")}">{escape(c["name"])}</a>'
        for c in CATALOG["categories"]) + "</div>"
    toolbar = """<div class="toolbar">
  <p class="results" data-results aria-live="polite"></p>
  <label>Ordenar por
    <select data-sort>
      <option value="">Recomendados</option>
      <option value="price-asc">Precio: menor a mayor</option>
      <option value="price-desc">Precio: mayor a menor</option>
      <option value="name">Nombre</option>
    </select>
  </label>
</div>"""
    item_list = lambda items: {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "url": absu(f"/producto/{p['slug']}/"), "name": p["name"]}
        for i, p in enumerate(items)]}

    body = f"""<section class="section container">
  <header class="section-head">
    <h1 class="section-title">Nuestro Menú de Comida Huasteca</h1>
    <p class="section-sub">Enchiladas de Huejutla, paquetes para compartir y salsas artesanales. <span data-search-label></span></p>
  </header>
  {chips('')}
  {toolbar}
  <div data-filterable>{product_grid(PRODUCTS, 'h2')}</div>
  <p class="empty" data-empty hidden>No encontramos productos con esa búsqueda. <a href="{u('/menu/')}">Ver todo el menú</a></p>
</section>"""
    layout(path="/menu/", title="Menú: enchiladas de Huejutla, paquetes y salsas",
           description="Menú completo de Eke: enchiladas de Huejutla, enchiladas con cecina, paquetes familiares y salsa huasteca artesanal. Ordena en línea con envío a todo México.",
           body=body, trail=[("Nuestro Menú", "/menu/")], schemas=[item_list(PRODUCTS)], priority="0.9", changefreq="weekly")

    for c in CATALOG["categories"]:
        items = [p for p in PRODUCTS if p["category"] == c["slug"]]
        path = f"/menu/{c['slug']}/"
        body = f"""<section class="section container">
  <header class="section-head">
    <h1 class="section-title">{escape(c['title'])}</h1>
    <p class="section-sub">{escape(c['intro'])}</p>
  </header>
  {chips(c['slug'])}
  {toolbar}
  <div data-filterable>{product_grid(items, 'h2')}</div>
</section>"""
        layout(path=path, title=c["title"], description=c["description"], body=body,
               trail=[("Nuestro Menú", "/menu/"), (c["name"], path)], schemas=[item_list(items)],
               priority="0.9", changefreq="weekly", images=[p["image"] for p in items])

    for p in PRODUCTS:
        path = f"/producto/{p['slug']}/"
        cat = CATEGORIES[p["category"]]
        related = [r for r in PRODUCTS if r["slug"] != p["slug"] and r["category"] == p["category"]][:3]
        if len(related) < 3:
            related += [r for r in PRODUCTS if r["slug"] != p["slug"] and r not in related][: 3 - len(related)]
        wa_text = f"Hola Eke, quiero pedir: {p['name']} ({money(p['price'])})"
        from urllib.parse import quote
        badge = f'<span class="tag tag-static">{escape(p["badge"])}</span>' if p.get("badge") else ""
        body = f"""<section class="container product-detail" data-product-page="{p['slug']}">
  <div class="pd-media">
    {badge}
    {img(p['image'], p['image_alt'], 263, 126, 'pd-img', lazy=False, title=p['name'])}
  </div>
  <div class="pd-info">
    <p class="eyebrow"><a href="{u('/menu/' + cat['slug'] + '/')}">{escape(cat['name'])}</a></p>
    <h1>{escape(p['name'])}</h1>
    <p class="pd-short">{escape(p['short'])}</p>
    <p class="price price-lg">{money(p['price'])}</p>
    <p class="stock" data-stock-for="{p['slug']}"></p>
    <div class="buy-row">
      <div class="qty" data-qty>
        <button type="button" data-qty-step="-1" aria-label="Disminuir cantidad">{icon('minus')}</button>
        <input type="number" min="1" value="1" inputmode="numeric" aria-label="Cantidad" data-qty-input>
        <button type="button" data-qty-step="1" aria-label="Aumentar cantidad">{icon('plus')}</button>
      </div>
      <button class="btn btn-wine btn-lg" data-add-to-cart="{p['slug']}" data-with-qty>{icon('cart')} Agregar al carrito</button>
      <button class="btn btn-ghost fav-inline" data-fav="{p['slug']}" aria-pressed="false" aria-label="Agregar a favoritos">{icon('heart')}</button>
    </div>
    <div class="buy-row">
      <a class="btn btn-yellow" href="{u('/carrito/')}" data-buy-now="{p['slug']}">Comprar ahora</a>
      <a class="btn btn-whatsapp" href="https://wa.me/{SITE['whatsapp']}?text={quote(wa_text)}" target="_blank" rel="noopener" data-track="whatsapp_click">{icon('whatsapp')} Pedir por WhatsApp</a>
    </div>
    <ul class="perks">
      <li>{icon('leaf')} Receta tradicional de Huejutla, hecha el mismo día</li>
      <li>{icon('truck')} Entrega local o envío nacional (gratis desde $800 MXN)</li>
      <li>{icon('shield')} Pago seguro con tarjeta, PayPal, SPEI o efectivo</li>
    </ul>
    <h2 class="h3">Descripción</h2>
    <p>{escape(p['description'])}</p>
    <dl class="specs"><dt>SKU</dt><dd>{p['sku']}</dd><dt>Categoría</dt><dd>{escape(cat['name'])}</dd></dl>
    {share_buttons(path, p['name'] + ' | Eke')}
  </div>
</section>
<section class="section container">
  <h2 class="section-title small">También te puede gustar</h2>
  {product_grid(related, 'h3')}
</section>"""
        schema = {
            "@context": "https://schema.org", "@type": "Product",
            "name": p["name"], "sku": p["sku"], "description": p["description"],
            "image": [absu(f"/assets/img/{p['image']}.webp")],
            "brand": {"@type": "Brand", "name": "Eke"},
            "category": cat["name"],
            "offers": {
                "@type": "Offer", "url": absu(path), "priceCurrency": "MXN", "price": f"{p['price']:.2f}",
                "availability": "https://schema.org/InStock" if p["stock"] > 0 else "https://schema.org/OutOfStock",
                "itemCondition": "https://schema.org/NewCondition",
                "seller": {"@id": absu("/#negocio")},
            },
        }
        layout(path=path, title=f"{p['name']} a domicilio", description=f"{p['short']} {p['description']}"[:158].rsplit(" ", 1)[0] + ".",
               body=body, schemas=[schema], og_type="product",
               trail=[("Nuestro Menú", "/menu/"), (cat["name"], f"/menu/{cat['slug']}/"), (p["name"], path)],
               priority="0.8", changefreq="weekly", images=[p["image"]], page_class="page-product")


BLOG_POSTS: list[dict] = []


def load_blog() -> None:
    for f in (SRC / "blog").glob("*.html"):
        meta, body = parse_front_matter(f.read_text(encoding="utf-8"))
        meta["body"] = body
        meta["slug"] = f.stem
        BLOG_POSTS.append(meta)
    BLOG_POSTS.sort(key=lambda m: m["date"], reverse=True)


def build_blog() -> None:
    body = f"""<section class="section container">
  <header class="section-head">
    <h1 class="section-title">Blog de cocina huasteca</h1>
    <p class="section-sub">Historias, recetas y tradiciones de Huejutla y la Huasteca Hidalguense.</p>
  </header>
  {latest_posts(len(BLOG_POSTS), "h2")}
</section>"""
    layout(path="/blog/", title="Blog de comida huasteca y tradiciones de Huejutla",
           description="Recetas, historia de las enchiladas de Huejutla, tradiciones de la Huasteca Hidalguense y consejos para disfrutar la comida huasteca en casa.",
           body=body, trail=[("Blog", "/blog/")], priority="0.7", changefreq="weekly")

    for post in BLOG_POSTS:
        path = f"/blog/{post['slug']}/"
        others = [p for p in BLOG_POSTS if p is not post][:2]
        more = "".join(f'<li><a href="{u("/blog/" + o["slug"] + "/")}">{escape(o["title"])}</a></li>' for o in others)
        body = f"""<article class="container article">
  <header>
    <p class="meta">Por {escape(post['author'])} · <time datetime="{post['date']}">{format_date(post['date'])}</time> · {post.get('read', '4')} min de lectura</p>
    <h1>{escape(post['title'])}</h1>
    <p class="lead">{escape(post['description'])}</p>
    {share_buttons(path, post['title'])}
  </header>
  <figure class="article-figure">
    {img(post['image'], post['image_alt'], 263, 126, lazy=False)}
    <figcaption>{escape(post['image_alt'])}</figcaption>
  </figure>
  <div class="prose">{render_tokens(post['body'])}</div>
  <aside class="cta-box">
    <h2 class="h3">¿Se te antojaron?</h2>
    <p>Pide tus enchiladas de Huejutla en línea y recíbelas en casa.</p>
    <a class="btn btn-yellow" href="{u('/menu/')}" data-track="blog_cta">{icon('cart')} Ordena en línea</a>
  </aside>
  {share_buttons(path, post['title'])}
  <nav class="more-posts" aria-label="Más artículos"><h2 class="h3">Sigue leyendo</h2><ul>{more}</ul></nav>
</article>"""
        schema = {
            "@context": "https://schema.org", "@type": "BlogPosting",
            "headline": post["title"], "description": post["description"],
            "image": absu(f"/assets/img/{post['image']}.webp"),
            "datePublished": post["date"], "dateModified": post.get("updated", post["date"]),
            "author": {"@type": "Person", "name": post["author"]},
            "publisher": {"@id": absu("/#negocio")},
            "mainEntityOfPage": absu(path), "keywords": post.get("keywords", ""),
        }
        layout(path=path, title=post["title"], description=post["description"], body=body,
               schemas=[schema], og_type="article", trail=[("Blog", "/blog/"), (post["title"][:40] + ("…" if len(post["title"]) > 40 else ""), path)],
               priority="0.7", images=[post["image"]], page_class="page-article")


def build_404() -> None:
    body = f"""<section class="section container center">
  <h1 class="section-title">Página no encontrada</h1>
  <p>La página que buscas no existe o cambió de dirección.</p>
  <p><a class="btn btn-yellow" href="{u('/')}">Ir al inicio</a> <a class="btn btn-ghost" href="{u('/menu/')}">Ver el menú</a></p>
</section>"""
    layout(path="/404.html", title="Página no encontrada", description="La página solicitada no existe en la tienda en línea de Eke.",
           body=body, noindex=True)


def build_catalog_js() -> None:
    data = {
        "products": [{k: p[k] for k in ("slug", "sku", "name", "category", "price", "stock", "image", "short")} for p in PRODUCTS],
        "categories": {c["slug"]: c["name"] for c in CATALOG["categories"]},
        "shipping": SITE["shipping"],
        "whatsapp": SITE["whatsapp"],
        "formspree": SITE["forms"]["formspree_id"],
        "build": BUILD_ID,
    }
    out = DIST / "assets" / "js" / "catalog.js"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("window.EKE_CATALOG=" + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")


def build_seo_files() -> None:
    # sitemap.xml dinámico: se regenera en cada build con todas las páginas indexables
    urls = []
    for e in sorted(SITEMAP, key=lambda e: -float(e["priority"])):
        imgs = "".join(
            f"<image:image><image:loc>{escape(absu('/assets/img/' + i + '.webp'))}</image:loc></image:image>"
            for i in dict.fromkeys(e["images"])
        )
        urls.append(
            f"  <url><loc>{escape(absu(e['path']))}</loc><lastmod>{BUILD_DATE}</lastmod>"
            f"<changefreq>{e['changefreq']}</changefreq><priority>{e['priority']}</priority>{imgs}</url>"
        )
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + "\n".join(urls) + "\n</urlset>\n",
        encoding="utf-8",
    )
    (DIST / "robots.txt").write_text(
        "# robots.txt - Eke Comida Tradicional Huasteca\n"
        "User-agent: *\n"
        "Allow: /\n"
        f"Disallow: {BASE}/carrito/\n"
        f"Disallow: {BASE}/pagar/\n"
        f"Disallow: {BASE}/pedido-confirmado/\n"
        f"Disallow: {BASE}/cuenta/\n"
        f"Disallow: {BASE}/favoritos/\n\n"
        f"Sitemap: {absu('/sitemap.xml')}\n",
        encoding="utf-8",
    )
    manifest = {
        "name": SITE["name"], "short_name": SITE["short_name"], "lang": SITE["lang"],
        "start_url": u("/"), "display": "standalone", "background_color": "#fbf3e6", "theme_color": "#6e1a1a",
        "icons": [{"src": u("/assets/img/icon-512.png"), "sizes": "512x512", "type": "image/png"},
                  {"src": u("/assets/img/apple-touch-icon.png"), "sizes": "180x180", "type": "image/png"}],
    }
    (DIST / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    (DIST / "version.json").write_text(json.dumps({"build": BUILD_ID, "date": BUILD_DATE}), encoding="utf-8")


def copy_static() -> None:
    shutil.copytree(SRC / "static", DIST / "assets", dirs_exist_ok=True)
    # Métricas de monitoreo (si existen) para la página /estado/
    metrics = ROOT / "monitoring" / "metrics.csv"
    if metrics.exists():
        (DIST / "assets" / "data").mkdir(parents=True, exist_ok=True)
        shutil.copy(metrics, DIST / "assets" / "data" / "metrics.csv")


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    copy_static()
    load_blog()
    build_pages()
    build_catalog_pages()
    build_blog()
    build_404()
    build_catalog_js()
    build_seo_files()
    n = len(list(DIST.rglob("*.html")))
    print(f"Build OK: {n} páginas HTML, {len(SITEMAP)} URLs en sitemap.xml -> {DIST} (BASE_PATH='{BASE}', SITE_URL='{SITE_URL}')")


if __name__ == "__main__":
    main()
