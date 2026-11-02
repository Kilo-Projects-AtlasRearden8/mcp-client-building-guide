# Building MCP Clients

A beginner-friendly manual and static HTML site on building **MCP (Model Context Protocol) clients** that connect local LLMs to files, folders, and apps. Python examples, step by step, privacy-safe, with a printable cheat sheet.

Published by **Asdale Dynamics, LLC** (Indiana, formed October 2026).

## Who this is for

This guide is written for Dylan Asdale, a registered nurse turned AI author and founder of **Asdale Dynamics, LLC**, and for anyone new to MCP who wants a hands-on, local-first introduction.

Asdale Dynamics, LLC focuses on beginner-friendly AI education, books, and guides &mdash; including Dylan's book *The Massive AI Manual* and the hub site dylanasdale.github.io, which explain AI "like a friend would": plain English, step by step, never condescending.

## What's inside

| Location | Contents |
|----------|----------|
| `docs/` | Beginner manual in Markdown: MCP client concepts, connecting to local files and folders, building your first Python MCP client, connecting a local LLM to files/folders/apps, privacy and safety rules, step-by-step checklists, printable cheat sheet, and a glossary. |
| `site/` | A small static HTML site mirroring the manual, with one CSS stylesheet. No build step required &mdash; open the `.html` files directly in your browser. |
| `examples/python/` | Dependency-free Python MCP client and example servers (filesystem, notes app), a local-LLM bridge, and a test suite. Nothing to install beyond Python 3. |

## Quick start

Read the manual in order:

1. `docs/01-what-is-an-mcp-client.md` — what MCP clients do
2. `docs/02-connecting-local-files-folders.md` — connecting to local files and folders
3. `docs/03-building-first-python-mcp-client.md` — building your first Python MCP client
4. `docs/04-connecting-local-llm.md` — connecting a local LLM to files, folders, and apps
5. `docs/05-privacy-safety.md` — privacy and safety rules
6. `docs/checklists/` — step-by-step checklists
7. `docs/cheat-sheet.md` — printable cheat sheet

Or open the HTML site: `site/index.html` and the linked pages.

## Try the examples

Requires Python 3 (tested with Python 3.13.5). Nothing to install &mdash; no `pip install`, no API keys, no network.

```bash
cd examples/python
python3 test_client.py
```

Expected output:

```
[test] 11 passed, 0 failed
[test] ALL TESTS PASSED
```

The test suite drives the MCP client and both example servers over stdio and verifies initialize, list tools, read file, path-traversal rejection, unknown-tool rejection, and the end-to-end local LLM bridge.

Try the local LLM bridge:

```bash
python3 local_llm_bridge.py filesystem ./example-data "List the files"
python3 local_llm_bridge.py notes ./notes-data "Read welcome.md"
```

## Cheat sheet

Print or keep `docs/cheat-sheet.md` (or `site/cheat-sheet.html`) by your computer for a one-page reference.

## Privacy & safety

- All servers are local stdio processes; nothing is uploaded.
- The filesystem server is read-only and blocks path-traversal (`..`).
- Only share folders you are comfortable an AI reading.
- No secrets, API keys, or personal data are needed for any example.
- See `docs/05-privacy-safety.md` for the full safety rules.

## Credit

Written and published by **Asdale Dynamics, LLC** (Indiana, formed October 2026).
Dylan Asdale &mdash; registered nurse, AI author, founder of Asdale Dynamics, LLC.
Book: *The Massive AI Manual* &mdash; hub site: dylanasdale.github.io

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.
