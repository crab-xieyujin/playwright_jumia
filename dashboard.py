import streamlit as st
import sqlite3
import pandas as pd
import json
import os
import subprocess
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Jumia Scraper Dashboard", layout="wide", page_icon="🛍️")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Data View", "Data Analytics", "New Scrape Job"])

def load_data_sqlite(db_path):
    if not os.path.exists(db_path):
        return None
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query("SELECT * FROM products", conn)
    except Exception:
        df = None
    finally:
        conn.close()
    return df

def load_data_jsonl(file_path):
    if not os.path.exists(file_path):
        return None
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return pd.DataFrame(data)

def get_jsonl_files():
    """Get all JSONL files in current directory"""
    jsonl_files = [f for f in os.listdir('.') if f.endswith('.jsonl')]
    return jsonl_files if jsonl_files else ["No JSONL files found"]

# Common Data Loading Logic
st.sidebar.header("Data Source")
data_source = st.sidebar.radio("Select Data Source", ["SQLite Database", "JSONL File"])

df = None
if data_source == "SQLite Database":
    db_file = st.sidebar.text_input("Database Path", "products.db")
    if st.sidebar.button("Load Data"):
        with st.spinner("Loading data..."):
            df = load_data_sqlite(db_file)
            if df is None:
                st.error(f"Database file not found or invalid: {db_file}")
            else:
                st.session_state['loaded_df'] = df
                st.success(f"Loaded {len(df)} records.")

elif data_source == "JSONL File":
    jsonl_files = get_jsonl_files()
    if jsonl_files[0] != "No JSONL files found":
        jsonl_file = st.sidebar.selectbox("Select JSONL File", jsonl_files)
    else:
        st.sidebar.warning("No JSONL files found in current directory")
        jsonl_file = st.sidebar.text_input("Or enter file path manually", "test_products_v2.jsonl")
    
    if st.sidebar.button("Load Data"):
        with st.spinner("Loading data..."):
            df = load_data_jsonl(jsonl_file)
            if df is None:
                st.error(f"File not found: {jsonl_file}")
            else:
                st.session_state['loaded_df'] = df
                st.success(f"Loaded {len(df)} records.")

# Retrieve data from session state if available
if 'loaded_df' in st.session_state:
    df = st.session_state['loaded_df']

# Data Preprocessing
if df is not None and not df.empty:
    # Numeric conversions
    numeric_cols = ['current_price', 'old_price', 'discount_percentage', 'rating', 'review_count', 'list_position']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Fill NA for critical display fields
    df['brand'] = df['brand'].fillna('Unknown')
    df['name'] = df['name'].fillna('Unknown')

