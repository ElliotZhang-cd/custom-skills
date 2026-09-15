#!/usr/bin/env python3
"""基线回归：对四条基线文件跑 lint，全 PASS 才退出 0。

改过 templates/、scripts/（compute/lint）后必跑；SKILL.md Phase 3.3 的执行器。
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
BASELINES = [
    ("单人模板", os.path.join("templates", "report-template.html")),
    ("单人样例", os.path.join("examples", "bfi2_sample.html")),
    ("双人模板", os.path.join("templates", "couple-report-template.html")),
    ("双人样例", os.path.join("examples", "bfi2_sampleA_sampleB.html")),
]

def main():
    failed = []
    for label, rel in BASELINES:
        path = os.path.join(BASE, rel)
        r = subprocess.run([sys.executable, os.path.join(HERE, "lint_report.py"), path],
                           capture_output=True, text=True)
        ok = r.returncode == 0
        print(f"[{'PASS' if ok else 'FAIL'}] {label}: {rel}")
        if not ok:
            failed.append(label)
            print(r.stdout.rstrip())
    if failed:
        print(f"\n{len(failed)}/{len(BASELINES)} baseline(s) FAILED: {', '.join(failed)}")
        sys.exit(1)
    print(f"\nPASS: {len(BASELINES)}/{len(BASELINES)} baselines")

if __name__ == "__main__":
    main()
