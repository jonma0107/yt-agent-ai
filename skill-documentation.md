# SKILL.md

## Plantilla y reglas para documentación en proyectos

Esta skill estandariza la documentación de cualquier proyecto.
Produce dos artefactos con el mismo contenido:

1. **HTML diseñado → PDF fiel**: con los colores, el orden y la
   tipografía del estándar HTML de esta carpeta (tomado de los
   archivos `docs-cliente.html` y `docs.html`), convertido a PDF con
   el script `.sh` incluido en esta skill.
2. **Markdown → PDF simple**: archivo `.md` convertido a PDF con el
   comando de pandoc de esta skill.

### 1. Verificar Pandoc

Antes de documentar, asegúrate de que Pandoc esté instalado globalmente. Si no lo está, instálalo:

```bash
sudo apt-get install pandoc
```

Para el PDF diseñado se requiere además `google-chrome`
(preserva colores y tipografías; pandoc no reproduce ese diseño).
Para el PDF pandoc se requiere `texlive-xetex`:

```bash
which pandoc google-chrome xelatex
fc-list | grep -i "dejavu"
sudo apt-get install texlive-xetex
```

### 2. Estructura inicial para toda documentación

Copia y adapta este bloque YAML al inicio de tu archivo .md:

---
title: "Título del Proyecto"
author: "Tu nombre o empresa"
date: "Año"
graphics: true
header-includes: |
  \usepackage{float}
  \usepackage{longtable}
  \usepackage{booktabs}
  \usepackage{array}
  \usepackage{makecell}
  \usepackage{fvextra}
  \DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,commandchars=\\\{\}}
  \renewcommand{\arraystretch}{1.4}
  \let\origfigure\figure
  \let\endorigfigure\endfigure
  \renewenvironment{figure}[1][2] {
    \expandafter\origfigure\expandafter[H]
  } {
    \endorigfigure
  }

geometry: "top=3cm,bottom=3cm,left=4cm,right=2cm"
lang: "es" # Esto ayuda a que los índices y fechas salgan en español
toc: true
toc-title: "Índice de Contenidos"  
---

### 3. Colores para títulos y subtítulos

Usa la siguiente sintaxis para títulos y subtítulos en Markdown:

```markdown
### \textcolor{blue}{TITULO}
### \textcolor{blue}{subtitulo}
```

### 4. Generar documentación

- Escribe la documentación en formato .md siguiendo la estructura y estilos anteriores.

### 5. Convertir a PDF

Utiliza el siguiente comando para convertir tu archivo Markdown a PDF:

```bash
pandoc README.md -o README.pdf --pdf-engine=xelatex -V colorlinks=true -V linkcolor=blue -V urlcolor=blue -V toccolor=black --highlight-style=tango --toc --toc-depth=3 -V papersize=a3 -V fontsize=11pt -V mainfont="DejaVu Sans" -V monofont="DejaVu Sans Mono"
```

> Reemplaza README.md por el nombre de tu archivo .md.

---

## Ejemplo de inicio de documentación

---
title: "Migración de DAS a AWS Fargate + ECS"
author: "TicSocial S. A. S."
date: "2026"
graphics: true
header-includes: |
  \usepackage{float}
  \usepackage{longtable}
  \usepackage{booktabs}
  \usepackage{array}
  \usepackage{makecell}
  \usepackage{fvextra}
  \DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,commandchars=\\\{\}}
  \renewcommand{\arraystretch}{1.4}
  \let\origfigure\figure
  \let\endorigfigure\endfigure
  \renewenvironment{figure}[1][2] {
    \expandafter\origfigure\expandafter[H]
  } {
    \endorigfigure
  }

geometry: "top=3cm,bottom=3cm,left=4cm,right=2cm"
lang: "es"
toc: true
toc-title: "Índice de Contenidos"  
---

### \textcolor{blue}{TITULO}

### \textcolor{blue}{subtitulo}

---

Este archivo SKILL.md puede copiarse y adaptarse en cualquier proyecto para estandarizar la documentación y su conversión a PDF.

---

## Estándar HTML diseñado (colores, orden y tipografía)

