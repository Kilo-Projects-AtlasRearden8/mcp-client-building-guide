# 03. Building your first Python MCP client

## The idea

In this section you build a small MCP **client** in Python. It connects to an
MCP server over stdio, runs the initialize handshake, lists the server's tools,
and calls a tool.

The example client uses only the Python standard library — nothing to install
beyond Python 3, no API keys, no network. It shows exactly what an MCP client
does using plain JSON-RPC messages.

## The client

The full client is in `examples/python/mcp_client.py`. Here are the key parts.

### Start the server

```python
client = MCPClient(["python3", "servers/filesystem_server.py", "./example-data"])
client.start()
```

`MCPClient` launches the server as a subprocess and starts a background thread
that reads the server's stdout line by line.

### Initialize (the handshake)

```python
info = client.initialize()
```

This sends an `initialize` JSON-RPC request and waits for the server's reply.
The reply tells the client the server's name, version, and capabilities.

### List the tools

```python
tools = client.list_tools()
for t in tools:
    print(t.name, "-", t.description)
```

This asks the server what tools it offers. These are the actions an AI is
allowed to perform through this client.

### Call a tool

```python
result = client.call_tool("read_file", {"path": "welcome.txt"})
```

This sends a `tools/call` request. The server runs the tool and returns the
result (for `read_file`, the file contents).

### Close

```python
client.close()
```

This closes the client and stops the server process.

## Run it yourself

From the `examples/python/` folder:

```bash
python3 mcp_client.py python3 servers/filesystem_server.py ./example-data
```

Expected output:

```text
Connected to server: example-python-filesystem
Available tools (2):
  - list_directory: List the files and folders in a shared folder (read-only)
  - read_file: Read the contents of a shared file (read-only)
```

## Run the tests

The test suite in `examples/python/test_client.py` drives the client and both
servers over stdio and checks the results:

```bash
python3 test_client.py
```

Expected output:

```text
[test] 11 passed, 0 failed
[test] ALL TESTS PASSED
```

It verifies initialize, list tools, read file, path-traversal rejection, and
unknown-tool rejection for the filesystem server, plus list/read/add for the
notes app server, and the end-to-end local LLM bridge.

## How the protocol works (under the hood)

Client and server exchange JSON-RPC messages, one per line, over stdio:

```json
// Client → Server
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"example-python-client","version":"1.0.0"}}}

// Server → Client
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"serverInfo":{"name":"example-python-filesystem","version":"0.1.0"}}}
```

The client handles opening the subprocess, sending messages, reading responses,
and matching each response to its request id — so you don't have to.

## For production

These examples use the standard library so they run anywhere and show the
protocol clearly. For production apps, consider the official
[modelcontextprotocol/mcp-python](https://github.com/modelcontextprotocol/mcp-python)
SDK (`pip install mcp`). It is already available in this environment.

Continue to `04-connecting-local-llm.md` to connect a local LLM to files,
folders, and apps through the MCP client.

---

**Credit:** Written and published by **Asdale Dynamics, LLC** (Indiana, formed October 2026). Dylan Asdale — registered nurse, AI author, founder of Asdale Dynamics, LLC. Book: *The Massive AI Manual* — hub site: dylanasdale.github.io

**License:** MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.
