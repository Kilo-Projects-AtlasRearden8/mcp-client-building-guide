# STATUS.md

## What was built

A beginner manual and static HTML site on building MCP (Model Context Protocol) **clients** that connect local LLMs to files, folders, and apps, plus runnable Python examples. Published by **Asdale Dynamics, LLC** (Indiana, formed October 2026).

### Contents

| Location | Contents |
|----------|----------|
| `README.md` | Project overview, quick start, example instructions, credit, license |
| `LICENSE` | MIT License, copyright line exactly `Copyright (c) 2026 Asdale Dynamics, LLC` |
| `docs/index.md` | Manual landing page: who it's for, how to use it, credit |
| `docs/01-what-is-an-mcp-client.md` | What MCP clients do (client vs. server, stdio, why it matters) |
| `docs/02-connecting-local-files-folders.md` | Connecting a client to local files and folders (7 steps, troubleshooting) |
| `docs/03-building-first-python-mcp-client.md` | Building your first Python MCP client |
| `docs/04-connecting-local-llm.md` | Connecting a local LLM to files, folders, and apps |
| `docs/05-privacy-safety.md` | Privacy and safety rules (golden rules, safety checklist) |
| `docs/cheat-sheet.md` | Printable one-page cheat sheet |
| `docs/glossary.md` | Plain-English glossary |
| `docs/checklists/checklist-01-connect-local-folder.md` | Checklist: connect a local folder |
| `docs/checklists/checklist-02-build-python-client.md` | Checklist: build your first Python MCP client |
| `docs/checklists/checklist-03-safety-review.md` | Checklist: safety review before connecting files |
| `site/index.html` | Static HTML landing page |
| `site/01-what-is-an-mcp-client.html` | HTML: section 1 |
| `site/02-connecting-local-files-folders.html` | HTML: section 2 |
| `site/03-building-first-python-mcp-client.html` | HTML: section 3 |
| `site/04-connecting-local-llm.html` | HTML: section 4 |
| `site/05-privacy-safety.html` | HTML: section 5 |
| `site/cheat-sheet.html` | HTML: printable cheat sheet |
| `site/glossary.html` | HTML: glossary |
| `site/style.css` | Single stylesheet for the static site |
| `examples/python/README.md` | Examples overview |
| `examples/python/mcp_client.py` | Dependency-free stdio MCP client (Python standard library) |
| `examples/python/servers/filesystem_server.py` | Read-only filesystem MCP server (list_directory, read_file, path-traversal guarded) |
| `examples/python/servers/notes_app_server.py` | Local notes app MCP server (list_notes, read_note, add_note) |
| `examples/python/local_llm_bridge.py` | Local LLM bridge connecting files/folders/apps via the MCP client |
| `examples/python/test_client.py` | Test suite driving the client and servers over stdio |
| `examples/python/example-data/` | Demo files for the filesystem server |
| `examples/python/notes-data/` | Demo notes for the notes app server |
| `STATUS.md` | This file |

### Style & compliance

- Plain English, step by step, never condescending ("like a friend would")
- Local-first: all examples run on the user's computer
- Python examples use only the standard library &mdash; nothing to install beyond Python 3
- No secrets, API keys, or personal data in any file
- No `.github/workflows` files
- MIT LICENSE with exact copyright line `Copyright (c) 2026 Asdale Dynamics, LLC`
- Asdale Dynamics, LLC credited in README and every doc/HTML page
- Credit: Dylan Asdale, registered nurse, AI author, founder of Asdale Dynamics, LLC; book *The Massive AI Manual*; hub site dylanasdale.github.io

## How to run it

### Read the manual

Open the Markdown files in `docs/` directly, or open the static HTML site in any browser &mdash; no build step required:

```
site/index.html
```

### Run the examples

Requires Python 3 (tested with Python 3.13.5). Nothing to install &mdash; no `pip install`, no API keys, no network.

From the project folder:

```bash
cd examples/python
python3 test_client.py
```

Expected output:

```
[test] PASS filesystem initialize
[test] PASS filesystem list_tools
[test] PASS filesystem list_directory
[test] PASS filesystem read_file
[test] PASS filesystem path traversal rejected
[test] PASS filesystem unknown tool rejected
[test] PASS notes list_notes
[test] PASS notes read and add
[test] PASS MCPClient library
[test] PASS local_llm_bridge filesystem
[test] PASS local_llm_bridge notes
[test] 11 passed, 0 failed
[test] ALL TESTS PASSED
```

### Try the local LLM bridge

```bash
cd examples/python
python3 local_llm_bridge.py filesystem ./example-data "List the files"
python3 local_llm_bridge.py notes ./notes-data "Read welcome.md"
```

The servers only access their configured demo folders; the filesystem server is read-only and rejects path-traversal.

## Verification results

- `python3 test_client.py` → **11 passed, 0 failed, ALL TESTS PASSED**
- `python3 -m py_compile` on all example files → OK
- `ruff check` on all example files → **All checks passed!**
- `ruff format --check` on all example files → **5 files already formatted**
- `python3 mcp_client.py python3 servers/filesystem_server.py ./example-data` → connects, lists 2 tools, exits cleanly
- Server handles `initialize`, `tools/list`, `tools/call` (list_directory + read_file)
- Path traversal (`../../etc/passwd`) correctly rejected with an error
- Unknown tool (`delete_file`) correctly rejected with an error
- Notes app server: list_notes, read_note, add_note all work
- HTML files are static and open directly in a browser (no build step)
- Every HTML page and doc contains credit to Asdale Dynamics, LLC and the copyright line
- LICENSE copyright line is exactly `Copyright (c) 2026 Asdale Dynamics, LLC`

## Known gaps

- No automated test runner / lint / typecheck tooling configured beyond `ruff` and `py_compile` (project is intentionally minimal: Markdown, HTML/CSS, Python stdlib scripts)
- The local LLM bridge uses a keyword-based stand-in LLM rather than a real model; connecting a real local LLM (Ollama, llama.cpp, etc.) is left as a next step for the reader
- The example was verified on Linux; Windows path handling uses Python `path`/`os.path`, which is cross-platform, but was only verified on Linux
- The static HTML site covers all 5 sections, the cheat sheet, and the glossary; checklists remain as Markdown (intentionally printable/copyable)
- Not yet committed to git (git init + commit is the next step)

## Next step

Initialize git and commit all work (plain commit messages, no Co-authored-by trailers, no push, no remote).
