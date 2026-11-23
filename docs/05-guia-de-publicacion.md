# Guía de publicación paso a paso

Sigue estos pasos en orden. Tiempo estimado: 1 a 2 horas (más 2 a 3 días para que Search Console muestre datos).

---

## Paso 1. Reemplazar los datos de ejemplo

En `data/site.json` cambia todos los valores que dicen `TODO`:

- [ ] `phone`, `whatsapp` (formato `52` + 10 dígitos, sin espacios) y `email`
- [ ] `social`: URLs reales de Facebook, Instagram, TikTok y YouTube
- [ ] `webconference`: enlace fijo de Google Meet, de Zoom y de la agenda (Google Calendar → *Agenda de citas*)
- [ ] Opcional: `video.youtube_id` cuando subas el video del proceso de preparación

> Las fotos actuales se recortaron de la maqueta. Si tienes fotos reales, colócalas en `assets-src/` con el
> mismo nombre y ejecuta `python scripts/optimize_images.py`.

## Paso 2. Crear el repositorio en GitHub

1. Crea una cuenta en <https://github.com> (si no tienes).
2. Crea un repositorio **público** llamado exactamente **`TU-USUARIO.github.io`**.
   Con ese nombre el sitio queda en la raíz del dominio (`https://TU-USUARIO.github.io/`), que es donde Google
   busca `robots.txt`.
3. En la carpeta del proyecto (ya inicializada con Git), ejecuta:

```bash
git add .
git commit -m "feat: tienda en línea Eke"
git remote add origin https://github.com/TU-USUARIO/TU-USUARIO.github.io.git
git push -u origin main
git switch -c develop
git push -u origin develop
```

## Paso 3. Activar GitHub Pages y el pipeline

1. En el repositorio, ve a **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. Ve a **Settings → Secrets and variables → Actions → Variables → New repository variable**:
   `SITE_URL` = `https://TU-USUARIO.github.io` (la usa el monitoreo).
3. Ve a **Actions → CD - despliegue a producción → Run workflow**. Cuando termine en verde, el sitio
   estará en línea. Esa es la **URL de entrega**.
4. Ve a **Actions → Monitoreo del sitio → Run workflow** para registrar la primera medición.
5. Opcional, recomendado para la evaluación de ALM: **Settings → Branches → Add rule** para `main` y
   `develop`, con *Require a pull request before merging* y *Require status checks (build-test)*.

## Paso 4. Google Analytics 4

1. Entra a <https://analytics.google.com> → **Administrar → Crear → Propiedad** (zona horaria México, moneda MXN).
2. **Flujos de datos → Web**: escribe la URL del sitio y copia el **ID de medición** (`G-XXXXXXXXXX`).
3. Pégalo en `data/site.json` → `analytics.ga4_measurement_id`, haz commit y push (o un PR de `develop` a `main`).
4. Comprueba en GA4 → **Informes → Tiempo real** que aparece tu visita.
5. En **Administrar → Eventos**, marca como *evento clave*: `purchase`, `generate_lead` y `whatsapp_click`.
6. Haz una compra de prueba y verifica en **Monetización** que se registra.

## Paso 5. Google Search Console

1. Entra a <https://search.google.com/search-console> → **Agregar propiedad → Prefijo de la URL** → escribe la URL del sitio.
2. Elige el método **Etiqueta HTML**, copia solo el valor de `content="..."`.
3. Pégalo en `data/site.json` → `analytics.gsc_verification`, haz commit y push y espera a que termine el despliegue.
4. Regresa a Search Console y da clic en **Verificar**.
5. En **Sitemaps**, envía `sitemap.xml`.
6. En **Inspección de URLs**, inspecciona la página de inicio y da clic en **Solicitar indexación**.
7. Opcional: en GA4 → **Administrar → Vinculaciones de Search Console**, vincula ambas herramientas.

## Paso 6. Recibir pedidos y tickets por correo (Formspree)

1. Crea una cuenta gratuita en <https://formspree.io> y un formulario nuevo.
2. Copia el ID (la parte final de `https://formspree.io/f/XXXXXXX`).
3. Pégalo en `data/site.json` → `forms.formspree_id`, haz commit y push.
4. Haz una compra, un ticket y una suscripción de prueba y confirma que llegan a tu correo.

## Paso 7. Validaciones finales

- [ ] <https://pagespeed.web.dev> con la URL del sitio: captura las puntuaciones para el reporte.
- [ ] <https://search.google.com/test/rich-results> con una página de producto: debe detectar *Product* y *Breadcrumb*.
- [ ] <https://www.xml-sitemaps.com/validate-xml-sitemap.html> con `/sitemap.xml`.
- [ ] Abre `/robots.txt` y `/sitemap.xml` en el navegador.
- [ ] Prueba el sitio en un celular.

## Paso 8. Entregables

| Entregable | Qué entregar |
|---|---|
| URL de la plataforma | `https://TU-USUARIO.github.io` y el enlace al repositorio |
| Manual técnico y de configuración | `docs/01-manual-tecnico.md` y `docs/03-gestion-de-servicios-itil.md`, con capturas de Actions, ramas y `/estado/` |
| Reporte de analítica y campaña SEM | `docs/04-reporte-analitica-y-mejora-continua.md` lleno con datos reales, y `docs/02-seo-y-campana-sem.md` |

Para convertir un `.md` a PDF: ábrelo en VS Code y usa una extensión como *Markdown PDF*, o pégalo en
Google Docs.
