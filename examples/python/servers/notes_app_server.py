"""A stdio MCP server that simulates a local notes app.

This server represents an "app" that a local LLM can reach through an MCP
client. It offers tools to list, read, and add notes stored in a local folder.
All data stays on your machine.

Usage:
    python3 servers/notes_app_server.py /path/to/notes/folder

"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "example-python-notes-app"
SERVER_VERSION = "0.1.0"


def _send(obj: Any) -> None:
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def _read_line() -> str | None:
    line = sys.stdin.readline()
    if line == "":
        return None
    return line.rstrip("\n")


def _resolve_safe_path(root: str, user_path: str) -> str:
    root_real = os.path.realpath(root)
    candidate = os.path.realpath(os.path.join(root_real, user_path))
    if candidate != root_real and not candidate.startswith(root_real + os.sep):
        raise ValueError("path escapes the notes root directory")
    return candidate


def _ensure_notes_dir(root: str) -> None:
    os.makedirs(root, exist_ok=True)


def _tool_list_notes() -> dict[str, Any]:
    return {
        "name": "list_notes",
        "description": "List notes in the local notes app folder",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    }


def _tool_read_note() -> dict[str, Any]:
    return {
        "name": "read_note",
        "description": "Read the contents of a note by filename",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Note filename (e.g. meeting.md)",
                }
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    }


def _tool_add_note() -> dict[str, Any]:
    return {
        "name": "add_note",
        "description": "Create or overwrite a note in the local notes app",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Note filename (e.g. meeting.md)",
                },
                "content": {
                    "type": "string",
                    "description": "Note contents",
                },
            },
            "required": ["name", "content"],
            "additionalProperties": False,
        },
    }


def _handle_list_notes(root: str) -> dict[str, Any]:
    _ensure_notes_dir(root)
    notes = []
    try:
        for name in sorted(os.listdir(root)):
            full = os.path.join(root, name)
            if os.path.isfile(full) and name.lower().endswith((".md", ".txt")):
                notes.append(name)
    except FileNotFoundError:
        return {"notes": [], "count": 0}
    return {"notes": notes, "count": len(notes)}


def _handle_read_note(root: str, args: dict[str, Any]) -> dict[str, Any]:
    name = args.get("name", "")
    safe = _resolve_safe_path(root, name)
    if not os.path.isfile(safe):
        return {"error": f"note not found: {name}"}
    try:
        with open(safe, "r", encoding="utf-8") as fh:
            return {"contents": fh.read(), "name": name}
    except (UnicodeDecodeError, PermissionError):
        return {"error": f"cannot read note: {name}"}


def _handle_add_note(root: str, args: dict[str, Any]) -> dict[str, Any]:
    name = args.get("name", "")
    content = args.get("content", "")
    # Reject path separators in the name so notes stay flat inside root.
    if "/" in name or "\\" in name or name in (".", ".."):
        return {"error": "invalid note name"}
    safe = _resolve_safe_path(root, name)
    _ensure_notes_dir(root)
    with open(safe, "w", encoding="utf-8") as fh:
        fh.write(content)
    return {"ok": True, "name": name, "bytes": len(content.encode("utf-8"))}


TOOL_HANDLERS = {
    "list_notes": lambda root, args: _handle_list_notes(root),
    "read_note": lambda root, args: _handle_read_note(root, args),
    "add_note": lambda root, args: _handle_add_note(root, args),
}


def _handle_request(root: str, message: dict[str, Any]) -> dict[str, Any]:
    method = message.get("method")
    msg_id = message.get("id")
    params = message.get("params") or {}

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": [_tool_list_notes(), _tool_read_note(), _tool_add_note()]
            },
        }

    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        handler = TOOL_HANDLERS.get(name)
        if handler is None:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"unknown tool: {name}"},
            }
        try:
            result = handler(root, args)
        except ValueError as exc:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32603, "message": str(exc)},
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32603, "message": f"internal error: {exc}"},
            }
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}

    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"unknown method: {method}"},
    }


def main(argv: list | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("Usage: python3 notes_app_server.py <notes-folder>", file=sys.stderr)
        return 2
    root = argv[0]
    _ensure_notes_dir(root)

    _send(
        {
            "jsonrpc": "2.0",
            "method": "server.info",
            "params": {
                "name": SERVER_NAME,
                "version": SERVER_VERSION,
                "root": os.path.abspath(root),
                "read_only": False,
            },
        }
    )

    while True:
        line = _read_line()
        if line is None:
            break
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            _send(
                {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": "parse error"},
                }
            )
            continue
        _send(_handle_request(root, message))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
