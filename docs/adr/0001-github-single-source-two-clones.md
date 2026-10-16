# GitHub 仓库是唯一源头，WSL 与 Windows 各持一个可编辑 clone

自建技能的唯一源头是 GitHub 上的 `ElliotZhang-cd/custom-skills`；WSL `~/custom-skills/` 与 Windows `%USERPROFILE%\custom-skills` 都是它的 clone，两端都能编辑，但**只有 push 才算发布**——分发目标目录里的任何改动都不算数。

## Considered Options

- **单端权威**（WSL 为主、Windows 只读）：冲突面最小，但 Windows 侧改一行也要开 WSL。
- **两端都可编辑**（选定）：任一端都能改，代价是必须守「改前先 pull、改完立刻 commit + push」，否则 `--ff-only` 守卫会挡住另一端（2026-08-11 实证：Windows 侧未提交的改动加一个 0 字节 untracked 文件，让 WSL 的 pull 直接失败）。
- 2026-10-17 的 TRAE 实证补上另一半：在工具面板里删技能是**目标级删除**，会连带删掉本体系的链接与手工副本；只在本地删、不在工具自己的账里删，还会被工具从云端复活。

## Consequences

- 两个 clone 必须指向同一 commit，否则两端会各自"对齐"到不同真相。
- 分发是**人肉触发**的：push 不会自动让另一端生效，必须跑 `sync-wsl.sh` / `sync-custom-skills.bat`。这是已知接受风险。
