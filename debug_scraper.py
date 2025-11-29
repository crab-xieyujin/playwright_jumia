from playwright.sync_api import sync_playwright

def debug_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        url = "https://www.jumia.com.ng/phones-tablets/"
        print(f"Navigating to {url}...")
        page.goto(url, timeout=60000)
        
        print(f"Page Title: {page.title()}")
        
        try:
            # Wait for products
            page.wait_for_selector("article.prd, article.c-prd", timeout=30000)
            
            # Get first card
            card = page.locator("article.prd, article.c-prd").first
            print("\nFirst Card HTML:")
            print(card.evaluate("el => el.outerHTML"))
        except Exception as e:
            print(f"Error: {e}")
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print("Saved page content to debug_page.html")
        
        browser.close()

if __name__ == "__main__":
    debug_page()
