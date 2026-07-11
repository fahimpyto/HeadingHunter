#!/usr/bin/env python3
"""
HeadingHunter — SEO Heading Analysis Tool

Extracts and validates HTML heading structure (H1-H6) along with critical
SEO meta tags from web pages. Supports single and bulk URL analysis with
concurrent processing via Playwright.
"""

import argparse
import csv
import json
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from bs4 import BeautifulSoup as bs
from playwright.sync_api import sync_playwright
from tqdm import tqdm


DEFAULT_TIMEOUT = 60000
DEFAULT_WORKERS = 3
MAX_RETRIES = 3
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/145.0.0.0 Safari/537.36"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("HeadingHunter")

FIELD_NAMES = [
    "URL",
    "Title",
    "Meta Description",
    "Canonical URL",
    "OG Title",
    "OG Description",
    "OG Image",
    "Meta Robots",
    "H1", "H2", "H3", "H4", "H5", "H6",
    "Heading Issues",
    "Total Images",
    "Images Missing Alt",
]


def normalize_url(url):
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def _get_meta_property(soup, property_name):
    tag = soup.find("meta", attrs={"property": property_name})
    if tag and tag.get("content"):
        return tag["content"].strip()
    return ""


def extract_meta(soup):
    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    meta_desc = ""
    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag and meta_tag.get("content"):
        meta_desc = meta_tag["content"].strip()

    canonical = ""
    link_tag = soup.find("link", rel="canonical")
    if link_tag and link_tag.get("href"):
        canonical = link_tag["href"].strip()

    og_title = _get_meta_property(soup, "og:title")
    og_description = _get_meta_property(soup, "og:description")
    og_image = _get_meta_property(soup, "og:image")

    robots = ""
    robots_tag = soup.find("meta", attrs={"name": "robots"})
    if robots_tag and robots_tag.get("content"):
        robots = robots_tag["content"].strip()

    return {
        "Title": title,
        "Meta Description": meta_desc,
        "Canonical URL": canonical,
        "OG Title": og_title,
        "OG Description": og_description,
        "OG Image": og_image,
        "Meta Robots": robots,
    }


def extract_headings(soup):
    headings_data = {"H1": [], "H2": [], "H3": [], "H4": [], "H5": [], "H6": []}
    for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        text = heading.get_text(strip=True)
        if text:
            headings_data[heading.name.upper()].append(text)
    return headings_data


def validate_headings(headings_data):
    issues = []
    h1_count = len(headings_data["H1"])

    if h1_count == 0:
        issues.append("Missing H1 tag")
    if h1_count > 1:
        issues.append(f"Multiple H1 tags ({h1_count})")

    all_heading_tags = []
    for tag_level in ["H1", "H2", "H3", "H4", "H5", "H6"]:
        for h in headings_data[tag_level]:
            all_heading_tags.append((tag_level, h))

    found_levels = sorted(set(int(tag[1]) for tag, _ in all_heading_tags))
    for i in range(1, len(found_levels)):
        if found_levels[i] > found_levels[i - 1] + 1:
            missing = found_levels[i] - 1
            issues.append(
                f" Skipped heading level: H{found_levels[i-1]} -> H{found_levels[i]} "
                f"(missing H{missing})"
            )

    for tag, text in all_heading_tags:
        words = len(text.split())
        chars = len(text)
        if chars > 0 and words < 2:
            issues.append(f"{tag} too short ({words} word): \"{text[:50]}\"")
        elif words > 15:
            issues.append(f"{tag} too long ({words} words): \"{text[:50]}...\"")

    return issues


def extract_images(soup):
    images = soup.find_all("img")
    total = len(images)
    missing_alt = sum(1 for img in images if not img.get("alt") or not img["alt"].strip())
    return {
        "Total Images": total,
        "Images Missing Alt": missing_alt,
    }


def scrape_page(url, timeout=DEFAULT_TIMEOUT, headless=True):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=headless)
                context = browser.new_context(user_agent=USER_AGENT)
                page = context.new_page()
                page.goto(url, wait_until="networkidle", timeout=timeout)
                html = page.content()
                browser.close()

            soup = bs(html, "html.parser")
            meta = extract_meta(soup)
            headings = extract_headings(soup)
            heading_issues = validate_headings(headings)
            images = extract_images(soup)

            result = {
                "URL": url,
                **meta,
                **{k: " \n ".join(v) if v else "" for k, v in headings.items()},
                "Heading Issues": " | ".join(heading_issues) if heading_issues else "None",
                **images,
            }

            logger.info(f"  OK  {url}")
            return result

        except Exception as e:
            logger.warning(f"  Attempt {attempt}/{MAX_RETRIES} failed for {url}: {e}")
            if attempt == MAX_RETRIES:
                logger.error(f"  FAIL {url}  {e}")
                return {
                    "URL": url,
                    "Title": "",
                    "Meta Description": "",
                    "Canonical URL": "",
                    "OG Title": "",
                    "OG Description": "",
                    "OG Image": "",
                    "Meta Robots": "",
                    "H1": "", "H2": "", "H3": "",
                    "H4": "", "H5": "", "H6": "",
                    "Heading Issues": f"Scrape failed: {e}",
                    "Total Images": 0,
                    "Images Missing Alt": 0,
                }


