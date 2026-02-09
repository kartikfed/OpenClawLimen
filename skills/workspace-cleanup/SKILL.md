# Workspace Cleanup Skill

Ultra-conservative workspace garbage collector. Only removes reinstallable dependencies and obvious temp files.

## Interactive Flow (with Telegram buttons)

When the user asks to clean up the workspace:

### Step 1: Scan and show results
```bash
python3 ~/.openclaw/workspace/skills/workspace-cleanup/cleanup.py --json
```

### Step 2: Parse JSON and present with buttons

If `clean: true` in output, just say "Workspace is already clean!"

Otherwise, format the results and send with confirmation buttons:

```
🧹 **Workspace Cleanup**

Found items to clean:
• `projects/foo/node_modules` (2.5MB) - Reinstallable dependency
• `projects/bar/venv` (15MB) - Reinstallable dependency

**Total: 17.5MB**

Confirm deletion?
```

Use inline buttons:
```json
{
  "buttons": [[
    {"text": "✅ Yes, delete", "callback_data": "cleanup_confirm_<token>"},
    {"text": "❌ Cancel", "callback_data": "cleanup_cancel"}
  ]]
}
```

The `<token>` is the `confirmation_token` from the JSON output.

### Step 3: Handle button callback

**If user clicks "Yes, delete"** (message matches `cleanup_confirm_<token>`):
```bash
python3 ~/.openclaw/workspace/skills/workspace-cleanup/cleanup.py --execute --confirm <token>
```

**If user clicks "Cancel"** (message matches `cleanup_cancel`):
Just acknowledge: "Cleanup cancelled."

### Step 4: Report results

Show what was deleted and total space freed.

---

## CLI Usage (non-interactive)

```bash
# Dry run with human-readable output
python3 ~/.openclaw/workspace/skills/workspace-cleanup/cleanup.py

# Dry run with JSON output  
python3 ~/.openclaw/workspace/skills/workspace-cleanup/cleanup.py --json

# Include stale cron jobs in scan
python3 ~/.openclaw/workspace/skills/workspace-cleanup/cleanup.py --crons

# Execute deletion (requires confirmation token from dry run)
python3 ~/.openclaw/workspace/skills/workspace-cleanup/cleanup.py --execute --confirm <token>
```

---

## What It Cleans

### Reinstallable Dependencies
- `**/node_modules/`
- `**/venv/`
- `**/.venv/`
- `**/__pycache__/`
- `**/.pytest_cache/`
- `**/.mypy_cache/`
- `**/.ruff_cache/`

### Cache Directories
- `.cache/knowledge-graph/`

### Cron Jobs (with --crons flag)
- Disabled jobs older than 24 hours
- Completed one-shot jobs

---

## What It NEVER Touches

- Any markdown file (`*.md`)
- Any source code (`*.py`, `*.ts`, `*.js`, `*.sh`, `*.jsx`, `*.tsx`)
- Any config (`*.json`, `*.yaml`, `*.yml`, `*.toml`)
- Protected directories:
  - `memory/` - your memories
  - `skills/` - skill definitions
  - `secrets/` - credentials
  - `scripts/` - automation
  - `library/` - saved content
  - `kitchen/` - pantry system
  - `docs/` - documentation
  - `chronicle/` - substack drafts
  - `writing/` - essays
  - `substack/` - substack content
  - `prompts/` - prompt templates

---

## Philosophy

**Allowlist only.** If something isn't explicitly on the "safe to delete" list, it's untouched. 

**Confirmation required.** The token ensures you're deleting exactly what you reviewed.
