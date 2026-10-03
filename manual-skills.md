# 手动安装第三方技能账本（manual-skills.md）

> 记录不经 sync-windows.bat 自建分发、由人工放置的第三方 skill（现存面：TRAE、ZCode）。
> check_distribution.py 读取本表，把对账时的 UNKNOWN 升格为「有账手动件」；「待溯源」条目需人工补来源。
> workbuddy 的 skillhub/市场件由其自身市场机制管理，不入本账。

| 名字 | 来源 | 一句话 | 更新时间 | 所在面 |
|---|---|---|---|---|
| Humanizer-zh-main | humanizer-zh（具体仓库待确认） | 去除文本 AI 生成痕迹 | 2026-08-23 | TRAE+ZCode |
| domain-modeling | github.com/mattpocock/skills | 构建打磨项目领域模型（CONTEXT.md/ADR），grill-with-docs 的依赖 | 2026-08-23 | TRAE+ZCode |
| grill-me | github.com/mattpocock/skills | 拷问式访谈打磨计划/设计（内部调用 grilling） | 2026-08-23 | TRAE+ZCode |
| grill-with-docs | github.com/mattpocock/skills | 拷问式访谈 + 顺带产出 ADR 和术语表（编排 grilling + domain-modeling） | 2026-08-23 | TRAE+ZCode |
| grilling | github.com/mattpocock/skills | 可复用拷问原语（设计树 + 分轮问 frontier），被 grill-me / grill-with-docs 依赖 | 2026-08-23 | TRAE+ZCode |
| handoff | github.com/mattpocock/skills | 把当前对话压缩成交接文档 | 2026-08-23 | TRAE+ZCode |
| market-research | skills CLI（WSL 锁文件） | Conduct market research, competitive analysis, investor due … | 2026-08-13 | TRAE+ZCode |
| marketing-campaign | skills CLI（WSL 锁文件） | End-to-end marketing campaign planning and execution. Covers… | 2026-08-13 | TRAE+ZCode |
| ppt-master | skills CLI（WSL 锁文件） | AI-driven presentation workflow for generating editable PPTX… | 2026-08-13 | TRAE+ZCode |
| guizang-ppt-skill | skills CLI（WSL 锁文件） | 生成横向翻页单文件 HTML 网页 PPT（杂志风/瑞士风双视觉系统，含演讲者模式、AI 配图、多平台封面） | 2026-09-06 | TRAE+ZCode |
| huashu-design | alchaincyf/huashu-design（skills CLI WSL 锁文件） | 花叔 Design：HTML 原生设计系统，高保真原型/幻灯片/动画/可视化，20 种设计哲学 + 5 维专家评审（任何新设计强制先出三个方向初稿再执行） | 2026-09-16 | TRAE+ZCode |
| teach | github.com/mattpocock/skills | 在工作区内多会话教你新技能/概念 | 2026-08-23 | TRAE+ZCode |
| to-questionnaire | github.com/mattpocock/skills | 把答不了的决策转成问卷给别人填 | 2026-08-23 | TRAE+ZCode |
| ui-ux-pro-max | skills CLI（WSL 锁文件） | UI/UX design intelligence for web and mobile. Searchable loc… | 2026-08-13 | TRAE+ZCode |
| wait-what | github.com/mattpocock/skills | 消息没落地时停止并用统一语言重述 | 2026-08-23 | TRAE+ZCode |
| writing-for-agents | github.com/mattpocock/skills | 给 agent 写文档（skills/AGENTS.md/CLAUDE.md） | 2026-08-23 | TRAE+ZCode |
| archify | tt-a1i/archify（skills CLI WSL 锁文件，v3.0.1；Windows 两面为同版本手动副本） | Agent 出 JSON IR → 校验 → 编译成单文件可交互架构/流程/时序/数据流/生命周期图，带机器可读修复回执 | 2026-09-30 | TRAE+ZCode |
| agent-browser | 待溯源 | Browser automation CLI for AI agents. Use when the user need… | 2026-08-13 | TRAE+ZCode |
| ai-textbook-distilling | 待溯源 | Distills multiple textbooks and lecture videos into one priv… | 2026-08-24 | TRAE+ZCode |
| banner-design | 待溯源 | Design banners for social media, ads, website heroes, creati… | 2026-08-13 | TRAE+ZCode |
| brand | 待溯源 | Brand voice, visual identity, messaging frameworks, asset ma… | 2026-08-13 | TRAE+ZCode |
| chart-visualization | 待溯源 | This skill should be used when the user wants to visualize d… | 2026-08-13 | TRAE+ZCode |
| consulting-analysis | 待溯源 | Use this skill when the user requests to generate, create, o… | 2026-08-13 | TRAE+ZCode |
| data-analysis | 待溯源 | Use this skill when the user uploads Excel (.xlsx/.xls) or C… | 2026-08-13 | TRAE+ZCode |
| design | 待溯源 | Comprehensive design skill: brand identity, design tokens, U… | 2026-08-13 | TRAE+ZCode |
| design-system | 待溯源 | Token architecture, component specifications, and slide gene… | 2026-08-13 | TRAE+ZCode |
| frontend-design | 待溯源 | Create distinctive, production-grade frontend interfaces wit… | 2026-08-13 | TRAE+ZCode |
| gh-cli | 待溯源 | GitHub CLI (gh) comprehensive reference for repositories, is… | 2026-08-13 | TRAE+ZCode |
| git-commit | 待溯源 | Execute git commit with conventional commit message analysis… | 2026-08-13 | TRAE+ZCode |
| slides | 待溯源 | Create strategic HTML presentations with Chart.js, design to… | 2026-08-13 | TRAE+ZCode |
| ui-styling | 待溯源 | Create beautiful, accessible user interfaces with shadcn/ui … | 2026-08-13 | TRAE+ZCode |

> 依赖：`grill-me` → `grilling`；`grill-with-docs` → `grilling` + `domain-modeling`。
> 目录名变体：`Humanizer-zh-main` 对应锁文件中的 `humanizer-zh`，待归一。
> 更新：2026-10-03，共 31 条（待溯源 14 条）；brainstorming / test-driven-development / writing-plans 三件已溯源为 obra/superpowers v5.0.6/5.0.7（2026-03），本机清理删除。
