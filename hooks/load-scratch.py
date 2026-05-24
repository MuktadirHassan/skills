#!/usr/bin/env python3
"""SessionStart hook for the `te` plugin.

Reads .agent-scratch/{notes,decisions,dead-ends}.md from the session cwd and
injects the (tail-trimmed) contents as additionalContext. Silently no-ops when
the directory or files are missing.
"""

from __future__ import annotations

import json
import os
import sys

MAX_BYTES = 2000
FILES = ("notes.md", "decisions.md", "dead-ends.md")


def read_tail(path: str) -> str | None:
    try:
        size = os.path.getsize(path)
    except OSError:
        return None
    try:
        with open(path, "rb") as f:
            if size > MAX_BYTES:
                f.seek(-MAX_BYTES, os.SEEK_END)
                content = f.read().decode("utf-8", errors="replace")
                return f"## {os.path.basename(path)} (tail, {size} bytes total)\n{content}\n"
            content = f.read().decode("utf-8", errors="replace")
            return f"## {os.path.basename(path)}\n{content}\n"
    except OSError:
        return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    cwd = payload.get("cwd") or ""
    scratch = os.path.join(cwd, ".agent-scratch")
    if not cwd or not os.path.isdir(scratch):
        return 0

    parts = []
    for name in FILES:
        chunk = read_tail(os.path.join(scratch, name))
        if chunk:
            parts.append(chunk)

    if not parts:
        return 0

    ctx = (
        "Loaded .agent-scratch context for this project. "
        "Read .agent-scratch/ directly for the full history; this is a snapshot.\n\n"
        + "\n".join(parts)
    )

    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": ctx,
            }
        },
        sys.stdout,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
