from playwright.sync_api import sync_playwright
import time

def debug_images():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        url = "https://www.jumia.com.ng/catalog/?q=menstrual+cup"
        print(f"Navigating to {url}...")
        page.goto(url, timeout=60000)
        
        # Scroll to trigger lazy loading
        print("Scrolling...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(2)
        
        # Get product cards
        cards = page.locator("article.prd, article.c-prd")
        count = cards.count()
        print(f"Found {count} cards")
        
        for i in range(min(5, count)):
            card = cards.nth(i)
            img = card.locator("img.img")
            if img.count():
                print(f"\nImage {i} HTML:")
                print(img.evaluate("el => el.outerHTML"))
            else:
                print(f"\nImage {i} not found")
        
        browser.close()

if __name__ == "__main__":
    debug_images()
