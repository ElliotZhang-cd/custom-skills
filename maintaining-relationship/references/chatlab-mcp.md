# ChatLab MCP 部署与查询

数据来源是 A 本机 ChatLab 已导入的聊天记录。本 skill 只读，不写、不导出。

## 一、部署检查（每次会话第一次用到时过一遍）

1. **CLI 是否安装**：终端执行 `clb --version`。没有就装：

   ```bash
   npm install -g chatlab-cli
   ```

   包名是 `chatlab-cli`，但它提供的**命令**是 `clb` 和 `chatlab`（不是 `chatlab-cli`）。

2. **桌面端是否已导入记录**：`clb sessions list`。空列表说明 ChatLab 里还没导入聊天，让 A 先在桌面端导入。

3. **MCP 是否注册**：`~/.zcode/cli/config.json` 里应有

   ```json
   {
     "mcp": {
       "servers": {
         "chatlab": {
           "command": "node",
           "args": [
             "<npm-global-root>/node_modules/chatlab-cli/bin/chatlab.mjs",
             "mcp"
           ]
         }
       }
     }
   }
   ```

   注意是 **`mcp.servers`**（嵌套），不是 `mcpServers`（那是 `.agents/mcp.json` 的兼容写法）。工作区可用 `<repo>/.zcode/config.json` 覆盖。

   **Windows 上必须用 `node` + 绝对路径，不要写 `clb`。** npm 全局装在 Windows 只生成 `clb.cmd` 和 shell 脚本，没有 `.exe`；用 spawn 直接调 `clb` 会 `ENOENT`，调 `clb.cmd` 会 `EINVAL`。实测只有 `node` + `chatlab.mjs` 绝对路径能稳定握手。

   `<npm-global-root>` 怎么取：Windows 是 `%APPDATA%\npm`，macOS/Linux 通常是 `$(npm root -g)` 的上一级，或直接 `npm root -g` 得到 `.../node_modules` 再拼包名。**不要照抄别人的用户名路径**，换机器必然失效。

4. **在线检查**：工具列表里应出现 19 个 `chatlab_*` 工具。没有就是没连上，按上面三步排查，**不要用编造的内容继续分析**。

如果 `clb` 已在 PATH 且不在 Windows 上，用 `{"command": "clb", "args": ["mcp"]}` 更简洁。

## 二、19 个工具

全部只读（`readOnlyHint: true`）。除 `chatlab_list_sessions` 外都强制要求 `session_id`。

| 工具 | 用途 | 主要参数 |
|---|---|---|
| `chatlab_list_sessions` | 列出所有会话 | `keyword` 按名筛选 |
| `chatlab_get_session_info` | 会话详情 | `include_members` |
| `chatlab_get_chat_overview` | 概览 + 活跃成员排行 | `top_n` |
| `chatlab_search_messages` | 关键词搜索，可限时间和发送者 | `keywords[]`、`sender_id`、`start_time`、`end_time`、`limit` |
| `chatlab_deep_search_messages` | LIKE 子串精确匹配 | 同上 |
| `chatlab_get_recent_messages` | 最近消息 | `limit`、`start_time`、`end_time` |
| `chatlab_get_message_context` | 按消息 ID 取前后文 | `message_ids[]` |
| `chatlab_get_segment_messages` | 取整段原文 | `segment_id` |
| `chatlab_get_segment_summaries` | 段落摘要列表 | `keywords[]`、`limit` |
| `chatlab_get_members` | 成员列表与统计 | — |
| `chatlab_get_member_stats` | 活跃度排行 | `top_n` |
| `chatlab_get_time_stats` | 时段分布 | `type`: hourly/weekday/daily/monthly |
| `chatlab_get_member_name_history` | 昵称变更史 | `member_id` |
| `chatlab_get_conversation_between` | 两人对话 | `member_id_1`、`member_id_2` |
| `chatlab_response_time_analysis` | 回复间隔分析 | — |
| `chatlab_keyword_frequency` | 词频统计 | — |
| `chatlab_render_chart` | 出图 | `chartSpec` |
| `chatlab_get_schema` | 表结构 | — |
| `chatlab_execute_sql` | **只读 SELECT**，最强大 | `sql` |

时间参数格式：`YYYY-MM-DD HH:mm`。多数工具支持 `format: "json"`，取结构化数据时用 json，取原文时用默认 text。

## 三、真实表结构（`chatlab_get_schema` 实测）

```sql
member(id, platform_id UNIQUE, account_name, group_nickname, aliases, avatar, roles)
member_name_history(id, member_id, name_type, name, start_ts, end_ts)
message(id, sender_id, sender_account_name, sender_group_nickname,
        ts INTEGER NOT NULL, type INTEGER NOT NULL, content,
        reply_to_message_id, platform_message_id)
message_context(message_id, segment_id, topic_id)
segment(id, start_ts, end_ts, message_count, is_manual, summary, summary_message_count)
meta(name, platform, type, imported_at, group_id, group_avatar, owner_id,
     schema_version, session_gap_threshold)
```

