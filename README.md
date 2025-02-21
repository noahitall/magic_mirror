# Magic Mirror

A Python-based web crawler that creates local mirrors of websites using Playwright. Magic Mirror allows you to save complete rendered versions of web pages, including content that requires JavaScript execution.

## Features

- Saves fully rendered HTML content of web pages
- Handles JavaScript-heavy websites using Playwright
- Crawls and saves multiple linked pages
- Configurable maximum page limit
- Creates organized local mirror structure
- Customizable output directory

## Installation

1. Clone this repository:
```bash
git clone https://github.com/noahitall/magic_mirror.git
cd magic_mirror
```

2. Install the required dependencies:
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
```

## Usage

Run the crawler using the following command:

```bash
python mirror.py <BASE_URL> <MAX_PAGES> [OUTPUT_DIR]
```

Arguments:
- `BASE_URL`: The starting URL to begin crawling from
- `MAX_PAGES`: Maximum number of pages to crawl and save
- `OUTPUT_DIR`: (Optional) Directory to save the mirrored files (defaults to "site_mirror")

Examples:
```bash
# Using default output directory (site_mirror)
python mirror.py https://example.com 10

# Using custom output directory
python mirror.py https://example.com 10 my_mirror
```

This will:
1. Create the output directory if it doesn't exist
2. Save the main page as `index.html`
3. Crawl up to 10 linked pages and save them as `page_0.html`, `page_1.html`, etc.

## Output

All mirrored pages are saved in the specified output directory (defaults to `site_mirror`). The files are saved as:
- `index.html`: The main page
- `page_N.html`: Additional crawled pages (where N is the page number)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 