# html-to-pdf-skill

一个 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 技能，使用 [Playwright](https://playwright.dev/python/)（无头 Chromium）将 HTML 文件转换为出版级 PDF。

> **功能：** 像浏览器一样精确渲染 HTML，然后导出为 PDF。完整支持 CSS，包括 `@page`、flexbox、grid、Web 字体、SVG 和背景色。

[English](README.md)

## 特性

- **像素级渲染** — 使用无头 Chromium，而非 wkhtmltopdf
- **完整 CSS 支持** — `@page` 规则、flexbox、grid、Web 字体、`@media print`
- **JavaScript 执行** — SPA 和动态内容开箱即用
- **批量转换** — 一条命令转换多个 HTML 文件
- **PDF 书签** — 从 `<h1>`–`<h6>` 标题自动生成目录
- **自定义页眉页脚** — 支持 `{{pageNumber}}` / `{{totalPages}}` 页码
- **可配置布局** — A4/Letter/Legal/A0-A6，纵向/横向，自定义边距
- **无障碍支持** — 可选的 Tagged PDF 输出
- **无需显示服务器** — Linux CI/Docker 无头环境可用

## 安装

### 1. 安装依赖

```bash
pip install playwright
playwright install chromium
```

Linux 环境可能还需要系统库：
```bash
playwright install-deps chromium
```

### 2. 安装技能

将本技能复制到 Claude Code 的技能目录：

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/html-to-pdf-skill.git

# 复制到技能目录
cp -r html-to-pdf-skill ~/.claude/skills/html-to-pdf
```

或手动将文件夹复制到 `~/.claude/skills/html-to-pdf/`。

安装后，当你要求 Claude 将 HTML 转换为 PDF 时，它会自动检测并使用这个技能。

## 使用方法

### 作为 Claude Code 技能

直接用自然语言对 Claude 说：

```
"把这个 HTML 转成 PDF"
"导出 report.html 为 PDF"
"用 A4 格式打印这个页面"
```

Claude 会自动调用这个技能。

### 独立使用（不依赖 Claude Code）

脚本可以独立运行：

```bash
# 基本转换
python scripts/html_to_pdf.py page.html
# -> 生成 page.pdf

# 指定输出路径
python scripts/html_to_pdf.py page.html output.pdf

# 遵循 CSS @page 规则（推荐）
python scripts/html_to_pdf.py --prefer-css-page-size report.html

# 完整出版级布局
python scripts/html_to_pdf.py --prefer-css-page-size --outline --tagged report.html

# 自定义边距
python scripts/html_to_pdf.py --margin-top 2cm --margin-bottom 2.5cm doc.html

# 横向（适合宽表格）
python scripts/html_to_pdf.py --landscape data-table.html

# 批量转换
python scripts/html_to_pdf.py ch1.html ch2.html ch3.html

# 自定义页脚（含页码）
python scripts/html_to_pdf.py \
  --footer-template '<div style="text-align:center;width:100%">第 <span class="pageNumber"></span> 页 / 共 <span class="totalPages"></span> 页</div>' \
  report.html
```

### 全部选项

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

## 环境要求

- Python 3.9+
- Playwright（`pip install playwright`）
- Chromium 浏览器（`playwright install chromium`）

## 工作原理

```
HTML 文件
  -> Playwright Chromium（无头模式）
  -> page.goto(file://, wait_until='networkidle')
  -> page.pdf() 使用可配置选项
  -> 输出 PDF
```

脚本启动一个无头 Chromium 实例，通过 `file://` URL 加载 HTML 文件，等待所有资源加载完成（`networkidle`），然后调用 Chromium 原生的 `Page.printToPDF` CDP 命令。

## 使用技巧

- **使用 `--prefer-css-page-size`** — 当 HTML 包含 `@page { size: A4; margin: 2cm; }` 规则时
- **使用 Web 字体**（Google Fonts、`@font-face`）— 确保跨平台一致的字体渲染
- **使用绝对路径或 data URI** — 避免图片路径解析问题
- **使用 `--outline`** — 为长文档生成可点击的 PDF 书签
- **使用 `@media print`** — 为 PDF 输出设置与屏幕显示不同的样式

## 许可证

MIT
