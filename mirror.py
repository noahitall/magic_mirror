import sys
import os
from playwright.sync_api import sync_playwright

def save_page(page, url, filename):
    """Saves the rendered HTML content of a page."""
    page.goto(url, wait_until="networkidle")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(page.content())

def crawl_and_save(base_url, max_pages, output_dir="site_mirror"):
    """Crawls and saves multiple pages."""
    os.makedirs(output_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Save the main page
        save_page(page, base_url, os.path.join(output_dir, "index.html"))

        # Extract and crawl links
        page.goto(base_url, wait_until="networkidle")
        links = page.evaluate("Array.from(document.querySelectorAll('a')).map(a => a.href)")
        
        for i, link in enumerate(links[:max_pages]):
            save_page(page, link, os.path.join(output_dir, f"page_{i}.html"))

        browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python crawler.py <BASE_URL> <MAX_PAGES> [OUTPUT_DIR]")
        sys.exit(1)

    base_url = sys.argv[1]
    max_pages = int(sys.argv[2])
    output_dir = sys.argv[3] if len(sys.argv) == 4 else "site_mirror"

    crawl_and_save(base_url, max_pages, output_dir)

