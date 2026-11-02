# 04. Connecting a local LLM to files, folders, and apps

## The idea

An MCP client is the bridge between a local LLM and the things on your
computer: files, folders, and apps. The client talks to MCP servers; each
server exposes tools. The LLM (through the client) can call those tools to read
a file, list a folder, or update a note — all on your machine.

This section shows the full flow:

1. Start an MCP server (filesystem or notes app).
2. Connect the MCP client to it.
3. List the server's tools (what the LLM is allowed to do).
4. The LLM chooses a tool and calls it through the client.
5. The result comes back and the LLM answers you.

## No real LLM required

Running a real local LLM (Ollama, llama.cpp, etc.) is optional and not needed
to learn MCP. The example `local_llm_bridge.py` includes a small stand-in LLM
that picks a tool based on keywords in your question. So the example is fully
testable, offline, and private — no model download, no API key.

## Try the filesystem server

From the `examples/python/` folder:

```bash
python3 local_llm_bridge.py filesystem ./example-data "List the files"
```

What happens:

1. The bridge starts `servers/filesystem_server.py` with root `./example-data`.
2. The MCP client connects and runs the initialize handshake.
3. The client lists the server's tools: `list_directory`, `read_file`.
4. The stand-in LLM chooses `list_directory` and calls it.
5. The server lists `welcome.txt` and `notes.md`; the bridge prints them.

You should see `welcome.txt` and `notes.md` in the output.

Try reading a file:

```bash
python3 local_llm_bridge.py filesystem ./example-data "Read welcome.txt"
```

## Try the notes app (an "app" server)

The notes app server represents a local app the LLM can reach. It offers
`list_notes`, `read_note`, and `add_note`:

```bash
python3 local_llm_bridge.py notes ./notes-data "Read welcome.md"
python3 local_llm_bridge.py notes ./notes-data "List the notes"
```

You can even add a note (the app server is read-write, unlike the filesystem
server):

```bash
python3 local_llm_bridge.py notes ./notes-data "Add a note"
```

## What the connection looks like

```
You ask the local LLM a question
    │
    ▼
Local LLM (through the MCP client)
    │ picks a tool, sends tools/call
    ▼
MCP client  ──►  MCP server (filesystem / notes app)
    │ reads/writes on your disk
    ▼
Your files / folders / local app
    │ sends result back
    ▼
MCP server  ──►  MCP client  ──►  LLM answer to you
```

## Privacy

- All servers are local stdio processes; nothing is uploaded.
- The filesystem server is read-only and blocks path-traversal (`..`).
- The notes app server writes notes only inside its own folder.
- Only share folders you are comfortable an AI reading.
- See the safety rules in `05-privacy-safety.md`.

Continue to `05-privacy-safety.md` for the privacy and safety rules.

---

**Credit:** Written and published by **Asdale Dynamics, LLC** (Indiana, formed October 2026). Dylan Asdale — registered nurse, AI author, founder of Asdale Dynamics, LLC. Book: *The Massive AI Manual* — hub site: dylanasdale.github.io

**License:** MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.
