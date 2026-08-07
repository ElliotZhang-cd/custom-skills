# hermes-skills.md — Hermes 侧技能档案（Windows）

> 记录**非内置**（非 builtin）的 Hermes 技能：来源、用途、安装/更新方式。
> 安装状态以 `hermes skills list` 为准；本文档只补静态字段（description / source / howtoinstall），装/卸技能时顺手更新。
> 与 `README.md`（WSL 侧，opencode/claude 链路）互为镜像：README 管自建 4 个 + openskills 第三方，本文档管 Hermes（Windows）侧。

## 当前收录（4）

### 1. guizang-ppt-skill — 归藏网页 PPT

- **description**：生成单文件 HTML 横向翻页 PPT（电子杂志风 / 瑞士国际主义风），含 WebGL 背景、22 种瑞士版式、多平台封面（公众号/小红书/视频号）、Codex 配图管线
- **source**：https://github.com/op7418/guizang-ppt-skill （AGPL-3.0）
- **howtoinstall**（Hermes/Windows）：
  ```bash
  # 安装（git clone，保留仓库形态以支持 skill 内置的更新检查）
  git -c http.proxy=http://127.0.0.1:7890 clone https://github.com/op7418/guizang-ppt-skill \
    "$HERMES_HOME/skills/guizang-ppt-skill"
  # 更新
  git -C "$HERMES_HOME/skills/guizang-ppt-skill" pull --ff-only
  ```
- **备注**：SKILL.md 在仓库根目录 + 带子目录资源，Hermes Hub 源（skills.sh / URL 直装）均无法解析，只能手动 clone

### 2. grill-me — 评审访谈入口

- **description**：A relentless interview to sharpen a plan or design.（/grilling 会话入口）
- **source**：https://github.com/mattpocock/skills （skills/productivity/grill-me）
- **howtoinstall**（Hermes/Windows）：
  ```bash
  # 安装（需代理环境变量 + HERMES_ALLOW_PRIVATE_URLS=true + .env 中 GITHUB_TOKEN）
  export HTTP_PROXY=http://127.0.0.1:7890 HTTPS_PROXY=http://127.0.0.1:7890 HERMES_ALLOW_PRIVATE_URLS=true
  hermes skills install skills-sh/mattpocock/skills/grill-me -y
  # 更新
  hermes skills update grill-me
  ```

### 3. grilling — 完整评审访谈流程

- **description**：Grill the user relentlessly about a plan, decision, or idea.（设计树分轮问询，每轮问完整 frontier 并给出推荐答案）
- **source**：https://github.com/mattpocock/skills （skills/productivity/grilling）
- **howtoinstall**（Hermes/Windows）：
  ```bash
  export HTTP_PROXY=http://127.0.0.1:7890 HTTPS_PROXY=http://127.0.0.1:7890 HERMES_ALLOW_PRIVATE_URLS=true
  hermes skills install skills-sh/mattpocock/skills/grilling -y
  # 更新
  hermes skills update grilling
  ```

### 4. cangjie-skill — 长内容蒸馏为技能

- **description**：把书/长视频/播客/课程/访谈蒸馏成一组原子化、可被 agent 调用的 skills（RIA-TV++ 方法论：Adler 理解 → 5 agent 并行提取 → 三重验证 → RIA++ 构造 → Zettelkasten 链接 → 压力测试）。NOT 书摘/读后感
- **source**：https://github.com/kangarooking/cangjie-skill （Hermes 适配版）
- **howtoinstall**：已由适配会话安装至 `$HERMES_HOME/skills/cangjie-skill/`（含 methodology/、extractors/、templates/）；更新需手动同步上游

## 维护规则

- 新增：装完顺手在本文档加一行（name/description/source/howtoinstall 四字段）
- 卸载：从本文档移除
- 安装状态核对：`hermes skills list`（Source 列区分 builtin / local / skills.sh）
- 本文件与 `README.md` 互不覆盖：README 的清单只管 WSL 侧（~/.agents/skills + ~/.claude/skills 符号链接链）
