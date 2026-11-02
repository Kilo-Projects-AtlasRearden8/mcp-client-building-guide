# MCP Client Cheat Sheet (printable)

A one-page reference for building and using MCP clients that connect local LLMs
to files, folders, and apps. Print this and keep it by your computer.

Published by **Asdale Dynamics, LLC** — MIT License, Copyright (c) 2026 Asdale Dynamics, LLC.

---

## 1. What MCP does

```
You ──► AI app (MCP client) ──► MCP server ──► your files/folders/apps
```

- **Client:** inside the AI app; starts the server, lists tools, carries requests.
- **Server:** a small program that exposes tools (read file, list folder, etc.).
- **stdio:** the most common beginner connection; server runs as a process on your computer.

## 2. Connect to local files and folders (6 steps)

1. Pick ONE folder to share (not your whole computer).
2. Start a read-only filesystem MCP server pointing at that folder.
3. Connect the MCP client to the server.
4. List the server's tools (`list_directory`, `read_file`).
5. Call a tool through the client (list or read).
6. Stop the server when done.

## 3. Build your first Python MCP client

```python
from mcp_client import MCPClient

client = MCPClient(["python3", "servers/filesystem_server.py", "./example-data"])
client.start()
info = client.initialize()            # handshake
tools = client.list_tools()           # what the AI can do
result = client.call_tool("read_file", {"path": "welcome.txt"})
client.close()                        # stops the server
```

Zero third-party dependencies — Python standard library only.

## 4. Run the examples

From `examples/python/`:

| Command | What it does |
|---------|--------------|
| `python3 test_client.py` | Run the full test suite (11 tests) |
| `python3 local_llm_bridge.py filesystem ./example-data "List the files"` | Filesystem server + client |
| `python3 local_llm_bridge.py notes ./notes-data "Read welcome.md"` | Notes app server + client |
| `python3 mcp_client.py python3 servers/filesystem_server.py ./example-data` | Client CLI, lists tools |

Expected test output ends with:

```
[test] ALL TESTS PASSED
```

## 5. Privacy & safety (golden rules)

- [ ] Share specific folders, never your whole computer
- [ ] Never share folders with secrets (passwords, keys, IDs, tax, medical, bank data)
- [ ] Prefer read-only servers
- [ ] You are in charge — stop or remove a server anytime
- [ ] Assume the AI provider sees what you send it

No API keys, secrets, or personal data are needed for any example.

## 6. Common MCP tools

| Tool | What it does |
|------|--------------|
| `list_directory` | List files/folders in a shared folder |
| `read_file` | Read the contents of a shared file |
| `list_notes` | List notes in a local notes app |
| `read_note` | Read a note by filename |
| `add_note` | Create or overwrite a note |

## 7. JSON-RPC message shape (one per line over stdio)

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{...}}
{"jsonrpc":"2.0","id":1,"result":{...}}
{"jsonrpc":"2.0","id":1,"error":{"code":-32601,"message":"unknown tool"}}
```

## 8. Troubleshooting

| Problem | Fix |
|---------|-----|
| Server won't start | Check the folder path and that the folder exists |
| Client can't connect | Confirm the server command and path |
| No file tools shown | The server may not be running |
| Permission denied | Your user needs read access to the folder |

## 9. Credit

Written and published by **Asdale Dynamics, LLC** (Indiana, formed October 2026).
Dylan Asdale — registered nurse, AI author, founder of Asdale Dynamics, LLC.
Book: *The Massive AI Manual* — hub site: dylanasdale.github.io

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.
