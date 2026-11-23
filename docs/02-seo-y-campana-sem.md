# Estrategia SEO y campaña SEM simulada

**Negocio:** Eke, Comida Tradicional Huasteca (Huejutla de Reyes, Hidalgo)
**Objetivo de marketing:** aumentar los pedidos en línea de enchiladas y paquetes en Huejutla, y las ventas
nacionales de Salsa Huasteca.

---

## Parte 1. SEO (posicionamiento orgánico)

### 1.1 Investigación de palabras clave

> El volumen y la dificultad se deben validar con **Google Keyword Planner** y **Google Trends** al
> publicar. La columna "Intención" orienta qué página debe posicionarse.

| Palabra clave | Intención | Página objetivo |
|---|---|---|
| enchiladas de huejutla | Informativa / transaccional | `/` y `/producto/enchiladas-de-huejutla-orden-tradicional/` |
| enchiladas huastecas | Informativa | `/blog/que-son-las-enchiladas-de-huejutla/` |
| comida huasteca a domicilio huejutla | Transaccional local | `/menu/` |
| enchiladas con cecina | Transaccional | `/producto/enchiladas-con-cecina/` |
| paquete de enchiladas para fiesta | Transaccional | `/menu/paquetes/` |
| salsa huasteca | Transaccional nacional | `/menu/salsas-y-complementos/` |
| comprar salsa huasteca en línea | Transaccional nacional | `/producto/salsa-huasteca-eke-250-ml/` |
| cómo recalentar enchiladas | Informativa (atracción) | `/blog/como-conservar-y-recalentar-enchiladas/` |
| recetas con salsa de chile seco | Informativa (atracción) | `/blog/salsa-huasteca-5-formas-de-usarla/` |
| historia enchiladas huejutla | Informativa | `/tradicion-de-huejutla/` |

### 1.2 SEO on-page implementado

| Elemento | Implementación |
|---|---|
| `<title>` | Único por página, con la palabra clave al inicio y la marca al final (≤ 70 caracteres, validado en CI) |
| `<meta description>` | Única, de 50 a 170 caracteres, con llamada a la acción |
| Encabezados | Un solo `H1` por página con la palabra clave; `H2` para secciones y `H3` para tarjetas, sin saltos (validado en CI) |
| URLs amigables | Minúsculas, guiones y sin parámetros: `/menu/paquetes/`, `/producto/enchiladas-con-cecina/` |
| Canonical | `<link rel="canonical">` absoluto en todas las páginas |
| Breadcrumbs | Visibles y con `BreadcrumbList` |
| Datos estructurados | `Restaurant`, `Product/Offer`, `ItemList`, `BlogPosting`, `FAQPage`, `VideoObject`, `WebSite/SearchAction` |
| Redes sociales | Open Graph y Twitter Card con imagen de 1200×630 |
| Enlazado interno | Menú, categorías, productos relacionados y enlaces desde el blog a los productos |
| Idioma y región | `lang="es-MX"`, `og:locale = es_MX` |
| Páginas sin valor de búsqueda | Carrito, pago, cuenta y favoritos con `noindex` y fuera del sitemap |

### 1.3 Indexación

- **robots.txt**: permite todo el sitio, bloquea las páginas transaccionales y declara el sitemap.
- **sitemap.xml**: se genera en cada build con `lastmod`, `changefreq`, `priority` y la extensión
  `image:image` (sitemap de imágenes). Las URLs se ordenan por prioridad.
- Se envía en Google Search Console → *Sitemaps* (ver la guía de publicación).

### 1.4 SEO de imágenes y video

- Formato **WebP** (de 1.2 MB a 155 KB en total, un 87 % menos), con variante de 640 px para móviles.
- Nombres de archivo descriptivos: `enchiladas-con-cecina-huasteca.webp`.
- `alt` descriptivo y `title` en el 100 % de las imágenes (validado en CI).
- `width` y `height` explícitos y carga diferida (`loading="lazy"`).
- Video promocional narrado (68 s, 2.8 MB, H.264 con `faststart`) generado con `scripts/make_video.py`:
  miniatura de vista previa (`poster`), `preload="none"` para no afectar la carga, subtítulos en español
  (`.vtt`, accesibilidad y SEO), `figcaption` y schema `VideoObject` (`name`, `description`,
  `thumbnailUrl`, `uploadDate`, `duration`, `contentUrl`). También se puede usar YouTube configurando
  `video.youtube_id`.