Los archivos `docs-cliente.html` (versión para cliente) y `docs.html`
(versión interna) definen el estándar. Todo HTML nuevo debe copiar su
`<style>` íntegro como base y componer el `<body>` en el orden
indicado abajo.

### A. Fuentes (no cambiar)

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Source+Sans+3:wght@400;600;700&family=Source+Code+Pro:wght@450;600&display=swap" rel="stylesheet" />
```

- Títulos y hero: `Fraunces, Georgia, serif`.
- Cuerpo: `"Source Sans 3", "Segoe UI", sans-serif`, `17px`, `1.55`.
- Código, chips, endpoints: `"Source Code Pro", ui-monospace, monospace`.

### B. Paleta exacta (`:root`, no cambiar valores)

```css
--blue: #3498db;
--blue-dark: #1f6fad;
--green: #3ab37e;
--orange: #f58d6d;
--ink: #353b4e;
--muted: #5c6578;
--line: #e4e7ec;
--paper: #f7f8fa;
--card: #ffffff;
--navy: #353b4e;
--teal: #3498db;
--sage: #e4f6ee;
--ok: #2f8f62;
--ok-bg: #e4f6ee;
--warn: #c05621;
--warn-bg: #ffeee8;
--err: #b91c1c;
--err-bg: #fee2e2;
--black: #0b0b0b;
```

Bloques de código: fondo `#0f172a`, texto `#e7efe9`, claves
`#8ec8f0`, strings `#e6c07b`, etiqueta `#9bb8b0`.
Hero: gradiente `145deg, #353b4e 0%, #1f6fad 58%, #3ab37e 100%`
con adorno `::after` en naranja al `0.22` de opacidad.
Barra superior: gradiente en tercios azul, verde y naranja.

### C. Componentes y orden del `<body>`

1. `.brand-bar` (barra tricolor de 6px).
2. `header.masthead` (logo + `.meta` con título y URL base).
3. `.shell` → `nav` (marca, subtítulo, enlaces con `class="active"`
   en el primero) + `main`.
4. `section.hero` (`.kicker`, `h1`, párrafo resumen, `.pills` con una
   `.pill.prod` destacada en naranja).
5. Secciones `h2` con `id`, con el `nav` enlazando a cada `id`.
6. Componentes según necesidad: `.callout` (`c-sage/c-warn/c-ok/c-info`
   con `.lbl`), `.steps` (`.step` + `.n`), `table` (`th` en azul
   oscuro), `.code` (con `.lbl`: JSON/bash/headers), `.endpoint`
   (`.verb`), `.groups` (`.group > h4 + .chips > .chip`), `.err`
   (header con código HTTP + `.code`), `.checklist` (`ol > li`).
7. `footer` (organización · producto · URL base · rama).
8. `<script>` de scroll-spy del nav (copiar de los HTML de referencia).

### D. Parche obligatorio: `code` dentro del hero

La regla global `p code { background: #eef2ff; }` pinta pastillas
claras ilegibles sobre el hero oscuro. Siempre agregar, con mayor
especificidad (gana a `p code`):

```css
.hero code {
  font-family: "Source Code Pro", ui-monospace, monospace;
  font-size: 0.86em;
  background: rgba(255, 255, 255, 0.16);
  color: #ffd9a3;
  padding: 1px 6px;
  border-radius: 5px;
}
.hero strong { color: #ffffff; }
```

### E. CSS de impresión (dentro del mismo `<style>`, no omitir)

```css
@media print {
  @page { size: A4; margin: 12mm 12mm 16mm; }
  body { background: #fff; }
  nav { display: none; }
  .shell { grid-template-columns: 1fr; padding: 16px 8px 0; max-width: none; }
  .masthead { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .brand-bar, .hero, .pill, .http, .n, th, .verb {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .hero { break-inside: avoid; }
  .callout, .step, .group, .err, table, .code { break-inside: avoid; }
  a { color: inherit; }
}
```

Sin `print-color-adjust: exact` el PDF sale en grises.

### F. Variantes cliente vs interna

- **Cliente** (`docs-cliente.html`): la contraparte entrega las
  credenciales por canal seguro; NO incluir sección de registro.
