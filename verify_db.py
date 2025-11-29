import sqlite3
import pandas as pd
import json

def verify_db(db_path):
    print(f"Verifying {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check columns
    cursor.execute("PRAGMA table_info(products)")
    columns = [info[1] for info in cursor.fetchall()]
    print(f"Columns found: {len(columns)}")
    print(columns)
    
    # Check data sample
    df = pd.read_sql_query("SELECT * FROM products LIMIT 5", conn)
    conn.close()
    
    print("\nData Sample:")
    print(df[['name', 'product_id', 'review_count', 'promo_tag', 'is_express']].to_string())
    
    print("\nChecking JSON fields:")
    if 'category_path' in df.columns and df['category_path'].iloc[0]:
        print(f"Category Path (Row 0): {df['category_path'].iloc[0]}")
    
    if 'gtm_tags' in df.columns and df['gtm_tags'].iloc[0]:
        print(f"GTM Tags (Row 0): {df['gtm_tags'].iloc[0]}")

if __name__ == "__main__":
    verify_db("test_enhanced.db")
