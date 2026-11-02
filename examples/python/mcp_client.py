"""A dependency-free stdio MCP client in pure Python standard library.

This module implements a small Model Context Protocol (MCP) client that talks
to an MCP server over standard input/output (stdio). It is intentionally
written with no third-party dependencies so it runs on any computer that has
Python 3 installed - nothing to pip-install, no API keys, no network required.

It is meant for learning: it shows exactly what an MCP client does
(initialize, list tools, call a tool) using plain JSON-RPC messages.

Example usage as a library:

    from mcp_client import MCPClient

    client = MCPClient(["python3", "servers/filesystem_server.py", "./example-data"])
    await client.start()
    await client.initialize()
    tools = await client.list_tools()
    result = await client.call_tool("read_file", {"path": "notes.txt"})
    await client.close()

Example usage from the command line:

    python3 mcp_client.py python3 servers/filesystem_server.py ./example-data

"""

from __future__ import annotations

import json
import queue
import shlex
import subprocess
import sys
import threading
from dataclasses import dataclass, field
from typing import Any


class MCPClientError(RuntimeError):
    """Raised when the MCP client or server reports an error."""


@dataclass
class MCPTool:
    """A single tool offered by an MCP server."""

    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPClient:
    """A stdio-based MCP client.

    Parameters
    ----------
    command:
        Command and arguments used to start the MCP server, e.g.
        ``["python3", "servers/filesystem_server.py", "./example-data"]``.
    """

    command: list[str]
    _proc: subprocess.Popen | None = None
    _pending: queue.Queue[str] = field(default_factory=queue.Queue)
    _reader_thread: threading.Thread | None = None
    _initialized: bool = False
    _message_id: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock)

    # ------------------------------------------------------------------ start
    def start(self) -> None:
        """Start the MCP server subprocess and a stdout reader thread."""
        if self._proc is not None:
            return
        try:
            self._proc = subprocess.Popen(
                self.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
        except FileNotFoundError as exc:
            raise MCPClientError(
                f"Could not start server command: {self.command[0]}"
            ) from exc

        # A dedicated thread reads stdout line-by-line and enqueues lines.
        # This avoids select/buffering pitfalls on text streams.
        self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._reader_thread.start()

    def _reader_loop(self) -> None:
        """Continuously read lines from server stdout and enqueue them."""
        proc = self._proc
        if proc is None or proc.stdout is None:
            return
        for line in proc.stdout:
            line = line.strip()
            if line:
                self._pending.put(line)
        # Stream ended: unblock any waiting reader with a sentinel.
        self._pending.put(None)

    # --------------------------------------------------------------- messaging
    def _next_id(self) -> int:
        with self._lock:
            self._message_id += 1
            return self._message_id

    def _send(self, message: dict[str, Any]) -> None:
        if self._proc is None or self._proc.stdin is None:
            raise MCPClientError("Server process is not running")
        payload = json.dumps(message) + "\n"
        self._proc.stdin.write(payload)
        self._proc.stdin.flush()

    def _read_response(self, expected_id: int, timeout: float = 10.0) -> dict[str, Any]:
        """Read one JSON-RPC response line from the server stdout.

        Skips notifications (no matching id) until the response for
        ``expected_id`` arrives.
        """
        while True:
            try:
                line = self._pending.get(timeout=timeout)
            except queue.Empty:
                raise MCPClientError("Timed out waiting for server response")
            if line is None:
                # Stream ended without a response.
                raise MCPClientError("Server process closed stdout before responding")
            try:
                res = json.loads(line)
            except json.JSONDecodeError:
                # Not valid JSON; skip noisy lines and keep waiting.
                continue
            if res.get("id") != expected_id:
                # Notification or a response to an older request; skip it.
                continue
            return res

    def _request(
        self, method: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        msg_id = self._next_id()
        message: dict[str, Any] = {"jsonrpc": "2.0", "id": msg_id, "method": method}
        if params is not None:
            message["params"] = params
        self._send(message)
        return self._read_response(msg_id)

    # --------------------------------------------------------------- protocol
    def initialize(self) -> dict[str, Any]:
        """Run the MCP initialize handshake."""
        res = self._request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "example-python-client", "version": "1.0.0"},
            },
        )
        if "error" in res:
            raise MCPClientError(f"initialize error: {res['error']}")
        result = res.get("result")
        if not result:
            raise MCPClientError("initialize missing result")
        self._initialized = True
        return result

    def list_tools(self) -> list[MCPTool]:
        """Ask the server for its list of tools."""
        res = self._request("tools/list", {})
        if "error" in res:
            raise MCPClientError(f"tools/list error: {res['error']}")
        tools_raw = res.get("result", {}).get("tools", [])
        tools: list[MCPTool] = []
        for t in tools_raw:
            tools.append(
                MCPTool(
                    name=t.get("name", ""),
                    description=t.get("description", ""),
                    input_schema=t.get("inputSchema", {}),
                )
            )
        return tools

    def call_tool(
        self, name: str, arguments: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Call a tool on the server and return its structured result."""
        if arguments is None:
            arguments = {}
        res = self._request("tools/call", {"name": name, "arguments": arguments})
        if "error" in res:
            raise MCPClientError(f"tools/call({name}) error: {res['error']}")
        return res.get("result", {})

    def close(self) -> None:
        """Close the client and stop the server process."""
        if self._proc is None:
            return
        try:
            if self._proc.stdin is not None and not self._proc.stdin.closed:
                self._proc.stdin.close()
        except (OSError, ValueError):
            pass
        try:
            self._proc.terminate()
            self._proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self._proc.kill()
        except (OSError, ValueError):
            pass
        self._proc = None


def run_cli(argv: list[str]) -> int:
    """Command-line entry point.

    Usage:
        python3 mcp_client.py <server-command> [server-args...]
    """
    if len(argv) < 2:
        print(
            "Usage: python3 mcp_client.py <server-command> [server-args...]",
            file=sys.stderr,
        )
        print(
            "Example: python3 mcp_client.py python3 servers/filesystem_server.py ./example-data",
            file=sys.stderr,
        )
        return 2

    command = shlex.join(argv[1:]) if False else argv[1:]
    client = MCPClient(command)
    try:
        client.start()
        info = client.initialize()
        print(
            f"Connected to server: {info.get('serverInfo', {}).get('name', 'unknown')}"
        )
        tools = client.list_tools()
        print(f"Available tools ({len(tools)}):")
        for t in tools:
            print(f"  - {t.name}: {t.description}")
    except MCPClientError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(sys.argv))
