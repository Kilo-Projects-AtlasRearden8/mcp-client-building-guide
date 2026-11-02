# Checklist 1 — Connect a Local Folder to an MCP Client

Goal: Connect an MCP client to one local folder so an AI can read files in it.

### Before you start
- [ ] I have Python 3 installed
- [ ] I have picked ONE specific folder to share
- [ ] The folder contains no secrets (passwords, keys, IDs, tax, medical, bank data)
- [ ] The folder contains no other people's personal data

### Steps
- [ ] Choose a folder to share (e.g. a dedicated `ai-readable/` folder)
- [ ] Start the filesystem server pointing at that folder
- [ ] Connect the MCP client to the server
- [ ] Confirm the server shows its tools (`list_directory`, `read_file`)
- [ ] Ask the AI: "List the files in my shared folder"
- [ ] Confirm the AI lists only files from my chosen folder
- [ ] Ask the AI to read one file and summarize it
- [ ] Confirm the answer matches the file contents

### When you are done
- [ ] Stop the server process (`Ctrl+C`)
- [ ] The AI no longer has access to the folder

**If any step fails:** check the folder path, confirm the folder exists, and see `docs/02-connecting-local-files-folders.md` and `docs/05-privacy-safety.md`.

---

**Credit:** Asdale Dynamics, LLC (Indiana, formed October 2026). MIT License — Copyright (c) 2026 Asdale Dynamics, LLC.
