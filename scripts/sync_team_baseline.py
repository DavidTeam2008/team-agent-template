#!/usr/bin/env python3
"""同步团队基线到目标文件。用法：sync_team_baseline.py [--check] [目标...]"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "templates" / "team-baseline.md"
DEFAULT_TARGETS = [ROOT / "templates" / "project-AGENTS.md"]
START = "<!-- TEAM-BASELINE:START -->"
END = "<!-- TEAM-BASELINE:END -->"


def build_block(body):
    return f"{START}\n{body}\n{END}"


def sync_text(text, block):
    start = text.find(START)
    end = text.find(END)
    if start == -1 or end == -1 or end < start:
        raise ValueError("缺少 TEAM-BASELINE 标记")
    return text[:start] + block + text[end + len(END):]


def main(argv):
    check = "--check" in argv
    args = [arg for arg in argv if not arg.startswith("--")]
    targets = [Path(arg) for arg in args] if args else DEFAULT_TARGETS
    block = build_block(SOURCE.read_text(encoding="utf-8").strip())
    failed = False

    for target in targets:
        try:
            text = target.read_text(encoding="utf-8")
            updated = sync_text(text, block)
        except (OSError, ValueError) as exc:
            print(f"[FAIL] {target}: {exc}")
            failed = True
            continue
        if check:
            print(f"[{'OK' if updated == text else 'FAIL'}] {target}")
            failed = failed or updated != text
        elif updated == text:
            print(f"[OK] {target}")
        else:
            target.write_text(updated, encoding="utf-8")
            print(f"[UPDATE] {target}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
