from playwright.sync_api import sync_playwright

url = input("Input URL : ")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )

    page = context.new_page()

    try:
        print(" Opening page... ")
        page.goto(url, wait_until="domcontentloaded", timeout=90000)

        page.wait_for_timeout(5000)

        headings = []
        for attempt in range(1, 4):
            headings = page.query_selector_all("h1, h2, h3, h4, h5, h6")

            if len(headings) > 0:
                print(f"[+] Headings found on attempt {attempt}")
                break

            print(f"[-] Attempt {attempt}: No headings found, waiting more...")
            page.wait_for_timeout(5000)

        print("\n================= RESULT =================")
        print("Total headings found:", len(headings))

        for h in headings:
            tag = h.evaluate("el => el.tagName")
            text = h.inner_text().strip()

            if text:
                print(f"{tag}: {text}")

        if len(headings) == 0:
            print("\n No headings found. Saving debug files...")
            page.screenshot(path="debug.png", full_page=True)

            with open("debug.html", "w", encoding="utf-8") as f:
                f.write(page.content())

            print(" Got all the Headings...")

    except Exception as e:
        print("Error occurred:", e)

    browser.close()
