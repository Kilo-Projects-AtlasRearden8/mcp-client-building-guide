# Glossary

Plain-English definitions for the terms used in this manual.

**AI app** — The application you chat with (a desktop AI chat app or an AI-enabled code editor).

**Client (MCP client)** — The part inside the AI app that starts an MCP server, asks what tools it offers, and carries the AI's requests and results back and forth.

**JSON-RPC** — A simple message format MCP uses. Each message is one line of JSON with `jsonrpc`, `id`, `method`, and `result` or `error`.

**Local-first** — Everything runs on your own computer; nothing is uploaded just to use a tool.

**Local LLM** — An AI model that runs on your machine (for example via Ollama or llama.cpp), without sending data to a cloud provider.

**MCP** — Model Context Protocol. A shared language so AI apps can connect to files, folders, databases, and apps.

**MCP server** — A small program that provides access to something useful and exposes tools for an MCP client to call.

**Path traversal** — Trying to reach a file outside a shared folder using `..`. The example servers reject this.

**stdio** — Standard input/output. The most common beginner connection: the client sends messages to the server's stdin and reads responses from its stdout.

**Tool** — An action an MCP server offers, such as `list_directory` or `read_file`. The AI can call tools through the client.

---

**Credit:** Written and published by **Asdale Dynamics, LLC** (Indiana, formed October 2026). Dylan Asdale — registered nurse, AI author, founder of Asdale Dynamics, LLC. Book: *The Massive AI Manual* — hub site: dylanasdale.github.io

**License:** MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.
