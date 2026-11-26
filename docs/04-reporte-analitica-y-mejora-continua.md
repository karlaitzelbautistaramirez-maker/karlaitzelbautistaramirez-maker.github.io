# Reporte de analítica y mejora continua

**Periodo:** 19 de noviembre al 26 de noviembre de 2026 (primera semana en línea)
**Elaboró:** ______________________
**Sitio:** <https://karlaitzelbautistaramirez-maker.github.io>

> **Fuentes:** Google Analytics 4 (propiedad "Tienda en línea Eke", ID `G-K92VQJNF97`), Google Search
> Console, PageSpeed Insights, el monitoreo programado (`monitoring/metrics.csv`) y el historial de GitHub
> Actions. Todas las cifras son reales y se tomaron de capturas del 26 de noviembre de 2026. Cuando un dato
> todavía no existe se indica "sin datos suficientes" y la fecha en que se volverá a medir.
>
> **Aviso:** es la primera semana del sitio. Casi todo el tráfico proviene del propio equipo y de pruebas
> funcionales. La compra registrada es una **compra de prueba**: no representa un ingreso real.

---

## 1. Resumen ejecutivo

En su primera semana la tienda recibió **27 usuarios activos** y **114 eventos** en GA4. Quedó indexada en
Google, con HTTPS válido y sin páginas excluidas. Obtuvo calificaciones de Lighthouse de **94 / 93 / 100 / 100**
en móvil y **99 / 97 / 100 / 100** en ordenador. Una compra de prueba completó el embudo
`view_item` → `purchase` y GA4 la registró como evento clave. El hallazgo principal fue un **incidente de
monitoreo**: durante 3 días todas las comprobaciones salieron como fallidas aunque el sitio funcionaba. Se
encontró la causa, se corrigió y se mejoró el script (ver sección 5.1). Para el siguiente periodo se propone
generar tráfico orgánico real con Facebook y el blog, y medir el embudo con visitantes que no sean del equipo.

## 2. Tráfico y comportamiento (Google Analytics 4)

**Dónde obtenerlo:** GA4 → *Informes* → *Adquisición* y *Participación*.

| Métrica | Valor del periodo | Periodo anterior | Variación |
|---|---|---|---|
| Usuarios activos (últimos 7 días, 19–25 nov) | 27 | No aplica (sitio nuevo) | — |
| Número de eventos (últimos 7 días) | 114 | No aplica | — |
| Eventos clave (últimos 7 días) | 0 (los eventos clave se configuraron el 26 nov) | No aplica | — |
| Usuarios activos en 30 minutos (tiempo real, 26 nov, durante la prueba) | 6 | — | — |
| Páginas vistas (tiempo real, 26 nov) | 16 `page_view` | — | — |
| Sesiones con interacción y duración media | Sin datos suficientes; se medirá el 3 dic 2026 en *Participación* | — | — |

El 22 de noviembre hubo un pico de unos 30 usuarios en el día: corresponde a la publicación del sitio y a
las primeras revisiones del equipo.

**Eventos registrados en tiempo real (26 nov 2026):**

| Evento | Cantidad |
|---|---|
| `page_view` | 16 |
| `web_vitals` | 10 |
| `user_engagement` | 9 |
| `scroll` | 5 |
| `first_visit` | 4 |
| `session_start` | 4 |
| `purchase` (evento clave) | 1 |

### Canales de adquisición

| Canal | Sesiones | % | Conversiones (`purchase`) |
|---|---|---|---|
| Directo (Direct) | 1 usuario en tiempo real | 100 % | 1 (prueba) |
| Búsqueda orgánica (Organic Search) | 0 | 0 % | 0 |
| Redes sociales (Organic Social) | 0 (Facebook se enlazó el 26 nov) | 0 % | 0 |
| Búsqueda pagada (Paid Search) | 0 (campaña solo simulada) | 0 % | 0 |
| Referencias (Referral) | 0 | 0 % | 0 |

### Páginas más visitadas (tiempo real, 26 nov 2026)

| Página | Vistas |
|---|---|
| Enchiladas de Huejutla en línea (inicio) | 4 |
| Carrito de compras | 3 |
| Menú: enchiladas de Huejutla | 3 |
| ¿Qué son las enchiladas de Huejutla? (blog) | 2 |
| Finalizar compra | 1 |
| Mesa de ayuda y preguntas frecuentes | 1 |

## 3. Comercio electrónico (embudo de compra)

**Dónde obtenerlo:** GA4 → *Informes* → *Monetización* → *Compras de comercio electrónico*, o *Explorar* →
*Exploración de embudo* con los pasos `view_item` → `add_to_cart` → `begin_checkout` → `purchase`.

