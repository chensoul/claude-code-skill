# OpenClaw prompt templates for Claude Code

Use these templates when OpenClaw needs to drive Claude Code in a stable, repeatable way.

## 1. Repository analysis

Use for: architecture overview, unfamiliar repos, change planning, entry-point discovery.

Prompt template:

```text
分析这个仓库的结构，说明：
1. 主要模块和入口
2. 核心依赖和技术栈
3. 哪些文件最关键
4. 如果要实现【目标】，建议从哪里改
先只分析，不要改代码。
```

Recommended mode:
- `--permission-mode plan`

## 2. Bug fixing

Use for: known bug, stack trace, failing behavior.

Prompt template:

```text
修复这个问题：
- 现象：{bug_description}
- 相关目录/文件：{paths}
- 验证方式：{test_or_command}
要求：
1. 先定位根因
2. 再实施修复
3. 跑验证命令
4. 最后总结原因和修复点
```

Recommended mode:
- headless
- narrow `--allowedTools`

Suggested tools:
- `Bash,Read,Edit`

## 3. Test repair

Use for: failing unit/integration tests.

Prompt template:

```text
请检查并修复当前测试失败。
要求：
1. 先运行测试并确认失败点
2. 找到根因，不要只绕过问题
3. 修复后重新运行测试
4. 输出失败原因、修复内容、验证结果
```

Suggested tools:
- `Bash,Read,Edit`

## 4. Refactor

Use for: cleanup, extract modules, improve maintainability.

Prompt template:

```text
请重构这部分代码，目标是：
- 提升可读性
- 降低重复
- 保持现有行为不变
范围：{paths}
验证方式：{test_or_command}
先简要说明重构方案，再实施并验证。
```

Suggested tools:
- `Bash,Read,Edit`

## 5. Structured JSON extraction

Use for: downstream automation, summaries, metadata extraction.

Prompt template:

```text
请读取这个项目，并按约定输出结构化结果：
- services
- entry_points
- risks
- recommended_changes
只输出符合 schema 的内容。
```

Recommended flags:
- `--output-format json`
- `--json-schema ...`

## 6. Interactive slash commands

Use for: `/clear`, `/compact`, skill commands, or workflows that may prompt.

Prompt template:

```text
/clear
/compact Focus on {topic}
```

Recommended mode:
- `--mode interactive`
- `--allowedTools "Bash,Read,Edit,Write"` when edits are expected

## 7. Continue previous session

Use for: follow-up work on a previous Claude Code thread.

Prompt template:

```text
继续刚才的任务，重点处理：
- {followup_goal}
并说明你沿用了哪些前文上下文。
```

Recommended flags:
- `--continue`
or
- `--resume <session-id>`

## 8. Plan mode only

Use for: when the user wants ideas or a plan but no edits.

Prompt template:

```text
请先阅读相关代码，输出一个可执行计划：
1. 需要改哪些文件
2. 为什么改
3. 风险点
4. 验证方式
现在不要改代码。
```

Recommended mode:
- `--permission-mode plan`
