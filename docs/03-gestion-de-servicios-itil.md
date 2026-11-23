# Gestión de servicios de TI (ITIL 4)

Este documento describe cómo se diseña, opera y mejora la plataforma digital de Eke según las prácticas de ITIL.

---

## 1. Estrategia del servicio

**Propuesta de valor:** que cualquier persona en México pueda comprar comida tradicional de Huejutla en
menos de 3 minutos, con pago seguro y atención cercana.

| Objetivo de negocio | Servicio digital que lo habilita | Indicador |
|---|---|---|
| Vender más fuera del local | Tienda en línea y envío nacional | Ingresos en línea (`purchase` en GA4) |
| Fidelizar clientes | Cuentas, favoritos, boletín | Clientes recurrentes, suscriptores |
| Ser encontrados en Google | SEO y SEM | Clics orgánicos (Search Console), conversiones de Ads |
| Resolver problemas rápido | Mesa de ayuda con SLA | % de tickets resueltos dentro del SLA |

### Partes interesadas

| Rol | Responsabilidad |
|---|---|
| Dueña o dueño del servicio | Prioriza cambios y aprueba precios y promociones |
| Agente de mesa de ayuda (nivel 1) | Registra, clasifica y resuelve tickets frecuentes |
| Cocina y logística (nivel 2) | Resuelve incidentes de pedidos y entregas |
| Responsable técnico (nivel 2 TI) | Resuelve incidentes del sitio, despliegues y monitoreo |
| Proveedores externos | GitHub (hosting y CI/CD), Google (Analytics, Search Console), pasarelas de pago, paquetería |

## 2. Diseño del servicio: catálogo de servicios

Publicado en `/catalogo-de-servicios/`.

| Servicio | Descripción | Canal | Horario | Nivel de servicio (SLA) |
|---|---|---|---|---|
| Tienda en línea | Catálogo, carrito, pago y seguimiento | Sitio web | 24/7 | Disponibilidad ≥ 99.5 % mensual |
| Entrega local | Domicilio en Huejutla | Sitio, WhatsApp | 8:00 a 16:00 h | Entrega en ≤ 60 min |
| Envío nacional | Salsas y paquetes al vacío | Sitio | Lunes a viernes | Envío en ≤ 24 h hábiles |
| Pedidos para eventos | Más de 6 personas o empresas | Mesa de ayuda, videollamada | 8:00 a 16:00 h | Cotización en ≤ 4 h |
| Facturación | CFDI | Mesa de ayuda | Lunes a viernes | ≤ 48 h |
| Atención a incidentes | Problemas con pedidos, pagos o el sitio | Mesa de ayuda, WhatsApp, correo | 8:00 a 16:00 h | Según prioridad |
| Clases en línea | Talleres por videoconferencia | Meet / Zoom | Con cita | Confirmación en ≤ 24 h |
| Boletín | Promociones mensuales | Correo | Mensual | Baja inmediata |

### Gestión de la capacidad y la disponibilidad

- Hosting en CDN (GitHub Pages) sin servidor que administrar; escala automáticamente.
- Monitoreo cada 6 h con alerta por correo cuando falla (`monitor.yml`).
- Plan de continuidad: el código completo está en Git; ante una falla del proveedor el sitio se publica en
  Netlify o Cloudflare Pages con el mismo `dist/` en menos de 30 minutos. Pedidos de respaldo por WhatsApp.

## 3. Transición del servicio: gestión de cambios

| Tipo de cambio | Ejemplo | Aprobación | Proceso |
|---|---|---|---|
| Estándar | Cambiar un precio, publicar una entrada de blog | Preaprobado | Rama `feature/*` → PR → CI en verde → merge |
| Normal | Nueva función, cambio de diseño | Dueño del servicio en el PR | Issue "Solicitud de cambio" → PR a `develop` → revisión → `main` |
| Emergencia | Corregir una caída o un error de pago (P1) | Responsable técnico | Rama `hotfix/*` desde `main` → CI → despliegue → revisión posterior |

**Vuelta atrás (rollback):** `git revert <commit>` en `main`; el pipeline publica la versión anterior en
unos 2 minutos. Cada build se identifica con el SHA del commit (`/version.json`).