Prueba funcional del 26 de noviembre de 2026, 2:28 p. m.: se agregó un producto al carrito, se completó el pago
y se generó el folio **EKE-20261126-1433** (1 × Paquete Pareja Eke, $260.00 MXN, recoger en tienda, tarjeta).
El pedido se consultó después en `/seguimiento/` con estado *Recibido*. GA4 lo registró como `purchase` y lo
agregó a la audiencia *Purchasers*.

| Paso | Eventos | Tasa respecto al paso anterior |
|---|---|---|
| `view_item` (vio un producto) | Sin datos suficientes en el periodo | — |
| `add_to_cart` (agregó al carrito) | Sin datos suficientes | — |
| `begin_checkout` (inició el pago) | Sin datos suficientes | — |
| `purchase` (compró) | 1 (prueba) | — |

El embudo completo se revisará el **3 de diciembre de 2026** en *Exploración de embudo*, cuando haya tráfico
de visitantes reales.

| Métrica | Valor |
|---|---|
| Ingresos | $0.00 MXN reales ($260.00 MXN de la compra de prueba) |
| Pedidos | 1 de prueba |
| Ticket promedio | No aplica (sin pedidos reales) |
| Producto más vendido | No aplica (sin pedidos reales) |
| Leads (`generate_lead`: boletín y mesa de ayuda) | Ticket de prueba enviado el 26 nov; conteo pendiente de confirmar en GA4 |
| Clics a WhatsApp (`whatsapp_click`) | Clic de prueba el 26 nov; conteo pendiente de confirmar en GA4 |

## 4. Posicionamiento orgánico (Google Search Console)

**Dónde obtenerlo:** Search Console → *Rendimiento* → *Resultados de búsqueda*; *Indexación* → *Páginas*;
*Sitemaps*.

| Métrica | Valor |
|---|---|
| Clics totales (22–24 nov) | 0 |
| Impresiones totales | Sin datos suficientes; se medirá el 3 dic 2026 |
| CTR medio | Sin datos suficientes |
| Posición media | Sin datos suficientes |
| Páginas indexadas / no indexadas | 1 indexada / 0 no indexadas |
| Estado del sitemap | Enviado (`/sitemap.xml`, 24 URL); indexación de la portada solicitada |
| Inspección de la portada | "La URL está en Google", página indexada, HTTPS válido |
| Videos indexados | 0 (el sitio todavía no publica video) |

### Consultas principales

| Consulta | Clics | Impresiones | CTR | Posición |
|---|---|---|---|---|
| Sin datos suficientes: Search Console tarda de 2 a 3 días en mostrar consultas. Se revisará el 3 dic 2026. | | | | |

## 5. Rendimiento y operación (métricas DevOps)

**Dónde obtenerlo:** página `/estado/`, resumen de la ejecución de *Monitoreo del sitio* en GitHub Actions,
evento `web_vitals` en GA4 y PageSpeed Insights.

| Métrica | Valor | Objetivo | ¿Cumple? |
|---|---|---|---|
| Disponibilidad (desde la corrección del 26 nov) | 100 % (6 de 6 comprobaciones) | ≥ 99.5 % | Sí |
| Tiempo de respuesta promedio | 124 ms (rango de 110 a 142 ms) | < 800 ms | Sí |
| Tasa de errores HTTP | 0 % | < 1 % | Sí |
| LCP / CLS de usuarios reales | Sin datos de campo ("No hay datos" en PageSpeed: el sitio aún no tiene tráfico suficiente) | ≤ 2.5 s / ≤ 0.1 | Se medirá con el evento `web_vitals` |
| Lighthouse móvil: rendimiento / accesibilidad / prácticas / SEO | **94 / 93 / 100 / 100** | ≥ 85 / 90 / — / 90 | Sí |
| Lighthouse ordenador: rendimiento / accesibilidad / prácticas / SEO | **99 / 97 / 100 / 100** | ≥ 85 / 90 / — / 90 | Sí |
| Despliegues en el periodo (CD a producción, 23–26 nov) | 16 | — | — |
| Despliegues fallidos (tasa de fallos de cambio) | 1 de 16 = 6.25 % | < 15 % | Sí |
| Ejecuciones de CI (build y pruebas) | 7 de 7 exitosas | — | — |

PageSpeed Insights, informe del 26 nov 2026 a las 14:59. "Navegación agéntica": 1/2 en móvil y 2/2 en ordenador.

### 5.1 Incidente: monitoreo con falsos negativos (resuelto)