### 1.5 SEO local (recomendado)

1. Crear el **Perfil de Negocio de Google** con categoría "Restaurante mexicano" y el enlace al sitio.
2. Usar los mismos nombre, dirección y teléfono (NAP) que en el sitio y en las redes.
3. Pedir reseñas reales a los clientes después de la entrega.

---

## Parte 2. Campaña SEM simulada (Google Ads)

### 2.1 Objetivos y KPIs

| Objetivo | KPI | Meta del primer mes |
|---|---|---|
| Ventas en línea | Conversiones (evento `purchase` importado desde GA4) | 40 pedidos |
| Rentabilidad | ROAS (ingresos ÷ inversión) | ≥ 3.0 |
| Costo por adquisición | CPA | ≤ $75 MXN |
| Calidad del tráfico | CTR de búsqueda | ≥ 5 % |
| Conocimiento de marca | Impresiones en Display/YouTube | 60,000 |

**Presupuesto mensual simulado:** $3,000 MXN (aproximadamente $100 MXN diarios).

### 2.2 Estructura de la cuenta

```
Cuenta: Eke Comida Huasteca
├── Campaña 1: Búsqueda · Huejutla local (CPC)               $1,200 / mes
│   ├── Grupo 1.1: Enchiladas a domicilio
│   ├── Grupo 1.2: Paquetes y eventos
│   └── Grupo 1.3: Marca (Eke)
├── Campaña 2: Búsqueda · Salsa nacional (CPC)               $900 / mes
│   └── Grupo 2.1: Salsa huasteca en línea
├── Campaña 3: Display + YouTube · Remarketing (CPM)         $600 / mes
│   ├── Grupo 3.1: Abandonaron el carrito
│   └── Grupo 3.2: Visitaron productos sin comprar
└── Campaña 4: Performance Max · Shopping (objetivo de ROAS) $300 / mes (prueba)
```

### 2.3 Palabras clave por grupo

| Grupo | Palabras clave (concordancia) | Página de destino |
|---|---|---|
| 1.1 Enchiladas a domicilio | [enchiladas a domicilio huejutla], "enchiladas huejutla", "comida huasteca a domicilio", +enchiladas +cecina +huejutla | `/menu/enchiladas/` |
| 1.2 Paquetes y eventos | "paquete de enchiladas", "comida para fiesta huejutla", "enchiladas para eventos" | `/menu/paquetes/` |
| 1.3 Marca | [eke huejutla], [eke enchiladas], "eke comida huasteca" | `/` |
| 2.1 Salsa nacional | "salsa huasteca", "comprar salsa huasteca", "salsa de chile seco en frasco", "salsa para enchiladas" | `/menu/salsas-y-complementos/` |

**Palabras clave negativas (nivel cuenta):** receta, gratis, empleo, vacante, pdf, video, cómo hacer, ingredientes,
"enchiladas suizas", "enchiladas verdes", "enchiladas potosinas".

### 2.4 Anuncios de búsqueda adaptables (RSA)

**Grupo 1.1 · Enchiladas a domicilio** → `https://<sitio>/menu/enchiladas/?utm_source=google&utm_medium=cpc&utm_campaign=busqueda_local&utm_content=enchiladas`

| Títulos (≤ 30 caracteres) | Descripciones (≤ 90 caracteres) |
|---|---|
| Enchiladas de Huejutla | Receta tradicional huasteca con salsa de chile seco y queso fresco. ¡Pide hoy! |
| Pide en Línea · Eke | Entrega a domicilio en Huejutla o recoge en tienda. Paga con tarjeta o PayPal. |
| Enchiladas con Cecina | Hechas el mismo día con ingredientes de la región. Ordena en minutos. |
| Entrega en Huejutla | |
| Hechas el Mismo Día | |
| Desde $95 MXN | |

**Grupo 2.1 · Salsa nacional** → `/menu/salsas-y-complementos/?utm_source=google&utm_medium=cpc&utm_campaign=salsa_nacional`

