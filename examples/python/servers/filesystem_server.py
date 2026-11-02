"""A read-only stdio MCP server that exposes local files and folders.

This is the server side counterpart to ``mcp_client.py``. It speaks the MCP
protocol over stdio and offers two read-only tools:

- ``list_directory`` - list the files and folders inside a shared folder
- ``read_file`` - read the contents of a shared file

The server is intentionally read-only and confines all access to a single
root directory, rejecting path-traversal attempts (``..``). No third-party
packages, no API keys, no network - everything runs on your machine.

Usage:
    python3 servers/filesystem_server.py /path/to/shared/folder

"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "example-python-filesystem"
SERVER_VERSION = "0.1.0"


def _send(obj: Any) -> None:
    """Write one JSON-RPC message (one line) to stdout."""
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def _read_line() -> str | None:
    """Read one line from stdin, or None on EOF."""
    line = sys.stdin.readline()
    if line == "":
        return None
    return line.rstrip("\n")


def _resolve_safe_path(root: str, user_path: str) -> str:
    """Resolve ``user_path`` inside ``root`` and reject escapes.

    Returns the absolute real path. Raises ValueError if the path escapes
    the root directory (path traversal).
    """
    root_real = os.path.realpath(root)
    # Join root with the user-supplied path, then normalize.
    candidate = os.path.realpath(os.path.join(root_real, user_path))
    # Ensure candidate is inside root (equal to root or a descendant).
    if candidate != root_real and not candidate.startswith(root_real + os.sep):
        raise ValueError("path escapes the shared root directory")
    return candidate


def _tool_list_directory() -> dict[str, Any]:
    return {
        "name": "list_directory",
        "description": "List the files and folders in a shared folder (read-only)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Folder path relative to the shared root",
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    }


def _tool_read_file() -> dict[str, Any]:
    return {
        "name": "read_file",
        "description": "Read the contents of a shared file (read-only)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path relative to the shared root",
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    }


def _handle_list_directory(root: str, args: dict[str, Any]) -> dict[str, Any]:
    path = args.get("path", ".")
    safe = _resolve_safe_path(root, path)
    if not os.path.isdir(safe):
        return {"error": f"not a directory: {path}"}
    entries = []
    try:
        for name in sorted(os.listdir(safe)):
            full = os.path.join(safe, name)
            entries.append(
                {
                    "name": name,
                    "type": "directory" if os.path.isdir(full) else "file",
                }
            )
    except PermissionError:
        return {"error": f"permission denied: {path}"}
    except FileNotFoundError:
        return {"error": f"folder not found: {path}"}
    return {"entries": entries, "count": len(entries), "path": path}


def _handle_read_file(root: str, args: dict[str, Any]) -> dict[str, Any]:
    path = args.get("path", "")
    safe = _resolve_safe_path(root, path)
    if not os.path.isfile(safe):
        return {"error": f"not a file: {path}"}
    try:
        with open(safe, "r", encoding="utf-8") as fh:
            contents = fh.read()
    except PermissionError:
        return {"error": f"permission denied: {path}"}
    except FileNotFoundError:
        return {"error": f"file not found: {path}"}
    except UnicodeDecodeError:
        return {"error": f"file is not text: {path}"}
    return {"contents": contents, "path": path}


TOOL_HANDLERS = {
    "list_directory": _handle_list_directory,
    "read_file": _handle_read_file,
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
            "result": {"tools": [_tool_list_directory(), _tool_read_file()]},
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
        except Exception as exc:  # noqa: BLE001 - surface errors to the client
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
        print(
            "Usage: python3 filesystem_server.py <shared-root-folder>", file=sys.stderr
        )
        return 2
    root = argv[0]
    if not os.path.isdir(root):
        print(f"Error: root folder does not exist: {root}", file=sys.stderr)
        return 2

    # Advertise capabilities once on startup (handy for humans reading stdout).
    _send(
        {
            "jsonrpc": "2.0",
            "method": "server.info",
            "params": {
                "name": SERVER_NAME,
                "version": SERVER_VERSION,
                "root": os.path.abspath(root),
                "read_only": True,
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
        response = _handle_request(root, message)
        _send(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
