# claude-code-skill

A reusable **OpenClaw skill** for running the local **Claude Code CLI** (`claude`) in either **headless** or **interactive** mode.

This repository is designed for people who want a practical, reusable way to let OpenClaw delegate work to Claude Code for repository analysis, planning, refactors, bug fixing, test repair, and structured output workflows.

---

## Why this skill exists

Claude Code is very capable, but wiring it into an OpenClaw workflow in a repeatable way takes some glue:

- deciding when to use headless vs interactive mode
- handling slash-command workflows such as `/clear` and `/compact`
- forcing PTY behavior when needed
- using `tmux` for interactive monitoring
- keeping invocation patterns consistent across repositories

This skill packages those conventions into a reusable OpenClaw-friendly wrapper.

---

## Features

- Run **Claude Code** from OpenClaw
- Support **headless** `claude -p` workflows
- Support **interactive slash-command** workflows through `tmux`
- Support **plan mode**, `--allowedTools`, JSON output, continue, and resume
- Include reusable **OpenClaw prompt templates**
- Include a **Chinese quick reference** for common trigger phrases
- Work with a general local Claude Code install instead of a machine-specific hardcoded path

---

## Good fit for

Use this skill when you want OpenClaw to delegate work to **Claude Code specifically**, for example:

- analyze a repository structure
- inspect a codebase and produce an implementation plan
- fix bugs and verify the result
- run tests and repair failures
- generate structured JSON output for downstream use
- run interactive Claude Code slash commands
- continue or resume a previous Claude Code session

---

## Not a good fit for

This skill is usually **not** the best choice when:

- the task is a tiny one-line local edit
- the task is only reading a file or small snippet
- OpenClaw can answer directly faster than invoking Claude Code
- the workflow should use an ACP-thread or remote harness instead of the local `claude` binary

---

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

---

## Requirements

### Required

- OpenClaw-compatible skill environment
- Claude Code CLI available locally as `claude`, or configured through `CLAUDE_CODE_BIN`
- Python 3.9+

### Recommended

- `tmux` for interactive slash-command workflows
- `script(1)` for stronger PTY behavior in headless mode

---

## Installation

Copy this repository's contents into a skill directory, for example:

```bash
mkdir -p ~/.openclaw/skills/claude-code
cp -R ./* ~/.openclaw/skills/claude-code/
```

Or keep it in a workspace-local skills directory used by OpenClaw.

---

## Quick examples

### 1. Analyze a repository in plan mode

```bash
python3 scripts/claude_code_run.py \
  -p "Analyze this repository and explain the architecture." \
  --cwd /path/to/repo \
  --permission-mode plan
```

### 2. Fix failing tests

```bash
python3 scripts/claude_code_run.py \
  -p "Run the tests, fix failures, and summarize the root cause." \
  --cwd /path/to/repo \
  --allowedTools "Bash,Read,Edit"
```

### 3. Produce structured JSON output

```bash
python3 scripts/claude_code_run.py \
  -p "Summarize this project in 5 bullets." \
  --cwd /path/to/repo \
  --output-format json
```

### 4. Run interactive slash commands

```bash
python3 scripts/claude_code_run.py \
  --mode interactive \
  --cwd /path/to/repo \
  --allowedTools "Bash,Read,Edit,Write" \
  -p $'/clear\n/compact Focus on auth module'
```

---

## How the wrapper chooses a mode

### Headless mode

Best for:

- one-shot prompts
- automation
- summaries
- JSON output
- plan-mode analysis

### Interactive mode

Best for:

- slash commands such as `/clear` and `/compact`
- multi-step interactive Claude Code workflows
- cases where you want to inspect or monitor the session in `tmux`

If the prompt contains slash-command lines, the wrapper can automatically switch into interactive mode.

---

## Binary discovery

The wrapper resolves the Claude Code binary in this order:

1. `--claude-bin`
2. `CLAUDE_CODE_BIN`
3. `claude` found in `PATH`
4. a few common fallback locations

This keeps the skill portable across machines instead of assuming one hardcoded binary path.

---

## Included references

- `SKILL.md` — main skill instructions and usage guidance
- `references/official-docs.md` — distilled notes from the Claude Code docs
- `references/doc-index.md` — official documentation entry points
- `references/openclaw-prompts.md` — reusable prompt templates for OpenClaw-driven workflows

---

## Known limitations

- Interactive mode expects `tmux`
- Headless behavior is best when `script(1)` is available
- This skill wraps the local Claude Code CLI; it does not replace hosted or ACP-based Claude harness flows
- Behavior can still vary depending on the installed Claude Code version

---

## FAQ

### Why not just call `claude` directly?

You can, but this skill gives OpenClaw a stable, reusable way to:

- choose a mode automatically
- manage PTY behavior
- support tmux-backed interactive sessions
- keep prompts and examples consistent

### Why is there no packaged `.skill` artifact in this repo?

This repository is intentionally source-first. The editable skill files live here; packaged artifacts can be generated separately when needed.

### Is this tied to one machine?

No. The wrapper now prefers environment-based and PATH-based binary resolution, with only a few fallbacks for convenience.

---

## License

MIT
