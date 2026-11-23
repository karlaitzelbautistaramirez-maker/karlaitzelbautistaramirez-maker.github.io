# Reporte de analítica y mejora continua

**Periodo:** ____ de __________ al ____ de __________ de 2026
**Elaboró:** ______________________

> **Cómo usar esta plantilla:** llena cada tabla con los datos reales de Google Analytics 4, Google Search
> Console, el monitoreo (`/estado/` o `monitoring/metrics.csv`) y los tickets de la mesa de ayuda. No
> inventes cifras: si un dato no existe todavía (por ejemplo, Search Console tarda unos días en mostrar
> información), escribe "sin datos suficientes" y la fecha en que se volverá a medir.

---

## 1. Resumen ejecutivo

<!-- 3 a 5 líneas: qué pasó en el periodo, el hallazgo principal y la mejora que se propone. -->

## 2. Tráfico y comportamiento (Google Analytics 4)

**Dónde obtenerlo:** GA4 → *Informes* → *Adquisición* y *Participación*.

| Métrica | Valor del periodo | Periodo anterior | Variación |
|---|---|---|---|
| Usuarios | | | |
| Sesiones | | | |
| Sesiones con interacción (%) | | | |
| Duración media de la interacción | | | |
| Páginas vistas | | | |

### Canales de adquisición

| Canal | Sesiones | % | Conversiones (`purchase`) |
|---|---|---|---|
| Búsqueda orgánica (Organic Search) | | | |
| Directo (Direct) | | | |
| Redes sociales (Organic Social) | | | |
| Búsqueda pagada (Paid Search) | | | |
| Referencias (Referral) | | | |

### Páginas más visitadas

| Página | Vistas | Tiempo medio |
|---|---|---|
| | | |
| | | |
| | | |

## 3. Comercio electrónico (embudo de compra)

**Dónde obtenerlo:** GA4 → *Informes* → *Monetización* → *Compras de comercio electrónico*, o *Explorar* →
*Exploración de embudo* con los pasos `view_item` → `add_to_cart` → `begin_checkout` → `purchase`.

| Paso | Eventos | Tasa respecto al paso anterior |
|---|---|---|
| `view_item` (vio un producto) | | — |
| `add_to_cart` (agregó al carrito) | | |
| `begin_checkout` (inició el pago) | | |
| `purchase` (compró) | | |

| Métrica | Valor |
|---|---|
| Ingresos | |
| Pedidos | |
| Ticket promedio | |
| Producto más vendido | |
| Leads (`generate_lead`: boletín y mesa de ayuda) | |
| Clics a WhatsApp (`whatsapp_click`) | |

## 4. Posicionamiento orgánico (Google Search Console)

**Dónde obtenerlo:** Search Console → *Rendimiento* → *Resultados de búsqueda*; *Indexación* → *Páginas*;
*Sitemaps*.

| Métrica | Valor |
|---|---|
| Clics totales | |
| Impresiones totales | |
| CTR medio | |
| Posición media | |
| Páginas indexadas / no indexadas | |
| Estado del sitemap | |

### Consultas principales

| Consulta | Clics | Impresiones | CTR | Posición |
|---|---|---|---|---|
| | | | | |
| | | | | |

## 5. Rendimiento y operación (métricas DevOps)

**Dónde obtenerlo:** página `/estado/`, resumen de la ejecución de *Monitoreo del sitio* en GitHub Actions,
evento `web_vitals` en GA4 y el informe de Lighthouse del workflow de CI.

| Métrica | Valor | Objetivo | ¿Cumple? |
|---|---|---|---|
| Disponibilidad | | ≥ 99.5 % | |
| Tiempo de respuesta promedio | | < 800 ms | |
| Tasa de errores HTTP | | < 1 % | |
| LCP (Web Vitals) | | ≤ 2.5 s | |
| CLS | | ≤ 0.1 | |
| Lighthouse: rendimiento / accesibilidad / SEO | | ≥ 85 / 90 / 90 | |
| Despliegues en el periodo | | — | |
| Despliegues fallidos (tasa de fallos de cambio) | | < 15 % | |

## 6. Mesa de ayuda (ITIL)

| Métrica | Valor |
|---|---|
| Tickets recibidos (incidentes / solicitudes / consultas) | |
| % resueltos dentro del SLA | |
| Tiempo medio de primera respuesta | |
| Categoría más frecuente | |
| Problemas abiertos (incidentes repetidos) | |

## 7. Campaña SEM (si se activó)

| Campaña | Inversión | Impresiones | Clics | CTR | CPC medio | Conversiones | CPA | ROAS |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

## 8. Hallazgos y propuestas de mejora

| # | Hallazgo (dato) | Mejora propuesta | Prioridad | Responsable | Fecha | Issue |
|---|---|---|---|---|---|---|
| 1 | *Ej.: el 60 % abandona en `begin_checkout`* | *Ej.: agregar pago con Mercado Pago real y reducir campos del formulario* | Alta | | | #__ |
| 2 | | | | | | |
| 3 | | | | | | |

**Ideas para revisar en cada iteración:**

- Consultas con muchas impresiones y CTR bajo → reescribir el `title` y la `description` de esa página.
- Productos con muchas vistas y pocas compras → mejorar fotos, precio o descripción.
- Páginas con LCP alto → optimizar la imagen principal.
- Tickets repetidos → abrir un problema y corregir la causa raíz.
- Palabras clave de Search Console que no tienen página → escribir una entrada de blog.

## 9. Metas para el siguiente periodo

| KPI | Actual | Meta |
|---|---|---|
| | | |
