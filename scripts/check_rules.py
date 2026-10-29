#!/usr/bin/env python3
"""校验规则文件的完整性、基线同步、占位符、链接、密钥模式和 token 预算。"""
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
START = "<!-- TEAM-BASELINE:START -->"
END = "<!-- TEAM-BASELINE:END -->"

REQUIRED = [
    "AGENTS.md",
    "README.md",
    ".claude/agents/l2-red-team.md",
    "templates/project-AGENTS.md",
    "templates/team-baseline.md",
    "references/memory.md",
    "references/wiki.md",
    "references/frontend.md",
    "references/verification.md",
    "references/review.md",
    "scripts/sync_team_baseline.py",
    "scripts/check_rules.py",
    ".github/workflows/check-rules.yml",
]

BUDGETS = {
    "AGENTS.md": 2500,
    ".claude/agents/l2-red-team.md": 800,
    "templates/project-AGENTS.md": 2000,
    "references/memory.md": 800,
    "references/wiki.md": 800,
    "references/frontend.md": 800,
    "references/verification.md": 800,
    "references/review.md": 800,
}

ALLOWED_PLACEHOLDERS = {"{{项目名}}", "{{TEAM_AGENTS_PATH}}"}
TRIGGERED_REFERENCES = [
    "references/memory.md",
    "references/wiki.md",
    "references/frontend.md",
    "references/verification.md",
    "references/review.md",
]

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"ghp_[A-Za-z0-9]{36}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
]

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
PLACEHOLDER_RE = re.compile(r"\{\{[^}]+\}\}")

errors = []
warnings = []


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def est_tokens(text):
    cjk = len(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff]", text))
    return cjk + math.ceil((len(text) - cjk) / 4)


def strip_code(text):
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`]*`", "", text)


def markdown_files():
    files = []
    for path in ROOT.rglob("*.md"):
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith(".git/") or rel.startswith("node_modules/"):
            continue
        files.append(rel)
    return sorted(files)


def check_required():
    missing = [rel for rel in REQUIRED if not (ROOT / rel).is_file()]
    for rel in missing:
        errors.append(f"缺少文件：{rel}")
    if not missing:
        print(f"[OK] {len(REQUIRED)} 个必需文件存在")


def check_claude_agent():
    rel = ".claude/agents/l2-red-team.md"
    if not (ROOT / rel).is_file():
        return
    text = read(rel)
    bad = 0
    if not text.startswith("---"):
        errors.append(f"{rel} 缺少 frontmatter")
        return
    parts = text.split("---", 2)
    if len(parts) < 3:
        errors.append(f"{rel} frontmatter 未闭合")
        return
    head = parts[1]
    if not re.search(r"(?m)^name:\s*l2-red-team\s*$", head):
        errors.append(f"{rel} 的 name 应为 l2-red-team")
        bad += 1
    if not re.search(r"(?m)^description:\s*\S+", head):
        errors.append(f"{rel} 缺少 description")
        bad += 1
    match = re.search(r"(?m)^tools:\s*(.+)$", head)
    if not match:
        errors.append(f"{rel} 缺少 tools 字段")
        bad += 1
    else:
        tools = {item.strip() for item in match.group(1).split(",") if item.strip()}
        if not tools:
            errors.append(f"{rel} 的 tools 不能为空")
            bad += 1
        extra = tools - {"Read", "Grep", "Glob"}
        if extra:
            errors.append(f"{rel} 含非只读工具：{', '.join(sorted(extra))}")
            bad += 1
    if not bad:
        print("[OK] Claude Code 子 Agent 为只读")


def check_baseline():
    body = read("templates/team-baseline.md").strip()
    expected = f"{START}\n{body}\n{END}"
    text = read("templates/project-AGENTS.md")
    if START not in text or END not in text:
        errors.append("templates/project-AGENTS.md 缺少 TEAM-BASELINE 标记")
        return
    start = text.index(START)
    end = text.index(END) + len(END)
    if text[start:end] != expected:
        errors.append("templates/project-AGENTS.md 的团队基线未同步，运行 scripts/sync_team_baseline.py")
    else:
        print("[OK] 团队基线一致")
    if "不是项目级覆盖" not in text:
        errors.append("项目模板需说明团队基线是副本，不是项目级覆盖")
    if "## 7. 项目级覆盖" not in text:
        errors.append("项目模板缺少“## 7. 项目级覆盖”")


def check_placeholders():
    bad = 0
    for rel in markdown_files():
        for match in PLACEHOLDER_RE.findall(strip_code(read(rel))):
            if rel.startswith("templates/") and match in ALLOWED_PLACEHOLDERS:
                continue
            errors.append(f"{rel} 存在未替换占位符：{match}")
            bad += 1
    if not bad:
        print("[OK] 占位符检查通过")


def check_links():
    bad = 0
    for rel in markdown_files():
        for raw in LINK_RE.findall(strip_code(read(rel))):
            target = raw.strip()
            if target.startswith(("http://", "https://", "mailto:", "#", "{{")):
                continue
            path = target.split("#", 1)[0].strip()
            if not path:
                continue
            if not ((ROOT / rel).parent / path).exists():
                errors.append(f"{rel} 链接不存在：{target}")
                bad += 1
    if not bad:
        print("[OK] 相对链接检查通过")


def check_budgets():
    for rel, budget in BUDGETS.items():
        tokens = est_tokens(read(rel))
        status = "OK" if tokens <= budget else "FAIL"
        print(f"[{status}] {rel} ≈ {tokens} tokens（预算 {budget}）")
        if tokens > budget:
            errors.append(f"{rel} 超出 token 预算：≈{tokens} > {budget}")


def check_fences():
    bad = 0
    for rel in markdown_files():
        fences = sum(1 for line in read(rel).splitlines() if line.strip().startswith("```"))
        if fences % 2:
            errors.append(f"{rel} 代码围栏未闭合")
            bad += 1
    if not bad:
        print("[OK] 代码围栏检查通过")


def check_secrets():
    bad = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix not in {".md", ".py", ".yml", ".yaml", ".txt", ".json", ".sh"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            for match in pattern.findall(text):
                rel = path.relative_to(ROOT).as_posix()
                errors.append(f"{rel} 疑似密钥：{match[:12]}...")
                bad += 1
    if not bad:
        print("[OK] 密钥模式检查通过")


def check_routing():
    text = read("AGENTS.md")
    for rel in TRIGGERED_REFERENCES:
        if rel not in text:
            errors.append(f"AGENTS.md 缺少细则触发项：{rel}")
    if (ROOT / "references/details.md").exists():
        errors.append("references/details.md 已拆分，应删除")
    for rel in markdown_files():
        if "references/details.md" in read(rel):
            errors.append(f"{rel} 仍引用已删除的 references/details.md")
    if not errors:
        print("[OK] 细则路由检查通过")


def main():
    check_required()
    check_claude_agent()
    check_baseline()
    check_placeholders()
    check_links()
    check_budgets()
    check_fences()
    check_secrets()
    check_routing()
    for warning in warnings:
        print(f"[WARN] {warning}")
    if errors:
        print("\n[FAIL]")
        for error in errors:
            print(f"- {error}")
        return 1
    print("\n[PASS] 规则检查全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
