# 05. Privacy and safety rules

## Privacy first

All examples in this manual are **local-first**:

- MCP servers run as processes on your computer.
- Files are read from and written to your disk.
- Nothing is uploaded to a third party just to use an MCP server.
- No API keys, secrets, or personal data are needed for any example.

That said, if you connect an MCP client to a real AI app, the AI provider may
still process the contents you send it. Treat anything you show the AI as if
the provider could see it.

## Golden rules

1. **Share specific folders, never your whole computer.** Pick one dedicated
   folder (for example, `~/ai-readable/`) rather than your home directory.
2. **Never share folders with secrets.** No passwords, keys, IDs, tax returns,
   medical records, or bank statements.
3. **Prefer read-only servers.** The filesystem server in this manual is
   read-only by design.
4. **You are in charge.** You can stop or remove a server at any time, and the
   AI loses access immediately.
5. **Assume the AI provider sees what you send it.** Even local-first tools can
   send contents to a cloud AI model.

## Path-traversal protection

The example filesystem server confines all access to a single root folder and
rejects attempts to escape it (`../etc/passwd`, etc.). The test suite verifies
this:

```
[test] PASS path traversal rejected
```

## Checklist before connecting real files

See `docs/checklists/checklist-03-safety-review.md` for a printable safety
review checklist.

## Healthcare note

This guide is for education only. It is never medical advice. If you are a
healthcare worker, do not put real patient data into an AI or an MCP server
unless you have confirmed it is permitted by your organization and by
applicable privacy law (such as HIPAA).

---

**Credit:** Written and published by **Asdale Dynamics, LLC** (Indiana, formed October 2026). Dylan Asdale — registered nurse, AI author, founder of Asdale Dynamics, LLC. Book: *The Massive AI Manual* — hub site: dylanasdale.github.io

**License:** MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.
