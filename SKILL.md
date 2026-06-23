---
name: html-to-pdf
description: >
  使用 Playwright（无头 Chromium）将 HTML 文件转换为出版级 PDF。
  当用户要求「HTML 转 PDF」「打印为 PDF」「导出 PDF」「从网页生成 PDF」或任何 HTML 转 PDF 请求时触发。
  支持 @page CSS、自定义边距、PDF 书签、自定义页眉页脚、批量转换。
author: 码孖AI
license: MIT
triggers:
  - html to pdf
  - html转pdf
  - 转pdf
  - 导出pdf
  - 打印pdf
  - convert to pdf
  - print to pdf
  - export pdf
allowed-tools:
  - Bash
  - Read
  - Glob
---

# HTML 转 PDF

使用 Playwright（无头 Chromium）将 HTML 文件转换为出版级 PDF。
渲染效果与浏览器完全一致，完整支持 `@page`、flexbox、grid、Web 字体、SVG 和背景色等 CSS 特性。

## 环境检查（首次运行）

```bash
# 检查 Python
python --version 2>/dev/null || python3 --version 2>/dev/null
# 检查 playwright
python -c "import playwright; print('playwright OK')" 2>/dev/null || python3 -c "import playwright; print('playwright OK')" 2>/dev/null
# 检查 chromium 浏览器
python -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(); b.close(); p.stop(); print('chromium OK')" 2>/dev/null
```

如果任一检查失败，安装依赖：

```bash
pip install playwright
playwright install chromium
```

Linux CI/Docker 环境可能还需要系统依赖：
```bash
playwright install-deps chromium
```

## 基本用法

转换脚本位于本 skill 目录下的 `scripts/html_to_pdf.py`。

确定脚本路径：
```bash
_SKILL_DIR=""
[ -n "$HOME" ] && [ -f "$HOME/.claude/skills/html-to-pdf/scripts/html_to_pdf.py" ] && _SKILL_DIR="$HOME/.claude/skills/html-to-pdf"
[ -z "$_SKILL_DIR" ] && [ -f ".claude/skills/html-to-pdf/scripts/html_to_pdf.py" ] && _SKILL_DIR=".claude/skills/html-to-pdf"
# 兜底：搜索脚本位置
[ -z "$_SKILL_DIR" ] && _SKILL_DIR=$(find "$HOME/.claude" -path "*/html-to-pdf/scripts" -type d 2>/dev/null | head -1 | sed 's|/scripts$||')
```

### 最常用场景 — 基本转换

```bash
python "$_SKILL_DIR/scripts/html_to_pdf.py" page.html
# -> 生成 page.pdf（同目录、同名）

python "$_SKILL_DIR/scripts/html_to_pdf.py" page.html output.pdf
# -> 指定输出路径 output.pdf
```

### 遵循 CSS @page 规则（推荐）

当 HTML 包含 `@page { size: A4; margin: 2cm; }` 规则时：

```bash
python "$_SKILL_DIR/scripts/html_to_pdf.py" --prefer-css-page-size page.html
```

自动使用 CSS 中定义的页面尺寸和边距。

### 批量转换

```bash
python "$_SKILL_DIR/scripts/html_to_pdf.py" ch1.html ch2.html ch3.html
# -> 生成 ch1.pdf, ch2.pdf, ch3.pdf
```

## 全部选项

```
页面布局:
  --format FORMAT             纸张大小: A4 (默认), Letter, Legal, A0-A6
  --landscape                 横向打印
  --prefer-css-page-size      使用 @page CSS 规则（推荐）
  --margin-top DIM            上边距 (如 2cm, 1in, 72pt)
  --margin-right DIM          右边距
  --margin-bottom DIM         下边距
  --margin-left DIM           左边距

功能:
  --outline                   从标题生成 PDF 书签
  --tagged                    添加无障碍标签
  --scale N                   缩放比例 (默认 1.0)
  --no-background             不打印背景色/图片

页眉页脚:
  --header-template HTML      页眉 HTML 模板
  --footer-template HTML      页脚 HTML 模板

输出:
  --quiet, -q                 静默模式
```

## 常见场景

### 完整出版级布局

```bash
python "$_SKILL_DIR/scripts/html_to_pdf.py" \
  --prefer-css-page-size --outline --tagged \
  report.html report.pdf
```

### Letter 尺寸 + 自定义边距

```bash
python "$_SKILL_DIR/scripts/html_to_pdf.py" \
  --format Letter \
  --margin-top 1in --margin-bottom 1in \
  --margin-left 1.2in --margin-right 1.2in \
  doc.html doc.pdf
```

### 横向打印（适合宽表格）

```bash
python "$_SKILL_DIR/scripts/html_to_pdf.py" \
  --landscape --format A4 \
  data-table.html data-table.pdf
```

### 自定义页眉页脚

页脚显示页码：`Page <span class="pageNumber"></span> of <span class="totalPages"></span>`

```bash
python "$_SKILL_DIR/scripts/html_to_pdf.py" \
  --footer-template '<div style="font-size:9px;text-align:center;width:100%">Page <span class="pageNumber"></span> / <span class="totalPages"></span></div>' \
  report.html report.pdf
```

## 何时触发此 Skill

当用户表达 HTML 转 PDF 的意图时触发，包括：

- 「把这个 HTML 转成 PDF」
- 「导出为 PDF」
- 「打印为 PDF」
- 「从这个页面生成 PDF」
- 「把这个 HTML 做成 PDF」
- 用户打开了 HTML 文件并要求生成 PDF

## 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 背景色丢失 | `print_background` 被覆盖 | 确保未设置 `--no-background` |
| 字体显示异常 | 系统缺少字体 | 使用 Web 字体（Google Fonts CDN）或 `@font-face` 嵌入 |
| 图片缺失 | 相对路径未解析 | 使用绝对路径或 `file://` 基础 URL；确认图片文件存在 |
| @page CSS 无效 | 未设置对应参数 | 添加 `--prefer-css-page-size` |
| PDF 空白 | JS 渲染内容未等待 | 脚本已使用 `wait_until='networkidle'`，通常可覆盖大部分情况 |
| `playwright install` 失败 | 缺少系统依赖（Linux） | 运行 `playwright install-deps chromium` |
| PDF 文件过大 | 高分辨率图片 | 压缩 HTML 源码中的图片 |
| 文字不可选中 | 扫描件/图片内容 | 属正常现象；扫描件请使用 OCR 工具 |

## 技术说明

- **渲染引擎**：Playwright Chromium（无头模式，无需显示服务器）
- **Python 版本**：3.9+
- **CSS 支持**：完整支持 — @page、flexbox、grid、Web 字体、SVG、@media print
- **JavaScript**：会执行（不同于 wkhtmltopdf）；SPA 和动态内容可正常工作
- **输出格式**：标准 PDF，可选书签和 accessibility 标签
- **并发**：逐文件处理（每个文件启动一个 Chromium 实例）
