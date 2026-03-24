#!/usr/bin/env python3
"""Run Claude Code reliably from OpenClaw.

Default mode is auto:
- prompts containing slash commands switch to interactive tmux mode
- all other prompts run headless through `script(1)` to force a PTY
"""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

COMMON_CLAUDE_PATHS = [
    "/home/chensoul/.nvm/versions/node/v25.8.0/bin/claude",
    "/usr/local/bin/claude",
    "/opt/homebrew/bin/claude",
]


def which(name: str) -> str | None:
    for p in os.environ.get("PATH", "").split(":"):
        cand = Path(p) / name
        try:
            if cand.is_file() and os.access(cand, os.X_OK):
                return str(cand)
        except OSError:
            pass
    return None


def resolve_default_claude() -> str:
    env_bin = os.environ.get("CLAUDE_CODE_BIN")
    if env_bin:
        return env_bin
    path_bin = which("claude")
    if path_bin:
        return path_bin
    for candidate in COMMON_CLAUDE_PATHS:
        if Path(candidate).exists():
            return candidate
    return "claude"


DEFAULT_CLAUDE = resolve_default_claude()


def looks_like_slash_commands(prompt: str | None) -> bool:
    if not prompt:
        return False
    return any(line.strip().startswith("/") for line in prompt.splitlines())


def build_headless_cmd(args: argparse.Namespace) -> list[str]:
    cmd: list[str] = [args.claude_bin]

    if args.permission_mode:
        cmd += ["--permission-mode", args.permission_mode]
    if args.prompt is not None:
        cmd += ["-p", args.prompt]
    if args.allowedTools:
        cmd += ["--allowedTools", args.allowedTools]
    if args.output_format:
        cmd += ["--output-format", args.output_format]
    if args.json_schema:
        cmd += ["--json-schema", args.json_schema]
    if args.append_system_prompt:
        cmd += ["--append-system-prompt", args.append_system_prompt]
    if args.system_prompt:
        cmd += ["--system-prompt", args.system_prompt]
    if args.continue_latest:
        cmd.append("--continue")
    if args.resume:
        cmd += ["--resume", args.resume]
    if args.extra:
        cmd += args.extra
    return cmd


def run_with_pty(cmd: list[str], cwd: str | None) -> int:
    script_bin = which("script")
    if not script_bin:
        return subprocess.run(cmd, cwd=cwd, text=True).returncode
    cmd_str = " ".join(shlex.quote(c) for c in cmd)
    return subprocess.run([script_bin, "-q", "-c", cmd_str, "/dev/null"], cwd=cwd, text=True).returncode


def tmux_cmd(socket_path: str, *args: str) -> list[str]:
    return ["tmux", "-S", socket_path, *args]


def tmux_capture(socket_path: str, target: str, lines: int = 200) -> str:
    return subprocess.check_output(
        tmux_cmd(socket_path, "capture-pane", "-p", "-J", "-t", target, "-S", f"-{lines}"),
        text=True,
    )


def tmux_wait_for_text(socket_path: str, target: str, pattern: str, timeout_s: int = 30, poll_s: float = 0.5) -> bool:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            if pattern in tmux_capture(socket_path, target, lines=200):
                return True
        except subprocess.CalledProcessError:
            pass
        time.sleep(poll_s)
    return False


