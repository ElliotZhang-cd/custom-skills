#!/usr/bin/env python3
"""Mechanical check for a portable SKILL.md.

Enforces the budget that prose alone fails to hold: a short description
(capability + trigger), a valid name, the required body sections, and
links that resolve.

Usage:
    python check-skill.py authoring-skills            # one skill dir
    python check-skill.py */SKILL.md                  # many
    python check-skill.py . --quiet                   # errors only

Exit code 0 when every file passes, 1 when any fails.
"""

import argparse
import os
import re
import sys

# Budget. Tune here, not in prose.
DESC_MAX_CHARS = 200
DESC_HARD_CHARS = 280
DESC_MAX_SENTENCES = 2
DESC_HARD_SENTENCES = 3
NAME_MAX = 64

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RESERVED = ("anthropic", "claude")

# A trigger sentence is required, in either language. `Triggers include: ...`
# counts as a trigger that is present-but-bad, so the inventory error speaks
# instead of a redundant "no trigger".
TRIGGER_RE = re.compile(
    r"(?:\buse\s+when\b|\buse\s+this\s+skill\s+when\b|\buse\s+for\b|"
    r"\btriggers?\s+(?:include|by|when)\b|当用户|时使用|用于|触发[:：]|适用[:：]|适用场景)",
    re.IGNORECASE,
)
# Capability must come first, so the description may not open with a trigger.
LEADING_TRIGGER_RE = re.compile(
    r"^\s*(?:use\s+(?:this\s+skill\s+)?(?:when|any\s+time|if|for)|当用户)", re.IGNORECASE
)
# Feature inventories are the usual cause of runaway descriptions.
ENUM_RE = re.compile(
    r"(?:\bthis\s+includes\b|\btriggers?\s+include\b|\bactions?\s*:|\bincludes\s*:|"
    r"\bactions\s+include\b|\bincluding\s+but\s+not\s+limited\s+to\b)",
    re.IGNORECASE,
)
ENUM_ZH_RE = re.compile(r"包括[:：]|例如[:：]")
EXCLUSION_RE = re.compile(
    r"(?:\bnot\s+for\b|\bdoes\s+not\s+cover\b|\bexcluding\b|\bexcludes\b|不用于|不负责)",
    re.IGNORECASE,
)
NARRATION_RE = re.compile(
    r"(?:\bfirst\b[^.]*,\s*then\b|^\s*(?:step\s+\d|首先|第一步))", re.IGNORECASE
)

REQUIRED_SECTIONS = [
    ("Goal", r"^##\s+Goal\b", r"^##\s*目标", "Goal"),
    ("Workflow", r"^##\s+Workflow\b", r"^##\s*工作流", "Workflow"),
    (
        "Success criteria",
        r"^##\s+Success\s+criteria\b",
        r"^##\s*成功标准",
        "Success criteria",
    ),
    ("Stop rules", r"^##\s+Stop\s+rules\b", r"^##\s*停止规则", "Stop rules"),
]

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def parse_frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", text, re.DOTALL)
    if not m:
        return None
    block = m.group(1)
    meta = {}
    key = None
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if re.match(r"^[A-Za-z_][\w-]*\s*:", line):
            key, _, value = line.partition(":")
            key = key.strip()
            meta[key] = value.strip()
        elif key:
            meta[key] += " " + line.strip()
    for k, v in meta.items():
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            meta[k] = v[1:-1]
        meta[k] = " ".join(meta[k].split())
    return meta, text[m.end():]


def count_sentences(text):
    if not text:
        return 0
    parts = re.split(r"(?<=[.!?。！？])\s+|(?<=[。！？])", text)
    return len([p for p in parts if p.strip()])


class Report:
    def __init__(self, path):
        self.path = path
        self.errors = []
        self.warns = []
        self.notes = []
        self.struct_issues = []

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warns.append(msg)

    def note(self, msg):
        self.notes.append(msg)

    def structural(self, msg):
        """Section-naming drift: a warning by default, an error under --strict.

        Description problems are always errors — that is the failure this
        checker exists for. Body section names are a house style, and flagging
        them as fatal on someone else's skill is not our call.
        """
        self.struct_issues.append(msg)


def check_name(meta, rep):
    name = meta.get("name")
    if not name:
        rep.err("frontmatter: missing `name`")
        return
    if not NAME_RE.match(name):
        rep.err("name: use lowercase letters, numbers, hyphens -> %r" % name)
    if len(name) > NAME_MAX:
        rep.err("name: %d chars > %d" % (len(name), NAME_MAX))
    low = name.lower()
    for word in RESERVED:
        if word in low:
            rep.err("name: contains reserved word %r" % word)
    # Single-word names (pdf, slides, brand) are legitimate domain labels; the
    # gerund rule is about the verb-phrase form, so it only applies when the
    # name is hyphenated.
    if "-" in name:
        head = name.split("-", 1)[0]
        if not head.endswith("ing"):
            rep.warn(
                "name: preferred form leads with a gerund (e.g. reviewing-pull-requests)"
            )


