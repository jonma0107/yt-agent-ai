# SKILL.md

## Plantilla y reglas para documentación en proyectos

Esta skill estandariza la documentación de cualquier proyecto.
Produce dos artefactos con el mismo contenido:

1. **HTML diseñado → PDF fiel**: con los colores, el orden y la
   tipografía del estándar HTML incluido en esta skill, convertido a PDF
   ejecutando el comando de Chrome headless directamente en la terminal
   (sin crear archivos `.sh`).
2. **Markdown → PDF simple**: archivo `.md` convertido a PDF ejecutando
   el comando de pandoc directamente en la terminal (sin crear archivos `.sh`).

> Regla operativa: el agente NUNCA crea scripts `.sh` para las
> conversiones. Ejecuta los comandos de esta skill tal cual en la
> terminal, adaptando solo nombres de archivo y carpeta.

### 1. Verificar herramientas

Antes de documentar, verifica que las herramientas estén instaladas. Si falta alguna, instálala:

```bash
which pandoc google-chrome xelatex
fc-list | grep -i "dejavu"
sudo apt-get install pandoc texlive-xetex
```

- PDF diseñado → requiere `google-chrome` (preserva colores y tipografías; pandoc no reproduce ese diseño).
- PDF pandoc → requiere `texlive-xetex` y fuentes DejaVu.

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

### 5. Convertir Markdown a PDF (comando directo, sin .sh)

Ejecuta en la terminal, adaptando nombres de archivo y carpeta:

```bash
cd docs && pandoc PROYECTO_STATE.md -o PROYECTO_STATE.pdf --pdf-engine=xelatex -V colorlinks=true -V linkcolor=blue -V urlcolor=blue -V toccolor=black --highlight-style=tango --toc --toc-depth=3 -V papersize=a3 -V fontsize=11pt -V mainfont="DejaVu Sans" -V monofont="DejaVu Sans Mono"
```

> Reemplaza `docs`, `PROYECTO_STATE.md` y `PROYECTO_STATE.pdf` por tu carpeta y archivos.

### 6. Convertir HTML diseñado a PDF (comando directo, sin .sh)

Ejecuta en la terminal, adaptando nombres de archivo y carpeta. Chrome headless preserva colores, orden y tipografías (sin headers/footers):

```bash
cd docs && google-chrome --headless --disable-gpu --no-sandbox --print-to-pdf="docs.pdf" --print-to-pdf-no-header "file://$(pwd)/docs.html"
```

> Reemplaza `docs`, `docs.html` y `docs.pdf` por tu carpeta y archivos.

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

Todo HTML nuevo debe copiar el `<head>` (fuentes) y el `<style>` íntegro de abajo como base, y componer el `<body>` en el orden indicado en la sección C.

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
con adorno `::after` en naranja al `0.22` de opacidad (cuadrado de
120px rotado 18deg en la esquina superior derecha).
Barra superior: gradiente horizontal en tercios azul, verde y naranja.
Píldoras HTTP: `200` verde, `201` azul, `400` naranja, `401` rojo, `405` gris.

### C. `<style>` base completo (copiar íntegro, no omitir nada)

