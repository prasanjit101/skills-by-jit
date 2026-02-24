---
name: Cursor Cloud Agents Orchestrator
description: Launch, manage, and monitor Cursor cloud agents via the Cloud Agents API. Use when users need to: (1) Launch agents to work on repositories, (2) Check agent status or conversation history, (3) Add follow-ups to running agents, (4) Stop or delete agents, (5) List agents or repositories, (6) Access API key info or available models.
---

# Cursor Cloud Agents Orchestrator

This skill provides tools to programmatically launch and manage cloud agents that work on your repositories via the Cursor Cloud Agents API.

## Quick Start

**Authentication:** All endpoints use Basic Auth with your Cursor API key from the [Cursor Dashboard](https://cursor.com/settings).

### 1. Save Your API Key (Recommended)

```bash
# Copy the template and fill in your real key
cp .env.example .env
# Edit .env and set: CURSOR_API_KEY=your_actual_api_key_here
```

The `.env` file is gitignored and will never be committed. Every script automatically loads it via `scripts/config.py` — no flags or exports required.

### 2. Run a Script

```bash
# Launch an agent (key is loaded from .env automatically)
python scripts/launch_agent.py \
  --repo https://github.com/org/repo \
  --prompt "Add a README.md file" \
  --auto-create-pr
```

### Or use curl directly

```bash
curl --request POST \
  --url https://api.cursor.com/v0/agents \
  -u YOUR_API_KEY: \
  --header 'Content-Type: application/json' \
  --data '{
  "prompt": {"text": "Add a README.md file"},
  "source": {"repository": "https://github.com/org/repo", "ref": "main"},
  "target": {"autoCreatePr": true}
}'

# Check status
curl --request GET \
  --url https://api.cursor.com/v0/agents/AGENT_ID \
  -u YOUR_API_KEY:
```

## Credentials & Security

| Method | How |
|--------|-----|
| `.env` file (recommended) | Add `CURSOR_API_KEY=...` to `cursor-cloud-agents/.env` |
| Shell export | `export CURSOR_API_KEY="your-key"` |
| Per-command flag | `--api-key YOUR_KEY` on any script |

**Priority:** `--api-key` flag > shell environment variable > `.env` file

`scripts/config.py` is a zero-dependency loader that auto-runs on `import config` (which every script does at startup). It reads `.env` from the skill root directory, parses it, and merges values into `os.environ` before argument parsing — so shell-level exports always take precedence over the file.

## Core Workflows

For complete API details, see **[references/api-reference.md](references/api-reference.md)**.

| Action | Endpoint | Script |
|--------|----------|--------|
| Launch agent | `POST /v0/agents` | `scripts/launch_agent.py` |
| Add follow-up | `POST /v0/agents/{id}/followup` | `scripts/followup.py` |
| Check status | `GET /v0/agents/{id}` | `scripts/check_status.py` |
| Get conversation | `GET /v0/agents/{id}/conversation` | `scripts/check_status.py --conversation` |
| Stop agent | `POST /v0/agents/{id}/stop` | `scripts/manage_agent.py --action stop` |
| Delete agent | `DELETE /v0/agents/{id}` | `scripts/manage_agent.py --action delete` |
| List agents | `GET /v0/agents` | `scripts/list_agents.py` |
| List repos | `GET /v0/repositories` | - |
| API key info | `GET /v0/me` | - |
| List models | `GET /v0/models` | - |

## Key Configuration Options

### Launch Agent

**Required:** `prompt.text`, `source.repository` (or `source.prUrl`)

**Optional:**
- `prompt.images` - Base64 images (max 5)
- `model` - LLM to use (default: auto-select)
- `source.ref` - Git ref (branch/tag/commit)
- `source.prUrl` - Work on existing PR
- `target.autoCreatePr` - Auto-create PR (default: false)
- `target.branchName` - Custom branch name
- `target.openAsCursorGithubApp` - Open PR as Cursor App
- `target.skipReviewerRequest` - Skip reviewer notification
- `webhook.url` - Status notification URL
- `webhook.secret` - Webhook secret (min 32 chars)

See **[references/api-reference.md](references/api-reference.md)** for full schemas.

### Webhooks

For webhook setup, payload verification, and examples, see **[references/webhooks.md](references/webhooks.md)**.

## Status Values

- `CREATING` → `RUNNING` → `FINISHED` (or `FAILED`)
- `RUNNING` → `STOPPED` (via API)
- `STOPPED` → `RUNNING` (via follow-up)

## Best Practices

1. **Store credentials in `.env`**: Never hardcode or commit your API key
2. **Model selection:** Use auto-select (omit `model` field)
3. **Branch naming:** Use prefixes: `feature/`, `fix/`, `docs/`
4. **Webhooks:** Configure for long-running agents; verify signatures
5. **Rate limits:** `/v0/repositories` has strict limits (1/min, 30/hour)
6. **Conversation access:** Retrieve before deleting (permanent loss)

See **[references/api-reference.md](references/api-reference.md)** for detailed best practices.

## Scripts Usage

All examples below assume your API key is saved in `.env`. 

```bash
# Launch
python scripts/launch_agent.py \
  --repo https://github.com/org/repo \
  --prompt "Add unit tests" \
  --auto-create-pr \
  --branch-name feature/tests

# Check status
python scripts/check_status.py --agent-id bc_abc123

# Get conversation
python scripts/check_status.py --agent-id bc_abc123 --conversation

# List running agents
python scripts/list_agents.py --status RUNNING

# Add follow-up
python scripts/followup.py --agent-id bc_abc123 --prompt "Add docs"

# Stop / Delete
python scripts/manage_agent.py --agent-id bc_abc123 --action stop
python scripts/manage_agent.py --agent-id bc_abc123 --action delete
```

## Files

```
cursor-cloud-agents/
├── SKILL.md                      # This file
├── README.md                     # Full usage guide
├── .env.example                  # Credentials template (committed to git)
├── .env                          # Your real credentials (gitignored, never committed)
├── .gitignore                    # Ignores .env and other sensitive files
├── scripts/
│   ├── config.py                 # Shared .env loader (auto-runs on import)
│   ├── launch_agent.py           # Launch new agents
│   ├── check_status.py           # Check status and conversation
│   ├── list_agents.py            # List and filter agents
│   ├── followup.py               # Add follow-up instructions
│   └── manage_agent.py           # Stop or delete agents
├── references/
│   ├── api-reference.md          # Complete API specification
│   └── webhooks.md               # Webhook configuration guide
└── assets/                       # (Optional assets)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Check `.env` has the correct key; verify with `GET /v0/me` |
| 404 Not Found | Agent doesn't exist or was deleted |
| 429 Rate Limited | Implement exponential backoff |
| Key not picked up | Ensure `.env` is in `cursor-cloud-agents/` root, not inside `scripts/` |
| Conversation missing | Agent was deleted (irreversible) |
| Follow-up fails | Agent must exist; stopped agents restart on follow-up |

See **[references/api-reference.md](references/api-reference.md)** for error handling details.
