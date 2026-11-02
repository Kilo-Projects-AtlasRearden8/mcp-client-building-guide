# 01. What is an MCP client?

## The idea

You have an AI assistant on your computer. You want it to read your files,
look at your notes, or use a local app — without you copying and pasting
everything into the chat.

MCP stands for **Model Context Protocol**. Think of it like a universal plug:
instead of every AI app inventing its own way to reach your files, your
calendar, or a database, MCP gives them one shared language.

## Client versus server

- The **client** lives inside the AI app you use. It asks, "what can this
  server do?" and carries the AI's requests back and forth.
- The **server** is a small program that provides access to something useful —
  your local files, a folder of documents, a notes app.

Client and server talk over a simple connection. The most common one for
beginners is called **stdio**: the server runs as a regular process on your
computer, and the client sends it messages over standard input/output.

```
You ──► AI app (MCP client) ──► MCP server ──► your files/folders/apps
```

## What the client does

The client:

1. Starts the server program.
2. Runs an "initialize" handshake so client and server agree on the protocol.
3. Asks the server for its list of **tools** (the things the AI is allowed to do).
4. Carries the AI's tool requests to the server and hands the results back.

The client never changes your files on its own. It only does what you — and the
server — allow.

## Why it matters

Without MCP, every AI integration is custom: one for your files, one for your
notes, one for your calendar. With MCP, one client can talk to many servers
using the same language. You pick which folders and apps to share, and you can
remove a server at any time.

## A tiny example

This manual's examples use only the Python standard library — nothing to
install beyond Python 3. The client in `examples/python/mcp_client.py` connects
to a server over stdio, lists its tools, and calls one:

```text
Connected to server: example-python-filesystem
Available tools (2):
  - list_directory: List the files and folders in a shared folder (read-only)
  - read_file: Read the contents of a shared file (read-only)
```

Continue to `02-connecting-local-files-folders.md` to connect a client to your
own files and folders.

---

**Credit:** Written and published by **Asdale Dynamics, LLC** (Indiana, formed October 2026). Dylan Asdale — registered nurse, AI author, founder of Asdale Dynamics, LLC. Book: *The Massive AI Manual* — hub site: dylanasdale.github.io

**License:** MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.
