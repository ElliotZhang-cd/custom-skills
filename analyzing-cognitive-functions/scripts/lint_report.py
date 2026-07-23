#!/usr/bin/env python3
"""lint_report.py — 校验 mbti-analyst 生成的报告 HTML 是否符合规范。

用法: python3 scripts/lint_report.py <报告文件.html>
退出码: 0 = 全部通过; 1 = 存在 FAIL; 2 = 文件/参数错误
"""
import re
import sys
from pathlib import Path

FUNCTION_CODES = ["Fi", "Ni", "Fe", "Ti", "Te", "Ne", "Se", "Si"]

# 正文禁用词（可选阅读附录 .appendix-tech 内不检查 Beebe 术语，其余全局检查）
FORBIDDEN_BODY = ["劣势功能", "主导功能", "Fi-Ni loop", "Fi-Ni Loop", "阴影功能",
                  "结构性情感失语", "病态", "缺陷",
                  # 已弃用的比喻命名
                  "价值罗盘", "情绪天线", "逻辑拆解器", "效率引擎",
                  "长线望远镜", "可能性喷泉", "安全基地", "当下雷达",
                  # 工程/IT/系统类（writing-style.md §4.5）
                  "系统", "架构", "机制", "流程", "输入", "输出", "通道", "带宽", "负载",
                  "算法", "迭代", "反馈", "模块", "组件", "审查", "监控", "容器", "支架",
                  "空转", "宕机", "重启", "调试", "程序", "数据库", "接口", "回路", "闭环",
                  "触发器", "运算", "处理器", "默认设置", "双核", "双引擎",
                  # 报告正文禁止的外部关系导向
                  "咨询师", "会谈", "咨询中"]
# 任何位置都禁止（含附录；神经质为整体不涉及）
FORBIDDEN_GLOBAL = ["你就是太", "你一定会", "你肯定会", "神经质", "情绪稳定性"]

REQUIRED_BLOCKS = {
    "阅读指南": "怎么读这份报告",
    "局限声明": "不构成临床诊断",
    "谦卑段落": "以你的经历为准",
}


def strip_regions(html: str, patterns) -> str:
    for pat in patterns:
        html = re.sub(pat, " ", html, flags=re.DOTALL | re.IGNORECASE)
    return html


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: python3 lint_report.py <报告文件.html>")
        return 2
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"错误: 文件不存在: {path}")
        return 2
    try:
        html = path.read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001 - 给调用者明确错误而非栈
        print(f"错误: 无法读取文件: {e}")
        return 2

    failures = []

    def check(name, ok, detail=""):
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}" + (f" — {detail}" if detail and not ok else ""))
        if not ok:
            failures.append(name)

    # 检查区 = 去掉 <style>、灰色括注 .fn-code、可选阅读附录 .appendix-tech
    body = strip_regions(html, [
        r"<style.*?</style>",
        r"<span[^>]*class=\"[^\"]*fn-code[^\"]*\"[^>]*>.*?</span>",
        r"<section[^>]*class=\"[^\"]*appendix-tech[^\"]*\"[^>]*>.*?</section>",
        r"<div[^>]*class=\"[^\"]*appendix-tech[^\"]*\"[^>]*>.*?</div>",
    ])
    # 去掉剩余标签，只留文本
    text = re.sub(r"<[^>]+>", " ", body)

    # 1. 正文裸功能代码
    bare = []
    for code in FUNCTION_CODES:
        for m in re.finditer(rf"(?<![A-Za-z一-鿿]){code}(?![A-Za-z一-鿿])", text):
            line = text[: m.start()].count("\n") + 1
            bare.append(f"{code}(第{line}行)")
    check("正文无裸功能代码", not bare, "出现: " + ", ".join(bare[:8]))

    # 2. 禁用词
    bad_words = [w for w in FORBIDDEN_BODY if w in text]
    bad_global = [w for w in FORBIDDEN_GLOBAL if w in html]
    check("无禁用词（正文）", not bad_words, "出现: " + ", ".join(bad_words))
    check("无禁用词（全局）", not bad_global, "出现: " + ", ".join(bad_global))

    # 3. 固定文本块
    for name, needle in REQUIRED_BLOCKS.items():
        check(f"固定文本块存在: {name}", needle in html, f"未找到关键句「{needle}」")

    # 4. 证据标签至少使用一次
    check("使用证据标签(ev-tag)", bool(re.search(r"ev-(research|theory|hypothesis)", html)))

    # 5. meter-fill CSS（仅当报告含评分条时检查）
    if "meter-bar" in html or "meter-fill" in html:
        m = re.search(r"\.meter-fill\s*\{([^}]*)\}", html)
        css = m.group(1) if m else ""
        ok = m is not None and "display:block" in css.replace(" ", "") and "min-width" in css
        check("meter-fill CSS 修复(display:block + min-width)", ok,
              "缺少 .meter-fill{display:block; min-width:...}")

    # 6. 速览卡
    check("存在一页速览卡(summary-card)", "summary-card" in html)

    # 7. 打印样式
    check("存在 @media print", "@media print" in html)

    print()
    if failures:
        print(f"共 {len(failures)} 项未通过，请修复后重新 lint。")
        return 1
    print("全部检查通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
