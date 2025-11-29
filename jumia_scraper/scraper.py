import time
import random
from typing import List, Optional
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from .config import ScraperConfig
from .models import ProductItem
from .utils import setup_logging, get_random_user_agent, clean_price

logger = setup_logging()

class JumiaScraper:
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def start(self):
        self.playwright = sync_playwright().start()
        proxy = {"server": self.config.PROXY_URL} if self.config.PROXY_URL else None
        
        self.browser = self.playwright.chromium.launch(
            headless=self.config.HEADLESS,
            proxy=proxy
        )
        
        self.context = self.browser.new_context(
            user_agent=get_random_user_agent(),
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = self.context.new_page()
        self.page.set_default_timeout(self.config.TIMEOUT)

    def stop(self):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def navigate(self, url: str):
        logger.info(f"Navigating to {url}")
        self.page.goto(url, wait_until="domcontentloaded")
        self._handle_popups()

    def _handle_popups(self):
        """Close common popups like newsletter subscription"""
        try:
            # Example selector for newsletter popup close button
            # This is a guess and might need adjustment based on actual site
            popup_close = self.page.locator("button[aria-label='newsletter_popup_close-cta']").or_(self.page.locator(".cls"))
            if popup_close.is_visible(timeout=2000):
                popup_close.click()
                logger.info("Closed popup")
        except Exception:
            pass

    def _scroll_to_bottom(self):
        """Scroll to bottom to trigger lazy loading"""
        logger.info("Scrolling to bottom to trigger lazy loading...")
        
        # Get page height
        page_height = self.page.evaluate("document.body.scrollHeight")
        viewport_height = self.page.viewport_size["height"]
        
        # Scroll in steps
        current_scroll = 0
        while current_scroll < page_height:
            current_scroll += viewport_height
            self.page.evaluate(f"window.scrollTo(0, {current_scroll})")
            self.page.wait_for_timeout(1000)  # Increased wait time
            
            # Update page height in case it grew (infinite scroll)
            new_height = self.page.evaluate("document.body.scrollHeight")
            if new_height > page_height:
                page_height = new_height

        # Final wait for images and dynamic content
        self.page.wait_for_timeout(3000)
        
        # Scroll back to top
        self.page.evaluate("window.scrollTo(0, 0)")
        self.page.wait_for_timeout(1000)

    def parse_page(self) -> List[ProductItem]:
        # Ensure network is idle before scrolling
        try:
            self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
            
        self._scroll_to_bottom()
        
        items = []
        product_cards = self.page.locator("article.prd, article.c-prd")
        count = product_cards.count()
        logger.info(f"Found {count} products on page")

        for i in range(count):
            try:
                card = product_cards.nth(i)

                # Extract URL and Link Element
                link = card.locator("a.core")
                if not link.count():
                    continue
                    
                url = link.get_attribute("href")
                if url and not url.startswith("http"):
                    url = self.config.base_url + url

                # ========== 必采字段 ==========
                # Extract product_id (Jumia内部商品唯一ID)
                # Priority: data-gtm-id > data-id > form action
                product_id = link.get_attribute("data-gtm-id") or link.get_attribute("data-id") or card.get_attribute("data-id")
                
                if not product_id:
                    # Try to extract from form action
                    form = card.locator("form")
                    if form.count():
                        action = form.get_attribute("action")
                        if action:
                            import re
                            match = re.search(r'/products/([^/]+)/', action)
                            if match:
                                product_id = match.group(1)

                # Extract Name
                name = "Unknown"
                name_el = card.locator("h3.name")
                if not name_el.count():
                    name_el = card.locator(".name")
                
                if name_el.count():
                    name = name_el.inner_text().strip()

                # Extract Brand (data-gtm-brand) - on <a> tag
                brand = link.get_attribute("data-gtm-brand") or card.get_attribute("data-brand")
                if not brand:
                    # Try to guess from name
                    brand = name.split()[0] if name != "Unknown" else None

                # Extract Price
                # Support both div.prc and p.prc
                price_el = card.locator("div.prc, p.prc")
                price_text = price_el.inner_text() if price_el.count() else "0"
                price = clean_price(price_text)

                # Extract Image - try multiple attributes
                img_el = card.locator("img.img")
                img_url = None
                if img_el.count():
                    # Priority: data-src > src > srcset
                    # Jumia uses data-src for lazy loading
                    img_url = img_el.get_attribute("data-src")
                    
                    if not img_url or img_url.startswith("data:"):
                        img_url = img_el.get_attribute("src")
                    
                    if not img_url or img_url.startswith("data:"):
                        srcset = img_el.get_attribute("srcset")
                        if srcset:
                            img_url = srcset.split(',')[0].split()[0]

                    # Clean up URL
                    if img_url:
                        img_url = img_url.strip()
                        # Handle protocol-relative URLs (//example.com)
                        if img_url.startswith("//"):
                            img_url = "https:" + img_url
                        # Handle relative URLs (/product/...)
                        elif not img_url.startswith("http") and not img_url.startswith("data:"):
                            img_url = self.config.base_url + img_url
                        
                        # Final check: if it's still a data URI, discard it
                        if img_url.startswith("data:"):
                            img_url = None

                # Extract Rating (data-gtm-dimension27 或评分显示) - on <a> tag
                rating = None
                rating_attr = link.get_attribute("data-gtm-dimension27")
                if rating_attr:
                    try:
                        rating = float(rating_attr)
                    except (ValueError, TypeError):
                        pass
                
                if rating is None:
                    rating_el = card.locator("div.stars._s")
                    if rating_el.count():
                        rating_text = rating_el.inner_text()
                        try:
                            rating = float(rating_text.split()[0]) if rating_text else None
                        except (ValueError, IndexError):
                            pass

                # Extract Review Count (评论量) - on <a> tag
                review_count = 0
                review_attr = link.get_attribute("data-gtm-dimension26")
                if review_attr:
                    try:
                        review_count = int(review_attr)
                    except (ValueError, TypeError):
                        pass
                
                if review_count == 0:
                    # Try to extract from text like "(696)"
                    review_el = card.locator("div.rev, .stars")
                    if review_el.count():
                        review_text = review_el.inner_text()
                        import re
                        match = re.search(r'\((\d+)\)', review_text)
                        if match:
                            review_count = int(match.group(1))

                # Extract Seller ID (店铺ID) - on <a> tag
                seller_id = link.get_attribute("data-gtm-dimension23")

                # Extract Category Path (完整类目层级) - on <a> tag
                category_path = []
                category_str = link.get_attribute("data-gtm-category")
                if category_str:
                    category_path = [c.strip() for c in category_str.split(" / ") if c.strip()]

                # ========== 建议采集字段 ==========
                # Extract Old Price
                old_price_el = card.locator("div.old")
                old_price = clean_price(old_price_el.inner_text()) if old_price_el.count() else None

                # Extract Discount
                discount_el = card.locator("div.bdg._dsct")
                discount_text = discount_el.inner_text() if discount_el.count() else None
                discount = None
                if discount_text:
                    try:
                        discount = float(discount_text.replace('%', '').replace('-', '').strip())
                    except ValueError:
                        pass

                # Extract Promo Tag (促销活动标签)
                promo_tag = None
                promo_el = card.locator("span.bdg:not(._dsct), div.bdg:not(._dsct)")
                if promo_el.count():
                    promo_tag = promo_el.first.inner_text().strip()

                # Extract is_express (是否为Jumia Express)
                is_express = card.locator("svg.ic.xprss").count() > 0

                # Extract GTM Tags (Jumia内部标签集) - on <a> tag
                gtm_tags = []
                gtm_tags_str = link.get_attribute("data-gtm-dimension43")
                if gtm_tags_str:
                    gtm_tags = [tag.strip() for tag in gtm_tags_str.split("|") if tag.strip()]

                # Extract List Position (商品在列表页的排序位置) - on <a> tag
                list_position = None
                position_str = link.get_attribute("data-gtm-position") or link.get_attribute("data-ga4-index")
                if position_str:
                    try:
                        list_position = int(position_str)
                    except (ValueError, TypeError):
                        pass

                # ========== 可选字段 ==========
                # Extract Rating Ratio (评分比例)
                rating_ratio = None
                ratio_el = card.locator("div.in")
                if ratio_el.count():
                    style = ratio_el.get_attribute("style")
                    if style:
                        import re
                        match = re.search(r'width:\s*(\d+)%', style)
                        if match:
                            rating_ratio = float(match.group(1)) / 100

                # Extract GA4 Categories - on <a> tag
                ga4_category_1 = link.get_attribute("data-ga4-item_category")
                ga4_category_2 = link.get_attribute("data-ga4-item_category2")

                # Extract GA4 Price - on <a> tag
                ga4_price = None
                ga4_price_str = link.get_attribute("data-ga4-price")
                if ga4_price_str:
                    try:
                        ga4_price = float(ga4_price_str)
                    except (ValueError, TypeError):
                        pass

                # Extract is_second_chance - on <a> tag
                is_second_chance = None
                second_chance_str = link.get_attribute("data-ga4-is_second_chance")
                if second_chance_str:
                    is_second_chance = second_chance_str.lower() == "true"

                # Create ProductItem
                item = ProductItem(
                    # 必采字段
                    product_id=product_id,
                    name=name,
                    brand=brand,
                    url=url,
                    image_url=img_url,
                    currency=self.config.COUNTRY_CODE.upper(),
                    current_price=price,
                    rating=rating,
                    review_count=review_count,
                    seller_id=seller_id,
                    category_path=category_path,
                    # 建议采集字段
                    old_price=old_price,
                    discount_percentage=discount,
                    promo_tag=promo_tag,
                    is_express=is_express,
                    gtm_tags=gtm_tags,
                    list_position=list_position,
                    # 可选字段
                    rating_ratio=rating_ratio,
                    ga4_category_1=ga4_category_1,
                    ga4_category_2=ga4_category_2,
                    ga4_price=ga4_price,
                    is_second_chance=is_second_chance
                )
                items.append(item)
            except Exception as e:
                logger.error(f"Error parsing product {i}: {e}")
                continue
        
        return items

    def run(self) -> List[ProductItem]:
        all_products = []
        try:
            self.start()
            current_url = self.config.CATEGORY_URL
            
            for page_num in range(1, self.config.MAX_PAGES + 1):
                logger.info(f"Scraping page {page_num}")
                self.navigate(current_url)
                
                products = self.parse_page()
                all_products.extend(products)
                
                # Check for next page
                # Jumia pagination usually has 'a[aria-label="Next Page"]'
                next_btn = self.page.locator("a[aria-label='Next Page']")
                if not next_btn.is_visible():
                    logger.info("No next page found. Stopping.")
                    break
                
                next_url = next_btn.get_attribute("href")
                if not next_url:
                    break
                    
                if not next_url.startswith("http"):
                    current_url = self.config.base_url + next_url
                else:
                    current_url = next_url
                
                # Random sleep
                time.sleep(random.uniform(1, 3))
                
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
        finally:
            self.stop()
            
        return all_products
