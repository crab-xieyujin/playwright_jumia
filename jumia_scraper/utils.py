import logging
from fake_useragent import UserAgent

def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("jumia_scraper")

def get_random_user_agent():
    try:
        ua = UserAgent()
        return ua.random
    except Exception:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def clean_price(price_str: str) -> float:
    """
    Cleans price string like 'KSh 12,345' to float 12345.0
    """
    if not price_str:
        return 0.0
    # Remove currency symbols and commas
    cleaned = ''.join(c for c in price_str if c.isdigit() or c == '.')
    try:
        return float(cleaned)
    except ValueError:
        return 0.0
