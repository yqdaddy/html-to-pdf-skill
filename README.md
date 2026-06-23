# html-to-pdf-skill

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that converts HTML files to publication-quality PDFs using [Playwright](https://playwright.dev/python/) (headless Chromium).

> **What it does:** Renders HTML exactly as the browser does, then exports to PDF. Full CSS support including `@page`, flexbox, grid, web fonts, SVG, and background colors.

[中文文档](README_zh.md)

## Features

- **Pixel-perfect rendering** — headless Chromium, not wkhtmltopdf
- **Full CSS support** — `@page` rules, flexbox, grid, web fonts, `@media print`
- **JavaScript execution** — SPAs and dynamic content work out of the box
- **Batch conversion** — convert multiple HTML files in one command
- **PDF bookmarks** — auto-generate outline from `<h1>`–`<h6>` headings
- **Custom headers/footers** — with page numbers via `{{pageNumber}}` / `{{totalPages}}`
- **Configurable layout** — A4/Letter/Legal/A0-A6, portrait/landscape, custom margins
- **Accessibility** — optional tagged PDF output
- **No display server needed** — works headless on Linux CI/Docker

## Installation

### 1. Install dependencies

```bash
pip install playwright
playwright install chromium
```

On Linux, you may also need system libraries:
```bash
playwright install-deps chromium
```

### 2. Install the skill

Copy this skill to your Claude Code skills directory:

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/html-to-pdf-skill.git

# Copy to your skills directory
cp -r html-to-pdf-skill ~/.claude/skills/html-to-pdf
```

Or manually copy the folder to `~/.claude/skills/html-to-pdf/`.

After installation, Claude Code will automatically detect and use this skill when you ask to convert HTML to PDF.

## Usage

### As a Claude Code skill

Just ask Claude naturally:

```
"Convert this HTML to PDF"
"Export report.html as PDF"
"Print this page to PDF with A4 format"
```

Claude will invoke the skill automatically.

### Standalone (without Claude Code)

The script works independently:

```bash
# Basic conversion
python scripts/html_to_pdf.py page.html
# -> page.pdf

# Explicit output path
python scripts/html_to_pdf.py page.html output.pdf

# Respect CSS @page rules (recommended)
python scripts/html_to_pdf.py --prefer-css-page-size report.html

# Full publication layout
python scripts/html_to_pdf.py --prefer-css-page-size --outline --tagged report.html

# Custom margins
python scripts/html_to_pdf.py --margin-top 2cm --margin-bottom 2.5cm doc.html

# Landscape for wide tables
python scripts/html_to_pdf.py --landscape data-table.html

# Batch conversion
python scripts/html_to_pdf.py ch1.html ch2.html ch3.html

# Custom footer with page numbers
python scripts/html_to_pdf.py \
  --footer-template '<div style="text-align:center;width:100%">Page <span class="pageNumber"></span> / <span class="totalPages"></span></div>' \
  report.html
```

### All options

```
Page layout:
  --format FORMAT             A4 (default), Letter, Legal, A0-A6
  --landscape                 Horizontal orientation
  --prefer-css-page-size      Use @page CSS rules (recommended)
  --margin-top DIM            Top margin (e.g., 2cm, 1in, 72pt)
  --margin-right DIM          Right margin
  --margin-bottom DIM         Bottom margin
  --margin-left DIM           Left margin

Features:
  --outline                   PDF bookmarks from headings
  --tagged                    Accessibility tags
  --scale N                   Zoom factor (default: 1.0)
  --no-background             Skip background colors/images

Header/Footer:
  --header-template HTML      Page header HTML template
  --footer-template HTML      Page footer HTML template

Output:
  --quiet, -q                 Suppress progress output
```

## Requirements

- Python 3.9+
- Playwright (`pip install playwright`)
- Chromium browser (`playwright install chromium`)

## How it works

```
HTML file
  -> Playwright Chromium (headless)
  -> page.goto(file://, wait_until='networkidle')
  -> page.pdf() with configurable options
  -> PDF output
```

The script launches a headless Chromium instance, loads the HTML file via `file://` URL, waits for all resources to load (`networkidle`), then calls Chromium's native `Page.printToPDF` CDP command.

## Tips

- **Use `--prefer-css-page-size`** when your HTML has `@page { size: A4; margin: 2cm; }` rules
- **Use web fonts** (Google Fonts, `@font-face`) for consistent cross-platform rendering
- **Use absolute paths or data URIs** for images to avoid path resolution issues
- **Use `--outline`** for long documents — creates clickable bookmarks in the PDF
- **Use `@media print`** CSS to style PDF output differently from screen display

## License

MIT
