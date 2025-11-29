import argparse
import sys
from jumia_scraper.config import ScraperConfig
from jumia_scraper.scraper import JumiaScraper
from jumia_scraper.storage import StorageHandler
from jumia_scraper.utils import setup_logging

logger = setup_logging()

def main():
    parser = argparse.ArgumentParser(description="Jumia Scraper")
    parser.add_argument("--country", type=str, default="ke", help="Country code (ng, ke, eg, gh, ma, dz, ci, sn, ug)")
    parser.add_argument("--category", type=str, required=True, help="Category URL or path (e.g. /phones-tablets/)")
    parser.add_argument("--pages", type=int, default=1, help="Number of pages to scrape")
    parser.add_argument("--output", type=str, default="jumia_products.jsonl", help="Output file path")
    parser.add_argument("--format", type=str, default="jsonl", help="Output format (jsonl, csv, sqlite)")
    parser.add_argument("--headless", action="store_true", default=True, help="Run in headless mode")
    parser.add_argument("--no-headless", action="store_false", dest="headless", help="Run in headful mode")

    args = parser.parse_args()

    # Construct full URL if only path is given
    base_url_map = {
        "ng": "https://www.jumia.com.ng",
        "ke": "https://www.jumia.co.ke",
        "eg": "https://www.jumia.com.eg",
        "gh": "https://www.jumia.com.gh",
        "ma": "https://www.jumia.ma",
        "dz": "https://www.jumia.dz",
        "ci": "https://www.jumia.ci",
        "sn": "https://www.jumia.sn",
        "ug": "https://www.jumia.ug"
    }
    base_url = base_url_map.get(args.country, "https://www.jumia.co.ke")
    
    category_url = args.category
    if not category_url.startswith("http"):
        if not category_url.startswith("/"):
            category_url = "/" + category_url
        category_url = base_url + category_url

    config = ScraperConfig(
        COUNTRY_CODE=args.country,
        CATEGORY_URL=category_url,
        MAX_PAGES=args.pages,
        OUTPUT_FILE=args.output,
        OUTPUT_FORMAT=args.format,
        HEADLESS=args.headless
    )

    logger.info(f"Starting scraper for {config.CATEGORY_URL}")
    
    scraper = JumiaScraper(config)
    products = scraper.run()
    
    logger.info(f"Scraped {len(products)} products")
    
    storage = StorageHandler(config.OUTPUT_FILE, config.OUTPUT_FORMAT)
    storage.save(products)

if __name__ == "__main__":
    main()
