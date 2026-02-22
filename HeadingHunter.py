from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup as bs
import csv


def heading_scraper(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
        )

        page = context.new_page()

        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            html = page.content()
            soup = bs(html, "html.parser")

            headings_data = {
                "URL": url,
                "H1": [],
                "H2": [],
                "H3": [],
                "H4": [],
                "H5": [],
                "H6": []
            }

            headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])

            for heading in headings:
                text = heading.get_text(strip=True)
                if text:
                    tag = heading.name.upper()
                    headings_data[tag].append(text)

            browser.close()

            # list -> string (For CSV cell )
            return {
                "URL": headings_data["URL"],
                "H1": " \n ".join(headings_data["H1"]),
                "H2": " \n ".join(headings_data["H2"]),
                "H3": " \n ".join(headings_data["H3"]),
                "H4": " \n ".join(headings_data["H4"]),
                "H5": " \n ".join(headings_data["H5"]),
                "H6": " \n ".join(headings_data["H6"]),
            }

        except Exception as e:
            browser.close()
            print(f"[ERROR] {url} -> {e}")
            return {
                "URL": url,
                "H1": "",
                "H2": "",
                "H3": "",
                "H4": "",
                "H5": "",
                "H6": ""
            }


def bulk_url(file_name="input.txt"):
    try:
        with open(file_name, "r") as f:
            urls = [line.strip() for line in f if line.strip()]

        if not urls:
            print("Foound No URL")
            return

        results = []
        for url in urls:
            results.append(heading_scraper(url))

        # Save to CSV
        with open("output.csv", "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["URL", "H1", "H2", "H3", "H4", "H5", "H6"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(results)

        print(" Output saved to output.csv")

    except FileNotFoundError:
        print("input.txt file not Found!! Please create input.txt and add URLs")


if __name__ == "__main__":
    print("1. Single URL scrape.\n2. Bulk URL Scraping")
    choice = input("Enter Choice (1/2): ")

    if choice == "1":
        url = input("Input URL: ")
        data = heading_scraper(url)

        with open("output.csv", "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["URL", "H1", "H2", "H3", "H4", "H5", "H6"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerow(data)

        print(" Output saved to output.csv")

    elif choice == "2":
        bulk_url("input.txt")

    else:
        print("Invalid Option. Please Choose between 1 or 2")

