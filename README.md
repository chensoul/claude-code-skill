# claude-code-skill

A reusable OpenClaw skill for running the local Claude Code CLI (`claude`) in either headless or interactive mode.

This repository contains the editable source files for the skill and is intended for reuse, customization, and publication.

## What this skill is for

Use this skill when you want OpenClaw to delegate work to **Claude Code** specifically, including:

- repository analysis
- plan-mode research
- bug fixing
- refactors
- test repair
- structured JSON output
- interactive slash-command workflows such as `/clear` and `/compact`

## What this skill is not for

This skill is usually **not** the best choice when:

- the task is a tiny one-line edit
- the task is just reading a file
- OpenClaw can directly answer the question faster without invoking Claude Code
- you want an ACP-thread workflow instead of the local `claude` CLI

## Repository layout

```text
.
├── SKILL.md
├── scripts/
│   └── claude_code_run.py
├── references/
│   ├── doc-index.md
│   ├── official-docs.md
│   └── openclaw-prompts.md
├── README.md
├── LICENSE
└── .gitignore
```

## Requirements

### Required

- OpenClaw-compatible skill environment
- Claude Code CLI available locally as `claude`, or configured through `CLAUDE_CODE_BIN`
- Python 3.9+

### Recommended

- `tmux` for interactive slash-command workflows
- `script(1)` for stronger PTY behavior in headless mode

## Installation

Copy this repository's contents into a skill directory, for example:

```bash
mkdir -p ~/.openclaw/skills/claude-code
cp -R ./* ~/.openclaw/skills/claude-code/
```

Or keep it in a workspace-local skills directory used by OpenClaw.

## Usage

### Headless analysis

```bash
python3 scripts/claude_code_run.py \
  -p "Analyze this repository and explain the architecture." \
  --cwd /path/to/repo \
  --permission-mode plan
```

### Fix tests

```bash
python3 scripts/claude_code_run.py \
  -p "Run the tests, fix failures, and summarize the root cause." \
  --cwd /path/to/repo \
  --allowedTools "Bash,Read,Edit"
```

### JSON output

```bash
python3 scripts/claude_code_run.py \
  -p "Summarize this project in 5 bullets." \
  --cwd /path/to/repo \
  --output-format json
```

### Interactive slash commands

```bash
python3 scripts/claude_code_run.py \
  --mode interactive \
  --cwd /path/to/repo \
  --allowedTools "Bash,Read,Edit,Write" \
  -p $'/clear\n/compact Focus on auth module'
```

## Binary discovery

The wrapper resolves the Claude Code binary in this order:

1. `--claude-bin`
2. `CLAUDE_CODE_BIN`
3. `claude` found in `PATH`
4. a small set of common fallback locations

## References

- `SKILL.md` — main skill instructions and usage guidance
- `references/official-docs.md` — distilled notes from the Claude Code docs
- `references/doc-index.md` — official documentation entry points
- `references/openclaw-prompts.md` — reusable prompt templates for OpenClaw-driven workflows

## License

MIT
