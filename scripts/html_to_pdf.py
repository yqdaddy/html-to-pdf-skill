#!/usr/bin/env python3
"""
html_to_pdf.py - Convert HTML files to publication-quality PDFs using Playwright.

Usage:
    python html_to_pdf.py [OPTIONS] <input.html> [output.pdf]
    python html_to_pdf.py [OPTIONS] <file1.html> <file2.html> ...

Requires: Python 3.9+, playwright (pip install playwright && playwright install chromium)
"""

import argparse
import os
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def check_dependencies():
    """Check if playwright is installed, print install instructions if not."""
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        print('Error: playwright is not installed.', file=sys.stderr)
        print('', file=sys.stderr)
        print('Install with:', file=sys.stderr)
        print('  pip install playwright', file=sys.stderr)
        print('  playwright install chromium', file=sys.stderr)
        return False


def resolve_output_path(input_path: Path, output_arg: str = None) -> Path:
    """Determine output PDF path from input path or explicit argument."""
    if output_arg:
        return Path(output_arg).resolve()
    return input_path.parent / (input_path.stem + '.pdf')


def convert_one(
    input_path: Path,
    output_path: Path,
    *,
    page_format: str = 'A4',
    landscape: bool = False,
    prefer_css_page_size: bool = False,
    outline: bool = False,
    tagged: bool = False,
    scale: float = 1.0,
    print_background: bool = True,
    margin_top: str = None,
    margin_right: str = None,
    margin_bottom: str = None,
    margin_left: str = None,
    header_template: str = None,
    footer_template: str = None,
    quiet: bool = False,
):
    """Convert a single HTML file to PDF."""
    from playwright.sync_api import sync_playwright

    if not quiet:
        print(f'  Input:  {input_path}')
        print(f'  Output: {output_path}')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        file_url = input_path.as_uri()
        page.goto(file_url, wait_until='networkidle')

        if not quiet:
            print(f'  Loaded: {page.title()}')

        # Build margin dict
        margin = {}
        if margin_top:
            margin['top'] = margin_top
        if margin_right:
            margin['right'] = margin_right
        if margin_bottom:
            margin['bottom'] = margin_bottom
        if margin_left:
            margin['left'] = margin_left

        # Build PDF options
        pdf_opts = {
            'path': str(output_path),
            'format': page_format,
            'landscape': landscape,
            'prefer_css_page_size': prefer_css_page_size,
            'outline': outline,
            'tagged': tagged,
            'scale': scale,
            'print_background': print_background,
        }

        if margin:
            pdf_opts['margin'] = margin

        # Header/footer require display_header_footer=True
        if header_template or footer_template:
            pdf_opts['display_header_footer'] = True
            if header_template:
                pdf_opts['header_template'] = header_template
            if footer_template:
                pdf_opts['footer_template'] = footer_template

        page.pdf(**pdf_opts)
        browser.close()

    size_kb = os.path.getsize(output_path) / 1024
    if not quiet:
        print(f'  Done ({size_kb:.0f} KB)')

    return size_kb


