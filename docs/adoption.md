# 新项目接入清单

> 目标：30~60 分钟把团队规则接进一个新仓。只采纳骨架，不复制整个模版仓。
> 适用：iOS / React Native / Web / 后端；按技术栈裁剪。
> 参考实现（iOS）：`https://github.com/davidtan2008/scantool`。

## 0. 先判断三件事

| 问题 | 影响 |
| --- | --- |
| 已有 `AGENTS.md` / `CLAUDE.md`？ | 有就**合并**，不要覆盖；保留项目铁律 |
| 有 `docs/` 和测试？ | 决定是否加文档索引 / 测试门禁 |
| 测试是否全绿？ | 有既有失败才需要 known-failures 白名单 |

## 1. 复制什么、不复制什么

| 模版件 | 新项目 |
| --- | --- |
| 团队 [AGENTS.md](../AGENTS.md) | 不复制全文；只放 5 行基线块 + 链接 |
| [templates/project-AGENTS.md](../templates/project-AGENTS.md) | 复制后填第 1~6 节 |
| [templates/team-baseline.md](../templates/team-baseline.md) | 不手工复制；由脚本生成 |
| [scripts/sync_team_baseline.py](../scripts/sync_team_baseline.py) | 从模版仓直接跑，不复制 |
| [scripts/check_rules.py](../scripts/check_rules.py) | **不要复制**：它校验的是模版仓 |
| [references/frontend.md](../references/frontend.md) | 仅 RN / Web 项目 |
| [references/verification.md](../references/verification.md) | 可参考，按项目改写 |
| [references/review.md](../references/review.md) | 需要 L2 红队时复制/改写 |
| [.claude/agents/l2-red-team.md](../.claude/agents/l2-red-team.md) | Claude Code 项目复制到 `.claude/agents/` |
| `MEMORY/` / `Wiki/` / `Resources/` | 不建平行树；先映射到现有 `docs/` |

## 2. 四步接入

### Step 0：准备

```bash
TEAM=<team-rules-path>        # 团队规则仓本地路径
cd <project>
git status                    # 干净，或先开分支
git -C "$TEAM" pull
```

### Step 1：合并项目 AGENTS

```bash
test -e AGENTS.md || cp "$TEAM/templates/project-AGENTS.md" AGENTS.md
```

已有 `AGENTS.md` 时手工合并：

- 现有铁律、命令、卡点全部保留；
- 项目差异写第 7 节“项目级覆盖”，不要重复团队规则；
- 第 1~6 节只写会影响决策的事实；
- 目标 ≤2k tokens，硬上限 2.5k；细节移到 `docs/` 或 `references/`。

### Step 2：同步团队基线

文件需有 `TEAM-BASELINE` 标记（模版自带）：

```bash
python3 "$TEAM/scripts/sync_team_baseline.py" AGENTS.md
python3 "$TEAM/scripts/sync_team_baseline.py" --check AGENTS.md
```

输出 `[OK]` 即可。报“缺少 TEAM-BASELINE 标记”时，先补上
`<!-- TEAM-BASELINE:START -->` / `<!-- TEAM-BASELINE:END -->` 再跑。

### Step 3：按需拆 references

只放“需要读一次、但不想每次冷启动加载”的内容，每篇 ≤800 tokens：

| 文件 | 放什么 |
| --- | --- |
| `references/contracts.md` | 不可破坏的契约、铁律理由、历史回归根因 |
| `references/verification.md` | 测试计数、已知债、真机/环境坑 |
| `references/workflow.md` | SDD/发布流程、状态归属、周期索引 |

AGENTS 里用一行链接 + 触发条件，不要全文复制。

### Step 4：文档检查与 CI

```bash
mkdir -p Tools .github/workflows
```

- **文档检查**：项目级脚本只扫当前文档，跳过 `build/`、历史证据、录屏；
  参考 `scantool` 的 `Tools/check-docs.py`，改 `targets()` 的目录。
  `make check-docs` 应校验相对链接、代码围栏、docs 索引覆盖。
- **团队基线 CI**：

```yaml
- uses: actions/checkout@v4
- uses: actions/checkout@v4
  with:
    repository: davidtan2008/team-agent-template
    path: .team-rules
    token: ${{ secrets.TEAM_RULES_TOKEN }}
- run: python3 .team-rules/scripts/sync_team_baseline.py --check AGENTS.md
- run: python3 Tools/check-docs.py
```

私有模版仓必须配 `TEAM_RULES_TOKEN`（只读）；未配置时建议跳过基线校验并告警，
不要让 CI 长期红。

- **PR 模板**：加 spec/需求链接、验证命令、真机/UI 证据、未验证项。
- **分支保护**：加协作者后保护 `main`（PR + 1 approval + `rules`）；
  私有仓的个人免费版可能不支持，具体看 GitHub 套餐。

## 3. 按技术栈裁剪

| 栈 | 额外项 |
| --- | --- |
| iOS | `references/contracts.md` + `verification.md`；真机验收清单；known-debt 门禁；自托管 macOS runner |
| RN / Web | [references/frontend.md](../references/frontend.md)；lint / type / build / e2e；可访问性与多浏览器 |
| 后端 | API/迁移契约；隔离环境跑迁移与回滚；不在 `AGENTS.md` 写密钥 |
| 纯文档 | 基线 + docs 检查即可，不建 test-gate |

## 4. 验证清单

```text
[ ] sync_team_baseline.py --check AGENTS.md  → OK
[ ] AGENTS.md ≤2k tokens（目标；硬上限 2.5k）
[ ] 无未替换的模版占位符
[ ] make check-docs → PASS（有 docs 时）
[ ] 测试/构建命令可跑；有既有债则 test-ci 通过
[ ] git diff 只含预期文件
```

## 5. 常见坑

1. **直接覆盖已有 `AGENTS.md`**：会丢项目铁律；先合并。
2. **复制 `check_rules.py`**：它要求模版仓的 13 个文件并扫描整仓，项目里会误报。
3. **把团队 `AGENTS.md` 全文复制进项目**：双真源；只放基线块 + 链接。
4. **建 `MEMORY/` / `Wiki/` 平行树**：与现有 `docs/` 冲突；先做映射。
5. **私有模版仓没配 token**：CI 在 checkout 团队规则时失败。
6. **`AGENTS.md` 写到 5k**：回到“什么都读”的老路；细节进 references。
7. **有既有债却要求 CI 全绿**：CI 永远红；用 known-failures 白名单，只拦新增失败。
8. **忘记同步基线**：团队规则更新后项目仍用旧副本；CI 的 `--check` 会拦。

## 6. 团队规则更新后

```bash
git -C "$TEAM" pull
python3 "$TEAM/scripts/check_rules.py"
python3 "$TEAM/scripts/sync_team_baseline.py" <project>/AGENTS.md
python3 "$TEAM/scripts/sync_team_baseline.py" --check <project>/AGENTS.md
```

然后在项目里提交基线块变更；CI 的 `rules` 会再次校验。

## 7. 最小可行版（30 分钟）

只做 **Step 1 + Step 2 + Step 4 的 `rules.yml`**：
项目 AGENTS + 团队基线 + CI 基线校验。docs 索引、test-gate、references
可以第二周按需补。
