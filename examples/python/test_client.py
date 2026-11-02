"""Test suite for the Python MCP client and example servers.

Runs entirely on stdio with no third-party packages, no API keys, and no
network. Verifies:

- MCPClient connects, initializes, lists tools, calls tools
- Filesystem server: list_directory, read_file, path-traversal rejection
- Notes app server: list_notes, read_note, add_note
- local_llm_bridge end-to-end flow

Usage:
    python3 test_client.py
"""

from __future__ import annotations

import os
import subprocess
import sys

# Make examples importable when run from the repo root.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_client import MCPClient, MCPClientError

ROOT = os.path.dirname(os.path.abspath(__file__))
EXAMPLE_DATA = os.path.join(ROOT, "example-data")
NOTES_DATA = os.path.join(ROOT, "notes-data")

passed = 0
failed = 0


def test(name, fn):
    global passed, failed
    try:
        fn()
        passed += 1
        print(f"[test] PASS {name}")
    except Exception as exc:  # noqa: BLE001
        failed += 1
        print(f"[test] FAIL {name}: {exc}")


def start_server(command):
    proc = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    return proc


def send(proc, message, expect_id=None):
    payload = json.dumps(message) + "\n"
    proc.stdin.write(payload)
    proc.stdin.flush()
    target = message.get("id") if expect_id is None else expect_id
    while True:
        line = proc.stdout.readline()
        if line == "":
            raise MCPClientError("server closed stdout")
        try:
            res = json.loads(line)
        except json.JSONDecodeError:
            continue
        # Skip notifications (no matching id) until we get our response.
        if res.get("id") == target:
            return res


import json


def close(proc):
    try:
        if proc.stdin and not proc.stdin.closed:
            proc.stdin.close()
    except (OSError, ValueError):
        pass
    try:
        proc.terminate()
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()


# --------------------------------------------------------------- filesystem
def t_filesystem_initialize():
    proc = start_server(["python3", "servers/filesystem_server.py", EXAMPLE_DATA])
    try:
        res = send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0.0"},
                },
            },
        )
        if res.get("jsonrpc") != "2.0" or res.get("id") != 1:
            raise AssertionError("bad envelope")
        result = res.get("result") or {}
        if result.get("protocolVersion") != "2024-11-05":
            raise AssertionError("bad protocolVersion")
        if (
            not result.get("serverInfo")
            or result["serverInfo"].get("name") != "example-python-filesystem"
        ):
            raise AssertionError("bad serverInfo")
        caps = result.get("capabilities") or {}
        if "tools" not in caps:
            raise AssertionError("missing tools capability")
    finally:
        close(proc)


def t_filesystem_list_tools():
    proc = start_server(["python3", "servers/filesystem_server.py", EXAMPLE_DATA])
    try:
        send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0.0"},
                },
            },
        )
        res = send(
            proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        )
        names = [t["name"] for t in (res.get("result") or {}).get("tools", [])]
        if "list_directory" not in names:
            raise AssertionError("missing list_directory")
        if "read_file" not in names:
            raise AssertionError("missing read_file")
    finally:
        close(proc)


def t_filesystem_list_directory():
    proc = start_server(["python3", "servers/filesystem_server.py", EXAMPLE_DATA])
    try:
        send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0.0"},
                },
            },
        )
        res = send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "list_directory", "arguments": {"path": "."}},
            },
        )
        text = json.dumps(res.get("result") or {})
        if "welcome.txt" not in text:
            raise AssertionError("welcome.txt not listed")
        if "notes.md" not in text:
            raise AssertionError("notes.md not listed")
    finally:
        close(proc)


def t_filesystem_read_file():
    proc = start_server(["python3", "servers/filesystem_server.py", EXAMPLE_DATA])
    try:
        send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0.0"},
                },
            },
        )
        res = send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "read_file", "arguments": {"path": "welcome.txt"}},
            },
        )
        text = json.dumps(res.get("result") or {})
        if "Welcome to your first MCP server!" not in text:
            raise AssertionError("unexpected file contents")
    finally:
        close(proc)


def t_filesystem_path_traversal_rejected():
    proc = start_server(["python3", "servers/filesystem_server.py", EXAMPLE_DATA])
    try:
        send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0.0"},
                },
            },
        )
        res = send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "read_file",
                    "arguments": {"path": "../../etc/passwd"},
                },
            },
        )
        if "error" not in res:
            raise AssertionError("expected an error for path traversal")
    finally:
        close(proc)