# ==========================================
# PAGE: Data View
# ==========================================
if page == "Data View":
    st.title("🛍️ Jumia Product Data View")

    if df is not None and not df.empty:
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Products", len(df))
        avg_price = df['current_price'].mean() if 'current_price' in df.columns else 0
        col2.metric("Avg Price", f"{avg_price:.2f}")
        
        avg_discount = df['discount_percentage'].mean() if 'discount_percentage' in df.columns else 0
        col3.metric("Avg Discount", f"{avg_discount:.1f}%")
        
        total_reviews = df['review_count'].sum() if 'review_count' in df.columns else 0
        col4.metric("Total Reviews", f"{int(total_reviews)}")

        # Filters
        st.subheader("Filters")
        col_f1, col_f2 = st.columns(2)
        search_term = col_f1.text_input("Search by Name")
        
        brands = ['All'] + sorted(df['brand'].unique().tolist())
        selected_brand = col_f2.selectbox("Filter by Brand", brands)
        
        filtered_df = df.copy()
        if search_term:
            filtered_df = filtered_df[filtered_df['name'].str.contains(search_term, case=False, na=False)]
        if selected_brand != 'All':
            filtered_df = filtered_df[filtered_df['brand'] == selected_brand]

        st.caption(f"Showing {len(filtered_df)} products")

        # Display Data
        st.subheader("Product List")
        
        # Configure columns for display
        # Prioritize new fields
        default_cols = [
            'image_url', 'name', 'brand', 'current_price', 'old_price', 
            'discount_percentage', 'rating', 'review_count', 
            'promo_tag', 'is_express', 'product_id', 'url'
        ]
        available_cols = [c for c in default_cols if c in filtered_df.columns]
        
        # Add other columns that might be interesting but not in default
        all_cols = filtered_df.columns.tolist()
        extra_cols = [c for c in all_cols if c not in available_cols]
        
        # Allow user to add columns
        selected_extra_cols = st.multiselect("Add more columns", extra_cols)
        final_cols = available_cols + selected_extra_cols

        st.dataframe(
            filtered_df[final_cols],
            column_config={
                "image_url": st.column_config.ImageColumn("Image"),
                "url": st.column_config.LinkColumn("Link"),
                "current_price": st.column_config.NumberColumn("Price", format="%.2f"),
                "old_price": st.column_config.NumberColumn("Old Price", format="%.2f"),
                "discount_percentage": st.column_config.NumberColumn("Discount", format="%.0f%%"),
                "rating": st.column_config.NumberColumn("Rating", format="%.1f ⭐"),
                "review_count": st.column_config.NumberColumn("Reviews"),
                "is_express": st.column_config.CheckboxColumn("Express"),
            },
            use_container_width=True,
            height=800
        )

    elif df is not None:
        st.warning("No data found in the selected source.")
    else:
        st.info("Please select a data source and click 'Load Data' in the sidebar.")

