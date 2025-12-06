import re

def analyze_homepage():
    print("Analyzing homepage.html...")
    with open("homepage.html", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find categories
    # <a href="/phones-tablets/" class="itm" role="menuitem">
    # <span class="text">Phones &amp; Tablets</span>
    
    categories = re.findall(r'<a href="([^"]+)" class="itm"[^>]*>.*?<span class="text">([^<]+)</span>', content, re.DOTALL)
    print(f"Found {len(categories)} categories:")
    for url, name in categories:
        print(f"  - {name} ({url})")
        
    # Find subcategories
    # They are nested in .flyout .sub
    # We might need to parse the DOM properly, but let's see if we can find them by pattern
    # <a href="/mobile-phones/" class="tit" role="menuitem">Mobile Phones</a>
    # <a href="/smartphones/" class="s-itm" role="menuitem">Smartphones</a>
    
    subcats = re.findall(r'<a href="([^"]+)" class="(?:tit|s-itm)"[^>]*>([^<]+)</a>', content)
    print(f"Found {len(subcats)} total subcategory links (tit + s-itm).")
    for url, name in subcats[:10]:
        print(f"  - {name} ({url})")

def analyze_category():
    print("\nAnalyzing category.html...")
    with open("category.html", "r", encoding="utf-8") as f:
        content = f.read()
        
    # Look for product count
    # Usually "123 products found" or "1-40 of over 2000 results"
    
    # Pattern 1: X products found
    match = re.search(r'(\d+(?:,\d+)*) products found', content)
    if match:
        print(f"Found count pattern 'products found': {match.group(1)}")
        
    # Pattern 2: results
    match = re.search(r'(\d+(?:,\d+)*) results', content)
    if match:
        print(f"Found count pattern 'results': {match.group(1)}")
        
    # Look for the element containing the count
    # <p class="-gy5 -phs">123 products found</p>
    match = re.search(r'<p class="([^"]+)">.*?products found.*?</p>', content)
    if match:
        print(f"Found count container class: {match.group(1)}")

if __name__ == "__main__":
    analyze_homepage()
    analyze_category()
