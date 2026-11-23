# Manual técnico y de configuración

**Proyecto:** Eke, tienda en línea de comida tradicional huasteca
**Materia:** Gestiones Tecnológicas Empresariales · ISC · IT Huejutla

---

## 1. Arquitectura

La plataforma usa una arquitectura **JAMstack**: un generador de sitios estáticos propio, escrito en Python,
produce HTML optimizado para SEO. Un CDN (GitHub Pages) lo sirve, y JavaScript en el navegador agrega la
lógica de comercio electrónico.

```
                ┌──────────────── Repositorio GitHub ─────────────────┐
  Desarrollador │ feature/* ──PR──> develop ──PR──> main               │
  (git push)    │      │ CI: build + pruebas + Lighthouse   │ CD        │
                └──────┼─────────────────────────────────────┼─────────┘
                       ▼                                     ▼
                Artefacto /dist                      GitHub Pages (CDN, HTTPS)
                                                            │
        ┌───────────────────────────────────────────────────┼──────────────────┐
        │ Navegador del cliente                             ▼                  │
        │  HTML + CSS + app.js ── carrito, inventario, checkout, mesa de ayuda │
        │        │                   │                     │                   │
        │        ▼                   ▼                     ▼                   │
        │  Google Analytics 4   Formspree (correo)    WhatsApp / Google Meet   │
        └──────────────────────────────────────────────────────────────────────┘
        Monitoreo programado (GitHub Actions cada 6 h) ──> monitoring/metrics.csv ──> /estado/
```

### ¿Por qué no WordPress + WooCommerce?

El documento de requisitos permite WordPress/WooCommerce "u otros según su conocimiento". Se eligió un
generador estático propio por estas razones:

| Criterio | WordPress + WooCommerce | Solución Eke (estática) |
|---|---|---|
| Hosting | Requiere PHP + MySQL (de pago) | GitHub Pages gratuito con HTTPS |
| Rendimiento | Depende de plugins de caché | HTML pre-generado, ~160 KB de imágenes en total |
| Seguridad | Actualizaciones de núcleo y plugins | Sin servidor ni base de datos expuestos |
| DevOps | CI/CD difícil (la BD vive en producción) | Todo versionado en Git, CI/CD nativo |
| SEO | Plugin Yoast/RankMath | Implementado en `build.py` (meta, Schema, sitemap) |

**Equivalencias con WooCommerce:**

| Función WooCommerce | Implementación en Eke |
|---|---|
| Productos y categorías | `data/products.json` → `/producto/<slug>/` y `/menu/<categoria>/` |
| Gestión de inventario | Campo `stock` por producto; las existencias se descuentan al comprar y se bloquea la venta sin stock |
| Carrito | `app.js` (localStorage) con contador y total en el encabezado |
| Pasarelas de pago | Mercado Pago (tarjeta), PayPal, SPEI y efectivo, **en modo de prueba** |
| Pedidos | Folio `EKE-AAAAMMDD-####`, confirmación, seguimiento y aviso por correo (Formspree) |
| Cuentas de cliente | Registro e inicio de sesión (demostración local con SHA-256) |
| Blog y compartir | `src/blog/` con botones para Facebook, X, WhatsApp, LinkedIn y compartir nativo |

> **Limitación conocida:** al ser un sitio sin servidor, los pedidos, el inventario vendido y las cuentas se
> guardan en el navegador del cliente (demostración). Para operar en producción real hay tres opciones:
> (a) conectar **Mercado Pago Checkout Pro** o **PayPal Checkout** con una función serverless que confirme el pago,
> (b) usar un backend como Supabase o Firebase para pedidos e inventario, o (c) migrar el catálogo a WooCommerce.
> La interfaz y el SEO no cambian con ninguna de las tres.

## 2. Componentes

| Archivo | Función |
|---|---|
| `scripts/build.py` | Generador: layout, navegación, SEO (title, description, canonical, Open Graph, Twitter Card, JSON-LD), páginas de producto, categoría y blog, sitemap.xml, robots.txt, manifest, `catalog.js` |
| `scripts/test_site.py` | Pruebas automáticas del sitio generado |
| `scripts/optimize_images.py` | Conversión a WebP, variantes responsivas, imagen Open Graph y favicons |
| `scripts/monitor.py` | Monitoreo de disponibilidad, tiempos de respuesta y errores HTTP |
| `src/static/js/app.js` | Carrito, inventario, favoritos, checkout, mesa de ayuda, seguimiento, cuentas, búsqueda, eventos GA4 y Web Vitals |
| `src/static/css/styles.css` | Diseño responsivo basado en la maqueta |
| `data/site.json` | Configuración central (URL, contacto, redes, GA4, Search Console, Formspree, video, envíos) |
| `data/products.json` | Catálogo, precios, SKU, inventario, textos SEO e imágenes |

### Datos estructurados (Schema.org)

| Página | Tipos JSON-LD |
|---|---|
| Inicio | `Restaurant` (dirección, geo, horario, redes), `WebSite` con `SearchAction` |
| Producto | `Product` + `Offer` (precio MXN, disponibilidad), `BreadcrumbList` |
| Categoría y menú | `ItemList`, `BreadcrumbList` |
| Blog | `BlogPosting`, `BreadcrumbList` |
| Ayuda | `FAQPage` (generado a partir de las preguntas frecuentes) |
| Tradición | `VideoObject` (cuando se configura `video.youtube_id`) |

## 3. Configuración

Todo se configura en `data/site.json`:

