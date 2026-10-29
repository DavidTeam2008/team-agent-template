# Agent 规则模板

## 文件

- `AGENTS.md`：团队级核心规则，所有项目默认继承。
- `templates/project-AGENTS.md`：项目级骨架，复制到项目根目录后填写；填完控制在 6–8KB。
- `references/details.md`：按需阅读的细则（决策模板、Wiki 规则、镜像/CDN、前端质量、验证示例），不进入每次会话。

## 应用

### 团队级

1. 把 `AGENTS.md` 和 `references/` 放到所有项目共同的父目录（例如 `~/Documents/code/`），或放到团队工具能加载的全局规则位置。
2. 不同工具默认文件不同：Qoder/Codex 用 `AGENTS.md`；Claude Code 用 `CLAUDE.md`；Gemini CLI 用 `GEMINI.md`；Cursor 用 `.cursor/rules/*.mdc`。
3. 工具不读取父目录时，靠项目级 `AGENTS.md` 的“团队基线”兜底。

### 项目级

1. 复制 `templates/project-AGENTS.md` 到 `<project>/AGENTS.md`。
2. 填写 6 个核心小节；不适用的小节直接删。
3. 需要时再加“按需补充”里的内容；详细背景链接到 `docs/`，不要复制。
4. 填完控制在 6–8KB；当前状态、测试计数、任务清单放 `docs/` 或 `TODO.md`，`AGENTS.md` 只留指针。

### 工具兼容

- Claude Code：`ln -s AGENTS.md CLAUDE.md`
- Gemini CLI：`ln -s AGENTS.md GEMINI.md`，或把 `contextFileName` 设为 `AGENTS.md`
- Cursor：`.cursor/rules/agents.mdc` 引用 `@AGENTS.md`
- 不手工维护多份完整规则；用符号链接或同步脚本。

### 同步团队基线

团队规则更新后，检查各项目 `AGENTS.md` 中 `<!-- TEAM-BASELINE:START -->` 与 `<!-- TEAM-BASELINE:END -->` 之间的内容是否一致，整块替换。项目级覆盖写进“项目级覆盖”并注明原因和作用域。

## 上下文成本

- 团队核心规则约 6KB；项目文件填完 6–8KB；细则只在需要时读。
- 易变状态不写进 `AGENTS.md`，放 `MEMORY/`、`TODO.md` 或交接文档。
- 长清单、历史复盘、方法论放 `references/`、`docs/` 或 `Wiki/`，`AGENTS.md` 只留链接。