- **Interna** (`docs.html`): SÍ incluir la sección de registro
  (“Registrar el cliente — una sola vez”) con tabs Postman/curl,
  respuesta `201` y callout de provisión.

### G. Script HTML → PDF (dentro de la skill)

Archivo `html_to_pdf.sh` (ejecutable). Convierte el HTML diseñado a
PDF preservando colores, orden y tipografías:

```bash
#!/usr/bin/env bash
# HTML diseñado -> PDF fiel (Chrome headless, sin headers/footers).
# Uso: ./html_to_pdf.sh [archivo.html] [nombre_base_pdf]
set -euo pipefail
cd "$(dirname "$0")"

HTML="${1:-index.html}"
BASE="${2:-${HTML%.html}}"

if ! command -v google-chrome >/dev/null 2>&1; then
  echo "ERROR: se requiere google-chrome para preservar colores y tipografías." >&2
  exit 1
fi

google-chrome \
  --headless \
  --disable-gpu \
  --no-sandbox \
  --print-to-pdf="${BASE}.pdf" \
  --print-to-pdf-no-header \
  "file://$(pwd)/${HTML}"

echo "OK: ${BASE}.pdf"
```

Uso:

```bash
./html_to_pdf.sh index.html Mi-Guia
```

### H. Script Markdown → PDF (dentro de la skill)

Archivo `md_to_pdf.sh` (ejecutable, recibe el `.md` como argumento):

```bash
#!/usr/bin/env bash
# Markdown -> PDF simple (pandoc + xelatex) según esta skill.
# Uso: ./md_to_pdf.sh [archivo.md]
set -euo pipefail
cd "$(dirname "$0")"

MD="${1:-README.md}"
PDF="${MD%.md}-pandoc.pdf"

pandoc "$MD" -o "$PDF" \
  --pdf-engine=xelatex \
  -V colorlinks=true -V linkcolor=blue -V urlcolor=blue -V toccolor=black \
  --highlight-style=tango --toc --toc-depth=3 \
  -V papersize=a3 -V fontsize=11pt \
  -V mainfont="DejaVu Sans" -V monofont="DejaVu Sans Mono"

echo "OK: $PDF"
```

Uso:

```bash
./md_to_pdf.sh README.md
```

---

## Reglas y buenas prácticas adicionales para la documentación

### 1. Sección de Preguntas Frecuentes (FAQ)
Incluye siempre una sección de “Preguntas Frecuentes” al final de la documentación. Esto ayuda a resolver dudas comunes y mejora la experiencia de los usuarios y desarrolladores.

### 2. Gráficos y diagramas
- Utiliza diagramas de flujo, secuencia o arquitectura para explicar procesos complejos.
- Puedes usar arte ASCII, herramientas como Mermaid, o imágenes externas.
- Ejemplo de diagrama de flujo (ASCII):

```
┌─────────────┐
│  INICIO     │
└─────┬───────┘
      ▼
  [Proceso]
      ▼
┌─────────────┐
│   FIN       │
└─────────────┘
```

- Ejemplo de diagrama de secuencia:

```
┌─────────┐   ┌─────────┐
│ Cliente │   │ Backend │
└────┬────┘   └────┬────┘
     │             │
     │ 1. Acción   │
     │────────────>│
     │             │
     │ 2. Respuesta│
     │<────────────│
```