| Títulos | Descripciones |
|---|---|
| Salsa Huasteca Artesanal | Salsa de chile seco tostado en comal, sin conservadores artificiales. |
| Envíos a Todo México | Lleva el sabor de Huejutla a tu cocina. Envío gratis desde $800 MXN. |
| Salsa Eke desde $65 | |
| Ideal Para Enchiladas | |

**Extensiones (recursos):** enlaces de sitio (Paquetes, Salsas, Tradición de Huejutla, Ayuda), textos
destacados ("Hecho el mismo día", "Pago seguro", "Envío nacional"), llamada (teléfono), ubicación
(Perfil de Negocio) y precios por producto.

### 2.5 Segmentación por audiencia

| Campaña | Ubicación | Audiencia | Horario y dispositivo |
|---|---|---|---|
| Búsqueda local | Huejutla de Reyes + 15 km | Personas que están en la zona o la visitan con frecuencia | 7:00 a 15:00 h (horario de cocina); +20 % de puja en móvil |
| Salsa nacional | México (+15 % de puja en CDMX, Edo. Méx., Monterrey y Pachuca, donde vive la diáspora huasteca) | Segmentos en el mercado: "Alimentos gourmet"; afinidad: "Amantes de la cocina" | Todo el día |
| Remarketing | México | Listas de GA4: `add_to_cart` sin `purchase` (7 días); `view_item` sin `add_to_cart` (14 días) | Límite de frecuencia: 3 impresiones al día |

Datos demográficos de referencia: personas de 25 a 54 años, de todos los géneros, con interés en comida
mexicana tradicional y personas originarias de la Huasteca que viven fuera.

### 2.6 Modelos de pricing y estrategia de puja

| Modelo | Dónde se usa | Por qué |
|---|---|---|
| **CPC** (costo por clic) con *Maximizar clics* y CPC máximo de $6 MXN durante las primeras 2 semanas | Búsqueda | Junta datos de conversión con el costo controlado |
| **CPA objetivo** de $75 MXN (a partir de 30 conversiones) | Búsqueda | Optimiza hacia el pedido |
| **CPM** (costo por mil impresiones) visible, de $25 a $40 MXN | Display y YouTube (remarketing) | El objetivo es la recordación de marca; se paga por exposición |
| **ROAS objetivo** del 300 % | Performance Max | Toma en cuenta el valor del carrito |

### 2.7 Proyección simulada del embudo (primer mes)

> Supuestos para la simulación. Se ajustan con los datos reales de Google Ads y GA4.

| Campaña | Inversión | CPC / CPM | Clics | CTR | Tasa de conversión | Pedidos | Ticket promedio | Ingresos | ROAS |
|---|---|---|---|---|---|---|---|---|---|
| Búsqueda local | $1,200 | $4.00 CPC | 300 | 6 % | 8 % | 24 | $220 | $5,280 | 4.4 |
| Salsa nacional | $900 | $5.00 CPC | 180 | 4 % | 4 % | 7 | $330 | $2,310 | 2.6 |
| Remarketing | $600 | $30 CPM (20,000 impresiones) | 120 | 0.6 % | 6 % | 7 | $250 | $1,750 | 2.9 |
| Performance Max | $300 | — | 60 | — | 3 % | 2 | $300 | $600 | 2.0 |
| **Total** | **$3,000** | | **660** | | | **40** | | **$9,940** | **3.3** |

CPA estimado: $3,000 ÷ 40 = **$75 MXN**.

### 2.8 Medición de conversiones

1. GA4 registra `purchase` (con `transaction_id`, valor e ítems), `begin_checkout`, `add_to_cart`, `generate_lead` y `whatsapp_click`.
2. En GA4 se marcan como **eventos clave**: `purchase`, `generate_lead` y `whatsapp_click`.
3. Se vincula Google Ads con GA4 y se importan las conversiones.
4. Todas las URLs de los anuncios llevan parámetros UTM para analizarlos en *Adquisición de tráfico*.

### 2.9 Otros canales de atracción

- **Email marketing:** formulario de boletín en la página de inicio (evento `generate_lead`). Envío mensual con Mailchimp o Brevo (plan gratuito) y segmentos por "compró salsa" o "compró enchiladas".
- **Redes sociales:** botones para compartir en productos y blog; anuncios en Meta con un público similar a los compradores.
- **WhatsApp Business:** catálogo y botón de pedido directo desde la tienda.
