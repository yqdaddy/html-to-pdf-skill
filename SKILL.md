---
name: html-to-pdf
description: >
  Convert HTML files to publication-quality PDFs using Playwright (headless Chromium).
  Use when the user asks to "convert HTML to PDF", "print HTML", "export as PDF",
  "generate PDF from HTML", "make a PDF from this page", or any HTML-to-PDF conversion request.
  Supports @page CSS, custom margins, outlines/bookmarks, headers/footers, batch conversion.
triggers:
  - html to pdf
  - convert to pdf
  - print to pdf
  - export pdf
  - generate pdf from html
  - make pdf
allowed-tools:
  - Bash
  - Read
  - Glob
---

# HTML to PDF

Convert HTML files to publication-quality PDFs using Playwright (headless Chromium).
Renders exactly what the browser renders, with full CSS support including `@page`,
flexbox, grid, web fonts, SVG, and background colors.

## Setup Check (run first)

```bash
# Check Python
python --version 2>/dev/null || python3 --version 2>/dev/null
# Check playwright
python -c "import playwright; print('playwright OK')" 2>/dev/null || python3 -c "import playwright; print('playwright OK')" 2>/dev/null
# Check chromium binary
python -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(); b.close(); p.stop(); print('chromium OK')" 2>/dev/null
```

If any check fails, install dependencies:

```bash
pip install playwright
playwright install chromium
```

On Linux CI/Docker, you may also need system dependencies:
```bash
playwright install-deps chromium
```

## Core Usage

The conversion script is at `scripts/html_to_pdf.py` relative to this skill directory.

Determine the script path:
```bash
_SKILL_DIR=""
[ -n "$HOME" ] && [ -f "$HOME/.claude/skills/html-to-pdf/scripts/html_to_pdf.py" ] && _SKILL_DIR="$HOME/.claude/skills/html-to-pdf"
[ -z "$_SKILL_DIR" ] && [ -f ".claude/skills/html-to-pdf/scripts/html_to_pdf.py" ] && _SKILL_DIR=".claude/skills/html-to-pdf"
# Fallback: search for the script
[ -z "$_SKILL_DIR" ] && _SKILL_DIR=$(find "$HOME/.claude" -path "*/html-to-pdf/scripts" -type d 2>/dev/null | head -1 | sed 's|/scripts$||')
```

### 80% case — basic conversion

```bash
python "$_SKILL_DIR/scripts/html_to_pdf.py" page.html
# -> page.pdf (same directory, same name)

python "$_SKILL_DIR/scripts/html_to_pdf.py" page.html output.pdf
# -> output.pdf (explicit output path)
```

### With CSS @page support (recommended)

If the HTML has `@page { size: A4; margin: 2cm; }` rules:

```bash
python "$_SKILL_DIR/scripts/html_to_pdf.py" --prefer-css-page-size page.html
```

This respects the page size and margins defined in CSS.

### Batch conversion

```bash
python "$_SKILL_DIR/scripts/html_to_pdf.py" ch1.html ch2.html ch3.html
# -> ch1.pdf, ch2.pdf, ch3.pdf
```

## All Options

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
  --header-template HTML      Page header HTML
  --footer-template HTML      Page footer HTML

Output:
  --quiet, -q                 Suppress progress output
```

## Common Patterns

### Full publication layout

```bash
python "$_SKILL_DIR/scripts/html_to_pdf.py" \
  --prefer-css-page-size --outline --tagged \
  report.html report.pdf
```

### Custom margins with Letter size

```bash
python "$_SKILL_DIR/scripts/html_to_pdf.py" \
  --format Letter \
  --margin-top 1in --margin-bottom 1in \
  --margin-left 1.2in --margin-right 1.2in \
  doc.html doc.pdf
```

### Landscape for wide tables

```bash
python "$_SKILL_DIR/scripts/html_to_pdf.py" \
  --landscape --format A4 \
  data-table.html data-table.pdf
```

### Custom header and footer

Footer shows page number: `Page <span class="pageNumber"></span> of <span class="totalPages"></span>`

```bash
python "$_SKILL_DIR/scripts/html_to_pdf.py" \
  --footer-template '<div style="font-size:9px;text-align:center;width:100%">Page <span class="pageNumber"></span> / <span class="totalPages"></span></div>' \
  report.html report.pdf
```

## When Claude should run it

Watch for HTML-to-PDF intent. Any of these patterns trigger this skill:

- "Convert this HTML to PDF"
- "Export as PDF"
- "Print to PDF"
- "Generate a PDF from this page"
- "Make this HTML into a PDF"
- User has an HTML file and says "make it a PDF"

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Background colors missing | `print_background` defaults to True but may be overridden | Ensure `--no-background` is NOT set |
| Fonts look wrong | System fonts missing | Use web fonts (Google Fonts CDN) or embed with `@font-face` |
| Images missing | Relative paths not resolved | Use absolute paths or `file://` base URLs; ensure images exist |
| @page CSS ignored | Flag not set | Add `--prefer-css-page-size` |
| Blank PDF | JavaScript-rendered content | Add wait time; the script uses `wait_until='networkidle'` which should handle most cases |
| `playwright install` fails | Missing system deps (Linux) | Run `playwright install-deps chromium` |
| PDF too large | High-res images | Compress images in the HTML source |
| Text not selectable | Scanned/image content | This is expected; use OCR tools for scanned PDFs |

## Technical Notes

- **Engine**: Playwright Chromium (headless mode, no display server needed)
- **Python**: 3.9+ required
- **CSS**: Full support — @page, flexbox, grid, web fonts, SVG, @media print
- **JavaScript**: Executed (unlike wkhtmltopdf); SPAs and dynamic content work
- **Output**: Standard PDF with optional outline bookmarks and accessibility tags
- **Concurrency**: One file at a time (Chromium instance per file)