def check_description(meta, rep):
    desc = meta.get("description")
    if not desc:
        rep.err("frontmatter: missing `description`")
        return
    n_chars = len(desc)
    n_sent = count_sentences(desc)
    rep.note("description: %d chars, %d sentence(s)" % (n_chars, n_sent))

    if n_sent > DESC_HARD_SENTENCES:
        rep.err(
            "description: %d sentences > %d. Keep capability + trigger only."
            % (n_sent, DESC_HARD_SENTENCES)
        )
    elif n_sent > DESC_MAX_SENTENCES:
        rep.warn(
            "description: %d sentences > %d. Merge or drop the extras."
            % (n_sent, DESC_MAX_SENTENCES)
        )

    if n_chars > DESC_HARD_CHARS:
        rep.err(
            "description: %d chars > %d. Move feature lists and edge cases into the body."
            % (n_chars, DESC_HARD_CHARS)
        )
    elif n_chars > DESC_MAX_CHARS:
        rep.warn("description: %d chars > %d target." % (n_chars, DESC_MAX_CHARS))

    if not TRIGGER_RE.search(desc):
        rep.err("description: no trigger. End with `Use when <2-3 signals>`.")
    if LEADING_TRIGGER_RE.search(desc):
        rep.err("description: opens with the trigger. Put the capability first.")
    if ENUM_RE.search(desc):
        rep.err(
            "description: feature/trigger inventory (this includes / triggers include / actions:). "
            "Name the class of work, not every member."
        )
    if ENUM_ZH_RE.search(desc):
        rep.warn("description: looks like an enumeration (包括/例如). Prefer a class description.")
    if EXCLUSION_RE.search(desc):
        rep.warn("description: states what it does NOT cover. Move exclusions to Constraints.")
    if NARRATION_RE.search(desc):
        rep.err("description: narrates the workflow. Describe the destination, not the steps.")


def check_body(body, rep):
    for label, en_re, zh_re, _ in REQUIRED_SECTIONS:
        if not (re.search(en_re, body, re.MULTILINE) or re.search(zh_re, body, re.MULTILINE)):
            rep.structural("body: missing section `%s`" % label)


def check_links(path, body, rep):
    base = os.path.dirname(os.path.abspath(path))
    for target in LINK_RE.findall(body):
        target = target.strip()
        if target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        if re.match(r"^[A-Za-z]:[\\/]", target) or "\\" in target:
            rep.err("link: use a forward-slash relative path -> %s" % target)
            continue
        clean = target.split("#", 1)[0]
        if not clean:
            continue
        if not os.path.exists(os.path.join(base, clean)):
            rep.err("link: target not found -> %s" % target)


def check_file(path, quiet):
    rep = Report(path)
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        rep.err("cannot read: %s" % exc)
        return rep
    parsed = parse_frontmatter(text)
    if not parsed:
        rep.err("no frontmatter block (--- ... ---)")
        return rep
    meta, body = parsed
    check_name(meta, rep)
    check_description(meta, rep)
    check_body(body, rep)
    check_links(path, body, rep)
    return rep


def resolve_targets(args):
    out = []
    for arg in args:
        if os.path.isdir(arg):
            direct = os.path.join(arg, "SKILL.md")
            if os.path.exists(direct):
                out.append(direct)
                continue
            # A workspace root: take every */SKILL.md one level down.
            found = sorted(
                os.path.join(arg, name, "SKILL.md")
                for name in os.listdir(arg)
                if os.path.exists(os.path.join(arg, name, "SKILL.md"))
            )
            out.extend(found or [direct])
        elif "*" in arg or "?" in arg:
            import glob

            out.extend(sorted(glob.glob(arg)))
        else:
            out.append(arg)  # reported as unreadable
    return out


def main():
    ap = argparse.ArgumentParser(description="Check SKILL.md budget/structure.")
    ap.add_argument("paths", nargs="+", help="skill directory or SKILL.md path")
    ap.add_argument("-q", "--quiet", action="store_true", help="only print failures")
    ap.add_argument(
        "--strict",
        action="store_true",
        help="treat missing house-style sections as errors, not warnings",
    )
    args = ap.parse_args()

    reports = [check_file(p, args.quiet) for p in resolve_targets(args.paths)]
    failed = 0
    for rep in reports:
        blocking = list(rep.errors)
        if args.strict:
            blocking.extend(rep.struct_issues)
        status = "FAIL" if blocking else "PASS"
        if blocking:
            failed += 1
        if args.quiet and not blocking:
            continue
        print("[%s] %s" % (status, rep.path))
        for note in rep.notes:
            print("   info  %s" % note)
        for w in rep.warns:
            print("   warn  %s" % w)
        for s in rep.struct_issues:
            print("   %s %s" % ("error" if args.strict else "style", s))
        for e in rep.errors:
            print("   error %s" % e)
    print("\n%d file(s): %d passed, %d failed" % (len(reports), len(reports) - failed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
