# claude-code-skill

A general-purpose OpenClaw skill for running the local Claude Code CLI (`claude`) in headless or interactive mode.

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
├── claude-code.skill
└── README.md
```

## What it does

- run Claude Code from OpenClaw
- support headless `claude -p` execution
- support interactive slash-command workflows through tmux
- support plan mode, allowedTools, JSON output, continue, and resume
- include reusable OpenClaw prompt templates and Chinese quick reference

## Notes

- `claude-code.skill` is the packaged artifact
- `SKILL.md` + `scripts/` + `references/` are the editable source files
