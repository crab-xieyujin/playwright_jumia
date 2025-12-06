from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Homepage
        print("Navigating to homepage...")
        page.goto("https://www.jumia.com.ng/")
        time.sleep(5)
        with open("homepage.html", "w", encoding="utf-8") as f:
            f.write(page.content())
            
        # Category Page
        print("Navigating to category page...")
        page.goto("https://www.jumia.com.ng/phones-tablets/")
        time.sleep(5)
        with open("category.html", "w", encoding="utf-8") as f:
            f.write(page.content())

        # Subcategory Page
        print("Navigating to subcategory page...")
        page.goto("https://www.jumia.com.ng/smartphones/")
        time.sleep(5)
        with open("subcategory.html", "w", encoding="utf-8") as f:
            f.write(page.content())
            
        browser.close()
        print("Done!")

if __name__ == "__main__":
    run()
