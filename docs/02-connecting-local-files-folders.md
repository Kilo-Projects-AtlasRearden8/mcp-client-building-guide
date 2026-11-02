# 02. Connecting an MCP client to local files and folders

## The idea

You have folders of documents, notes, or books on your computer. You want an AI
assistant to read them and answer questions — without you copying and pasting
everything into the chat. An MCP **filesystem server** gives the AI controlled
access to chosen folders on your machine.

This section shows you how to connect a client to local files and folders, step
by step. We use a read-only filesystem MCP server as the example, because it is
the most common first server people run.

## Step 1: Pick the folders you want to share

Before installing anything, decide exactly which folders the AI may see. Good
choices:

- A dedicated folder you create for this purpose, such as `~/ai-readable/`
- A specific project folder
- Your notes or drafts folder

Avoid sharing:

- Your whole home directory (`~` or `C:\Users\you`)
- Folders with passwords, tax documents, medical records, IDs, or bank statements
- System folders or folders belonging to other people on the computer

**Rule of thumb:** share only what you would be comfortable showing the AI. You
can always add more folders later; removing access is harder once files have
been read.

## Step 2: Start the filesystem server

Our example server lives in
`examples/python/servers/filesystem_server.py`. It is read-only and confines
all access to a single root folder, rejecting path-traversal attempts (`..`).

From the project folder, run:

```bash
python3 examples/python/servers/filesystem_server.py examples/python/example-data
```

The server starts and waits for a client to connect. It only sees
`examples/python/example-data/`, nothing else on your computer.

## Step 3: Connect the MCP client

In another terminal, run the example client:

```bash
python3 examples/python/mcp_client.py python3 examples/python/servers/filesystem_server.py examples/python/example-data
```

You should see:

```text
Connected to server: example-python-filesystem
Available tools (2):
  - list_directory: List the files and folders in a shared folder (read-only)
  - read_file: Read the contents of a shared file (read-only)
```

The client started the server, ran the initialize handshake, and asked for the
list of tools. These are the tools an AI is allowed to use.

## Step 4: List the folder

Ask the client to list the shared folder:

```bash
# (Driven through the client in the examples.)
python3 examples/python/local_llm_bridge.py filesystem examples/python/example-data "List the files"
```

Expected output lists `welcome.txt` and `notes.md`. The AI (simulated by the
bridge) used the `list_directory` tool through the client, and the server read
the folder from your disk.

## Step 5: Read a file

Ask the client to read a specific file:

```bash
python3 examples/python/local_llm_bridge.py filesystem examples/python/example-data "Read welcome.txt"
```

The client calls `read_file`, the server reads the file from disk, and the
contents come back. The file stays on your computer.

## Step 6: Confirm safety guards

The server rejects path-traversal and unknown tools:

```bash
python3 examples/python/test_client.py
```

This runs the full test suite, including "path traversal rejected" and "unknown
tool rejected." All tests should pass.

## Step 7: Disconnect when you are done

When you no longer need the AI to see those files, stop the server process
(`Ctrl+C` in its terminal). The AI loses access immediately.

## What the connection looks like

```
You ask AI to read a file
    │
    ▼
AI app (MCP client)
    │ sends request over stdio
    ▼
Filesystem MCP server (runs on your computer)
    │ reads the file from your disk
    ▼
Your local folder
    │ sends file contents back
    ▼
Filesystem MCP server  ──►  MCP client  ──►  AI answer to you
```

The files stay on your computer. Nothing is uploaded to a third party just for
this step (though the AI provider may still process the contents — see section
05).

## Troubleshooting

| Problem | Likely fix |
|---------|------------|
| Server won't start | Check the folder path is correct and the folder exists |
| Client can't connect | Confirm the server command and path are correct |
| AI says it has no file tools | The server may not be running; check the terminal running the server |
| "Permission denied" | The user account running the client needs read access to the folder |

Continue to `03-building-first-python-mcp-client.md` to build your own Python
MCP client from scratch.

---

**Credit:** Written and published by **Asdale Dynamics, LLC** (Indiana, formed October 2026). Dylan Asdale — registered nurse, AI author, founder of Asdale Dynamics, LLC. Book: *The Massive AI Manual* — hub site: dylanasdale.github.io

**License:** MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.
