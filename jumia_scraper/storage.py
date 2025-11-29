import json
import csv
import sqlite3
from typing import List
from .models import ProductItem
import logging

logger = logging.getLogger("jumia_scraper.storage")

class StorageHandler:
    def __init__(self, output_file: str, format: str):
        self.output_file = output_file
        self.format = format.lower()

    def save(self, items: List[ProductItem]):
        if not items:
            logger.warning("No items to save.")
            return

        if self.format == 'jsonl':
            self._save_jsonl(items)
        elif self.format == 'csv':
            self._save_csv(items)
        elif self.format == 'sqlite':
            self._save_sqlite(items)
        else:
            logger.error(f"Unsupported format: {self.format}")

    def _save_jsonl(self, items: List[ProductItem]):
        with open(self.output_file, 'a', encoding='utf-8') as f:
            for item in items:
                f.write(item.model_dump_json() + '\n')
        logger.info(f"Saved {len(items)} items to {self.output_file}")

    def _save_csv(self, items: List[ProductItem]):
        # Check if file exists to write header
        file_exists = False
        try:
            with open(self.output_file, 'r') as f:
                file_exists = True
        except FileNotFoundError:
            pass

        with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=items[0].model_dump().keys())
            if not file_exists:
                writer.writeheader()
            for item in items:
                writer.writerow(item.model_dump())
        logger.info(f"Saved {len(items)} items to {self.output_file}")

    def _save_sqlite(self, items: List[ProductItem]):
        conn = sqlite3.connect(self.output_file)
        cursor = conn.cursor()
        
        # Define proper SQL types for fields
        field_type_mapping = {
            'product_id': 'TEXT PRIMARY KEY',
            'name': 'TEXT',
            'brand': 'TEXT',
            'url': 'TEXT',
            'image_url': 'TEXT',
            'currency': 'TEXT',
            'current_price': 'REAL',
            'old_price': 'REAL',
            'discount_percentage': 'REAL',
            'rating': 'REAL',
            'review_count': 'INTEGER',
            'seller_id': 'TEXT',
            'category_path': 'TEXT',  # JSON
            'promo_tag': 'TEXT',
            'is_express': 'BOOLEAN',
            'gtm_tags': 'TEXT',  # JSON
            'list_position': 'INTEGER',
            'rating_ratio': 'REAL',
            'ga4_category_1': 'TEXT',
            'ga4_category_2': 'TEXT',
            'ga4_price': 'REAL',
            'is_second_chance': 'BOOLEAN',
            'sku': 'TEXT',
            'is_shipped_from_abroad': 'BOOLEAN',
            'crawled_at': 'TEXT'
        }
        
        # Get all fields from the first item
        fields = list(items[0].model_dump().keys())
        
        # Create table with proper types
        columns_def = []
        for field in fields:
            sql_type = field_type_mapping.get(field, 'TEXT')
            columns_def.append(f"{field} {sql_type}")
        
        create_table_sql = f"CREATE TABLE IF NOT EXISTS products ({', '.join(columns_def)})"
        cursor.execute(create_table_sql)
        
        # Insert data
        for item in items:
            data = item.model_dump()
            
            # Convert list fields to JSON strings
            if 'category_path' in data and isinstance(data['category_path'], list):
                data['category_path'] = json.dumps(data['category_path'], ensure_ascii=False)
            if 'gtm_tags' in data and isinstance(data['gtm_tags'], list):
                data['gtm_tags'] = json.dumps(data['gtm_tags'], ensure_ascii=False)
            
            # Convert datetime to string
            if 'crawled_at' in data and hasattr(data['crawled_at'], 'isoformat'):
                data['crawled_at'] = data['crawled_at'].isoformat()
            
            placeholders = ', '.join(['?'] * len(data))
            values = [str(v) if v is not None else None for v in data.values()]
            
            try:
                cursor.execute(f"INSERT OR REPLACE INTO products VALUES ({placeholders})", values)
            except sqlite3.IntegrityError as e:
                logger.warning(f"Duplicate product_id, skipping: {e}")
                continue
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(items)} items to {self.output_file}")