| Clave | Uso |
|---|---|
| `site_url` | URL pública (en el pipeline se toma automáticamente de GitHub Pages) |
| `analytics.ga4_measurement_id` | ID de Google Analytics 4 (`G-XXXXXXXXXX`). Si está vacío no se carga GA |
| `analytics.gsc_verification` | Código de la etiqueta HTML de Google Search Console |
| `forms.formspree_id` | ID de formulario de Formspree para recibir pedidos, tickets y suscripciones por correo |
| `video.youtube_id` | ID del video en YouTube. Activa el reproductor y el schema `VideoObject` |
| `social`, `webconference`, `whatsapp`, `phone`, `email` | Canales de contacto |
| `shipping` | Modalidades y costos de envío |

**Agregar un producto:** añade un objeto en `data/products.json` (slug en minúsculas con guiones, `image`
igual al nombre del WebP) y coloca la imagen original en `assets-src/`. Luego ejecuta `optimize_images.py`
y `build.py`. La página, el sitemap y el catálogo se generan solos.

**Agregar una entrada de blog:** crea `src/blog/<slug>.html` con front matter (`title`, `description`,
`date`, `author`, `image`, `image_alt`, `keywords`).

### Eventos de Google Analytics 4 implementados

`view_item_list`, `view_item`, `search`, `add_to_cart`, `remove_from_cart`, `view_cart`, `add_to_wishlist`,
`begin_checkout`, `add_shipping_info`, `add_payment_info`, `purchase`, `share`, `generate_lead` (boletín y
mesa de ayuda), `sign_up`, `login`, `video_start`, `whatsapp_click`, `social_click`, `webconference`,
`web_vitals` (LCP, CLS, FCP, TTFB, tiempo de carga) y `exception` (errores de JavaScript).

Para depurar los eventos en la consola del navegador: `localStorage.setItem('eke_debug','true')`.

## 4. Control de versiones (ALM)

Estrategia **Git Flow simplificado**:

| Rama | Propósito | Protección recomendada |
|---|---|---|
| `main` | Producción. Cada push despliega | PR obligatorio + CI en verde |
| `develop` | Integración de funciones | PR obligatorio + CI en verde |
| `feature/<nombre>` | Nueva función o contenido | — |
| `hotfix/<nombre>` | Corrección urgente desde `main` | — |

Flujo: `feature/*` → PR a `develop` (CI) → PR de `develop` a `main` (CI) → despliegue automático.
Los commits siguen *Conventional Commits* (`feat:`, `fix:`, `docs:`, `chore:`).
Las plantillas `.github/ISSUE_TEMPLATE` registran **incidentes** y **solicitudes de cambio** (ITIL), y
`.github/pull_request_template.md` incluye la lista de verificación de calidad.

## 5. Pipeline CI/CD (GitHub Actions)

| Workflow | Disparador | Etapas |
|---|---|---|
| `ci.yml` | Push a `develop`, `feature/**`, `hotfix/**`; PR a `main`/`develop` | Build → pruebas (`test_site.py`) → artefacto `dist` → auditoría **Lighthouse** (rendimiento, accesibilidad, buenas prácticas, SEO ≥ 90) |
| `deploy.yml` | Push a `main` o manual | Build con la URL de producción → pruebas → publicación en GitHub Pages → prueba de humo en producción |
| `monitor.yml` | Cada 6 horas o manual | Comprueba 6 URLs → guarda `metrics.csv` → republica `/estado/` → falla (y GitHub envía correo) si el sitio no responde |

Pruebas automáticas (`test_site.py`): title de 10 a 70 caracteres, description de 50 a 170, un solo H1,
jerarquía de encabezados, canonical, Open Graph, imágenes con `alt`, `title`, dimensiones y formato WebP,
enlaces internos sin rotos, URLs amigables, JSON-LD válido, sitemap bien formado y robots.txt con Sitemap.

## 6. Monitoreo y métricas DevOps

| Métrica | Fuente | Objetivo |
|---|---|---|
| Disponibilidad | `monitor.py` (cada 6 h) | ≥ 99.5 % mensual |
| Tiempo de respuesta (promedio y p95) | `monitor.py` | < 800 ms promedio |
| Tasa de errores HTTP (4xx/5xx) | `monitor.py` | < 1 % |
| LCP / CLS / FCP / TTFB (usuarios reales) | Evento `web_vitals` en GA4 | LCP ≤ 2.5 s, CLS ≤ 0.1 |
| Puntuación Lighthouse | `ci.yml` | ≥ 90 en SEO, ≥ 85 en rendimiento |
| Errores de JavaScript | Evento `exception` en GA4 | 0 |
| Frecuencia de despliegue y tasa de fallos de cambio (DORA) | Historial de Actions | Registrar mensualmente |

La página pública **`/estado/`** muestra el historial del monitoreo, una prueba en vivo desde el navegador
y los Web Vitals de la visita.

**Optimizaciones de rendimiento aplicadas:** imágenes WebP (−87 % de peso), `width`/`height` explícitos
(evita CLS), `loading="lazy"` y `fetchpriority="high"` en la imagen principal, `srcset` responsivo, fuentes
con `display=swap` y `preconnect`, JavaScript diferido sin dependencias, video con fachada (el iframe de
YouTube solo se carga al hacer clic) y caché del CDN con *cache busting* por versión de build.

## 7. Seguridad y privacidad

- HTTPS obligatorio (GitHub Pages).
- Sin datos de tarjeta en el sitio: los pagos se delegan a la pasarela.
- Todo texto ingresado por el usuario se escapa antes de insertarlo en la página (prevención de XSS).
- Contraseñas de la demostración guardadas como hash SHA-256 (en producción se usaría un proveedor de identidad).
- Aviso de privacidad conforme a la LFPDPPP (`/aviso-de-privacidad/`).
- Enlaces externos con `rel="noopener"`.
