from playwright.sync_api import sync_playwright
import json, os


INPUT_FILE = "input.json"
OUTPUT_FILE = "output.json"


if not os.path.exists(INPUT_FILE):
    with open(INPUT_FILE, "w", encoding="utf-8") as f:
        json.dump({"urls": []}, f, indent=4)


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    try:
        data = json.load(f)
    except json.JSONDecodeError:
        data = {"urls": []}

urls = data.get("urls", [])


if not urls:
    url = input("Input URL : ").strip()
    urls = [url]


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )

    page = context.new_page()
    results = {}

    try:
        for url in urls:
            print(f"\n Opening page: {url}")

            page.goto(url, wait_until="domcontentloaded", timeout=90000)
            page.wait_for_timeout(5000)

            elements = []
            for attempt in range(1, 4):
                elements = page.query_selector_all("h1, h2, h3, h4, h5, h6")

                if len(elements) > 0:
                    print(f"[+] Headings found on attempt {attempt}")
                    break

                print(f"[-] Attempt {attempt}: No headings found, waiting more...")
                page.wait_for_timeout(5000)

            headings_list = []

            for h in elements:
                tag = h.evaluate("el => el.tagName")
                text = h.inner_text().strip()
                if text and text not in ["×", "x", "X"]:
                    headings_list.append({"tag": tag, "text": text})
                

            results[url] = headings_list

    except Exception as e:
        print("Error occurred:", e)

    browser.close()


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print(f"\nOutput saved in {OUTPUT_FILE}")
