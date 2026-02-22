````md
# HeadingHunter 🕵️‍♂️📌

HeadingHunter is a Playwright-based web scraping tool that extracts all HTML headings (**H1–H6**) from any given webpage URL.  
It supports both **Single URL scraping** and **Bulk URL scraping** (via `input.txt`) and saves results into a structured **CSV file**.

----

## 🚀 Features

✅ Extracts headings: **H1, H2, H3, H4, H5, H6**  
✅ Supports **Single URL Mode**  
✅ Supports **Bulk URL Mode** using `input.txt`  
✅ Saves output in **output.csv**  
✅ Multiple headings are separated using **new lines** inside CSV cells  
✅ Uses Playwright rendering (works even for JavaScript-heavy sites)

---

## 📂 Project Files

| File | Description |
|------|-------------|
| `HeadingHunter.py` | Main scraper script |
| `input.txt` | List of URLs for bulk scraping |
| `output.csv` | Generated output file |

---

## ⚙️ Installation

### 1️⃣ Install Python dependencies

Make sure Python is installed, then run:

```bash
pip install playwright beautifulsoup4
````

### 2️⃣ Install Playwright browser

```bash
playwright install
```

---

## 🧑‍💻 Usage

Run the script:

```bash
python HeadingHunter.py
```

You will see:

```
1. Single URL scrape.
2. Bulk URL Scraping
Enter Choice (1/2):
```

---

## 🔹 Option 1: Single URL Scraping

Choose:

```
1
```

Then enter a URL:

```
Input URL: https://example.com
```

Output will be saved in:

✅ `output.csv`

---

## 🔹 Option 2: Bulk URL Scraping

Choose:

```
2
```

The script will read URLs from `input.txt` and scrape them one by one.

---

## 📝 How to Write input.txt (IMPORTANT)

Your `input.txt` file must contain:

✅ **One URL per line**
✅ **No commas (,)**
✅ **No extra spaces**

---

### ✅ Correct Format (Good)

```
https://diggitymarketing.com/
https://diggitymarketing.com/reddit-engagement-case-study/
https://diggitymarketing.com/news-roundup-jan-2026/
```

---

### ❌ Wrong Format (Bad)

Do NOT write URLs like this:

```
https://diggitymarketing.com/,
https://diggitymarketing.com/reddit-engagement-case-study/,
https://diggitymarketing.com/news-roundup-jan-2026/,
```

Comma দিলে URL invalid হয়ে যাবে এবং scraper error দিতে পারে।

---

## 📄 Output Format (CSV)

The generated `output.csv` will contain columns like:

| URL | H1 | H2 | H3 | H4 | H5 | H6 |
| --- | -- | -- | -- | -- | -- | -- |

Each heading type can contain multiple headings separated by **new lines**.

---

## 📝 Notes

* If you open `output.csv` in Excel, enable **Wrap Text** to properly view multi-line headings.
* Bulk scraping may take time depending on the number of URLs.
* If you get `PermissionError`, close `output.csv` if it's open in Excel.

---

## 📌 Example Output Message

After scraping, you will see:

```
Output saved to output.csv
```

---

## 🔥 Author

Developed by **Fahim**
Project Name: **HeadingHunter**

```
```
