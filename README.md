# Agent 规则模板

团队级 Agent 规则、项目模板和校验脚本。优先级：用户当次指令 > 项目 `AGENTS.md` > 团队 `AGENTS.md` > 工具默认；安全底线不可覆盖。

## 文件

| 文件 | 作用 | 加载方式 |
| --- | --- | --- |
| [AGENTS.md](AGENTS.md) | 团队规则，所有项目默认继承 | 工具自动加载；预算 ≤2.5k tokens |
| [templates/project-AGENTS.md](templates/project-AGENTS.md) | 项目模板，复制后填写 | 项目根 `AGENTS.md`；预算 ≤2k tokens |
| [templates/team-baseline.md](templates/team-baseline.md) | 团队基线源，供脚本生成 | 不手工编辑 |
| [.claude/agents/l2-red-team.md](.claude/agents/l2-red-team.md) | Claude Code 只读 L2 审查子 Agent | 复制到项目 `.claude/agents/`；预算 ≤800 tokens |
| [references/memory.md](references/memory.md) | MEMORY、决策、交接细则 | 按需 |
| [references/wiki.md](references/wiki.md) | Wiki 沉淀与归档细则 | 按需 |
| [references/frontend.md](references/frontend.md) | 前端/RN 质量、依赖、CDN 细则 | 按需 |
| [references/verification.md](references/verification.md) | 验证、长任务记录、阻塞报告 | 按需 |
| [references/review.md](references/review.md) | L2 独立对抗审查、提示词、harness 对照 | 按需 |
| [scripts/sync_team_baseline.py](scripts/sync_team_baseline.py) | 同步团队基线 | 手动或 CI |
| [scripts/check_rules.py](scripts/check_rules.py) | 校验文件、基线、链接、预算、密钥 | 手动或 CI |
| [docs/adoption.md](docs/adoption.md) | 新项目接入清单（30~60 分钟） | 接入时读 |

默认只加载 `AGENTS.md`；references 由第 5 节的触发表按需读取，每个预算 ≤800 tokens。

## 应用

### 团队级

1. 把 `AGENTS.md` 和 `references/` 放到所有项目共同的父目录，或团队工具能加载的全局规则位置。
2. 工具默认文件不同：Qoder/Codex 用 `AGENTS.md`；Claude Code 用 `CLAUDE.md`；Gemini CLI 用 `GEMINI.md` 或配置 `contextFileName`；Cursor 用 `.cursor/rules/*.mdc` 或 `AGENTS.md`。
3. 工具不读父目录时，用项目模板第 0 节的团队基线兜底。

### 项目级

1. 复制 `templates/project-AGENTS.md` 到 `<project>/AGENTS.md`。
2. 填写第 1–6 节；不适用的小节删除；项目差异只写第 7 节。
3. 运行 `python3 scripts/sync_team_baseline.py <project>/AGENTS.md` 同步基线。
4. 控制在 2k tokens 内；状态、测试计数、任务清单放 `MEMORY/`、`TODO.md` 或 `docs/`。
5. 需要 L2 审查时，把 `.claude/agents/l2-red-team.md` 复制到 `<project>/.claude/agents/`，用“用 l2-red-team 审查 docs/plan.md 及引用文件；只读，输出 P0/P1/P2、证据和结论”调用；其他工具用 `references/review.md` 的提示词。

### 导入现有项目

1. 先 `git status`，读现有 `AGENTS.md`、`CLAUDE.md` 和工具规则；有未提交改动先提交或备份。
2. 不要直接覆盖：把现有内容并入模板第 1–6 节，项目差异写第 7 节；安全底线不可覆盖。
3. 复制 `templates/project-AGENTS.md` 为项目 `AGENTS.md`，替换 `{{项目名}}` 和 `{{TEAM_AGENTS_PATH}}`；后者用团队规则的标准本地路径。
4. 运行 `python3 <template>/scripts/sync_team_baseline.py <project>/AGENTS.md`，再用 `--check` 校验基线。
5. Claude Code 复制 `.claude/agents/l2-red-team.md` 到 `<project>/.claude/agents/`；已有 `CLAUDE.md` 不要覆盖，在文件头加 `@AGENTS.md` 或合并。
6. 测试计数、当前主线、任务清单等易变状态移到 `MEMORY/`、`TODO.md` 或 `docs/`；项目 `AGENTS.md` 保持 ≤2k tokens。
7. 检查占位符、相对链接和 `git diff`；提交前确认。

团队规则只维护一份：项目通过 `{{TEAM_AGENTS_PATH}}` 指向它，或依赖第 0 节基线；不要把 `references/` 复制进每个项目。多人环境把模板克隆到约定路径，避免路径失效。

### 工具兼容

- Claude Code：`ln -s AGENTS.md CLAUDE.md`；子 Agent 定义放 `.claude/agents/`，`l2-red-team` 仅开放 Read/Grep/Glob。
- Gemini CLI：`ln -s AGENTS.md GEMINI.md`，或设置 `contextFileName`
- Cursor：`.cursor/rules/agents.mdc` 引用 `@AGENTS.md`

不手工维护多份完整规则；用符号链接或同步脚本。工具行为按版本确认，以各工具官方文档为准。

## 维护

- 改团队规则后运行 `python3 scripts/sync_team_baseline.py`，再运行 `python3 scripts/check_rules.py`。
- CI 在 push 和 PR 时执行 `python3 scripts/check_rules.py`。
- 团队基线是副本，不是项目级覆盖；冲突以团队 `AGENTS.md` 为准。
- 易变状态不进 `AGENTS.md`；长清单、历史复盘和方法论放 `references/`、`docs/` 或 `Wiki/`。

## 目录

```text
AGENTS.md
README.md
.claude/agents/l2-red-team.md
templates/
  project-AGENTS.md
  team-baseline.md
references/
  memory.md
  wiki.md
  frontend.md
  verification.md
  review.md
scripts/
  sync_team_baseline.py
  check_rules.py
.github/workflows/check-rules.yml
```