**四个必须记住的坑：**

1. **时间列叫 `ts`，不是 `timestamp`**，类型是 Unix 秒（INTEGER）。
2. **`ts` 是 UTC。** 所有按小时、按天的判断都要加 `'+8 hours'`，否则“深夜发起”会整体偏 8 小时。
   ```sql
   datetime(ts, 'unixepoch', '+8 hours')                 -- 本地时间
   strftime('%Y-%m', ts, 'unixepoch', '+8 hours')        -- 本地年月
   strftime('%H', ts, 'unixepoch', '+8 hours')           -- 本地小时
   ```
3. **`type = 0` 是普通文本**。其他类型（1、7、25、80…）是图片、表情、系统消息等，做文本分析时必须过滤 `type = 0`。
4. **`meta.owner_id` 是 A 的 `platform_id`。** 判定谁是 A、谁是 B，唯一可靠依据就是它。

## 四、A / B 判定

不要靠昵称、不要靠谁消息多。用这一句：

```sql
SELECT CASE WHEN m.platform_id = (SELECT owner_id FROM meta) THEN 'A' ELSE 'B' END AS who,
       COUNT(*) AS n
FROM message g JOIN member m ON m.id = g.sender_id
WHERE g.type = 0
GROUP BY who
```

两个成员时这就是完整分组。群聊里 `owner_id` 仍是 A，其余都归“对方/其他人”，分析前先确认 A 说的是哪个人。

## 五、常用查询范式

**凡是不按 GROUP BY 聚合、可能返回大量行的查询，都要带 `LIMIT`。** 聚合查询（2 个成员、24 个小时、12 个月）结果天然有界，不必强加。工具会截断超量结果，但截断前已经占用了上下文。

`chatlab_execute_sql` 返回字符串单元格默认脱敏，取原文要 `--raw`（CLI）；MCP 这条实测返回明文。

**月度消息量与趋势（追踪 agent 用）**

```sql
SELECT strftime('%Y-%m', ts, 'unixepoch', '+8 hours') AS ym,
       SUM(CASE WHEN m.platform_id = (SELECT owner_id FROM meta) THEN 1 ELSE 0 END) AS a_msgs,
       SUM(CASE WHEN m.platform_id <> (SELECT owner_id FROM meta) THEN 1 ELSE 0 END) AS b_msgs
FROM message g JOIN member m ON m.id = g.sender_id
WHERE g.type = 0
GROUP BY ym ORDER BY ym DESC LIMIT 12
```

**发起方占比（用间隔 > 6 小时判定"新会话"）**

```sql
WITH ordered AS (
  SELECT ts, sender_id, LAG(ts) OVER (ORDER BY ts) AS prev_ts
  FROM message WHERE type = 0
)
SELECT CASE WHEN mem.platform_id = (SELECT owner_id FROM meta) THEN 'A' ELSE 'B' END AS who,
       COUNT(*) AS initiations
FROM ordered o JOIN member mem ON mem.id = o.sender_id
WHERE o.prev_ts IS NULL OR o.ts - o.prev_ts > 21600
GROUP BY who
```

**活跃时段分布（判断"深夜发起"）**

```sql
SELECT CAST(strftime('%H', ts, 'unixepoch', '+8 hours') AS INTEGER) AS hour_local,
       COUNT(*) AS n
FROM message WHERE type = 0
GROUP BY hour_local ORDER BY hour_local
```

**月度回复间隔中位数（修复速度）**

真中位数要用窗口函数算。SQLite 没有内置 `PERCENTILE`：

```sql
WITH pairs AS (
  SELECT ts,
         ts - LAG(ts) OVER (ORDER BY ts) AS gap,
         sender_id,
         LAG(sender_id) OVER (ORDER BY ts) AS prev_sender
  FROM message WHERE type = 0
),
gaps AS (
  SELECT strftime('%Y-%m', ts, 'unixepoch', '+8 hours') AS ym, gap
  FROM pairs
  WHERE prev_sender IS NOT NULL AND prev_sender <> sender_id AND gap < 86400
),
ranked AS (
  SELECT ym, gap,
         ROW_NUMBER() OVER (PARTITION BY ym ORDER BY gap) AS rn,
         COUNT(*) OVER (PARTITION BY ym) AS cnt
  FROM gaps
)
SELECT ym, gap AS median_gap_sec
FROM ranked
WHERE rn = (cnt + 1) / 2
ORDER BY ym DESC LIMIT 12
```

