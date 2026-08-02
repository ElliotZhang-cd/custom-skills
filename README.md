# agent-skills

个人自定义技能仓库（WSL 为准）。仅包含自建技能，第三方技能由 `npx skills` 独立管理，不入本仓库。

## 自建技能（本仓库）

| 技能 | 用途 |
|---|---|
| `analyzing-bigfive` | BFI-2 大五人格分析，生成来访者视角 HTML 报告 |
| `analyzing-cognitive-functions` | 荣格八维认知功能分析、MBTI 推断、依恋类型、恋爱适配/情侣报告 |
| `analyzing-complex-systems` | 复杂适应系统分析：反馈回路、涌现行为、战略博弈、临界转变 |
| `maintaining-llm-wiki` | LLM Wiki 知识库维护：入库、查询、lint、派生同步 |

## 常用第三方技能（`npx skills` 管理）

### 文档与办公
- `docx` / `pptx` / `pdf` / `xlsx` — Word/PPT/PDF/Excel 读写与转换
- `ppt-master` — 可编辑 PPTX 生成与模板填充工作流

### 浏览器与自动化
- `browser-use` — CDP 直接控制浏览器（自动化、抓取、截图）
- `playwright-cli` — Playwright 浏览器交互与测试
- `obsidian` — Obsidian vault CLI 读写

### 写作与产品
- `humanizer-zh` — 去除 AI 写作痕迹
- `doc-coauthoring` — 文档共创工作流
- `product-spec-builder` — 产品需求收集与文档编写
- `internal-comms` — 公司内部沟通文案（状态报告、更新、FAQ 等）

### 分析与研究
- `market-research` — 市场调研、竞争分析、投资尽调
- `marketing-campaign` — 营销活动规划与落地
- `ui-ux-pro-max` — UI/UX 设计知识库（风格、配色、字体、动效、图表）

### 方法与流程
- `grill-me` / `grilling` — 方案严苛评审访谈
- `analyzing-complex-systems` — 见自建列表（本地维护版）
- `find-skills` — 发现并安装新技能
- `mcp-builder` — MCP 服务器构建指南
- `template-skill` — 技能模板占位

## 维护

- 自建技能在 `~/.agents/skills/<name>`（git 仓库根），修改后 `git add/commit/push`
- 第三方技能：`npx skills install <name>` 安装/更新，各自环境独立
- 行尾：`.gitattributes` 强制 LF，避免 Windows 检出 CRLF
