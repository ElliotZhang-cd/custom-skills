# 手工技能登记表（manual-skills.md）

> 记录不由同步脚本分发、由人工放置的第三方技能（现存目标：ZCode、DSH）。它们在分发目标里是**真实副本**，不是链接。
> `check_distribution.py` 读取本表：有账的名字不再算「多余」，漏登则该名字会以提醒形式出现（仅列出、不报错）。
> 入账纪律：名字若在锁文件 `~/.agents/.skill-lock.json` 里，**来源以锁文件为准**（取 `sourceUrl`）；查不到就写「来源不详」，不要留空。
> workbuddy 的市场件由其自身市场机制管理，不入本账。
> 新增/下线分发目标：把目录复制到该目标的 skills 下（或删除），并在本表「所在目标」列补/删该目标名。漏改只会产生提醒，不会报错。

| 名字 | 来源 | 一句话 | 更新时间 | 所在目标 |
|---|---|---|---|---|
| Humanizer-zh-main | humanizer-zh（具体仓库待确认） | 去除文本 AI 生成痕迹 | 2026-08-23 | ZCode+DSH |
| domain-modeling | github.com/mattpocock/skills | 构建打磨项目领域模型（CONTEXT.md/ADR），grill-with-docs 的依赖 | 2026-08-23 | ZCode+DSH |
| grill-me | github.com/mattpocock/skills | 拷问式访谈打磨计划/设计（内部调用 grilling） | 2026-08-23 | ZCode+DSH |
| grill-with-docs | github.com/mattpocock/skills | 拷问式访谈 + 顺带产出 ADR 和术语表（编排 grilling + domain-modeling） | 2026-08-23 | ZCode+DSH |
| grilling | github.com/mattpocock/skills | 可复用拷问原语（设计树 + 分轮问 frontier），被 grill-me / grill-with-docs 依赖 | 2026-08-23 | ZCode+DSH |
| handoff | github.com/mattpocock/skills | 把当前对话压缩成交接文档 | 2026-08-23 | ZCode+DSH |
| market-research | skills CLI（WSL 锁文件） | Conduct market research, competitive analysis, investor due … | 2026-08-13 | ZCode+DSH |
| marketing-campaign | skills CLI（WSL 锁文件） | End-to-end marketing campaign planning and execution. Covers… | 2026-08-13 | ZCode+DSH |
| ppt-master | skills CLI（WSL 锁文件） | AI-driven presentation workflow for generating editable PPTX… | 2026-08-13 | ZCode+DSH |
| guizang-ppt-skill | skills CLI（WSL 锁文件） | 生成横向翻页单文件 HTML 网页 PPT（杂志风/瑞士风双视觉系统，含演讲者模式、AI 配图、多平台封面） | 2026-09-06 | ZCode+DSH |
| huashu-design | alchaincyf/huashu-design（skills CLI WSL 锁文件） | 花叔 Design：HTML 原生设计系统，高保真原型/幻灯片/动画/可视化，20 种设计哲学 + 5 维专家评审（任何新设计强制先出三个方向初稿再执行） | 2026-09-16 | ZCode+DSH |
| teach | github.com/mattpocock/skills | 在工作区内多会话教你新技能/概念 | 2026-08-23 | ZCode+DSH |
| to-questionnaire | github.com/mattpocock/skills | 把答不了的决策转成问卷给别人填 | 2026-08-23 | ZCode+DSH |
| ui-ux-pro-max | skills CLI（WSL 锁文件） | UI/UX design intelligence for web and mobile. Searchable loc… | 2026-08-13 | ZCode+DSH |
| wait-what | github.com/mattpocock/skills | 消息没落地时停止并用统一语言重述 | 2026-08-23 | ZCode+DSH |
| writing-for-agents | github.com/mattpocock/skills | 给 agent 写文档（skills/AGENTS.md/CLAUDE.md） | 2026-08-23 | ZCode+DSH |
| archify | tt-a1i/archify（skills CLI WSL 锁文件，v3.0.1；Windows 两面为同版本手动副本） | Agent 出 JSON IR → 校验 → 编译成单文件可交互架构/流程/时序/数据流/生命周期图，带机器可读修复回执 | 2026-09-30 | ZCode+DSH |
| agent-browser | 来源不详 | Browser automation CLI for AI agents. Use when the user need… | 2026-08-13 | ZCode+DSH |
| ai-textbook-distilling | 来源不详 | Distills multiple textbooks and lecture videos into one priv… | 2026-08-24 | ZCode+DSH |
| banner-design | 来源不详 | Design banners for social media, ads, website heroes, creati… | 2026-08-13 | ZCode+DSH |
| brand | 来源不详 | Brand voice, visual identity, messaging frameworks, asset ma… | 2026-08-13 | ZCode+DSH |
| chart-visualization | 来源不详 | This skill should be used when the user wants to visualize d… | 2026-08-13 | ZCode+DSH |
| consulting-analysis | 来源不详 | Use this skill when the user requests to generate, create, o… | 2026-08-13 | ZCode+DSH |
| data-analysis | 来源不详 | Use this skill when the user uploads Excel (.xlsx/.xls) or C… | 2026-08-13 | ZCode+DSH |
| design | 来源不详 | Comprehensive design skill: brand identity, design tokens, U… | 2026-08-13 | ZCode+DSH |
| design-system | 来源不详 | Token architecture, component specifications, and slide gene… | 2026-08-13 | ZCode+DSH |
| frontend-design | 来源不详 | Create distinctive, production-grade frontend interfaces wit… | 2026-08-13 | ZCode+DSH |
| gh-cli | 来源不详 | GitHub CLI (gh) comprehensive reference for repositories, is… | 2026-08-13 | ZCode+DSH |
| git-commit | 来源不详 | Execute git commit with conventional commit message analysis… | 2026-08-13 | ZCode+DSH |
| slides | 来源不详 | Create strategic HTML presentations with Chart.js, design to… | 2026-08-13 | ZCode+DSH |
| ui-styling | 来源不详 | Create beautiful, accessible user interfaces with shadcn/ui … | 2026-08-13 | ZCode+DSH |

> 依赖：`grill-me` → `grilling`；`grill-with-docs` → `grilling` + `domain-modeling`。
> 目录名变体：`Humanizer-zh-main` 对应锁文件中的 `humanizer-zh`，待归一。
> 更新：2026-10-03，共 31 条（来源不详 14 条）；brainstorming / test-driven-development / writing-plans 三件已溯源为 obra/superpowers v5.0.6/5.0.7（2026-03），本机清理删除。
