# Magic Mirror

A Python-based web crawler that creates local mirrors of websites using Playwright. Magic Mirror allows you to save complete rendered versions of web pages, including content that requires JavaScript execution.

## Features

- Saves fully rendered HTML content of web pages
- Handles JavaScript-heavy websites using Playwright
- Crawls and saves multiple linked pages
- Configurable maximum page limit
- Creates organized local mirror structure

## Installation

1. Clone this repository:
```bash
git clone https://github.com/noahitall/magic_mirror.git
cd magic_mirror
```

2. Install the required dependencies:
```bash
pip install playwright
playwright install chromium
```

## Usage

Run the crawler using the following command:

```bash
python mirror.py <BASE_URL> <MAX_PAGES>
```

Arguments:
- `BASE_URL`: The starting URL to begin crawling from
- `MAX_PAGES`: Maximum number of pages to crawl and save

Example:
```bash
python mirror.py https://example.com 10
```

This will:
1. Create a `site_mirror` directory
2. Save the main page as `index.html`
3. Crawl up to 10 linked pages and save them as `page_0.html`, `page_1.html`, etc.

## Output

All mirrored pages are saved in the `site_mirror` directory. The files are saved as:
- `index.html`: The main page
- `page_N.html`: Additional crawled pages (where N is the page number)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 