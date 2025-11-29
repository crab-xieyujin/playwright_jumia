# Jumia E-Commerce Scraper & Analytics Dashboard

这是一个功能强大的 Jumia 电商数据采集与分析工具，支持非洲 9 个国家站点的商品数据抓取、可视化展示及多维度数据分析。

## ✨ 主要功能

- **多站点支持**：覆盖 Nigeria, Kenya, Egypt, Ghana, Morocco 等 9 个国家站点。
- **全字段采集**：自动提取 20+ 个关键字段，包括：
  - 基础信息：商品ID、标题、品牌、图片链接、详情页链接
  - 价格信息：现价、原价、折扣率、货币单位
  - 评价数据：评分、评论数、评分比例
  - 营销信息：促销标签、Jumia Express 标识、店铺ID
  - 内部数据：类目路径、GTM 标签、列表排名等
- **数据分析 Dashboard**：
  - **价格分布**：直方图与箱线图展示价格区间及品牌定价策略
  - **品牌热度**：Top 10 热门品牌统计
  - **爆款发现**：基于评论量的热门商品分析
  - **优质品牌**：基于平均评分的品牌筛选
- **多种导出格式**：支持 JSONL (推荐)、SQLite 数据库、CSV 格式。

## 🚀 快速开始

### 1. 安装依赖

需要 Python 3.10+ 环境。

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 启动可视化 Dashboard

这是最简单的使用方式，提供图形化界面进行数据查看和分析。

```bash
python -m streamlit run dashboard.py
```

启动后浏览器将自动打开，您可以在左侧导航栏切换：
- **Data View**: 查看已采集的数据列表，支持筛选和排序。
- **Data Analytics**: 查看自动生成的数据分析图表。
- **New Scrape Job**: 配置并启动新的采集任务。

### 3. 命令行工具 (CLI)

适合批量任务或服务器环境运行。

**基本用法：**
```bash
# 采集肯尼亚站点手机类目，抓取 1 页，保存为 SQLite 数据库
python main.py --country ke --category /phones-tablets/ --pages 1 --output products.db --format sqlite
```

**完整参数说明：**
```bash
python main.py \
  --country ng \                    # 国家代码 (ng, ke, eg, gh, ma, dz, ci, sn, ug)
  --category /phones-tablets/ \     # 类目路径或完整URL
  --pages 5 \                       # 抓取页数
  --output my_products.jsonl \      # 输出文件名
  --format jsonl \                  # 输出格式 (jsonl/csv/sqlite)
  --no-headless                     # 显示浏览器窗口（调试用）
```

## 📊 数据分析功能

Dashboard 内置了强大的数据分析模块，帮助您快速洞察市场：

1.  **价格分布分析**：了解市场主流价格区间，辅助定价。
2.  **品牌竞争格局**：识别市场上的主导品牌（Top 10）。
3.  **消费者偏好**：通过评论量和评分发现用户最喜欢的商品和品牌。
4.  **折扣策略分析**：分析原价与现价的关系，了解折扣力度。

## 📂 项目结构

```
jumia_scraper/
├── jumia_scraper/     # 核心爬虫包
│   ├── scraper.py     # 爬虫逻辑
│   ├── models.py      # 数据模型 (Pydantic)
│   ├── storage.py     # 数据存储 (SQLite/JSONL/CSV)
│   └── config.py      # 配置管理
├── main.py            # CLI 入口脚本
├── dashboard.py       # Streamlit 数据分析看板
└── requirements.txt   # 项目依赖
```

## 📝 常见问题

**Q: 如何获取 category 参数？**
A: 打开 Jumia 对应国家的网站，点击进入某个类目（如 Phones & Tablets），复制 URL 中的路径部分（如 `/phones-tablets/`）即可。

**Q: 支持哪些输出格式？**
A: 
- **JSONL**: 推荐格式，适合大数据量处理。
- **SQLite**: 适合进行 SQL 查询和 Dashboard 展示。
- **CSV**: 适合 Excel 打开查看。

**Q: 采集速度如何？**
A: 爬虫会自动处理分页和图片懒加载，速度取决于网络状况和设置的页数。建议在稳定的网络环境下运行。

## 📄 许可证

MIT License