def save_csv(results, filepath):
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELD_NAMES)
        writer.writeheader()
        writer.writerows(results)
    logger.info(f"CSV saved -> {filepath}")


def save_json(results, filepath):
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    logger.info(f"JSON saved -> {filepath}")


def _output_path(base, ext):
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    return f"{base}_{ts}.{ext}"


def _output_paths(csv_path, fmt):
    if fmt == "csv":
        return csv_path, None
    if fmt == "json":
        return None, csv_path
    base = os.path.splitext(csv_path)[0] if csv_path else "output"
    if fmt == "both":
        if csv_path:
            base = os.path.splitext(csv_path)[0]
            return f"{base}.csv", f"{base}.json"
        return _output_path("output", "csv"), _output_path("output", "json")
    return None, None


def scrape_single(url, args):
    url = normalize_url(url)
    data = scrape_page(url, args.timeout, not args.visible)

    csv_path, json_path = _output_paths(args.output, args.format)
    if csv_path:
        save_csv([data], csv_path)
    if json_path:
        save_json([data], json_path)

    if not csv_path and not json_path:
        save_csv([data], _output_path("output", "csv"))


def scrape_bulk(urls, args):
    results = []
    normalized = [normalize_url(u) for u in urls]
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(scrape_page, u, args.timeout, not args.visible): u
            for u in normalized
        }
        for future in tqdm(as_completed(futures), total=len(futures), desc="Scraping", unit="url"):
            results.append(future.result())

    csv_path, json_path = _output_paths(args.output, args.format)
    if csv_path:
        save_csv(results, csv_path)
    if json_path:
        save_json(results, json_path)

    if not csv_path and not json_path:
        csv_p = _output_path("output", "csv")
        save_csv(results, csv_p)


def interactive_mode():
    print("HeadingHunter - SEO Heading Analyzer")
    print("  1. Single URL scrape")
    print("  2. Bulk URL scraping")
    choice = input("Enter choice (1/2): ").strip()

    if choice == "1":
        url = input("Input URL: ").strip()
        data = scrape_page(normalize_url(url))
        path = _output_path("output", "csv")
        save_csv([data], path)
    elif choice == "2":
        filepath = input("Input file path (default: input.txt): ").strip() or "input.txt"
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                urls = [line.strip() for line in f if line.strip()]
            if not urls:
                logger.error("No URLs found in file.")
                return
            class Args:
                workers = DEFAULT_WORKERS
                timeout = DEFAULT_TIMEOUT
                visible = False
                format = "csv"
                output = None
            scrape_bulk(urls, Args())
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
    else:
        print("Invalid choice. Please enter 1 or 2.")


def main():
    parser = argparse.ArgumentParser(
        description="HeadingHunter - SEO Heading Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python HeadingHunter.py --url https://example.com\n"
            "  python HeadingHunter.py --file urls.txt --format both --workers 5\n"
            "  python HeadingHunter.py --url https://example.com --output report.csv\n"
            "  python HeadingHunter.py                       (interactive mode)"
        ),
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--url", help="Single URL to analyze")
    group.add_argument("--file", help="Path to file with URLs (one per line)")

    parser.add_argument("--output", help="Output file path (auto-generated if omitted)")
    parser.add_argument(
        "--format", choices=["csv", "json", "both"], default="csv",
        help="Output format (default: csv)",
    )
    parser.add_argument(
        "--workers", type=int, default=DEFAULT_WORKERS,
        help=f"Concurrent workers for bulk mode (default: {DEFAULT_WORKERS})",
    )
    parser.add_argument(
        "--timeout", type=int, default=DEFAULT_TIMEOUT,
        help=f"Page load timeout in ms (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--visible", action="store_true",
        help="Show browser window during scraping",
    )

    args = parser.parse_args()

    if args.url:
        scrape_single(args.url, args)
    elif args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                urls = [line.strip() for line in f if line.strip()]
            if not urls:
                logger.error("No URLs found in file.")
                sys.exit(1)
            scrape_bulk(urls, args)
        except FileNotFoundError:
            logger.error(f"File not found: {args.file}")
            sys.exit(1)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