# ==========================================
# PAGE: Data Analytics
# ==========================================
elif page == "Data Analytics":
    st.title("📊 Data Analytics")

    if df is not None and not df.empty:
        
        # 1. Price Distribution Analysis
        st.subheader("1. Price Distribution Analysis")
        col_p1, col_p2 = st.columns(2)
        
        with col_p1:
            # Histogram of Current Price
            fig_price = px.histogram(
                df, 
                x="current_price", 
                nbins=50, 
                title="Distribution of Current Price",
                labels={"current_price": "Price"},
                color_discrete_sequence=['#1f77b4']
            )
            st.plotly_chart(fig_price, use_container_width=True)
            
        with col_p2:
            # Box Plot for Price vs Brand (Top 10 Brands)
            top_brands = df['brand'].value_counts().head(10).index.tolist()
            df_top_brands = df[df['brand'].isin(top_brands)]
            
            fig_box = px.box(
                df_top_brands, 
                x="brand", 
                y="current_price", 
                title="Price Distribution by Top 10 Brands",
                color="brand"
            )
            st.plotly_chart(fig_box, use_container_width=True)

        # Discount Analysis
        if 'discount_percentage' in df.columns and 'old_price' in df.columns:
            st.markdown("#### Discount Analysis")
            # Fill NaN values in discount_percentage with 0 to avoid Plotly errors
            df['discount_percentage'] = df['discount_percentage'].fillna(0)
            fig_discount = px.scatter(
                df, 
                x="old_price", 
                y="current_price", 
                color="discount_percentage",
                size="discount_percentage",
                hover_data=['name', 'brand'],
                title="Old Price vs Current Price (Color/Size = Discount %)",
                labels={"old_price": "Old Price", "current_price": "Current Price"}
            )
            st.plotly_chart(fig_discount, use_container_width=True)

        st.divider()

        # 2. Brand Popularity Top 10
        st.subheader("2. Brand Popularity Top 10 (by Product Count)")
        
        brand_counts = df['brand'].value_counts().head(10).reset_index()
        brand_counts.columns = ['brand', 'count']
        
        fig_brand = px.bar(
            brand_counts, 
            x='brand', 
            y='count', 
            title="Top 10 Brands by Number of Products",
            text='count',
            color='count',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_brand, use_container_width=True)

        st.divider()

        # 3. Review Count Top 5
        st.subheader("3. Top 5 Products by Review Count")
        
        if 'review_count' in df.columns:
            top_reviews = df.nlargest(5, 'review_count')[['name', 'brand', 'review_count', 'rating', 'current_price', 'url']]
            
            # Display as a styled table
            st.dataframe(
                top_reviews,
                column_config={
                    "url": st.column_config.LinkColumn("Link"),
                    "current_price": st.column_config.NumberColumn("Price", format="%.2f"),
                    "rating": st.column_config.NumberColumn("Rating", format="%.1f ⭐"),
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Bar chart for visual
            fig_reviews = px.bar(
                top_reviews,
                x='review_count',
                y='name',
                orientation='h',
                title="Top 5 Most Reviewed Products",
                color='rating',
                hover_data=['brand', 'current_price']
            )
            fig_reviews.update_layout(yaxis={'categoryorder':'total ascending'}) # Sort bars
            st.plotly_chart(fig_reviews, use_container_width=True)
        else:
            st.warning("Review count data not available.")

        st.divider()

        # 4. Highest Rated Brands
        st.subheader("4. Highest Rated Brands (Avg Rating)")
        st.caption("Minimum 3 products required to be included")

        if 'rating' in df.columns:
            # Filter brands with at least 3 products to avoid outliers
            brand_stats = df.groupby('brand').agg({
                'rating': 'mean',
                'name': 'count'
            }).reset_index()
            
            brand_stats_filtered = brand_stats[brand_stats['name'] >= 3]
            top_rated_brands = brand_stats_filtered.nlargest(10, 'rating')
            
            fig_rating = px.bar(
                top_rated_brands,
                x='brand',
                y='rating',
                title="Top 10 Highest Rated Brands (Avg Rating)",
                color='rating',
                range_y=[0, 5], # Rating is 0-5
                text_auto='.2f'
            )
            st.plotly_chart(fig_rating, use_container_width=True)
        else:
            st.warning("Rating data not available.")

    elif df is not None:
        st.warning("No data found to analyze.")
    else:
        st.info("Please load data from the sidebar first.")

# ==========================================
# PAGE: New Scrape Job
# ==========================================
elif page == "New Scrape Job":
    st.title("🕷️ Run Jumia Scraper")
    st.markdown("Configure and start a new scraping job directly from here.")

    with st.form("scraper_form"):
        # Country mapping with friendly names
        COUNTRIES = {
            "ng": "🇳🇬 Nigeria (尼日利亚)",
            "ke": "🇰🇪 Kenya (肯尼亚)",
            "eg": "🇪🇬 Egypt (埃及)",
            "gh": "🇬🇭 Ghana (加纳)",
            "ma": "🇲🇦 Morocco (摩洛哥)",
            "dz": "🇩🇿 Algeria (阿尔及利亚)",
            "ci": "🇨🇮 Ivory Coast (科特迪瓦)",
            "sn": "🇸🇳 Senegal (塞内加尔)",
            "ug": "🇺🇬 Uganda (乌干达)"
        }
        
        col1, col2 = st.columns(2)
        country_display = col1.selectbox("Country Site", list(COUNTRIES.values()))
        country = [k for k, v in COUNTRIES.items() if v == country_display][0]
        pages = col2.number_input("Number of Pages", min_value=1, max_value=50, value=1)
        
        category_url = st.text_input("Category URL", help="Full URL (e.g. https://www.jumia.co.ke/phones-tablets/) or Path (e.g. /phones-tablets/)")
        
        keyword_filter = st.text_input("Keyword Filter (Optional)", 
                                       help="Filter products by keyword (e.g., 'perfume', '香水'). Leave empty to scrape all products.",
                                       placeholder="e.g., perfume, samsung, iphone")
        
        col3, col4 = st.columns(2)
        output_format = col3.selectbox("Output Format", ["jsonl", "sqlite", "csv"])
        output_file = col4.text_input("Output Filename", "scraped_data.jsonl")
        
        headless = st.checkbox("Headless Mode (Hide Browser)", value=True)
        
        submitted = st.form_submit_button("🚀 Start Scraping", type="primary")
        
        if submitted:
            if not category_url:
                st.error("Please enter a Category URL.")
            else:
                status_container = st.status("Initializing Scraper...", expanded=True)
                
                try:
                    # Build CLI command
                    cmd = [
                        "python", "main.py",
                        "--country", country,
                        "--category", category_url,
                        "--pages", str(pages),
                        "--output", output_file,
                        "--format", output_format
                    ]
                    
                    if not headless:
                        cmd.append("--no-headless")
                    
                    status_container.write(f"Running command: `{' '.join(cmd)}`")
                    status_container.write("Starting scraper via CLI...")
                    
                    # Run the command
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1
                    )
                    
                    # Stream output
                    output_lines = []
                    for line in process.stdout:
                        line = line.strip()
                        if line:
                            output_lines.append(line)
                            if "INFO" in line or "Scraped" in line or "Saved" in line:
                                status_container.write(line)
                    
                    process.wait()
                    
                    if process.returncode == 0:
                        status_container.write("✅ Scraping process completed successfully")
                        
                        # Load and count results
                        if output_format == "jsonl":
                            if os.path.exists(output_file):
                                file_size = os.path.getsize(output_file)
                                st.info(f"Debug: File `{output_file}` found. Size: {file_size} bytes.")
                                
                                with open(output_file, 'r', encoding='utf-8') as f:
                                    products_data = []
                                    for i, line in enumerate(f):
                                        line = line.strip()
                                        if line:
                                            try:
                                                products_data.append(json.loads(line))
                                            except json.JSONDecodeError as e:
                                                st.warning(f"Debug: Failed to parse line {i+1}: {e}")
                                
                                st.info(f"Debug: Loaded {len(products_data)} items from file.")
                            else:
                                st.error(f"Debug: File `{output_file}` NOT found in {os.getcwd()}")
                                products_data = []
                            
                            # Apply keyword filter if provided
                            if keyword_filter:
                                original_count = len(products_data)
                                products_data = [p for p in products_data if keyword_filter.lower() in p.get('name', '').lower()]
                                status_container.write(f"Filtered: {original_count} → {len(products_data)} products (keyword: '{keyword_filter}')")
                                
                                # Save filtered results
                                if len(products_data) < original_count:
                                    filtered_file = output_file.replace('.jsonl', '_filtered.jsonl')
                                    with open(filtered_file, 'w', encoding='utf-8') as f:
                                        for p in products_data:
                                            f.write(json.dumps(p, ensure_ascii=False) + '\n')
                                    status_container.write(f"Saved filtered results to: {filtered_file}")
                            
                            product_count = len(products_data)
                            status_container.update(label="✅ Scraping Complete!", state="complete", expanded=False)
                            
                            if keyword_filter and len(products_data) < original_count:
                                st.warning(f"Scraped {original_count} items, but only {product_count} matched your filter: '{keyword_filter}'")
                                st.success(f"Saved {product_count} filtered items to `{output_file}`")
                            else:
                                st.success(f"Successfully scraped {product_count} items to `{output_file}`")
                            
                            # Preview
                            if product_count > 0:
                                st.subheader("Preview (First 5 items)")
                                preview_df = pd.DataFrame(products_data[:5])
                                st.dataframe(preview_df)
                        else:
                            status_container.update(label="✅ Scraping Complete!", state="complete", expanded=False)
                            st.success(f"Data saved to `{output_file}`")
                    else:
                        status_container.update(label="❌ Scraping Failed", state="error", expanded=True)
                        st.error(f"Scraper exited with code {process.returncode}")
                        st.code('\n'.join(output_lines), language="text")
                        
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    status_container.update(label="❌ Scraping Failed", state="error", expanded=True)
                    st.error(f"An error occurred: {str(e)}")
                    st.code(error_details, language="python")