| Campo | Detalle |
|---|---|
| Detección | 26 nov 2026, al revisar `monitoring/metrics.csv` para este reporte |
| Síntoma | Del 23 al 26 nov, las 7 ejecuciones programadas de *Monitoreo del sitio* fallaron. Las 42 comprobaciones registraron estado 0 (sin respuesta) en 0–9 ms, aunque el sitio respondía 200 a los visitantes. |
| Impacto | Ninguno para los clientes: el sitio siempre estuvo disponible. La métrica de disponibilidad mostraba 0 % por error. |
| Causa raíz | La variable `SITE_URL` de GitHub tenía un espacio o salto de línea invisible al final. Eso generaba URL inválidas antes de conectar. Se reprodujo de forma local con el mismo valor. |
| Solución | 1) Se volvió a capturar `SITE_URL` a mano. 2) `scripts/monitor.py` limpia los espacios de la variable e imprime el motivo cuando una URL no responde. 3) Se descartaron las 42 mediciones inválidas (commit `31b6420`). |
| Verificación | Ejecución manual #8 del 26 nov: 6 de 6 URL con estado 200 y promedio de 124 ms. |
| Lección aprendida | Validar la configuración del monitoreo justo después de crearla y no ocultar el motivo de los errores. |

## 6. Mesa de ayuda (ITIL)

| Métrica | Valor |
|---|---|
| Tickets recibidos (incidentes / solicitudes / consultas) | 1 ticket de prueba (26 nov) para validar el formulario de `/ayuda/` |
| % resueltos dentro del SLA | Sin tickets de clientes reales en el periodo |
| Tiempo medio de primera respuesta | Sin datos suficientes |
| Categoría más frecuente | Sin datos suficientes |
| Incidentes internos | 1: monitoreo con falsos negativos (sección 5.1), resuelto el mismo día en que se detectó |
| Problemas abiertos (incidentes repetidos) | 0 |

## 7. Campaña SEM (si se activó)

La campaña **no se activó**. Su diseño completo (anuncios, segmentación, presupuesto y CPC estimado) está en
[`02-seo-y-campana-sem.md`](02-seo-y-campana-sem.md) como campaña simulada.

| Campaña | Inversión | Impresiones | Clics | CTR | CPC medio | Conversiones | CPA | ROAS |
|---|---|---|---|---|---|---|---|---|
| Simulada (no activada) | $0 | — | — | — | — | — | — | — |

## 8. Hallazgos y propuestas de mejora

| # | Hallazgo (dato) | Mejora propuesta | Prioridad | Responsable | Fecha | Issue |
|---|---|---|---|---|---|---|
| 1 | El monitoreo registró 100 % de fallas falsas durante 3 días por una variable mal capturada | Hecho: limpieza de la variable, mensaje de error descriptivo y verificación manual después de cada cambio de configuración | Alta | Equipo Eke | 26 nov 2026 (resuelto) | — |
| 2 | 0 clics orgánicos y 0 tráfico social; todo el tráfico es directo | Publicar en Facebook (enlazado el 26 nov) con enlaces a productos y al blog; poner la URL de la tienda en el perfil de Facebook | Alta | Equipo Eke | 3 dic 2026 | — |
| 3 | Accesibilidad móvil de 93 frente a 97 en ordenador, y navegación agéntica de 1/2 en móvil | Revisar en PageSpeed los elementos señalados en móvil (contraste y tamaño de áreas táctiles) y corregirlos | Media | Equipo Eke | 3 dic 2026 | — |
| 4 | Search Console reporta 0 videos indexados | Subir un video corto del proceso a YouTube y configurar `video.youtube_id` en `data/site.json` | Baja | Equipo Eke | 10 dic 2026 | — |

**Ideas para revisar en cada iteración:**

- Consultas con muchas impresiones y CTR bajo → reescribir el `title` y la `description` de esa página.
- Productos con muchas vistas y pocas compras → mejorar fotos, precio o descripción.
- Páginas con LCP alto → optimizar la imagen principal.
- Tickets repetidos → abrir un problema y corregir la causa raíz.
- Palabras clave de Search Console que no tienen página → escribir una entrada de blog.

## 9. Metas para el siguiente periodo

| KPI | Actual | Meta (al 10 dic 2026) |
|---|---|---|
| Usuarios activos por semana | 27 | 50 |
| Clics orgánicos (Search Console) | 0 | Primeros 10 clics |
| Páginas indexadas | 1 | Al menos 15 de las 24 del sitemap |
| Pedidos reales (`purchase`) | 0 | Primeros 3 |
| Disponibilidad del monitoreo | 100 % desde el 26 nov | ≥ 99.5 % |
| Lighthouse móvil: accesibilidad | 93 | ≥ 95 |
