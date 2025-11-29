from pydantic_settings import BaseSettings
from typing import Optional, Dict

class ScraperConfig(BaseSettings):
    BASE_URL_MAP: Dict[str, str] = {
        "ng": "https://www.jumia.com.ng",  # Nigeria (尼日利亚)
        "ke": "https://www.jumia.co.ke",   # Kenya (肯尼亚)
        "eg": "https://www.jumia.com.eg",  # Egypt (埃及)
        "gh": "https://www.jumia.com.gh",  # Ghana (加纳)
        "ma": "https://www.jumia.ma",      # Morocco (摩洛哥)
        "dz": "https://www.jumia.dz",      # Algeria (阿尔及利亚)
        "ci": "https://www.jumia.ci",      # Ivory Coast (科特迪瓦)
        "sn": "https://www.jumia.sn",      # Senegal (塞内加尔)
        "ug": "https://www.jumia.ug"       # Uganda (乌干达)
    }
    
    COUNTRY_CODE: str = "ke"
    CATEGORY_URL: str
    MAX_PAGES: int = 5
    HEADLESS: bool = True
    PROXY_URL: Optional[str] = None
    TIMEOUT: int = 30000 # ms
    
    OUTPUT_FILE: str = "jumia_products.jsonl"
    OUTPUT_FORMAT: str = "jsonl" # jsonl, csv, sqlite

    @property
    def base_url(self) -> str:
        return self.BASE_URL_MAP.get(self.COUNTRY_CODE.lower(), "https://www.jumia.co.ke")