```css
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: "Source Sans 3", "Segoe UI", sans-serif;
  font-size: 17px;
  line-height: 1.55;
}
.brand-bar {
  height: 6px;
  background: linear-gradient(
    90deg,
    var(--blue) 0 33.3%,
    var(--green) 33.3% 66.6%,
    var(--orange) 66.6% 100%
  );
}
.masthead {
  background: #fff;
  padding: 18px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  border-bottom: 1px solid var(--line);
}
.masthead img {
  height: 52px;
  width: auto;
  display: block;
}
.masthead .meta {
  color: var(--muted);
  font-size: 13px;
  text-align: right;
}
.masthead strong { color: var(--ink); font-weight: 600; }
.shell {
  display: grid;
  grid-template-columns: 220px minmax(0, 880px);
  gap: 0 40px;
  max-width: 1120px;
  margin: 0 auto;
  padding: 0 20px 72px;
}
nav {
  position: sticky;
  top: 0;
  height: 100vh;
  padding: 32px 16px 24px 0;
  overflow: auto;
  border-right: 1px solid var(--line);
}
.brand {
  font-family: Fraunces, Georgia, serif;
  font-size: 18px;
  color: var(--ink);
  margin-bottom: 4px;
}
.brand em { color: var(--blue); font-style: normal; }
nav .sub {
  margin: 0 0 24px;
  color: var(--muted);
  font-size: 13px;
}
nav a {
  display: block;
  color: var(--muted);
  text-decoration: none;
  font-size: 14px;
  padding: 6px 0 6px 12px;
  border-left: 2px solid transparent;
}
nav a:hover { color: var(--navy); }
nav a.active {
  color: var(--blue-dark);
  font-weight: 600;
  border-left-color: var(--blue);
}
main { padding-top: 32px; min-width: 0; }
.hero {
  background: linear-gradient(145deg, #353b4e 0%, #1f6fad 58%, #3ab37e 100%);
  color: #fff;
  border-radius: 18px;
  padding: 34px 36px 30px;
  margin-bottom: 8px;
  position: relative;
  overflow: hidden;
}
.hero::after {
  content: "";
  position: absolute;
  right: -12px;
  top: -12px;
  width: 120px;
  height: 120px;
  background: var(--orange);
  opacity: 0.22;
  border-radius: 28px;
  transform: rotate(18deg);
}
.kicker {
  margin: 0 0 8px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 11px;
  color: #dbeafe;
}
.hero h1 {
  font-family: Fraunces, Georgia, serif;
  font-size: 38px;
  font-weight: 500;
  letter-spacing: -0.03em;
  margin: 0 0 10px;
}
.hero p { margin: 0; color: #e0e7ff; max-width: 40em; position: relative; z-index: 1; }
.hero h1 { position: relative; z-index: 1; }
.pills { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 20px; position: relative; z-index: 1; }
.pill {
  font-size: 12px;
  font-weight: 600;
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.16);
  color: #fff;
}
.pill.prod {
  background: var(--orange);
  color: #1c1917;
}
h2 {
  font-family: Fraunces, Georgia, serif;
  font-weight: 500;
  font-size: 26px;
  color: var(--blue-dark);
  margin: 44px 0 12px;
}
h3 { font-size: 17px; margin: 26px 0 8px; color: var(--blue-dark); }
p { margin: 0 0 12px; }
p code, td code, li code {
  font-family: "Source Code Pro", ui-monospace, monospace;
  font-size: 0.86em;
  background: #eef2ff;
  padding: 1px 6px;
  border-radius: 5px;
}
.callout {
  border-radius: 12px;
  padding: 13px 16px;
  margin: 14px 0 18px;
  font-size: 15px;
}
.callout .lbl {
  display: block;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 4px;
}
.c-sage { background: var(--sage); color: #14532d; }
.c-warn { background: var(--warn-bg); color: #9a3412; }
.c-ok { background: var(--ok-bg); color: #14532d; }
.c-info { background: #dbeafe; color: #1e3a8a; }
.steps { display: grid; gap: 10px; margin: 16px 0 8px; }
.step {
  display: grid;
  grid-template-columns: 36px 1fr;
  gap: 12px;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 14px;
}
.n {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--blue);
  color: #fff;
  display: grid;
  place-items: center;
  font-weight: 700;
}
.step:nth-child(2) .n { background: var(--green); }
.step:nth-child(3) .n { background: var(--orange); }
.step h4 { margin: 0 0 2px; font-size: 16px; }
.step p { margin: 0; color: var(--muted); font-size: 15px; }
table {
  width: 100%;
  border-collapse: collapse;
  background: var(--card);
  border-radius: 12px;
  overflow: hidden;
  font-size: 15px;
  margin: 10px 0 20px;
}
th, td { text-align: left; padding: 9px 14px; border-bottom: 1px solid var(--line); }
th { background: var(--blue-dark); color: #fff; font-size: 13px; }
.code {
  position: relative;
  background: #0f172a;
  color: #e7efe9;
  border-radius: 12px;
  padding: 16px 16px 14px;
  overflow: auto;
  margin: 8px 0 18px;
  font-family: "Source Code Pro", ui-monospace, monospace;
  font-size: 13.5px;
  line-height: 1.5;
}
.code .lbl {
  position: absolute;
  top: 8px;
  right: 12px;
  font-family: "Source Sans 3", sans-serif;
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #9bb8b0;
}
pre { margin: 0; white-space: pre-wrap; }
.k { color: #8ec8f0; }
.s { color: #e6c07b; }
.http {
  display: inline-block;
  font-family: "Source Code Pro", monospace;
  font-weight: 700;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 999px;
}
.h200 { background: var(--ok-bg); color: var(--ok); }
.h201 { background: #dbeafe; color: var(--blue-dark); }
.h400 { background: var(--warn-bg); color: var(--warn); }
.h401 { background: var(--err-bg); color: var(--err); }
.h405 { background: #ececec; color: #444; }
.endpoint {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 14px 16px;
  margin: 10px 0 16px;
  font-family: "Source Code Pro", monospace;
  font-size: 14px;
  overflow-x: auto;
}
.verb {
  background: var(--teal);
  color: #fff;
  font-weight: 700;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 6px;
}
.groups { display: grid; gap: 12px; margin: 10px 0 8px; }
.group {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 12px 14px;
}
.group h4 {
  margin: 0 0 8px;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--blue-dark);
}
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 3px 8px;
  font-family: "Source Code Pro", monospace;
  font-size: 12px;
}
.tabs { display: flex; gap: 6px; margin: 8px 0 0; }
.tab {
  border: 1px solid var(--line);
  background: transparent;
  padding: 6px 12px;
  border-radius: 999px;
  cursor: pointer;
  font: inherit;
  font-size: 14px;
  color: var(--muted);
}
.tab[aria-selected="true"] {
  background: var(--blue);
  color: #fff;
  border-color: var(--blue);
}
.panel[hidden] { display: none; }
.err {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 14px;
  margin: 0 0 12px;
  overflow: hidden;
}
.err header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px 4px;
  font-weight: 600;
}
.err .code { margin: 8px 14px 14px; }
.checklist {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 4px 6px;
}
.checklist ol { margin: 0; padding: 0; }
.checklist li {
  list-style: none;
  padding: 10px 10px 10px 36px;
  position: relative;
  border-bottom: 1px solid var(--line);
}
.checklist li:last-child { border-bottom: 0; }
.checklist li::before {
  content: "";
  position: absolute;
  left: 10px;
  top: 14px;
  width: 15px;
  height: 15px;
  border-radius: 4px;
  border: 2px solid var(--green);
}
footer {
  margin-top: 40px;
  padding-top: 16px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 14px;
}
@media (max-width: 840px) {
  .shell { grid-template-columns: 1fr; }
  nav {
    position: relative;
    height: auto;
    border: 0;
    border-bottom: 1px solid var(--line);
  }
  .hero h1 { font-size: 30px; }
}
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

### E. Orden del `<body>` (no cambiar)

1. `.brand-bar` (barra tricolor de 6px).
2. `header.masthead` (logo `<img>` + `.meta` con título y URL base).
3. `.shell` → `nav` (marca, subtítulo, enlaces con `class="active"`
   en el primero) + `main`.
4. `section.hero` con `id` (`.kicker`, `h1`, párrafo resumen, `.pills`
   con una `.pill.prod` destacada en naranja).
5. Secciones `h2` con `id`, con el `nav` enlazando a cada `id`.
6. Componentes según necesidad: `.callout` (`c-sage`/`c-warn`/`c-ok`/`c-info`
   con `.lbl`), `.steps` (`.step` + `.n` + `h4` + `p`), `table`
   (`th` en azul oscuro), `.code` (con `.lbl`: JSON/bash/headers y
   resaltado `.k`/`.s`), `.endpoint` (`.verb`), `.groups`
   (`.group > h4 + .chips > .chip`), `.tabs` + `.tab` + `.panel`,
   `.err` (header con píldora `.http` + `.code`), `.checklist` (`ol > li`).
7. `footer` (organización · producto · URL base · rama).
8. `<script>` con dos bloques: tabs (Postman/curl) y scroll-spy del nav:

```html
<script>
  document.querySelectorAll(".tabs").forEach((tabs) => {
    const buttons = [...tabs.querySelectorAll(".tab")];
    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        buttons.forEach((b) => b.setAttribute("aria-selected", "false"));
        btn.setAttribute("aria-selected", "true");
        buttons.forEach((b) => {
          const panel = document.getElementById(b.dataset.tab);
          if (panel) panel.hidden = b !== btn;
        });
      });
    });
  });
  const links = [...document.querySelectorAll("nav a")];
  const sections = links
    .map((a) => document.querySelector(a.getAttribute("href")))
    .filter(Boolean);
  document.addEventListener("scroll", () => {
    const y = window.scrollY + 90;
    let current = sections[0];
    for (const section of sections) {
      if (section.offsetTop <= y) current = section;
    }
    links.forEach((a) => {
      a.classList.toggle(
        "active",
        a.getAttribute("href") === "#" + current.id
      );
    });
  }, { passive: true });
