#!/usr/bin/env python3
"""扫描已跟踪文件中的疑似敏感信息。

用法: python3 check_secrets.py [wiki_root]
  wiki_root 可选，默认平台自识别（见 wiki_paths.py）
"""
import os, re, sys, subprocess, pathlib
from wiki_paths import default_wiki_root

W = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else default_wiki_root())

# 常见密钥模式；命中后还需人工确认是否真实密钥
PATTERNS = [
    (re.compile(r"\bsk-[A-Za-z0-9]{16,}\b"), "疑似 OpenAI/DeepSeek API Key"),
    (re.compile(r"\b(api[_-]?key|apikey)\s*[:=]\s*['\"][^'\"]{8,}['\"]", re.I), "疑似 API Key"),
    (re.compile(r"\b(password|passwd)\s*[:=]\s*['\"][^'\"]{8,}['\"]", re.I), "疑似密码"),
    (re.compile(r"\b(token|access_token|auth_token)\s*[:=]\s*['\"][^'\"]{8,}['\"]", re.I), "疑似 Token"),
]

errors = []

def tracked_files():
    r = subprocess.run(["git", "ls-files"], cwd=W, capture_output=True, text=True)
    if r.returncode != 0:
        return []
    return [line for line in r.stdout.splitlines() if line]

for rel in tracked_files():
    if not rel.endswith((".md", ".py", ".json", ".yml", ".yaml", ".env", ".txt", ".sh", ".bat")):
        continue
    path = W / rel
    if not path.exists():
        continue
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    for i, line in enumerate(text.splitlines(), 1):
        for pattern, desc in PATTERNS:
            if pattern.search(line):
                # 忽略明显占位符
                if any(ph in line.lower() for ph in ["your-", "example", "xxxx", "placeholder", "<your"]):
                    continue
                errors.append(f"[secret] {rel}:{i} 疑似{desc}")

for e in errors:
    print(f"[E] {e}")
print(f"\n== {len(errors)} ERROR ==")
sys.exit(1 if errors else 0)
