# Jumia Scraper - 使用指南

## 项目概述

这是一个功能完整的 Jumia 电商数据采集工具，支持 9 个非洲国家站点的商品数据抓取。

## 支持的国家

- 🇳🇬 Nigeria (尼日利亚)
- 🇰🇪 Kenya (肯尼亚)  
- 🇪🇬 Egypt (埃及)
- 🇬🇭 Ghana (加纳)
- 🇲🇦 Morocco (摩洛哥)
- 🇩🇿 Algeria (阿尔及利亚)
- 🇨🇮 Ivory Coast (科特迪瓦)
- 🇸🇳 Senegal (塞内加尔)
- 🇺🇬 Uganda (乌干达)

## 安装

```bash
pip install -r requirements.txt
playwright install chromium
```

## 使用方法

### ✅ 推荐：命令行方式（CLI）

命令行版本已经过完整测试，功能稳定可靠。

**基本用法：**
```bash
python main.py --country ke --category /phones-tablets/ --pages 1 --output products.jsonl
```

**完整参数：**
```bash
python main.py \
  --country ng \                    # 国家代码
  --category /phones-tablets/ \     # 类目路径或完整URL
  --pages 5 \                       # 抓取页数
  --output my_products.jsonl \      # 输出文件名
  --format jsonl \                  # 输出格式 (jsonl/csv/sqlite)
  --no-headless                     # 显示浏览器（可选）
```

**示例：**
```bash
# 抓取尼日利亚站点的手机类目，前3页
python main.py --country ng --category /phones-tablets/ --pages 3 --output nigeria_phones.jsonl

# 抓取加纳站点的香水类目，保存为SQLite
python main.py --country gh --category /beauty-health/fragrances/ --pages 2 --output perfumes.db --format sqlite

# 抓取肯尼亚站点，显示浏览器窗口
python main.py --country ke --category /phones-tablets/ --pages 1 --no-headless
```

### ⚠️ Dashboard 方式（存在已知问题）

Dashboard 提供了可视化界面，但目前在 Streamlit 环境中调用 Playwright 时存在执行问题，会返回 0 结果。

**启动 Dashboard：**
```bash
python -m streamlit run dashboard.py
```

**功能：**
- ✅ 数据查看：支持 SQLite 和 JSONL 文件的可视化展示
- ✅ 文件选择：自动扫描并列出所有 JSONL 文件
- ✅ 数据过滤：按商品名称搜索
- ⚠️ 数据采集：由于技术限制，建议使用 CLI

## 输出格式

### JSONL 格式（推荐）
每行一个 JSON 对象，便于流式处理：
```json
{"sku":null,"name":"Samsung Galaxy A05...","brand":"Samsung","url":"https://...","current_price":10799.0,"currency":"KE",...}
```

### SQLite 格式
结构化数据库，适合大量数据查询：
```bash
python main.py --country ke --category /phones-tablets/ --format sqlite --output products.db
```

### CSV 格式
表格数据，适合 Excel 分析：
```bash
python main.py --country ke --category /phones-tablets/ --format csv --output products.csv
```

## 关键词过滤

虽然 Dashboard 的关键词过滤功能受限，但您可以在 CLI 抓取后使用 Python 脚本过滤：

```python
import json

# 读取数据
with open('products.jsonl', 'r', encoding='utf-8') as f:
    products = [json.loads(line) for line in f]

# 过滤香水相关商品
perfumes = [p for p in products if 'perfume' in p['name'].lower() or '香水' in p['name'].lower()]

# 保存过滤结果
with open('perfumes_only.jsonl', 'w', encoding='utf-8') as f:
    for p in perfumes:
        f.write(json.dumps(p, ensure_ascii=False) + '\n')

print(f"Found {len(perfumes)} perfume products out of {len(products)} total")
```

## 测试结果

### ✅ CLI 测试通过
- Nigeria: 138 商品 ✅
- Ghana: 152 商品 ✅
- Kenya: 127 商品 ✅

### ⚠️ Dashboard 已知问题
- 数据查看功能：正常 ✅
- 数据采集功能：返回 0 结果 ⚠️
- 原因：Streamlit 执行环境与 Playwright 浏览器上下文冲突

## 技术栈

- **Python 3.10+**
- **Playwright**: 浏览器自动化
- **Pydantic**: 数据验证
- **Tenacity**: 请求重试
- **Streamlit**: Dashboard 界面
- **SQLite/Pandas**: 数据存储

## 项目结构

```
jumia_scraper/
├── __init__.py
├── config.py          # 配置管理
├── models.py          # 数据模型
├── scraper.py         # 核心爬虫逻辑
├── storage.py         # 数据存储
└── utils.py           # 工具函数
main.py                # CLI 入口
dashboard.py           # Dashboard 界面
requirements.txt       # 依赖列表
```

## 常见问题

**Q: 为什么 Dashboard 返回 0 结果？**
A: Streamlit 的执行模型与 Playwright 存在兼容性问题。请使用 CLI 版本。

**Q: 如何抓取特定商品（如香水）？**
A: 先抓取整个类目，然后用 Python 脚本按关键词过滤（见上方示例）。

**Q: 支持代理吗？**
A: 支持。在 `config.py` 中设置 `PROXY_URL` 环境变量。

**Q: 如何查看抓取的数据？**
A: 使用 Dashboard 的数据查看功能，或直接打开 JSONL/CSV 文件。

## 下一步优化建议

1. **修复 Dashboard 执行问题**：将爬虫任务移到后台进程
2. **添加实时进度**：在 Dashboard 中显示爬取进度
3. **支持定时任务**：自动定期抓取数据
4. **数据分析功能**：价格趋势、热门商品等

## 许可证

MIT License
