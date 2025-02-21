import sys
import os
from urllib.parse import urlparse, urljoin
from playwright.sync_api import sync_playwright
from typing import List, Dict, Tuple
import re
import yaml
from pathlib import Path

def is_safe_path(base_dir: str, path: str) -> bool:
    """
    Check if the path is safe (no directory traversal, relative to base_dir).
    Returns the safe absolute path or None if unsafe.
    """
    try:
        # Convert to absolute path and resolve any symlinks/relative components
        base_path = os.path.abspath(base_dir)
        full_path = os.path.abspath(os.path.join(base_dir, path))
        
        # Check if the resolved path is under the base directory
        return os.path.commonpath([base_path, full_path]) == base_path
    except Exception:
        return False

def sanitize_path(base_dir: str, path: str, default: str) -> str:
    """
    Sanitize a path to prevent directory traversal.
    Returns the sanitized path or the default if the path is unsafe.
    """
    if not path or not is_safe_path(base_dir, path):
        print(f"Warning: Invalid or unsafe path '{path}'. Using '{default}' instead.")
        return default
    return path

def load_config(config_path: str = "config.yaml") -> Dict:
    """Load ranking configuration from YAML file."""
    default_config = {
        "domain": {"internal_link_bonus": 3.0},
        "content": {"title_word_match_weight": 0.5},
        "position": {"vertical_position_weight": 2.0},
        "context": {
            "content_area_bonus": 2.0,
            "navigation_area_penalty": -1.0,
            "content_indicators": ["article", "main", "section", "div"],
            "navigation_indicators": ["nav", "footer", "header", "sidebar"]
        },
        "prominence": {
            "visible_link_bonus": 1.0,
            "bold_text_bonus": 0.5,
            "large_font_bonus": 0.5,
            "large_font_threshold": 16
        }
    }
    
    # Sanitize config path
    current_dir = os.getcwd()
    safe_config_path = sanitize_path(current_dir, config_path, "config.yaml")
    
    try:
        with open(safe_config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config if config else default_config
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"Warning: Could not load config file ({str(e)}). Using default configuration.")
        return default_config

def get_base_domain(url: str) -> str:
    """Extract the base domain from a URL."""
    parsed = urlparse(url)
    return parsed.netloc

def calculate_link_score(page, link_element, base_url: str, page_title: str, config: Dict) -> float:
    """Calculate a relevance score for a link based on various heuristics."""
    score = 0.0
    
    # Get link properties
    href = link_element.get_attribute('href')
    if not href:
        return -1.0  # Invalid link
    
    absolute_url = urljoin(base_url, href)
    link_text = link_element.text_content() or ''
    
    # 1. Domain relevance (internal links get a boost)
    if get_base_domain(absolute_url) == get_base_domain(base_url):
        score += config["domain"]["internal_link_bonus"]
    
    # 2. Text relevance to page title
    title_words = set(re.findall(r'\w+', page_title.lower()))
    link_words = set(re.findall(r'\w+', link_text.lower()))
    word_overlap = len(title_words.intersection(link_words))
    score += word_overlap * config["content"]["title_word_match_weight"]
    
    # 3. Position in document (higher = better)
    bounding_box = link_element.bounding_box()
    if bounding_box:
        # Normalize position (0 to 1, where 0 is top of page)
        viewport_height = page.viewport_size['height']
        position_score = 1.0 - (min(bounding_box['y'], viewport_height) / viewport_height)
        score += position_score * config["position"]["vertical_position_weight"]
    
    # 4. Main content area detection
    parent_tags = page.evaluate("""(element) => {
        const parents = [];
        let current = element;
        while (current && current.tagName) {
            parents.push(current.tagName.toLowerCase());
            current = current.parentElement;
        }
        return parents;
    }""", link_element)
    
    content_indicators = set(config["context"]["content_indicators"])
    navigation_indicators = set(config["context"]["navigation_indicators"])
    
    if any(tag in content_indicators for tag in parent_tags[:3]):
        score += config["context"]["content_area_bonus"]
    if any(tag in navigation_indicators for tag in parent_tags[:3]):
        score += config["context"]["navigation_area_penalty"]
    
    # 5. Link prominence
    styles = page.evaluate("""(element) => {
        const style = window.getComputedStyle(element);
        return {
            fontSize: parseFloat(style.fontSize),
            isVisible: style.display !== 'none' && style.visibility !== 'hidden',
            isBold: style.fontWeight >= 600
        };
    }""", link_element)
    
    if styles.get('isVisible', False):
        score += config["prominence"]["visible_link_bonus"]
        if styles.get('isBold', False):
            score += config["prominence"]["bold_text_bonus"]
        font_size = styles.get('fontSize', 0)
        if font_size > config["prominence"]["large_font_threshold"]:
            score += config["prominence"]["large_font_bonus"]
    
    return max(0.0, score)  # Ensure non-negative score

