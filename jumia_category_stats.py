import argparse
import json
import time
import re
from playwright.sync_api import sync_playwright

def get_category_stats(mode="structure_only", output_file="jumia_hierarchy.json", limit=None):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print("Navigating to Jumia Nigeria homepage...")
        try:
            page.goto("https://www.jumia.com.ng/", timeout=60000)
            
            try:
                close_btn = page.wait_for_selector("#newsletter_popup_close-cta", timeout=5000)
                if close_btn:
                    close_btn.click()
            except:
                pass
                
            page.wait_for_selector(".flyout", timeout=15000)
        except Exception as e:
            print(f"Error loading homepage: {e}")
            return

        print("Extracting 3-level category hierarchy...")
        hierarchy = []
        
        flyout = page.query_selector(".flyout")
        if not flyout:
            print("Flyout menu not found!")
            return
            
        itms = flyout.query_selector_all(".itm")
        subs = flyout.query_selector_all(".sub")
        
        print(f"Found {len(itms)} .itm elements and {len(subs)} .sub elements.")
        
        for i, item in enumerate(itms):
            text_el = item.query_selector(".text")
            l1_name = text_el.text_content() if text_el else "Unknown"
            l1_url = item.get_attribute("href")
            if l1_url and not l1_url.startswith("http"):
                l1_url = "https://www.jumia.com.ng" + l1_url
            
            print(f"Processing Level 1: {l1_name}")
            
            l1_data = {
                "name": l1_name,
                "url": l1_url,
                "subcategories": []
            }
            
            if i < len(subs):
                sub_menu = subs[i]
                cat_groups = sub_menu.query_selector_all(".cat")
                
                for cat_group in cat_groups:
                    tit_el = cat_group.query_selector(".tit")
                    if tit_el:
                        l2_name = tit_el.text_content()
                        l2_url = tit_el.get_attribute("href")
                        if l2_url and not l2_url.startswith("http"):
                            l2_url = "https://www.jumia.com.ng" + l2_url
                        
                        l2_data = {
                            "name": l2_name,
                            "url": l2_url,
                            "children": []
                        }
                        
                        s_items = cat_group.query_selector_all(".s-itm")
                        for s_item in s_items:
                            l3_name = s_item.text_content()
                            l3_url = s_item.get_attribute("href")
                            if l3_url and not l3_url.startswith("http"):
                                l3_url = "https://www.jumia.com.ng" + l3_url
                                
                            l3_data = {
                                "name": l3_name,
                                "url": l3_url,
                                "count": None
                            }
                            l2_data["children"].append(l3_data)
                        
                        l1_data["subcategories"].append(l2_data)
            
            hierarchy.append(l1_data)

        if mode == "with_counts":
            print("\nScraping product counts for leaf nodes (Level 3)...")
            scraped_count = 0
            
            for l1 in hierarchy:
                for l2 in l1["subcategories"]:
                    for l3 in l2["children"]:
                        if limit and scraped_count >= limit:
                            break
                            
                        if not l3["url"]:
                            continue
                        
                        try:
                            page.goto(l3["url"], timeout=30000)
                            
                            count = 0
                            found = False
                            
                            try:
                                h1_text = page.inner_text("h1")
                                match = re.search(r'\((\d+(?:,\d+)*) products found\)', h1_text)
                                if match:
                                    count = int(match.group(1).replace(',', ''))
                                    found = True
                            except:
                                pass
                                
                            if not found:
                                body_text = page.inner_text("body")
                                match = re.search(r'(\d+(?:,\d+)*) products found', body_text)
                                if match:
                                    count = int(match.group(1).replace(',', ''))
                                    found = True
                            
                            if found:
                                l3["count"] = count
                                print(f"    {l3['name']}: {count}")
                            else:
                                print(f"    {l3['name']}: Count not found")
                                l3["count"] = 0
                                
                        except Exception as e:
                            print(f"    Error visiting {l3['url']}: {e}")
                            l3["count"] = -1
                            
                        scraped_count += 1
                    if limit and scraped_count >= limit:
                        break
                if limit and scraped_count >= limit:
                    break
                            
        browser.close()
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(hierarchy, f, indent=2, ensure_ascii=False)
        print(f"\nSaved hierarchy to {output_file}")
        
        total_l1 = len(hierarchy)
        total_l2 = sum(len(c["subcategories"]) for c in hierarchy)
        total_l3 = sum(len(s["children"]) for c in hierarchy for s in c["subcategories"])
        print(f"Summary: {total_l1} Main Categories, {total_l2} Subcategories, {total_l3} Leaf Nodes.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["structure_only", "with_counts"], default="structure_only")
    parser.add_argument("--output", default="jumia_hierarchy.json")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    
    get_category_stats(mode=args.mode, output_file=args.output, limit=args.limit)
