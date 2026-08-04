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

### 架构

- 本仓库（`~/custom-skills/`）= 4 个自建 skill 的唯一真相源
- 分发：`~/.agents/skills/` → `~/.claude/skills/` 全为符号链接，改本仓库即刻全局生效
- GitHub remote（`ElliotZhang-cd/custom-skills`）= 备份真相源，push 是备份不是分发

### 铁律

1. 自建 skill 绝不进入 openskills 账本（`~/.agents/.skill-lock.json` 只含第三方）；不对自建 skill 跑 `openskills update`（会毁掉链接）
2. `npx skills` 只做发现（`npx skills find`），不做任何写入
3. 编辑只发生在本仓库，不编辑 `~/.claude/skills/` 下的任何目录（全是链接，防止改错副本）
4. 维护面 = 使用面：只维护 opencode + claude 两条链路

### 更新自建

```bash
vim <skill>/...                                    # 编辑真相源，立即生效
git add -A && git commit -m "[skill] 变更说明"
git -c http.proxy=$HTTPS_PROXY -c https.proxy=$HTTPS_PROXY push origin master
```

### 第三方（openskills 管理，不入本仓库）

- 引入：`npx skills find xxx`（发现）→ `npx openskills install owner/repo -y` → `npx openskills sync`
- 更新：发现问题 `npx openskills update <name>`；季度全量 `npx openskills update -y`
- 行尾：`.gitattributes` 强制 LF，避免 Windows 检出 CRLF
