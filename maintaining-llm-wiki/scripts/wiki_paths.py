#!/usr/bin/env python3
"""平台自识别的 wiki 根目录解析（双平台共享）。

Windows:  %USERPROFILE%\\Documents\\LLMWiki（如 C:\\Users\\elliot\\Documents\\LLMWiki）
WSL:      /mnt/c/Users/<Windows用户名>/Documents/LLMWiki（$USER 推断，不存在则回退 elliot）

用法: from wiki_paths import default_wiki_root
"""

import os


def default_wiki_root():
    if os.name == "nt":
        return os.path.join(os.environ["USERPROFILE"], "Documents", "LLMWiki")
    user = os.environ.get("USER", "elliot")
    p = f"/mnt/c/Users/{user}/Documents/LLMWiki"
    if os.path.isdir(p):
        return p
    return "/mnt/c/Users/elliot/Documents/LLMWiki"