def run_interactive_tmux(args: argparse.Namespace) -> int:
    if not which("tmux"):
        print("tmux not found in PATH; cannot run interactive mode.", file=sys.stderr)
        return 2

    socket_dir = args.tmux_socket_dir or os.environ.get("OPENCLAW_TMUX_SOCKET_DIR") or f"{os.environ.get('TMPDIR', '/tmp')}/openclaw-tmux-sockets"
    Path(socket_dir).mkdir(parents=True, exist_ok=True)
    socket_path = str(Path(socket_dir) / args.tmux_socket_name)
    session = args.tmux_session
    target = f"{session}:0.0"

    subprocess.run(tmux_cmd(socket_path, "kill-session", "-t", session), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.check_call(tmux_cmd(socket_path, "new", "-d", "-s", session, "-n", "shell"))

    cwd = args.cwd or os.getcwd()
    claude_parts = [args.claude_bin]
    if args.permission_mode:
        claude_parts += ["--permission-mode", args.permission_mode]
    if args.allowedTools:
        claude_parts += ["--allowedTools", args.allowedTools]
    if args.append_system_prompt:
        claude_parts += ["--append-system-prompt", args.append_system_prompt]
    if args.system_prompt:
        claude_parts += ["--system-prompt", args.system_prompt]
    if args.continue_latest:
        claude_parts.append("--continue")
    if args.resume:
        claude_parts += ["--resume", args.resume]
    if args.extra:
        claude_parts += args.extra

    launch = f"cd {shlex.quote(cwd)} && " + " ".join(shlex.quote(p) for p in claude_parts)
    subprocess.check_call(tmux_cmd(socket_path, "send-keys", "-t", target, "-l", "--", launch))
    subprocess.check_call(tmux_cmd(socket_path, "send-keys", "-t", target, "Enter"))

    if tmux_wait_for_text(socket_path, target, "Yes, I trust this folder", timeout_s=20):
        subprocess.run(tmux_cmd(socket_path, "send-keys", "-t", target, "Enter"), check=False)
        time.sleep(0.8)
        if tmux_wait_for_text(socket_path, target, "Yes, I trust this folder", timeout_s=2):
            subprocess.run(tmux_cmd(socket_path, "send-keys", "-t", target, "1"), check=False)
            subprocess.run(tmux_cmd(socket_path, "send-keys", "-t", target, "Enter"), check=False)

    if args.prompt:
        for line in [ln for ln in args.prompt.splitlines() if ln.strip()]:
            subprocess.check_call(tmux_cmd(socket_path, "send-keys", "-t", target, "-l", "--", line))
            subprocess.check_call(tmux_cmd(socket_path, "send-keys", "-t", target, "Enter"))
            time.sleep(args.interactive_send_delay_ms / 1000.0)

    print("Started interactive Claude Code in tmux.")
    print("To monitor:")
    print(f"  tmux -S {shlex.quote(socket_path)} attach -t {shlex.quote(session)}")
    print("To snapshot output:")
    print(f"  tmux -S {shlex.quote(socket_path)} capture-pane -p -J -t {shlex.quote(target)} -S -200")

    if args.interactive_wait_s > 0:
        time.sleep(args.interactive_wait_s)
        try:
            print("\n--- tmux snapshot (last 200 lines) ---\n")
            print(tmux_capture(socket_path, target, lines=200))
        except subprocess.CalledProcessError:
            pass
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Run Claude Code reliably (headless or interactive via tmux)")
    ap.add_argument("-p", "--prompt", help="Prompt text")
    ap.add_argument("--mode", choices=["auto", "headless", "interactive"], default="auto")
    ap.add_argument("--permission-mode", default=None)
    ap.add_argument("--allowedTools", dest="allowedTools")
    ap.add_argument("--output-format", dest="output_format", choices=["text", "json", "stream-json"])
    ap.add_argument("--json-schema", dest="json_schema")
    ap.add_argument("--append-system-prompt", dest="append_system_prompt")
    ap.add_argument("--system-prompt", dest="system_prompt")
    ap.add_argument("--continue", dest="continue_latest", action="store_true")
    ap.add_argument("--resume")
    ap.add_argument("--claude-bin", default=DEFAULT_CLAUDE)
    ap.add_argument("--cwd")
    ap.add_argument("--tmux-session", default="claude-code")
    ap.add_argument("--tmux-socket-dir", default=None)
    ap.add_argument("--tmux-socket-name", default="claude-code.sock")
    ap.add_argument("--interactive-wait-s", type=int, default=0)
    ap.add_argument("--interactive-send-delay-ms", type=int, default=800)
    ap.add_argument("extra", nargs=argparse.REMAINDER)
    args = ap.parse_args()

    extra = args.extra
    if extra and extra[0] == "--":
        extra = extra[1:]
    args.extra = extra

    chosen = Path(args.claude_bin)
    if not chosen.exists() and which(args.claude_bin) is None:
        print(f"claude binary not found: {args.claude_bin}", file=sys.stderr)
        print("Set CLAUDE_CODE_BIN=/path/to/claude or pass --claude-bin /path/to/claude", file=sys.stderr)
        return 2

    mode = args.mode
    if mode == "auto" and looks_like_slash_commands(args.prompt):
        mode = "interactive"

    if mode == "interactive":
        return run_interactive_tmux(args)
    return run_with_pty(build_headless_cmd(args), cwd=args.cwd or os.getcwd())


if __name__ == "__main__":
    raise SystemExit(main())