def main():
    parser = argparse.ArgumentParser(
        description='Convert HTML files to PDF using Playwright (headless Chromium).',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Examples:\n'
               '  %(prog)s page.html\n'
               '  %(prog)s page.html output.pdf\n'
               '  %(prog)s --prefer-css-page-size --outline report.html\n'
               '  %(prog)s --landscape --format Letter slides.html\n'
               '  %(prog)s --margin-top 2cm --margin-bottom 2.5cm doc.html\n',
    )
    parser.add_argument(
        'files',
        nargs='+',
        metavar='input.html',
        help='HTML file(s) to convert. If the last arg ends with .pdf, it is used as output path (single file only).',
    )

    # Page layout
    layout = parser.add_argument_group('Page layout')
    layout.add_argument('--format', default='A4', metavar='FORMAT',
                        help='Page format: A4 (default), Letter, Legal, A0-A6')
    layout.add_argument('--landscape', action='store_true',
                        help='Horizontal orientation')
    layout.add_argument('--prefer-css-page-size', action='store_true',
                        help='Use @page CSS rules for page size and margins (recommended)')
    layout.add_argument('--margin-top', metavar='DIM',
                        help='Top margin (e.g., 2cm, 1in, 72pt)')
    layout.add_argument('--margin-right', metavar='DIM',
                        help='Right margin')
    layout.add_argument('--margin-bottom', metavar='DIM',
                        help='Bottom margin')
    layout.add_argument('--margin-left', metavar='DIM',
                        help='Left margin')

    # Features
    feat = parser.add_argument_group('Features')
    feat.add_argument('--outline', action='store_true',
                      help='Generate PDF bookmarks from headings (h1-h6)')
    feat.add_argument('--tagged', action='store_true',
                      help='Add accessibility tags')
    feat.add_argument('--scale', type=float, default=1.0, metavar='N',
                      help='Zoom scale factor (default: 1.0)')
    feat.add_argument('--no-background', action='store_true',
                      help='Do not print background colors/images')

    # Header/footer
    hf = parser.add_argument_group('Header/Footer')
    hf.add_argument('--header-template', metavar='HTML',
                    help='HTML template for page header (requires --display-header-footer)')
    hf.add_argument('--footer-template', metavar='HTML',
                    help='HTML template for page footer')

    # Output control
    out = parser.add_argument_group('Output')
    out.add_argument('--quiet', '-q', action='store_true',
                     help='Suppress progress output')

    args = parser.parse_args()

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Detect if last arg is a .pdf output path
    files = args.files
    output_override = None
    if len(files) == 2 and files[-1].lower().endswith('.pdf'):
        # Could be: input.html output.pdf
        if files[0].lower().endswith(('.html', '.htm')):
            output_override = files[1]
            files = [files[0]]

    # Validate input files
    input_paths = []
    for f in files:
        p = Path(f).resolve()
        if not p.exists():
            print(f'Error: {p} not found', file=sys.stderr)
            sys.exit(1)
        if not p.suffix.lower() in ('.html', '.htm'):
            print(f'Warning: {p} does not look like an HTML file', file=sys.stderr)
        input_paths.append(p)

    # Print header
    count = len(input_paths)
    if not args.quiet:
        print(f'Converting {count} file{"s" if count > 1 else ""}...')
        if args.prefer_css_page_size:
            print(f'Mode: CSS @page size enabled')
        print()

    # Convert
    total_kb = 0
    start_time = time.time()

    for i, input_path in enumerate(input_paths):
        if count > 1 and not args.quiet:
            print(f'[{i + 1}/{count}] {input_path.name}')

        output_path = resolve_output_path(
            input_path,
            output_override if len(input_paths) == 1 else None,
        )

        try:
            size_kb = convert_one(
                input_path,
                output_path,
                page_format=args.format,
                landscape=args.landscape,
                prefer_css_page_size=args.prefer_css_page_size,
                outline=args.outline,
                tagged=args.tagged,
                scale=args.scale,
                print_background=not args.no_background,
                margin_top=args.margin_top,
                margin_right=args.margin_right,
                margin_bottom=args.margin_bottom,
                margin_left=args.margin_left,
                header_template=args.header_template,
                footer_template=args.footer_template,
                quiet=args.quiet,
            )
            total_kb += size_kb
        except Exception as e:
            print(f'Error converting {input_path.name}: {e}', file=sys.stderr)
            sys.exit(2)

    # Summary
    elapsed = time.time() - start_time
    if not args.quiet:
        if count > 1:
            print()
            print(f'All done. {count} files, {total_kb:.0f} KB total, {elapsed:.1f}s')
        else:
            print(f'Finished in {elapsed:.1f}s')


if __name__ == '__main__':
    main()