想要平均值（更快、但对极端值敏感）就把 `AVG` 那版留着用，**但不要叫它中位数**。趋势判断用中位数，因为它不被偶发的隔天回复拉偏。

**某话题的全部原文（冲突取证）**

先用 `chatlab_search_messages` 定位，再用 `chatlab_get_message_context` 取前后文。需要精确原文时直接 SQL：

```sql
SELECT id, sender_id, datetime(ts,'unixepoch','+8 hours') AS t, content
FROM message
WHERE type = 0
  AND datetime(ts,'unixepoch','+8 hours') BETWEEN '2026-10-30 00:00' AND '2026-10-30 23:59'
ORDER BY ts LIMIT 300
```

**某月双方各说了多少字（A 的"追加长文"模式）**

```sql
SELECT CASE WHEN m.platform_id = (SELECT owner_id FROM meta) THEN 'A' ELSE 'B' END AS who,
       COUNT(*) AS n, CAST(AVG(LENGTH(g.content)) AS INTEGER) AS avg_len
FROM message g JOIN member m ON m.id = g.sender_id
WHERE g.type = 0 AND strftime('%Y-%m', g.ts,'unixepoch','+8 hours') = '2026-10'
GROUP BY who
LIMIT 10
```

**冲突频率（每日消息量骤降/骤升，追踪 agent 用）**

"冲突"没有标记字段，只能用代理指标：某天消息量突增、且集中在深夜。这是**推理**，不是事实。

```sql
SELECT strftime('%Y-%m-%d', ts, 'unixepoch', '+8 hours') AS d,
       COUNT(*) AS n,
       SUM(CASE WHEN CAST(strftime('%H', ts,'unixepoch','+8 hours') AS INTEGER) >= 23
                  OR CAST(strftime('%H', ts,'unixepoch','+8 hours') AS INTEGER) <= 3
             THEN 1 ELSE 0 END) AS late_night_n
FROM message WHERE type = 0
GROUP BY d HAVING n > 0
ORDER BY d DESC LIMIT 120
```

## 六、哪些指标能算，哪些算不了

追踪 agent 要求的六个指标，只有四个能直接从 SQL 得到。**必须对 A 说清楚哪项是算的、哪项是判的。**

| 指标 | 能否量化 | 做法 |
|---|---|---|
| 冲突频率 | 只能代理 | 用上面的日量异常 + 深夜占比，标推理(中) |
| 平均修复时长 | 可算 | 中位数查询；需人工确认哪段算"修复完成" |
| 消息量 / 主动发起占比 | 可算 | 精确 |
| 亲密表达频率（非性/性分开） | 只能代理 | 关键词命中数，标推理(中)，不能当事实 |
| 蔑视 / 筑墙出现次数 | **算不了** | 纯语义判断。只能逐条读原文标注，且必须给样本量和置信度 |
| 回复间隔中位数 | 可算 | 精确 |

**"蔑视 / 筑墙"这类需要读语义的指标，不要假装能用 SQL 统计。** 正确做法：抽 20–40 条代表性原文，人工（agent）逐条判定，写明"基于 N 条抽样"，置信度标中。抽查样本要说明是怎么选的（如每月前 10 条争执）。

## 七、数据边界（必须对 A 说明一次）

- 记录只有**已导入的部分**。没导入的时段、线下对话、删除的消息、语音转文字失败的内容，都不在数据里。
- 段落摘要（`segment.summary`）是 AI 生成的，用于定位，不是原文。任何引文都要落回 `message.content`。
- 消息数 < 200 或跨度不足三个月：模式识别和趋势判断都降级，并在开头明说降级原因（不是静默降级，也不是完全拒绝分析）。
- `meta.session_gap_threshold` 是 ChatLab 自己的分段阈值；本 skill 的“新会话”判定用 6 小时，两者不同，不要混用。

## 八、排查

| 现象 | 原因 | 处理 |
|---|---|---|
| 工具列表没有 `chatlab_*` | MCP 未注册或启动命令在 Windows 上失效 | 用 `node` + `chatlab.mjs` 绝对路径，别写 `clb` |
| 启动后立刻退出 / `ENOENT` | `clb` 在 Windows 只有 `.cmd`，spawn 找不到 | 同上 |
| `no such column: timestamp` | 列名是 `ts` | 改用 `ts` |
| `no such column: "table"` | SQLite 字符串要用单引号 | 单引号 |
| 返回空数组 | `session_id` 错了，或该时段无 `type = 0` 消息 | 先 `chatlab_list_sessions` 核对 |
| 时间整体偏 8 小时 | 忘了加 `'+8 hours'` | 所有本地时间判断都加 |
| `clb sessions` 报 deprecated | 是别名 | 用 `clb sessions list` |
