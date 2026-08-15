#!/usr/bin/env python3
"""更新 README.md 的“当前状态”段（自动生成部分）。

用法: python3 update_readme.py [wiki_root]
  wiki_root 可选，默认平台自识别（见 wiki_paths.py）
"""
import os, re, sys, pathlib, datetime
from wiki_paths import default_wiki_root

W = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else default_wiki_root())
README = W / "README.md"
INDEX = W / "index.md"
LOG = W / "log.md"

START = "<!-- AUTO_STATUS_START -->"
END = "<!-- AUTO_STATUS_END -->"

def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""

def build_status():
    idx = read_text(INDEX)
    m = re.search(r"wiki 页面：(\d+) concepts \+ (\d+) entities \+ (\d+) syntheses = (\d+) \| 原始资料：(\d+)", idx)
    if m:
        counts = f"{m.group(1)} concepts + {m.group(2)} entities + {m.group(3)} syntheses = {m.group(4)} | raw {m.group(5)}"
    else:
        counts = "未知"
    recent = []
    log_text = read_text(LOG)
    for line in log_text.splitlines():
        if line.startswith("## ["):
            recent.append(line)
        if len(recent) >= 5:
            break
    recent_block = "\n".join(recent) if recent else "暂无"
    today = datetime.date.today().isoformat()
    return (
        f"{START}\n"
        f"> 自动更新：{today}\n\n"
        f"**当前状态**：{counts}\n\n"
        f"**最近操作**：\n\n{recent_block}\n\n"
        f"{END}"
    )

def update():
    status = build_status()
    if README.exists():
        text = read_text(README)
        if START in text and END in text:
            new_text = re.sub(rf"{START}.*?{END}", status, text, flags=re.S)
        else:
            new_text = text.rstrip() + "\n\n## 当前状态\n\n" + status + "\n"
        README.write_text(new_text, encoding="utf-8")
    else:
        content = (
            "# LLM Wiki\n\n"
            "> Markdown 为载体，LLM 维护，人类监督。\n\n"
            "## 这是什么\n\n个人 LLM Wiki 知识库。\n\n"
            "## 目录结构\n\n- `raw/`：原始素材，只读\n- `wiki/`：结构化知识\n- `index.md`：目录\n- `log.md`：操作日志\n- `skills/`：维护 skill\n\n"
            "## 当前状态\n\n" + status + "\n"
        )
        README.write_text(content, encoding="utf-8")
    print("README 当前状态已更新")

if __name__ == "__main__":
    update()