def t_filesystem_unknown_tool_rejected():
    proc = start_server(["python3", "servers/filesystem_server.py", EXAMPLE_DATA])
    try:
        send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0.0"},
                },
            },
        )
        res = send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "delete_file", "arguments": {}},
            },
        )
        if "error" not in res:
            raise AssertionError("expected an error for unknown tool")
    finally:
        close(proc)


# --------------------------------------------------------------- notes app
def t_notes_list():
    proc = start_server(["python3", "servers/notes_app_server.py", NOTES_DATA])
    try:
        send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0.0"},
                },
            },
        )
        res = send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "list_notes", "arguments": {}},
            },
        )
        text = json.dumps(res.get("result") or {})
        if "welcome.md" not in text:
            raise AssertionError("welcome.md not listed")
    finally:
        close(proc)


def t_notes_read_and_add():
    proc = start_server(["python3", "servers/notes_app_server.py", NOTES_DATA])
    try:
        send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0.0"},
                },
            },
        )
        # add a note
        res = send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "add_note",
                    "arguments": {
                        "name": "test-note.md",
                        "content": "hello from the MCP client",
                    },
                },
            },
        )
        if not (res.get("result") or {}).get("ok"):
            raise AssertionError("add_note did not report ok")
        # read it back
        res = send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "read_note", "arguments": {"name": "test-note.md"}},
            },
        )
        text = json.dumps(res.get("result") or {})
        if "hello from the MCP client" not in text:
            raise AssertionError("added note contents not readable back")
    finally:
        close(proc)


# --------------------------------------------------------------- MCPClient library
def t_mcp_client_library():
    client = MCPClient(["python3", "servers/filesystem_server.py", EXAMPLE_DATA])
    try:
        client.start()
        info = client.initialize()
        if info.get("serverInfo", {}).get("name") != "example-python-filesystem":
            raise AssertionError("bad server info from library client")
        tools = client.list_tools()
        names = [t.name for t in tools]
        if "list_directory" not in names or "read_file" not in names:
            raise AssertionError("library client missing tools")
        result = client.call_tool("read_file", {"path": "welcome.txt"})
        if "Welcome to your first MCP server!" not in json.dumps(result):
            raise AssertionError("library client read_file failed")
    finally:
        client.close()


# --------------------------------------------------------------- local_llm_bridge
def t_bridge_filesystem():
    proc = subprocess.Popen(
        [
            "python3",
            "local_llm_bridge.py",
            "filesystem",
            EXAMPLE_DATA,
            "List the files",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    out, err = proc.communicate(timeout=20)
    if proc.returncode != 0:
        raise AssertionError(f"bridge exited {proc.returncode}: {err}")
    if "welcome.txt" not in out:
        raise AssertionError("bridge output missing welcome.txt")


def t_bridge_notes():
    proc = subprocess.Popen(
        ["python3", "local_llm_bridge.py", "notes", NOTES_DATA, "Read welcome.md"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    out, err = proc.communicate(timeout=20)
    if proc.returncode != 0:
        raise AssertionError(f"bridge exited {proc.returncode}: {err}")
    if "Meeting notes" not in out:
        raise AssertionError("bridge output missing note contents")


def main():
    print("Python MCP client test suite")
    print("=" * 40)

    test("filesystem initialize", t_filesystem_initialize)
    test("filesystem list_tools", t_filesystem_list_tools)
    test("filesystem list_directory", t_filesystem_list_directory)
    test("filesystem read_file", t_filesystem_read_file)
    test("filesystem path traversal rejected", t_filesystem_path_traversal_rejected)
    test("filesystem unknown tool rejected", t_filesystem_unknown_tool_rejected)
    test("notes list_notes", t_notes_list)
    test("notes read and add", t_notes_read_and_add)
    test("MCPClient library", t_mcp_client_library)
    test("local_llm_bridge filesystem", t_bridge_filesystem)
    test("local_llm_bridge notes", t_bridge_notes)

    print("=" * 40)
    print(f"[test] {passed} passed, {failed} failed")
    if failed:
        print("[test] SOME TESTS FAILED")
        return 1
    print("[test] ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
