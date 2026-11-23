# Eke · Tienda en línea de Comida Tradicional Huasteca

Proyecto Web Integral de la materia **Gestiones Tecnológicas Empresariales**
Ingeniería en Sistemas Computacionales · Instituto Tecnológico de Huejutla

Tienda en línea de **enchiladas de Huejutla**, paquetes y salsa huasteca, con SEO técnico, analítica,
mesa de ayuda basada en ITIL y un pipeline DevOps (CI/CD + monitoreo) sobre GitHub Actions y GitHub Pages.

---

## Inicio rápido

Requisitos: **Python 3.10+** (no necesita librerías para generar el sitio; Pillow solo para optimizar imágenes).

```bash
python scripts/build.py              # genera el sitio en /dist
python scripts/test_site.py          # pruebas automáticas (SEO, imágenes, enlaces, sitemap)
python -m http.server 8000 -d dist   # vista previa en http://localhost:8000
```

Otros scripts:

```bash
python scripts/optimize_images.py                        # PNG/JPG de /assets-src -> WebP en /src/static/img
SITE_URL=https://tu-sitio python scripts/monitor.py      # disponibilidad, tiempos y errores HTTP
```

## Estructura

```
data/            site.json (configuración, GA4, redes, envíos) · products.json (catálogo e inventario)
src/pages/       páginas con front matter (title, description, ruta)  ← se editan como en un CMS
src/blog/        entradas del blog
src/static/      css, js, img (se publican en /assets)
assets-src/      imágenes originales (se convierten a WebP)
scripts/         build.py · test_site.py · optimize_images.py · monitor.py
monitoring/      metrics.csv (historial del monitoreo)
.github/         workflows de CI/CD y monitoreo, plantillas de issues (ITIL) y PR
docs/            manual técnico, SEO/SEM, ITIL, reporte de analítica, guía de publicación
design/          maqueta original
```

## Cumplimiento de requisitos

| Requisito | Dónde se cumple |
|---|---|
| 1.1 SEO on-page (title, description, H1-H3, URLs amigables) | `scripts/build.py` (layout), `src/pages/*`, URLs como `/producto/enchiladas-con-cecina/` |
| 1.2 robots.txt y sitemap XML dinámico | Se generan en cada build (`build_seo_files`), validados por `test_site.py` |
| 1.3 SEO de imágenes y video | WebP + `alt` + `title` + `width/height`; `optimize_images.py`; video con VideoObject y fachada |
| 1.4 Campaña SEM simulada | [`docs/02-seo-y-campana-sem.md`](docs/02-seo-y-campana-sem.md) |
| 2.1 Plataforma, blog, share, tienda, pagos, categorías, inventario | `/blog/`, botones para compartir, `/menu/`, `/carrito/`, `/pagar/`, `data/products.json` |
| 2.2 Google Analytics y Search Console | `data/site.json > analytics`; eventos de e-commerce GA4 en `app.js` |
| 2.3 Webconferencias y redes sociales | `/nosotros/#videollamada` (Google Meet y agenda de citas), redes en el pie de página |
| 3.1 Repositorio y ramas | Git Flow: `main`, `develop`, `feature/*`, `hotfix/*` |
| 3.2 Pipeline CI/CD | `.github/workflows/ci.yml` y `deploy.yml` |
| 3.3 Monitoreo y métricas | `monitor.yml`, `scripts/monitor.py`, página `/estado/`, Web Vitals a GA4 |
| 4.1 Catálogo de servicios | `/catalogo-de-servicios/`, [`docs/03-gestion-de-servicios-itil.md`](docs/03-gestion-de-servicios-itil.md) |
| 4.2 Mesa de ayuda | `/ayuda/` (incidentes y solicitudes, prioridad y SLA), `/seguimiento/` |
| 4.3 Mejora continua | [`docs/04-reporte-analitica-y-mejora-continua.md`](docs/04-reporte-analitica-y-mejora-continua.md) |

Documentación completa: [`docs/`](docs/). Para publicar el sitio, sigue [`docs/05-guia-de-publicacion.md`](docs/05-guia-de-publicacion.md).