## 4. Operación del servicio: mesa de ayuda

Implementada en `/ayuda/` con seguimiento en `/seguimiento/`.

### 4.1 Tipos de ticket

| Tipo | Definición ITIL | Ejemplos |
|---|---|---|
| **Incidente** | Interrupción no planificada o reducción de la calidad de un servicio | Pedido incompleto, retraso, cobro duplicado, página con error |
| **Solicitud de servicio** | Petición de algo estándar que ya está en el catálogo | Factura, cambio de dirección, pedido para evento, cancelación |
| **Consulta** | Petición de información | Ingredientes, alérgenos, cobertura de envío |

### 4.2 Matriz de prioridad (impacto × urgencia)

| Impacto \ Urgencia | Alta | Media | Baja |
|---|---|---|---|
| **Alto** | P1 | P2 | P3 |
| **Medio** | P2 | P3 | P4 |
| **Bajo** | P3 | P4 | P4 |

| Prioridad | Primera respuesta | Resolución | Escalamiento |
|---|---|---|---|
| P1 Crítica | 1 h | 4 h | Inmediato al nivel 2 y a la dueña o dueño del servicio |
| P2 Alta | 2 h | 8 h | Al nivel 2 si no se resuelve en 4 h |
| P3 Media | 4 h | 24 h | Al nivel 2 si no se resuelve en 16 h |
| P4 Baja | 8 h | 48 h | Revisión semanal |

El formulario calcula la prioridad automáticamente y muestra el SLA al cliente antes de enviar.

### 4.3 Ciclo de vida del ticket

```
Registro ──> Clasificación ──> Diagnóstico ──> Resolución ──> Cierre
(folio TCK)  (tipo, categoría,  (nivel 1;       (solución o     (cliente confirma;
             prioridad, SLA)     escala a N2)    reposición)     causa raíz registrada)
```

1. **Registro:** el cliente envía el formulario y recibe un folio `TCK-#####`. El ticket llega por correo (Formspree) y se registra el evento `generate_lead` en GA4.
2. **Clasificación:** tipo, categoría (pedido, entrega, pago, facturación, sitio, otro), impacto, urgencia y prioridad.
3. **Diagnóstico y escalamiento:** nivel 1 (atención) → nivel 2 (cocina y logística, o TI).
4. **Resolución:** reposición, reembolso, corrección o respuesta.
5. **Cierre:** confirmación del cliente y registro de la causa.

### 4.4 Gestión de problemas

Cuando un mismo incidente se repite 3 o más veces en un mes (por ejemplo, "pedido llegó frío"), se abre un
**problema** con un issue en GitHub (`.github/ISSUE_TEMPLATE/incidente.yml`) para encontrar la causa raíz
y proponer un cambio permanente.

### 4.5 Gestión de eventos (monitoreo)

| Evento | Detección | Acción |
|---|---|---|
| Sitio no responde (HTTP 0 o 5xx) | `monitor.yml` | Correo automático de GitHub → incidente P1 |
| Respuesta lenta (> 2 s) | `monitor.py` marca "(lento)" | Revisar el tamaño de las imágenes y del CDN; P3 |
| Error de JavaScript | Evento `exception` en GA4 | Corregir en `hotfix/*` |
| Build o pruebas fallan | `ci.yml` / `deploy.yml` | No se publica; corregir antes del merge |

## 5. Mejora continua

Se aplica el modelo de mejora continua de ITIL en cada revisión mensual:

1. **¿Cuál es la visión?** Ser la marca de referencia de comida huasteca en línea.
2. **¿Dónde estamos?** Datos de GA4, Search Console, monitoreo y tickets.
3. **¿Dónde queremos estar?** Metas medibles para el siguiente mes.
4. **¿Cómo llegamos?** Lista priorizada de mejoras (issues "Solicitud de cambio").
5. **Tomar acción:** implementar con el flujo de cambios.
6. **¿Lo logramos?** Comparar los KPIs en el siguiente reporte.
7. **¿Cómo mantenemos el impulso?** Documentar los aprendizajes y repetir.

El formato del reporte está en [`04-reporte-analitica-y-mejora-continua.md`](04-reporte-analitica-y-mejora-continua.md).
