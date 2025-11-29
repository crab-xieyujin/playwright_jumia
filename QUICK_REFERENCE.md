# 数据字段快速参考

## 📁 关键文件位置

```
jumia_scraper/
├── models.py          👈 【1. 在这里定义字段】
├── scraper.py         👈 【2. 在这里提取数据】
├── storage.py         (自动处理，无需修改)
└── utils.py           (辅助函数，如需要可添加)
```

## 🎯 修改流程（2步走）

### 第1步：定义字段 (`models.py`)

**文件位置**: `jumia_scraper/models.py`

**找到这个类**:
```python
class ProductItem(BaseModel):
```

**添加新字段**:
```python
class ProductItem(BaseModel):
    # === 现有字段 ===
    sku: Optional[str] = Field(None, description="商品唯一标识")
    name: str = Field(..., description="商品名称")
    brand: Optional[str] = Field(None, description="品牌")
    url: str = Field(..., description="商品详情页链接")
    image_url: Optional[str] = Field(None, description="主图链接")
    currency: str = Field(..., description="货币符号")
    current_price: float = Field(..., description="当前售价")
    old_price: Optional[float] = Field(None, description="原价")
    discount_percentage: Optional[float] = Field(None, description="折扣率")
    rating: Optional[float] = Field(None, description="评分")
    review_count: Optional[int] = Field(0, description="评论数")
    is_shipped_from_abroad: bool = Field(False, description="是否海外发货")
    crawled_at: datetime = Field(default_factory=datetime.utcnow)
    
    # === ✅ 在这里添加新字段 ===
    seller_name: Optional[str] = Field(None, description="卖家名称")
    stock_status: Optional[str] = Field(None, description="库存状态")
```

### 第2步：提取数据 (`scraper.py`)

**文件位置**: `jumia_scraper/scraper.py`

**找到这个方法**: 
```python
def parse_page(self) -> List[ProductItem]:
```

**在循环中添加提取逻辑** (约第80-120行):
```python
for i in range(count):
    try:
        card = product_cards.nth(i)
        
        # === 现有提取逻辑 ===
        # Extract URL
        link = card.locator("a.core")
        url = link.get_attribute("href")
        
        # Extract Name
        name_el = card.locator("h3.name")
        name = name_el.inner_text() if name_el.count() else "Unknown"
        
        # ... 其他现有字段 ...
        
        # === ✅ 在这里添加新字段提取 ===
        # Extract Seller Name
        seller_el = card.locator("span.seller")  # 根据实际HTML调整
        seller_name = seller_el.inner_text() if seller_el.count() else None
        
        # Extract Stock Status
        stock_el = card.locator("div.stock")  # 根据实际HTML调整
        stock_status = stock_el.inner_text() if stock_el.count() else None
        
        # === 创建 ProductItem 时包含新字段 ===
        item = ProductItem(
            name=name,
            url=url,
            # ... 其他现有字段 ...
            
            # ✅ 添加新字段
            seller_name=seller_name,
            stock_status=stock_status
        )
```

## 🔍 如何找到正确的选择器

### 方法1: 浏览器开发者工具
1. 打开 https://www.jumia.co.ke/phones-tablets/
2. 按 `F12`
3. 点击左上角"选择元素"图标
4. 点击商品卡片上的目标元素
5. 查看 HTML 结构，找到类名或标签

### 方法2: 运行可见浏览器
```bash
python main.py --country ke --category /phones-tablets/ --pages 1 --no-headless
```

观察浏览器中的页面结构。

## 📋 当前已提取的字段

| 字段名 | 类型 | 说明 | 提取位置 (scraper.py) |
|--------|------|------|---------------------|
| `sku` | str | 商品ID | 约第85行 |
| `name` | str | 商品名称 | 约第90行 |
| `brand` | str | 品牌 | 约第95行 |
| `url` | str | 详情链接 | 约第82行 |
| `image_url` | str | 图片链接 | 约第100行 |
| `currency` | str | 货币 | 约第105行 |
| `current_price` | float | 当前价格 | 约第105行 |
| `old_price` | float | 原价 | 约第110行 |
| `discount_percentage` | float | 折扣 | 约第115行 |
| `rating` | float | 评分 | 约第120行 |
| `review_count` | int | 评论数 | 约第125行 |
| `is_shipped_from_abroad` | bool | 海外发货 | 约第130行 |

## 🧪 测试修改

修改后运行测试：
```bash
python main.py --country ke --category /phones-tablets/ --pages 1 --output test.jsonl
```

查看输出：
```bash
# Windows
type test.jsonl

# 或用 Python 查看
python -c "import json; [print(json.loads(line)) for line in open('test.jsonl')]"
```

## 💡 常用选择器模式

```python
# 单个元素
element = card.locator("div.class-name")
text = element.inner_text() if element.count() else None

# 属性值
value = element.get_attribute("data-attribute")

# 多个元素
elements = card.locator("div.items")
count = elements.count()

# 条件判断
if card.locator("div.badge").count():
    badge = card.locator("div.badge").inner_text()
```

## 📞 需要帮助？

查看完整指南: `FIELD_GUIDE.md`