### 3. Saltos de línea tras subtítulos
Después de cada subtítulo (### \textcolor{blue}{...}), deja siempre un salto de línea antes del contenido. Esto mejora la legibilidad y el formato al convertir a PDF.

### 4. Tablas para resúmenes y comparativas
- Usa tablas **solo cuando las columnas sean cortas** (máx. 2-3 palabras por celda).
- Ejemplo de tabla adecuada:

| Archivo                       | Descripción                        | Tests |
|-------------------------------|------------------------------------|-------|
| `test_category_permission.py`  | Tests del modelo CategoryPermission| 5     |
| `test_support_files_view.py`   | Tests CRUD de archivos             | 11    |

### 5. Evitar superposición de texto en tablas

Cuando una tabla tiene columnas con textos largos (nombres de funciones, descripciones extensas, etc.), el texto se **superpone** en el PDF generado. Para evitarlo:

**Opción 1 — Convertir a listas (recomendado para textos largos):**

En lugar de:

```markdown
| Test | Descripción |
|------|-------------|
| `test_file_upload_saves_url_in_form_data` | Archivos subidos generan URLs |
```

Usar:

```markdown
- **`test_file_upload_saves_url_in_form_data`**:
  Archivos subidos generan URLs.
```

**Opción 2 — Acortar contenido:**

Si se necesita tabla, acortar los textos para que cada celda no supere ~40 caracteres.

**Opción 3 — Los paquetes LaTeX del header:**

Los paquetes `longtable`, `booktabs`, `array`, `makecell` y `\arraystretch{1.4}` ya están incluidos en la plantilla YAML de esta skill. Estos mejoran el soporte de tablas, pero **no resuelven completamente** la superposición en columnas muy anchas. Siempre prefiere la Opción 1 cuando el contenido es extenso.

> **Regla general:** Si una tabla tiene más de 2 columnas con textos largos, conviértela a lista.

### 6. Evitar desbordamiento de rutas o texto inline (código largo sin espacios)

Al documentar rutas extensas de directorios (e.g. `/home/user/.npm/...`) o variables largas dentro de listas, la compilación en PDF suele aglomerar el texto y desbordarlo fuera de los márgenes de la página por restricciones nativas de LaTeX o Markdown con código inline (` ` ).

**Para evitar que esto suceda:**
- No utilices comillas invertidas simples (backticks \` \`) para rutas muy largas.
- Usa siempre **bloques de código completos** estructurados con tres comillas simples (\`\`\`text).
- **Proactividad:** Divide siempre de forma manual (presionando `Enter`) la ruta dentro del bloque para asegurar que salte a la siguiente línea si consideras que excederá la mitad del tamaño visual del renglón impreso.  
*(Al aplicar `fvextra` y `breaklines` en la plantilla de encabezado, los bloques están protegidos para respetar dichos márgenes y tus saltos).*

### 7. Sección de componentes principales
Incluye una sección que resuma los principales módulos, scripts o componentes del proyecto, con una breve descripción de cada uno.

### 8. Buenas prácticas para gráficos
- Usa gráficos para explicar flujos de permisos, procesos de negocio, o arquitectura.
- Si el flujo es complejo, acompaña el gráfico con una breve explicación textual.

### 9. Ejemplo de sección FAQ

### 	extcolor{blue}{Preguntas Frecuentes}

- **¿Cómo genero el PDF?**  
  Usa el comando Pandoc especificado en la plantilla.
- **¿Qué hago si falta un permiso?**  
  Revisa la sección de componentes y verifica la configuración en Django.

### 10. Enlaces, imágenes y videos

Puedes incluir enlaces a recursos externos, imágenes o videos para enriquecer la documentación.

- Para imágenes, usa la sintaxis Markdown:

  ![Descripción de la imagen](https://url.de/imagen.jpg)

  Ejemplo:
  ![Configuración en Render](https://i.ibb.co/DnmdpTd/render.jpg)

- Para enlaces a videos o recursos:

  [Ver video explicativo](https://www.youtube.com/watch?v=video_id)

- Si mencionas un video en la solicitud o documentación, incluye el link en la sección correspondiente.

---

## Checklist de verificación (no entregar sin esto)

- [ ] El HTML copia el `<style>` de referencia e incluye el parche
  `.hero code` (códigos del hero legibles, sin pastillas blancas).
- [ ] El nav enlaza a todos los `id` de sección; scroll-spy activo.
- [ ] PDF diseñado generado (`./html_to_pdf.sh`) y revisada la página 1.
- [ ] `.md` con YAML, títulos `\textcolor{blue}`, FAQ, componentes y
  diagramas donde aplique.
- [ ] PDF pandoc generado (`./md_to_pdf.sh`) sin errores de LaTeX.
- [ ] Variante correcta: cliente (sin registro) o interna (con registro).