</script>
```

### F. Variantes cliente vs interna

- **Versión para cliente**: la contraparte entrega las
  credenciales por canal seguro; NO incluir sección de registro.
- **Versión interna**: SÍ incluir la sección de registro
  (“Registrar el cliente — una sola vez”) con tabs Postman/curl,
  respuesta `201` y callout de provisión.

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
- Si mencionas el contenido de un video en la documentación, incluye su link en la sección correspondiente.

### 9. Ejemplo de sección FAQ

### \textcolor{blue}{Preguntas Frecuentes}

- **¿Cómo genero el PDF?**  
  Ejecuta en la terminal el comando pandoc de la sección 5 (Markdown → PDF)
  o el comando de Chrome de la sección 6 (HTML diseñado → PDF).
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

- [ ] El HTML copia el `<style>` base íntegro de esta skill e incluye el parche
  `.hero code` (códigos del hero legibles, sin pastillas blancas).
- [ ] El nav enlaza a todos los `id` de sección; scroll-spy activo.
- [ ] PDF diseñado generado (comando Chrome headless de la sección 6,
  ejecutado directo en terminal) y revisada la página 1.
- [ ] `.md` con YAML, títulos `\textcolor{blue}`, FAQ, componentes y
  diagramas donde aplique.
- [ ] PDF pandoc generado (comando pandoc de la sección 5, ejecutado
  directo en terminal) sin errores de LaTeX.
- [ ] Variante correcta: para cliente (sin registro) o interna (con registro).
