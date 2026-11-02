# Checklist 2 — Build and Run Your First Python MCP Client

Goal: Build a Python MCP client that connects to a server, lists tools, and calls a tool.

### Before you start
- [ ] Python 3 is installed (`python3 --version`)
- [ ] You are in the `examples/python/` folder

### Steps
- [ ] Run the filesystem server: `python3 servers/filesystem_server.py ./example-data`
- [ ] In another terminal, run the client: `python3 mcp_client.py python3 servers/filesystem_server.py ./example-data`
- [ ] Confirm output shows "Connected to server" and two tools
- [ ] Run the tests: `python3 test_client.py`
- [ ] Confirm all 11 tests pass
- [ ] Try the local LLM bridge: `python3 local_llm_bridge.py filesystem ./example-data "List the files"`

### When you are done
- [ ] Stop the server process (`Ctrl+C`)

**If any step fails:** see `docs/03-building-first-python-mcp-client.md` and `docs/05-privacy-safety.md`.

---

**Credit:** Asdale Dynamics, LLC (Indiana, formed October 2026). MIT License — Copyright (c) 2026 Asdale Dynamics, LLC.
