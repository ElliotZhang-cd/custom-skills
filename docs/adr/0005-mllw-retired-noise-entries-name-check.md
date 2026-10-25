# mllw 类别退役（并入自建）、面内噪音裁定（noise_entries）与目录名/frontmatter 一致性判定（[NAME]）

日期：2026-10-25　状态：已实施

## 背景

- `maintaining-llm-wiki` 原是独立于 custom-skills 的「第二个来源」（LLMWiki 仓库内，`mllw` 来源类别）。
- 2026-10-17 commit `52593cf` 把它迁入本仓库（「自建技能收敛为一个 git 仓库」），但声明层与文档没有跟着收敛：清单各面的 `expect` 仍含 `mllw`、三个同步/判定脚本仍带 mllw 分支与 LLMWiki 源探测、五处文档仍按「两个真相源」教操作（README 手写散文与它自己的生成表直接矛盾——生成表已把 mllw 列为自建）。两端对账长期打印 `mllw 0`：类别已成空壳，只剩漂移成本。
- 同时暴露两个判定盲区：① `Humanizer-zh-main`（手工副本，目录名 ≠ frontmatter `name: humanizer-zh`）与 junction 版同名件在 ZCode 里构成双注册，对账按目录名判、看不见这层冲突；② workbuddy 面常驻 16 条 `[UNK]` 市场件倾倒——`known_noise` 只能裁定整目录，盖不住已登记面内部的条目，该面"永远不绿"。

## 决定

1. **mllw 一刀切退役**：清单 `expect` 不再有 `mllw`（自检词表同步收紧，残留即报错）；`check_distribution.py` / `ensure_junctions.ps1` / `sync-wsl.sh` / `gen-skills-table.py` 的 mllw 分支与 LLMWiki 源探测全部移除；文档五处（SKILL.md、environment / workflows / reconciliation、README、architecture）随改。`maintaining-llm-wiki` 技能包内的 `install_links.sh` / `check_skill_links.py` 随迁移失去服务对象——保留文件不动技能包，但体系不再引用。
2. **噪音裁定两档粒度**：`known_noise`（整目录，原有）+ `noise_entries`（面 id + 名单 + 理由，新增）。已裁定条目从 `[UNK]` 降为一行 `[裁定]`，且**不再抑制该面的 `[OK]`**——裁定是治"永不绿"的正道；数量或构成一变仍须重新裁定（I8 不变）。
3. **新增 `[NAME]` 提醒级判定**：面内条目目录名 ≠ frontmatter `name` 即点名（已裁定噪音除外）。抑制 `[OK]` 但不改退出码——它抓的是"工具按 name 注册"层的同名重复，[CONFLICT] 抓的是声明层的同名，两者互补。
4. 顺带三项：① 两端同步脚本支持 `--strict`（对账失败 → 退出码 1，供计划任务/钩子），失败时打印「未完成」不再假报「完成」；② 新增 `check-all.bat` 跨端一键对账（任一端失败退出码 1）；③ ZCode 对 `~/.agents/skills` 的原生扫描造成的第三方双注册，裁定为**已接受冗余**（保留 junction，不依赖原生扫描行为），记在 zcode 面 `note`。

## 后果

- 正面：声明层回到与事实一致（来源三类）；对账信息量上升（workbuddy 回绿、同名重复可见）；退出码可承载自动化。
- 代价/风险：`[NAME]` 可能点名 frontmatter 与目录名有意不同的存量件（当前这类只存在于已裁定噪音里，已被排除）；若未来某工具要求 name ≠ 目录名，把该名字裁定进噪音机制即可。
- 回退路径：git revert 本次提交系列即可（mllw 池本身已空，回退无数据损失，但文档漂移会回来）。
