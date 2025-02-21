# Magic Mirror

A Python-based web crawler that creates local mirrors of websites using Playwright. Magic Mirror allows you to save complete rendered versions of web pages, including content that requires JavaScript execution. It uses smart link ranking to prioritize the most relevant pages for crawling.

## Features

- Saves fully rendered HTML content of web pages
- Handles JavaScript-heavy websites using Playwright
- Smart link ranking algorithm that prioritizes:
  - Internal links within the same domain
  - Links with text relevant to the page title
  - Links positioned higher on the page
  - Links in main content areas vs navigation/footer
  - Prominent links (larger text, bold styling)
- Configurable ranking weights via YAML configuration
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
python mirror.py <BASE_URL> <MAX_PAGES> [OUTPUT_DIR] [CONFIG_PATH]
```

Arguments:
- `BASE_URL`: The starting URL to begin crawling from
- `MAX_PAGES`: Maximum number of pages to crawl and save
- `OUTPUT_DIR`: (Optional) Directory to save the mirrored files (defaults to "site_mirror")
- `CONFIG_PATH`: (Optional) Path to ranking configuration file (defaults to "config.yaml")

Examples:
```bash
# Using default output directory and configuration
python mirror.py https://example.com 10

# Using custom output directory
python mirror.py https://example.com 10 my_mirror

# Using custom configuration
python mirror.py https://example.com 10 site_mirror custom_config.yaml
```

This will:
1. Create the output directory if it doesn't exist
2. Save the main page as `index.html`
3. Analyze and rank all links on the page
4. Display the top 5 ranked links with their scores
5. Crawl up to the specified number of pages, prioritizing the highest-ranked links

## Output

All mirrored pages are saved in the specified output directory (defaults to `site_mirror`). The files are saved as:
- `index.html`: The main page
- `page_N.html`: Additional crawled pages (where N is the page number)

## Link Ranking Configuration

The crawler uses a YAML configuration file to customize the link ranking algorithm. If no configuration file is provided, default values are used.

Example configuration (config.yaml):
```yaml
# Domain relevance
domain:
  internal_link_bonus: 3.0

# Content relevance
content:
  title_word_match_weight: 0.5

# Position weights
position:
  vertical_position_weight: 2.0

# Context weights
context:
  content_area_bonus: 2.0
  navigation_area_penalty: -1.0
  content_indicators:
    - article
    - main
    - section
    - div
  navigation_indicators:
    - nav
    - footer
    - header
    - sidebar

# Visual prominence
prominence:
  visible_link_bonus: 1.0
  bold_text_bonus: 0.5
  large_font_bonus: 0.5
  large_font_threshold: 16  # pixels
```

### Configuration Options

1. **Domain Relevance**
   - `internal_link_bonus`: Points added for links to the same domain

2. **Content Relevance**
   - `title_word_match_weight`: Points per word matching the page title

3. **Position**
   - `vertical_position_weight`: Maximum points for links at the top of the page

4. **Context**
   - `content_area_bonus`: Points for links in main content areas
   - `navigation_area_penalty`: Points deducted for links in navigation areas
   - `content_indicators`: HTML tags indicating main content
   - `navigation_indicators`: HTML tags indicating navigation areas

5. **Visual Prominence**
   - `visible_link_bonus`: Points for visible links
   - `bold_text_bonus`: Additional points for bold text
   - `large_font_bonus`: Additional points for large text
   - `large_font_threshold`: Font size threshold for "large" text (pixels)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 