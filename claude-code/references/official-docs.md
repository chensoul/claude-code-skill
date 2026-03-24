# Claude Code official docs notes

This file condenses the official documentation at `https://code.claude.com/docs` into the parts most useful for OpenClaw usage.

## Core positioning

Claude Code is an agentic coding tool that can read files, edit files, run commands, and work across a repo from the terminal, IDE, desktop app, or web.

For OpenClaw integration, the most relevant surface is the local CLI:

- interactive session: `claude`
- one-shot/headless run: `claude -p "..."`
- continue latest session: `claude -c`
- resume specific session: `claude -r <session>`

## High-value CLI flags

### Headless / scripted use

- `-p`, `--print` — run non-interactively
- `--output-format text|json|stream-json`
- `--json-schema <schema>` — structured output inside JSON metadata
- `--continue`
- `--resume <session-id>`

### Permission control

- `--permission-mode <mode>`
- `--allowedTools "..."`
- `--allow-dangerously-skip-permissions` only when explicitly needed

### Context / startup control

- `--bare` — skip hooks, skills, plugins, MCP, auto memory, and CLAUDE.md discovery for faster, more deterministic scripted calls
- `--append-system-prompt`
- `--append-system-prompt-file`
- `--system-prompt`

## Best-practice takeaways

### 1) Give Claude a way to verify

The docs strongly emphasize adding explicit verification:

- run tests
- run lint
- run build
- compare screenshots
- confirm expected output

Without a verification loop, quality drops.

### 2) Explore first, then plan, then implement

For non-trivial work:

1. ask Claude to inspect the codebase in plan mode
2. request a concrete implementation plan
3. approve the plan
4. let Claude implement and verify

### 3) Manage context aggressively

The docs repeatedly note that context fills quickly and quality degrades as it fills.

Operational implications:

- prefer one focused task per run
- use JSON output for downstream automation
- use `--bare` in scripted runs when local context should not leak in
- use fresh sessions for unrelated work

### 4) Be precise in prompts

Useful prompts usually name:

- the relevant files or directories
- the expected outcome
- the validation command
- any style or architecture constraints

### 5) Skills and slash commands are interactive-first

The docs explicitly note that user-invoked skills and built-in slash commands are only available in interactive mode.

Therefore:

- use headless mode for normal one-shot prompts and automation
- use interactive mode for `/clear`, `/compact`, skill invocations, or workflows that may pause for confirmation

## Why this skill uses a wrapper

The wrapper script exists because the CLI often behaves more reliably when attached to a PTY.

It also helps by:

- auto-switching to interactive mode for slash-command prompts
- printing tmux attach/capture instructions for monitoring
- exposing a stable command shape for OpenClaw automation

## Recommended OpenClaw usage patterns

### Safe repo analysis

Use plan mode:

```bash
python3 .../claude_code_run.py -p "Analyze this repo and propose a plan" --permission-mode plan --cwd /path/to/repo
```

### Autonomous bug fixing with bounded tools

```bash
python3 .../claude_code_run.py -p "Fix the failing tests and re-run them" --allowedTools "Bash,Read,Edit" --cwd /path/to/repo
```

### Structured extraction

```bash
python3 .../claude_code_run.py -p "Extract the public API surface" --output-format json --cwd /path/to/repo
```

### Interactive slash-command workflow

```bash
python3 .../claude_code_run.py --mode interactive --cwd /path/to/repo -p $'/clear\n/compact Focus on auth'
```
