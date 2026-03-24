---
name: claude-code
description: Run the locally installed Claude Code CLI (`claude`) from OpenClaw for repository analysis, plan-mode research, bug fixing, refactors, test repair, structured JSON output, or interactive slash-command workflows. Use when the user asks in Chinese or English to use Claude Code, Claude CLI, `claude -p`, Plan Mode, continue/resume a Claude session, auto-approve tools with `--allowedTools`, request JSON output, or drive interactive `/` commands. Typical triggers include: “用 Claude Code …”, “用 claude …”, “用 Anthropic 的 coder …”, “run Claude Code on this repo”, “用 Claude Code 分析/修复/重构/生成计划”, or “用 claude 跑交互命令”.
---

# Claude Code

Use the local **Claude Code** CLI through the bundled wrapper script.

Prefer this skill when the user specifically wants **Claude Code** behavior rather than generic shell execution.

## Chat-trigger guidance

Treat these user requests as strong triggers for this skill:

- “用 Claude Code 看一下这个项目”
- “用 claude code 修一下这个 bug”
- “用 claude 跑 plan mode”
- “用 Claude Code 输出 JSON”
- “用 Claude Code 继续上一次会话”
- “用 Claude Code 跑 `/clear`、`/compact`、`/review-*` 这类交互命令”

Do not use this skill when:

- the task is a trivial one-line local edit that OpenClaw can do directly
- the user only wants to read a file or inspect a small snippet
- the task is better handled by ACP harness spawning rather than the local `claude` CLI

## 中文速查

- “用 Claude Code 分析这个仓库” → `plan mode`
- “用 Claude Code 给我一个实现方案，不要改代码” → `plan mode`
- “用 Claude Code 修复这个 bug 并验证” → headless + `Bash,Read,Edit`
- “用 Claude Code 跑测试并修复失败” → headless + `Bash,Read,Edit`
- “用 Claude Code 输出 JSON 总结” → headless + `--output-format json`
- “用 Claude Code 执行 `/clear` 或 `/compact`” → interactive
- “用 Claude Code 继续刚才那个会话” → `--continue` 或 `--resume`

如果需求只是小改一行、本地直接读文件、或简单总结，不必强行用 Claude Code，直接由 OpenClaw 处理更轻。

## Quick start

### Headless one-shot prompt

```bash
python3 /home/chensoul/.openclaw/workspace/skills/claude-code/scripts/claude_code_run.py \
  -p "Summarize this repository and list the key modules." \
  --cwd /path/to/repo \
  --permission-mode plan
```

### Auto-approve a narrow set of tools

```bash
python3 /home/chensoul/.openclaw/workspace/skills/claude-code/scripts/claude_code_run.py \
  -p "Run the tests and fix any failures." \
  --cwd /path/to/repo \
  --allowedTools "Bash,Read,Edit"
```

### Structured JSON output

```bash
python3 /home/chensoul/.openclaw/workspace/skills/claude-code/scripts/claude_code_run.py \
  -p "Summarize this repo in 5 bullets." \
  --cwd /path/to/repo \
  --output-format json
```

### Interactive slash commands

Use interactive mode when the prompt includes Claude slash commands such as `/clear`, `/compact`, skill commands, or multi-step interactive workflows.

```bash
python3 /home/chensoul/.openclaw/workspace/skills/claude-code/scripts/claude_code_run.py \
  --mode interactive \
  --cwd /path/to/repo \
  --permission-mode acceptEdits \
  --allowedTools "Bash,Read,Edit,Write" \
  -p $'/clear\n/review-pr'
```

## Execution rules

### 1) Choose the mode deliberately

- Use `--permission-mode plan` for read-only exploration and implementation planning.
- Use headless mode (`-p`) for normal one-shot tasks, automation, summaries, and JSON output.
- Use interactive mode for prompts containing slash commands, multi-step interactive workflows, or when Claude may need follow-up confirmation.
- If the task is scripted/CI-like and should ignore local hooks, memory, and skills, add `--bare` via extra args.