def get_ranked_links(page, base_url: str, config: Dict) -> List[Tuple[str, float]]:
    """Get all links on the page with their relevance scores."""
    # Get page title for relevance comparison
    page_title = page.title()
    
    # Get all links and calculate their scores
    links = page.query_selector_all('a[href]')
    ranked_links = []
    
    for link in links:
        href = link.get_attribute('href')
        if href:
            absolute_url = urljoin(base_url, href)
            score = calculate_link_score(page, link, base_url, page_title, config)
            if score > 0:  # Only include valid links
                ranked_links.append((absolute_url, score))
    
    # Sort by score in descending order
    ranked_links.sort(key=lambda x: x[1], reverse=True)
    return ranked_links

def save_page(page, url: str, filename: str) -> bool:
    """Saves the rendered HTML content of a page."""
    try:
        # Ensure the directory exists and is safe
        output_dir = os.path.dirname(filename)
        if output_dir and not is_safe_path(os.getcwd(), output_dir):
            print(f"Error: Unsafe output path '{filename}'")
            return False
            
        # Create directory if it doesn't exist
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        page.goto(url, wait_until="networkidle")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(page.content())
        return True
    except Exception as e:
        print(f"Error saving {url}: {str(e)}")
        return False

def crawl_and_save(base_url: str, max_pages: int, output_dir: str = "site_mirror", config_path: str = "config.yaml"):
    """Crawls and saves multiple pages."""
    # Sanitize output directory path
    current_dir = os.getcwd()
    safe_output_dir = sanitize_path(current_dir, output_dir, "site_mirror")
    
    try:
        os.makedirs(safe_output_dir, exist_ok=True)
    except Exception as e:
        print(f"Error creating output directory: {str(e)}")
        return
    
    # Load ranking configuration
    config = load_config(config_path)
    print("Loaded ranking configuration from:", config_path if os.path.exists(config_path) else "default configuration")
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Set a reasonable viewport size
        page.set_viewport_size({"width": 1280, "height": 800})
        
        # Save the main page
        if not save_page(page, base_url, os.path.join(safe_output_dir, "index.html")):
            print("Failed to save main page. Exiting.")
            browser.close()
            return
        
        # Get ranked links from the main page
        ranked_links = get_ranked_links(page, base_url, config)
        print(f"\nFound {len(ranked_links)} links, ranked by relevance:")
        for i, (url, score) in enumerate(ranked_links[:5], 1):
            print(f"{i}. Score {score:.2f}: {url}")
        
        # Crawl the highest-ranked pages up to max_pages
        pages_saved = 1  # Count main page
        for i, (url, score) in enumerate(ranked_links):
            if pages_saved >= max_pages:
                break
                
            print(f"\nCrawling {url} (relevance score: {score:.2f})")
            if save_page(page, url, os.path.join(safe_output_dir, f"page_{i}.html")):
                pages_saved += 1
        
        browser.close()
        print(f"\nFinished crawling. Saved {pages_saved} pages.")

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 5:
        print("Usage: python crawler.py <BASE_URL> <MAX_PAGES> [OUTPUT_DIR] [CONFIG_PATH]")
        sys.exit(1)

    base_url = sys.argv[1]
    max_pages = int(sys.argv[2])
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "site_mirror"
    config_path = sys.argv[4] if len(sys.argv) > 4 else "config.yaml"

    # Validate max_pages
    try:
        max_pages = int(max_pages)
        if max_pages < 1:
            raise ValueError("MAX_PAGES must be a positive integer")
    except ValueError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

    crawl_and_save(base_url, max_pages, output_dir, config_path)

