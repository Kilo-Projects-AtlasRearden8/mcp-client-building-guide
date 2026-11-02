# Python MCP client examples

This folder contains dependency-free Python examples for building MCP
**clients** that connect local LLMs to files, folders, and apps. Everything
runs on your computer with nothing to install beyond Python 3 — no API keys,
no network, no secrets.

## What's inside

| File | Purpose |
|------|---------|
| `mcp_client.py` | A stdio MCP client in the Python standard library (initialize, list tools, call a tool). |
| `servers/filesystem_server.py` | Read-only filesystem MCP server (list_directory, read_file, path-traversal guarded). |
| `servers/notes_app_server.py` | A local notes app MCP server (list_notes, read_note, add_note). |
| `local_llm_bridge.py` | Connects a (simulated) local LLM to files/folders/apps through the MCP client. |
| `test_client.py` | Test suite that drives the client and servers over stdio. |
| `example-data/` | Demo files used by the filesystem server tests. |
| `notes-data/` | Demo notes used by the notes app server tests. |

## Run the tests

From the `examples/python/` folder:

```bash
python3 test_client.py
```

Expected output ends with:

```
[test] ALL TESTS PASSED
```

## Try the local LLM bridge

```bash
# Connect to the filesystem server
python3 local_llm_bridge.py filesystem ./example-data "List the files"

# Connect to the notes app server
python3 local_llm_bridge.py notes ./notes-data "Read welcome.md"
```

The bridge starts a server, connects the MCP client, lists the server's tools
(what an LLM is allowed to do), simulates the LLM choosing a tool, and prints
the result. No real LLM or model download is required.

## Try the client directly

```bash
python3 mcp_client.py python3 servers/filesystem_server.py ./example-data
```

## Production note

These examples use only the Python standard library so they run anywhere and
show the protocol clearly. For production apps, consider the official
[modelcontextprotocol/mcp-python](https://github.com/modelcontextprotocol/mcp-python)
SDK (`pip install mcp`), which is already available in this environment.

## Privacy & safety

- All servers are local stdio processes; nothing is uploaded.
- The filesystem server is read-only and blocks path-traversal (`..`).
- Only share folders you are comfortable an AI reading.
- See the safety rules in `../docs/05-privacy-safety.md`.

## Credit

Written and published by **Asdale Dynamics, LLC** (Indiana, formed October 2026).
Dylan Asdale — registered nurse, AI author, founder of Asdale Dynamics, LLC.
Book: *The Massive AI Manual* — hub site: dylanasdale.github.io

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.
