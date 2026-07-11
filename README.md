<div align="center">

# HeadingHunter

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue?logo=python&logoColor=white)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?logo=opensourceinitiative)]()
[![Playwright](https://img.shields.io/badge/Playwright-1.40+-green?logo=google-chrome)]()

A professional **SEO heading analysis tool** that extracts and validates HTML heading structure (H1-H6) along with critical SEO meta tags from web pages. Built with Playwright for accurate rendering of JavaScript-heavy sites.

</div>

---

## Features

### SEO Meta Extraction
- Page `<title>` tag
- `<meta name="description">` content
- `<link rel="canonical">` URL
- Open Graph tags (`og:title`, `og:description`, `og:image`)
- `<meta name="robots">` directives

### Heading Analysis
- Extract all H1-H6 tags with content
- **Validation**: detects missing H1, multiple H1s, skipped heading levels
- **Quality check**: flags headings that are too short or too long

### Image SEO
- Total image count
- Images missing `alt` attribute

### Performance
- **Concurrent scraping** via `ThreadPoolExecutor` for bulk mode
- **Retry logic** with up to 3 attempts on failure
- **Progress bar** (tqdm) for bulk operations

### Output
- CSV export (UTF-8 BOM for Excel compatibility)
- JSON export for API integration
- Timestamped filenames (no accidental overwrites)
- CLI arguments for automation

---

## Quick Start

### Prerequisites
- Python 3.8+
- Google Chrome / Chromium (auto-installed by Playwright)

### Installation

```bash
git clone https://github.com/fahimpyto/HeadingHunter.git
cd HeadingHunter
pip install -r requirements.txt
playwright install chromium
```

### Analyze a single URL

```bash
python HeadingHunter.py --url https://example.com
```

### Analyze multiple URLs from file

```bash
python HeadingHunter.py --file urls.txt
```

### Interactive mode

```bash
python HeadingHunter.py
```

Then choose:
```
1. Single URL scrape
2. Bulk URL scraping
```

---

## CLI Reference

```
usage: HeadingHunter.py [-h] [--url URL | --file FILE]
                        [--output OUTPUT] [--format {csv,json,both}]
                        [--workers WORKERS] [--timeout TIMEOUT]
                        [--visible]

HeadingHunter - SEO Heading Analysis Tool

optional arguments:
  -h, --help            Show this help message and exit
  --url URL             Single URL to analyze
  --file FILE           Path to file with URLs (one per line)
  --output OUTPUT       Output file path (auto-generated if omitted)
  --format {csv,json,both}
                        Output format (default: csv)
  --workers WORKERS     Concurrent workers for bulk mode (default: 3)
  --timeout TIMEOUT     Page load timeout in ms (default: 60000)
  --visible             Show browser window during scraping
```

### Examples

```bash
# JSON output
python HeadingHunter.py --url https://example.com --format json

# Both CSV and JSON
python HeadingHunter.py --url https://example.com --format both

# Bulk with 5 workers, JSON output
python HeadingHunter.py --file input.txt --workers 5 --format json

# Custom filename
python HeadingHunter.py --url https://example.com --output report.csv

# Show browser for debugging
python HeadingHunter.py --url https://example.com --visible
```

---

## Input File Format (`input.txt`)

One URL per line. No commas, no extra spaces.

```text
https://example.com
https://example.com/about
https://example.com/contact
```

---

## Output Format

### CSV Columns

| Column | Description |
|--------|-------------|
| URL | Scraped page URL |
| Title | Page `<title>` tag |
| Meta Description | `<meta name="description">` content |
| Canonical URL | `<link rel="canonical">` href |
| OG Title | `og:title` meta property |
| OG Description | `og:description` meta property |
| OG Image | `og:image` meta property |
| Meta Robots | `robots` meta tag directives |
| H1-H6 | Heading text (multiple values separated by newlines) |
| Heading Issues | Heading validation warnings |
| Total Images | Number of `<img>` tags |
| Images Missing Alt | Count of images without alt attribute |

### JSON Schema

An array of objects with the same fields as CSV, formatted for programmatic consumption.

---

## Understanding Heading Issues

| Issue | Severity | Explanation |
|-------|----------|-------------|
| Missing H1 tag | Critical | Search engines expect a primary heading |
| Multiple H1 tags | High | Dilutes topical relevance; use one H1 per page |
| Skipped heading level | Medium | Breaks content hierarchy (e.g., H1 -> H3 with no H2) |
| Heading too short (<2 words) | Low | Lacks descriptive context |
| Heading too long (>15 words) | Low | Loses scannability |

---

## Requirements

```
playwright>=1.40.0
beautifulsoup4>=4.12.0
tqdm>=4.66.0
```

---

## Development

```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
playwright install chromium
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Author

Developed by **Fahim** ([@fahimpyto](https://github.com/fahimpyto))

