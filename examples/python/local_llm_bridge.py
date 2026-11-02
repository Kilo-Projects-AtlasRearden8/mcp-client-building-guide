"""Demonstrate connecting a local LLM to files, folders, and apps via MCP.

This script shows the complete flow of an MCP **client** bridging a local LLM
to local files, folders, and apps:

1. Start an MCP server (filesystem or notes app).
2. Connect the stdio MCP client to it.
3. List the server's tools (what the LLM is allowed to do).
4. Simulate the LLM choosing and calling a tool through the client.
5. Print the result back as the LLM would.

No real LLM, API key, or network connection is required. The "LLM" here is a
small rule-based stand-in that picks a tool based on the user's question, so
the example is fully testable and privacy-safe.

Usage:
    python3 local_llm_bridge.py filesystem ./example-data "What files are in the shared folder?"
    python3 local_llm_bridge.py notes ./notes-data "Read my meeting note"

"""

from __future__ import annotations

import os
import sys

# Allow running from the repo root without installing anything.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_client import MCPClient, MCPClientError

EXAMPLE_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "example-data")
NOTES_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes-data")


def pick_tool(question: str, tools: list[str]) -> str | None:
    """A tiny stand-in LLM: picks a tool based on keywords in the question.

    A real local LLM (Ollama, llama.cpp, etc.) would receive the tool list and
    decide which tool to call. Here we hard-code a few keyword rules so the
    example runs without installing a model.
    """
    q = question.lower()
    if "list" in q or "files" in q or "folder" in q:
        if "list_directory" in tools:
            return "list_directory"
        if "list_notes" in tools:
            return "list_notes"
    if "read" in q or "note" in q or "contents" in q:
        if "read_file" in tools:
            return "read_file"
        if "read_note" in tools:
            return "read_note"
    if ("add" in q or "write" in q or "save" in q) and "add_note" in tools:
        return "add_note"
    return None


def pick_arguments(tool: str, question: str) -> dict:
    """Choose tool arguments based on the question (stand-in LLM reasoning)."""
    if tool == "list_directory":
        return {"path": "."}
    if tool == "list_notes":
        return {}
    if tool == "read_file":
        # Guess a likely filename mentioned in the question.
        for token in question.split():
            token = token.strip(".,?!")
            if "." in token and not token.startswith("."):
                return {"path": token}
        return {"path": "welcome.txt"}
    if tool == "read_note":
        for token in question.split():
            token = token.strip(".,?!")
            if token.endswith((".md", ".txt")):
                return {"name": token}
        return {"name": "welcome.md"}
    if tool == "add_note":
        return {
            "name": "llm-created.md",
            "content": f"Note created by the local LLM bridge.\nQuestion: {question}\n",
        }
    return {}


def run(mode: str, root: str, question: str) -> int:
    if mode == "filesystem":
        server_cmd = ["python3", "servers/filesystem_server.py", root]
    elif mode == "notes":
        server_cmd = ["python3", "servers/notes_app_server.py", root]
    else:
        print(f"Unknown mode: {mode} (use 'filesystem' or 'notes')", file=sys.stderr)
        return 2

    client = MCPClient(server_cmd)
    try:
        client.start()

        # 1. Initialize the MCP session (client <-> server handshake).
        info = client.initialize()
        server_name = info.get("serverInfo", {}).get("name", "unknown")
        print(f"[bridge] Connected to MCP server: {server_name}")

        # 2. List tools - this is what the LLM sees it can do.
        tools = client.list_tools()
        tool_names = [t.name for t in tools]
        print(f"[bridge] Server offers tools: {', '.join(tool_names)}")

        # 3. The (simulated) LLM decides which tool to call.
        chosen = pick_tool(question, tool_names)
        if chosen is None:
            print("[bridge] The LLM could not match a tool to your question.")
            print(
                "[bridge] Try asking: 'List the files', 'Read welcome.txt', or 'Add a note'."
            )
            return 0

        arguments = pick_arguments(chosen, question)
        print(f"[bridge] LLM chooses tool '{chosen}' with arguments {arguments}")

        # 4. Client calls the tool on the server; result comes back.
        result = client.call_tool(chosen, arguments)

        # 5. Present the result as the LLM's answer.
        print("\n[bridge] LLM answer (from tool result):")
        if "entries" in result:
            for entry in result["entries"]:
                print(f"  - {entry['name']} ({entry['type']})")
        elif "contents" in result:
            print(result["contents"])
        elif "notes" in result:
            if result["notes"]:
                for n in result["notes"]:
                    print(f"  - {n}")
            else:
                print("  (no notes)")
        elif result.get("ok"):
            print(f"  Saved note '{result['name']}' ({result['bytes']} bytes).")
        elif "error" in result:
            print(f"  Error: {result['error']}")
        else:
            print(result)
    except MCPClientError as exc:
        print(f"[bridge] Error: {exc}", file=sys.stderr)
        return 1
    finally:
        client.close()
    return 0


def main(argv: list | None = None) -> int:
    argv = sys.argv[1:]
    if len(argv) < 3:
        print(
            "Usage: python3 local_llm_bridge.py <mode> <root-folder> <question>",
            file=sys.stderr,
        )
        print("Modes: filesystem, notes", file=sys.stderr)
        print(
            "Example: python3 local_llm_bridge.py filesystem ./example-data 'List the files'",
            file=sys.stderr,
        )
        return 2
    return run(argv[0], argv[1], " ".join(argv[2:]))


if __name__ == "__main__":
    raise SystemExit(main())