Quick mapping:

- “分析这个仓库 / 给我方案” → `plan`
- “修 bug / 改代码 / 跑测试” → headless + narrow `--allowedTools`
- “执行 `/clear` `/compact` 或 skill 命令” → interactive

### 2) Always give Claude a verification target

When asking Claude Code to change code, include a concrete success condition:

- run the tests
- run the build
- run lint
- compare screenshot/output
- explain what was verified

This follows the official best-practices guidance and materially improves result quality.

### 3) Prefer explore → plan → implement for medium/large changes

For unfamiliar or multi-file work:

1. Run with `--permission-mode plan`
2. Ask Claude to inspect the code and propose a plan
3. Review the plan
4. Re-run with edit permissions to implement it

### 4) Keep permissions narrow

Prefer explicit `--allowedTools` allowlists such as:

- `Read`
- `Read,Edit`
- `Bash(git status *),Bash(git diff *),Read`
- `Bash,Read,Edit,Write` only when the task truly needs it

Avoid broad approvals when a smaller allowlist will do.

### 5) Use structured output when another tool or script will consume the result

- `--output-format json` for single JSON output
- `--json-schema ...` when a downstream system expects a fixed shape
- `--output-format stream-json` only when you explicitly need streaming events

### 6) Continue or resume sessions when the user wants continuity

- `--continue` to continue the latest session in the same working directory
- `--resume <session-id>` to reopen a specific Claude session

## OpenClaw-oriented patterns

### 中文聊天示例

```bash
python3 /home/chensoul/.openclaw/workspace/skills/claude-code/scripts/claude_code_run.py \
  -p "分析这个仓库的结构，给我一个修改方案，不要动代码。" \
  --cwd /path/to/repo \
  --permission-mode plan
```

```bash
python3 /home/chensoul/.openclaw/workspace/skills/claude-code/scripts/claude_code_run.py \
  -p "修复这个项目的测试失败，跑测试验证，然后总结原因。" \
  --cwd /path/to/repo \
  --allowedTools "Bash,Read,Edit"
```

```bash
python3 /home/chensoul/.openclaw/workspace/skills/claude-code/scripts/claude_code_run.py \
  --mode interactive \
  --cwd /path/to/repo \
  --allowedTools "Bash,Read,Edit,Write" \
  -p $'/clear\n/compact Focus on auth module'
```

### Analyze a codebase without editing

```bash
python3 /home/chensoul/.openclaw/workspace/skills/claude-code/scripts/claude_code_run.py \
  -p "Read this repo and explain the architecture, entry points, and risky areas." \
  --cwd /path/to/repo \
  --permission-mode plan
```

### Fix a bug and verify it

```bash
python3 /home/chensoul/.openclaw/workspace/skills/claude-code/scripts/claude_code_run.py \
  -p "Fix the failing tests, run the suite again, and summarize the root cause and the fix." \
  --cwd /path/to/repo \
  --allowedTools "Bash,Read,Edit"
```

### Produce machine-readable output

```bash
python3 /home/chensoul/.openclaw/workspace/skills/claude-code/scripts/claude_code_run.py \
  -p "List the main services in this repo." \
  --cwd /path/to/repo \
  --output-format json
```

## References

Read these files only when needed:

- `references/official-docs.md` — concise notes distilled from the official Claude Code docs
- `references/doc-index.md` — major official documentation entry points
- `references/openclaw-prompts.md` — reusable OpenClaw prompt templates for repo analysis, bug fixing, refactors, plan mode, JSON output, and interactive slash-command workflows

## Notes

- The wrapper forces a PTY for headless calls because Claude Code behaves better with a terminal.
- The wrapper auto-switches to interactive mode when the prompt contains lines beginning with `/`.
- The wrapper defaults to the local binary path on this machine: `/home/chensoul/.nvm/versions/node/v25.8.0/bin/claude`.
- If you correct a repeated Claude Code mistake in a repo, tell Claude to update its `CLAUDE.md` with the lesson when appropriate.
