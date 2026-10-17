# Windows 的 `~/.agents/skills` 是 npx 的仓库层，只能由 npx 写

Windows 侧 `%USERPROFILE%\.agents\skills` 从 2026-10-17 起是**第三方技能的仓库层**：由 `npx skills` 的全局模式写（它的全局根硬编码为 `<home>/.agents/skills`，**没有任何环境变量能改**），权威是同一目录下的 `.skill-lock.json`。**机主裁定：第三方 skill 统一由 npx 管理，且 npx 只管仓库层、不管平台**（见 `docs/adr/0001`、`docs/adr/0002`）——各平台面上的第三方是对这一层的**链接**，由同步脚本建、由对账检查。

历史与本决定的边界：2026-09-03 曾删除该目录，因为它是 2026-07-03 的**冻结快照**——脱离管理近两个月，`maintaining-llm-wiki` 还是缺三个工作流文件的旧架构。**病根是"无人管理的陈旧内容"，不是目录本身**。所以现在仍然禁止：手工往里放或改技能、让它变陈旧、把它当自建技能的存放处（自建只在本仓库，走链接分发）。

## Consequences

- DSH 会按固定 rank 扫 `<agentsHome>/skills`（rank 500）并把内容当技能加载——**现在这是期望行为**（第三方因此对 DSH 可见），代价是这里的内容必须始终新鲜：只准 npx 写。
- 两套存储（WSL `~/.agents/skills` 与 Windows 同名目录）+ 两套锁是**按平台**的第三方真相（`docs/adr/0001`）。它们是两回事，**不要相互"对齐"**；跨平台差异靠对账点名，不靠脚本抹平。
- 对账上它是一个普通的 win 面：`role=storage`、`expect=["thirdparty"]`。`ensure_junctions.ps1` 只处理 `role=junction`，不会碰它。
- 它一旦存在，Windows 端的第三方池就不再结构性为空（`check_distribution.py` 读的就是这个目录下的锁）。
- **已知缺口**：`npx skills`（v1.7.0）的 agent 表里有 `zcode`，但**没有 `dsh` / `workbuddy`**——它不会往那两个面物化，那两侧仍需手工副本（登记表）或另写脚本补。

## Considered Options

- **保持禁令，Windows 只用非全局（项目级）npx**：不建该目录，但第三方在 Windows 变成"按项目"而不是"按平台"，与"各 agent 平台的技能列表"这个目标不对齐，且项目级技能根不在清单模型内。
- **保持禁令，Windows 完全不跑 npx**（2026-09-03 – 2026-10-17 的现状）：Windows 各面的第三方只能手工复制，靠登记表记账；漂移只能靠对账点名。
- **收编为存储面**（选定）：与"第三方由 npx 管"一致，且 DSH 顺带获得第三方可见性。
