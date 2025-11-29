# 部署指南 / Deployment Guide

本指南将帮助您实现项目的"Serverless"自动化部署。

## ⚠️ 关于 Vercel 部署的重要说明

虽然您提到了 Vercel，但对于本项目（Streamlit + Playwright），Vercel **不是**最佳选择，原因如下：

1.  **Streamlit 不兼容**: Streamlit 需要长连接（WebSocket）来保持交互状态，而 Vercel Serverless Functions 是无状态且短连接的，会导致应用无法正常运行或频繁断开。
2.  **Playwright 超时风险**: Vercel 函数通常有 10-60 秒的执行限制。爬虫任务通常需要几分钟甚至更久，极易超时被杀。
3.  **体积限制**: Playwright 浏览器二进制文件很大，容易超出 Vercel 的 50MB 函数体积限制。

---

## ✅ 推荐方案：Streamlit Cloud + GitHub Actions

为了达到"自动部署"和"无服务器管理"的目标，我们推荐以下组合方案：

### 1. 前端部署：Streamlit Cloud (免费且官方支持)

Streamlit Cloud 是部署 Streamlit 应用的最佳平台，支持 GitHub 自动同步。

**步骤：**
1.  访问 [share.streamlit.io](https://share.streamlit.io/) 并使用 GitHub 登录。
2.  点击 "New app"。
3.  选择您的仓库 (`playwright_jumia`)、分支 (`main` 或 `deploy-vercel`) 和主文件 (`dashboard.py`)。
4.  点击 "Deploy"。

**配置依赖：**
项目中的 `requirements.txt` 会被自动识别安装。

### 2. 爬虫自动化：GitHub Actions (Serverless 运行)

利用 GitHub Actions 的免费计算资源，我们可以定时运行爬虫，并将数据自动保存回仓库。

**已为您创建的工作流文件**: `.github/workflows/scrape.yml`

**功能：**
*   **定时运行**: 每天 UTC 00:00 (北京时间 08:00) 自动执行。
*   **手动触发**: 可以在 GitHub Actions 页面手动点击运行。
*   **数据持久化**: 爬取的数据会自动 commit 并 push 回仓库，Dashboard 会自动更新。

---

## 🧪 Vercel 部署尝试 (仅供参考)

如果您坚持尝试 Vercel，我们提供了一个实验性的 `vercel.json` 配置，但请注意：
*   仅能运行极简单的 Python 脚本。
*   Streamlit 界面**无法**在 Vercel 上正常工作。
*   爬虫极大概率会超时。

要尝试 Vercel，请安装 Vercel CLI 并运行 `vercel`，或在 Vercel 控制台导入此项目。
