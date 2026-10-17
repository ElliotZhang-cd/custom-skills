# 自建 skill 的真相源是 GitHub 仓库；第三方 skill 由 npx 管理

**自建技能**的唯一源头是 GitHub 上的 `ElliotZhang-cd/custom-skills`：WSL `~/custom-skills/` 与 Windows `%USERPROFILE%\custom-skills` 都是它的 clone，两端都能编辑，但**只有 push 才算发布**——分发目标目录里的任何改动都不算数。

**第三方技能**不属于本仓库、也不由本仓库分发：它们由 `npx skills` 管理，权威是**该平台自己的仓库层与锁**（`<home>/.agents/skills` + `.skill-lock.json`，按平台各一份）。本体系对第三方只负责两件事：在分发清单里声明「哪个平台应该有第三方技能」，以及把实际落地的条目点出来对账。

> 本文只讲**决定与理由**；分层、归属、不变量、形态表一律见 `docs/architecture.md`（避免两处各自描述同一结构）。

一句话分界：**自建看 git，第三方看 npx。** 两者都不允许手工在分发目标里改（那是"无账拷贝"）。

## Considered Options

- **单端权威**（WSL 为主、Windows 只读）：冲突面最小，但 Windows 侧改一行也要开 WSL。
- **两端都可编辑**（选定，仅针对自建技能）：任一端都能改，代价是必须守「改前先 pull、改完立刻 commit + push」，否则 `--ff-only` 守卫会挡住另一端（2026-08-11 实证：Windows 侧未提交的改动加一个 0 字节 untracked 文件，让 WSL 的 pull 直接失败）。
- **自建也交给 `npx skills` 管**（否决）：它会把链接换成 GitHub 拷贝、覆盖本地修改（见 `docs/adr/0002`）。
- 2026-10-17 的 TRAE 实证补上另一半：在工具面板里删技能是**目标级删除**，会连带删掉本体系的链接与手工副本；只在本地删、不在工具自己的账里删，还会被工具从云端复活。

## Consequences

- 两个 clone 必须指向同一 commit，否则两端会各自"对齐"到不同真相。
- 自建的分发是**人肉触发**的：push 不会自动让另一端生效，必须跑 `sync-wsl.sh` / `sync-custom-skills.bat`。这是已知接受风险。
- 第三方的"真相"是**按平台**的（各端一份锁），所以第三方集合跨平台不一致是常态，靠对账点名叫人裁决，而不是靠同步脚本抹平。
- 第三方在本体系里的**形态由来源决定**：已进该平台仓库层的名字，在各链接面上是**链接**（→ 仓库层）；只有"尚未纳入 npx"的名字才是真实副本（登记在 `manual-skills.md`）。形态表见 `docs/architecture.md`。
