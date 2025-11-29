import re

def extract_html():
    try:
        with open('debug_log.txt', 'r', encoding='utf-16') as f:
            for line in f:
                if "First card HTML:" in line:
                    # Extract the HTML part
                    match = re.search(r'First card HTML: (.*)', line)
                    if match:
                        html_content = match.group(1)
                        print(f"Found HTML with length: {len(html_content)}")
                        with open('card_full.html', 'w', encoding='utf-8') as out:
                            out.write(html_content)
                        return
        print("HTML not found in log.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_html()
