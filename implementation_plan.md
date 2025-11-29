# Jumia Scraping Module - Implementation Plan

## 1. Goal Description
构建一个可复用、模块化的 Jumia 电商平台数据采集工具。
目标是支持多站点（KE, NG, MA, EG 等）、指定类目、自动翻页、数据清洗与结构化输出。
核心设计原则是**配置化**、**容错性**（重试机制）和**数据规范化**。

## 2. User Review Required
> [!IMPORTANT]
> - **Proxy Strategy**: 本方案提供 Proxy 接口配置，但默认不包含具体的代理池实现。用户需在配置文件或环境变量中提供 `PROXY_URL`。
> - **Anti-Bot**: Jumia 可能有反爬策略（Cloudflare 等）。我们将使用 `fake-useragent` 和 Playwright 的真实浏览器指纹来规避，但无法保证 100% 长期有效。建议配合高质量代理使用。
> - **Sync vs Async**: 根据需求，默认实现 **Sync** 版本以保持简单和稳定性（KISS原则）。如果需要高并发，后续可重构为 Async。

## 3. Proposed Architecture & Spec

### 3.1 Directory Structure
```
jumia_scraper/
├── __init__.py
├── config.py           # Pydantic 配置管理
├── models.py           # Pydantic 数据模型定义
├── scraper.py          # 核心采集逻辑 (Playwright + Tenacity)
├── storage.py          # 数据存储 (JSONL, SQLite, CSV)
└── utils.py            # 工具函数 (UserAgent, Logging)
main.py                 # CLI 入口
requirements.txt        # 依赖列表
```

### 3.2 Data Models (`models.py`)
使用 Pydantic 定义标准输出格式。

```python
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime

class ProductItem(BaseModel):
    sku: Optional[str] = Field(None, description="商品唯一标识")
    name: str = Field(..., description="商品名称")
    brand: Optional[str] = Field(None, description="品牌")
    url: HttpUrl = Field(..., description="商品详情页链接")
    image_url: Optional[HttpUrl] = Field(None, description="主图链接")
    
    currency: str = Field(..., description="货币符号, e.g. KSh")
    current_price: float = Field(..., description="当前售价")
    old_price: Optional[float] = Field(None, description="原价")
    discount_percentage: Optional[float] = Field(None, description="折扣率")
    
    rating: Optional[float] = Field(None, description="评分 (0-5)")
    review_count: Optional[int] = Field(0, description="评论数")
    
    is_shipped_from_abroad: bool = Field(False, description="是否海外发货")
    crawled_at: datetime = Field(default_factory=datetime.utcnow)
```

### 3.3 Configuration (`config.py`)
```python
from pydantic_settings import BaseSettings

class ScraperConfig(BaseSettings):
    BASE_URL_MAP: dict = {
        "ke": "https://www.jumia.co.ke",
        "ng": "https://www.jumia.com.ng",
        "ma": "https://www.jumia.ma",
        "eg": "https://www.jumia.com.eg"
    }
    
    COUNTRY_CODE: str = "ke"
    CATEGORY_URL: str
    MAX_PAGES: int = 5
    HEADLESS: bool = True
    PROXY_URL: Optional[str] = None
    TIMEOUT: int = 30000 # ms
    
    OUTPUT_FILE: str = "jumia_products.jsonl"
    OUTPUT_FORMAT: str = "jsonl" # jsonl, csv, sqlite
```

### 3.4 Core Logic (`scraper.py`)
- **Initialization**: Launch Playwright browser with `proxy` and `user_agent`.
- **Navigation**: 
    - Go to `CATEGORY_URL`.
    - Check for popup/modal (e.g. newsletter) and close if exists.
- **Pagination Loop**:
    - Parse current page products.
    - Check for "Next Page" button.
    - If `current_page < MAX_PAGES` and "Next" exists, click or navigate to next URL.
    - Sleep random interval (1-3s) between pages.
- **Parsing**:
    - Use Playwright locators to extract data.
    - `article.prd` is the typical selector for product cards.
- **Resilience**:
    - Use `tenacity` decorators on network request methods (`@retry(stop=stop_after_attempt(3))`).

## 4. Proposed Changes

### [New Project Setup]
#### [NEW] [requirements.txt](file:///d:/item/playwright_jumia/requirements.txt)
Dependencies: `playwright`, `pydantic`, `pydantic-settings`, `tenacity`, `fake-useragent`, `pandas` (for csv/excel if needed).

#### [NEW] [jumia_scraper/models.py](file:///d:/item/playwright_jumia/jumia_scraper/models.py)
#### [NEW] [jumia_scraper/config.py](file:///d:/item/playwright_jumia/jumia_scraper/config.py)
#### [NEW] [jumia_scraper/storage.py](file:///d:/item/playwright_jumia/jumia_scraper/storage.py)
#### [NEW] [jumia_scraper/utils.py](file:///d:/item/playwright_jumia/jumia_scraper/utils.py)
#### [NEW] [jumia_scraper/scraper.py](file:///d:/item/playwright_jumia/jumia_scraper/scraper.py)
#### [NEW] [main.py](file:///d:/item/playwright_jumia/main.py)
#### [NEW] [dashboard.py](file:///d:/item/playwright_jumia/dashboard.py)

## 5. Verification Plan

### Automated Tests
- Run `pytest` for data model validation and utility functions.
- Run a "dry run" scraper test against a saved HTML fixture to verify selectors without network.

### Manual Verification
- Run `python main.py --country ke --category "phones-tablets" --pages 1`
- Check `jumia_products.jsonl` for valid JSON objects.
- Verify fields: Price, Name, URL are not empty.
- Run `streamlit run dashboard.py` and verify data display.
