#!/usr/bin/env python3
"""平台自识别的 wiki 根目录解析（双平台共享）。

本 skill 住在 **custom-skills 仓库**（2026-10-17 从 LLMWiki 迁出），所以不能再用
「脚本自身位置」反推 wiki 根——脚本与 wiki 已不在同一目录树下。解析顺序：

1. 环境变量 `LLMWIKI_ROOT`（显式覆盖，便于测试与非常规布局）；
2. 平台默认用户路径：Windows `%USERPROFILE%\\Documents\\LLMWiki`，
   POSIX `/mnt/c/Users/<user>/Documents/LLMWiki`。

返回值即使不存在也照原样返回（保持"解析"职责单一）——**路径不存在由调用方报错**，
本模块不做静默降级。

用法: from wiki_paths import default_wiki_root
"""

import os


def default_wiki_root():
    env = os.environ.get("LLMWIKI_ROOT")
    if env:
        return env
    if os.name == "nt":
        return os.path.join(os.environ["USERPROFILE"], "Documents", "LLMWiki")
    return f"/mnt/c/Users/{os.environ.get('USER', 'elliot')}/Documents/LLMWiki"
