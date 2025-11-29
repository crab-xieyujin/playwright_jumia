# 数据字段修改指南

## 📍 数据字段定义位置

爬取的数据字段定义在 **`jumia_scraper/models.py`** 文件中。

## 🔍 当前数据字段

打开 `jumia_scraper/models.py`，您会看到 `ProductItem` 类定义了所有爬取的字段：

```python
class ProductItem(BaseModel):
    sku: Optional[str] = Field(None, description="商品唯一标识")
    name: str = Field(..., description="商品名称")
    brand: Optional[str] = Field(None, description="品牌")
    url: str = Field(..., description="商品详情页链接")
    image_url: Optional[str] = Field(None, description="主图链接")
    
    currency: str = Field(..., description="货币符号, e.g. KSh")
    current_price: float = Field(..., description="当前售价")
    old_price: Optional[float] = Field(None, description="原价")
    discount_percentage: Optional[float] = Field(None, description="折扣率")
    
    rating: Optional[float] = Field(None, description="评分 (0-5)")
    review_count: Optional[int] = Field(0, description="评论数")
    
    is_shipped_from_abroad: bool = Field(False, description="是否海外发货")
    crawled_at: datetime = Field(default_factory=datetime.utcnow)
```

## ➕ 如何添加新字段

### 步骤1: 在 models.py 中添加字段

例如，要添加"库存状态"和"卖家名称"：

```python
# 在 jumia_scraper/models.py 中
class ProductItem(BaseModel):
    # ... 现有字段 ...
    
    # 新增字段
    stock_status: Optional[str] = Field(None, description="库存状态")
    seller_name: Optional[str] = Field(None, description="卖家名称")
    seller_rating: Optional[float] = Field(None, description="卖家评分")
```

### 步骤2: 在 scraper.py 中提取数据

打开 `jumia_scraper/scraper.py`，找到 `parse_page()` 方法（约第62行开始）。

在这个方法中，找到商品卡片解析的循环：

```python
def parse_page(self) -> List[ProductItem]:
    # ... 现有代码 ...
    
    for i in range(count):
        try:
            card = product_cards.nth(i)
            
            # 现有字段提取
            # Extract URL
            link = card.locator("a.core")
            url = link.get_attribute("href")
            # ... 其他字段 ...
            
            # ✅ 添加新字段提取
            # Extract Stock Status
            stock_el = card.locator("div.stock-status")  # 根据实际HTML调整选择器
            stock_status = stock_el.inner_text() if stock_el.count() else None
            
            # Extract Seller Name
            seller_el = card.locator("span.seller-name")  # 根据实际HTML调整选择器
            seller_name = seller_el.inner_text() if seller_el.count() else None
            
            # 创建 ProductItem 时包含新字段
            item = ProductItem(
                name=name,
                url=url,
                # ... 其他现有字段 ...
                
                # ✅ 添加新字段
                stock_status=stock_status,
                seller_name=seller_name
            )
```

## 🎯 如何找到正确的选择器

### 方法1: 使用浏览器开发者工具

1. 打开 Jumia 网站（如 https://www.jumia.co.ke/phones-tablets/）
2. 按 `F12` 打开开发者工具
3. 点击左上角的"选择元素"图标
4. 点击页面上的商品卡片
5. 在 HTML 中找到对应的元素和类名

### 方法2: 使用 Playwright Inspector

运行爬虫时不使用 headless 模式：

```bash
python main.py --country ke --category /phones-tablets/ --pages 1 --no-headless
```

然后在代码中添加断点或使用 Playwright 的 `page.pause()` 来检查页面结构。

## 📝 常见选择器示例

基于 Jumia 的 HTML 结构，这里是一些常见的选择器：

```python
# 商品卡片
product_cards = self.page.locator("article.prd")

# 商品名称
name = card.locator("h3.name").inner_text()

# 价格
price = card.locator("div.prc").inner_text()

# 折扣标签
discount = card.locator("div.bdg._dsct").inner_text()

# 图片
image = card.locator("img.img").get_attribute("data-src")

# 评分
rating = card.locator("div.stars._s").inner_text()

# 品牌（可能在 data 属性中）
brand = card.get_attribute("data-brand")
```

## 🔧 实际示例：添加"配送方式"字段

### 1. 修改 models.py

```python
class ProductItem(BaseModel):
    # ... 现有字段 ...
    shipping_method: Optional[str] = Field(None, description="配送方式")
```

### 2. 修改 scraper.py

```python
def parse_page(self) -> List[ProductItem]:
    # ... 
    for i in range(count):
        try:
            card = product_cards.nth(i)
            
            # ... 现有字段提取 ...
            
            # 提取配送方式
            shipping_el = card.locator("div.bdg._mall")  # Jumia Mall 标识
            if shipping_el.count():
                shipping_method = "Jumia Mall"
            else:
                shipping_el = card.locator("div.bdg._fs")  # Free Shipping
                shipping_method = "Free Shipping" if shipping_el.count() else "Standard"
            
            item = ProductItem(
                # ... 现有字段 ...
                shipping_method=shipping_method
            )
```

## ⚠️ 注意事项

1. **字段类型**：
   - 必填字段用 `Field(...)`
   - 可选字段用 `Optional[类型]` 和 `Field(None)`

2. **选择器可能变化**：
   - Jumia 可能更新网站结构
   - 不同国家站点的 HTML 可能略有不同
   - 建议添加 `try-except` 处理

3. **性能考虑**：
   - 每个新字段都需要额外的 DOM 查询
   - 如果字段很多，可能影响爬取速度

4. **数据验证**：
   - Pydantic 会自动验证数据类型
   - 如果提取的数据格式不对，会抛出错误

## 🧪 测试新字段

修改后，运行测试：

```bash
python main.py --country ke --category /phones-tablets/ --pages 1 --output test_new_fields.jsonl
```

然后检查输出文件，确认新字段是否正确提取。

## 📚 相关文件

- **数据模型**: `jumia_scraper/models.py` - 定义字段
- **爬虫逻辑**: `jumia_scraper/scraper.py` - 提取数据
- **数据存储**: `jumia_scraper/storage.py` - 保存数据
- **工具函数**: `jumia_scraper/utils.py` - 辅助函数（如价格清洗）

## 💡 高级技巧

### 提取详情页数据

如果需要从商品详情页提取更多信息：

```python
def scrape_product_detail(self, url: str) -> dict:
    """访问详情页获取额外信息"""
    self.page.goto(url)
    
    # 提取详情页特有的信息
    description = self.page.locator("div.markup").inner_text()
    specifications = self.page.locator("ul.specs").inner_text()
    
    return {
        "description": description,
        "specifications": specifications
    }
```

### 使用正则表达式清洗数据

```python
import re

# 提取数字
def extract_number(text: str) -> Optional[float]:
    match = re.search(r'[\d,]+\.?\d*', text)
    if match:
        return float(match.group().replace(',', ''))
    return None
```

## 🆘 遇到问题？

1. **字段总是 None**：检查选择器是否正确
2. **类型错误**：确认数据格式与字段类型匹配
3. **爬取变慢**：减少不必要的字段或优化选择器

需要更详细的帮助，请查看代码中的注释或询问我！
