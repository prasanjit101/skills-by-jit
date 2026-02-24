# Cursor Cloud Agents Orchestrator Skill

A comprehensive skill for orchestrating Cursor Cloud Agents via the Cloud Agents API.

## What This Skill Provides

This skill enables you to:

1. **Launch agents** to work on your GitHub repositories
2. **Monitor status** and retrieve conversation history
3. **Add follow-ups** to guide agent work
4. **Stop or delete** agents as needed
5. **List and filter** all your cloud agents
6. **Configure webhooks** for status notifications

## Installation

Copy the `cursor-cloud-agents` directory to your skills folder:

```bash
# For Qwen Code skills
cp -r cursor-cloud-agents ~/.qwen/skills/
```

## Authentication & Credentials Setup

All API calls require a Cursor API key from your [Cursor Dashboard](https://cursor.com/settings).

### Recommended: Save Your Key in a `.env` File

The skill includes a built-in credential loader (`scripts/config.py`) that automatically reads a `.env` file from the skill root directory. This means you only set your key once and every script picks it up without any extra flags.

**Step 1 — Create your `.env` file from the template:**

```bash
cp cursor-cloud-agents/.env.example cursor-cloud-agents/.env
```

**Step 2 — Add your real API key:**

```
# cursor-cloud-agents/.env
CURSOR_API_KEY=your_actual_api_key_here
```

The `.env` file is listed in `.gitignore` and will **never be committed** to version control. The `.env.example` template file is committed instead, so collaborators know what to fill in.

### Alternative: Shell Environment Variable

```bash
export CURSOR_API_KEY="your-api-key"
```

### Alternative: Pass Directly per Command

```bash
python scripts/launch_agent.py --api-key your-api-key ...
```

### Priority Order

When a script runs, the API key is resolved in this order (highest wins):

| Priority | Source |
|----------|--------|
| 1 (highest) | `--api-key` CLI flag |
| 2 | `CURSOR_API_KEY` exported in shell |
| 3 | `CURSOR_API_KEY` in `.env` file |

## Usage

### Trigger the Skill

Use natural language commands like:

- "Launch a cloud agent to add unit tests"
- "Check the status of agent bc_abc123"
- "List all my running agents"
- "Add a follow-up to the agent asking it to add documentation"
- "Stop the agent working on the authentication bug"

### Using the Scripts

All examples below assume your API key is already saved in `.env` (recommended). Add `--api-key YOUR_KEY` to any command if you prefer to pass it directly.

#### Launch an Agent

```bash
python scripts/launch_agent.py \
  --repo https://github.com/your-org/your-repo \
  --prompt "Add a README.md file with installation instructions" \
  --ref main \
  --auto-create-pr \
  --branch-name feature/add-readme
```

#### Check Status

```bash
python scripts/check_status.py --agent-id bc_abc123
```

#### Get Conversation

```bash
python scripts/check_status.py --agent-id bc_abc123 --conversation
```

#### List Agents

```bash
python scripts/list_agents.py --status RUNNING
```

#### Add Follow-up

```bash
python scripts/followup.py \
  --agent-id bc_abc123 \
  --prompt "Also add a troubleshooting section"
```

#### Stop or Delete Agent

```bash
# Stop
python scripts/manage_agent.py --agent-id bc_abc123 --action stop

# Delete (with confirmation)
python scripts/manage_agent.py --agent-id bc_abc123 --action delete
```

## Files Structure

```
cursor-cloud-agents/
├── SKILL.md                      # Main skill documentation
├── README.md                     # This file
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

### How `config.py` Works

`scripts/config.py` is a zero-dependency `.env` loader that is **automatically imported** by every script in the `scripts/` directory. You do not need to call it manually.

- Locates `.env` in the skill root (one directory above `scripts/`)
- Parses `KEY=VALUE` pairs, handling quotes and inline comments
- Merges values into `os.environ` before argument parsing begins
- **Does not override** values already set in your shell

## API Reference

See [references/api-reference.md](references/api-reference.md) for complete API documentation including:

- All endpoints and parameters
- Request/response schemas
- Example curl commands
- Error handling

## Webhooks

See [references/webhooks.md](references/webhooks.md) for webhook configuration including:

- Setting up webhook endpoints
- Payload verification
- Example implementations (Node.js, Python)

## Best Practices

1. **Store credentials in `.env`**: Never hardcode or commit your API key
2. **Auto-select models**: Let Cursor pick the best model unless you have specific needs
3. **Use webhooks**: Get notified when long-running agents complete
4. **Descriptive branch names**: Use `feature/`, `fix/`, `docs/` prefixes
5. **Verify webhooks**: Always verify webhook signatures
6. **Handle rate limits**: Especially for `/v0/repositories` (1/min, 30/hour)

## Troubleshooting

### Common Issues

- **401 Unauthorized**: Check your `.env` has the correct key, or verify with `GET /v0/me`
- **404 Not Found**: Verify agent ID exists
- **429 Too Many Requests**: Implement exponential backoff
- **Conversation not found**: Agent may have been deleted
- **Key not picked up**: Make sure `.env` is in the `cursor-cloud-agents/` root (not inside `scripts/`)

### Get Help

```bash
python scripts/launch_agent.py --help
python scripts/check_status.py --help
python scripts/list_agents.py --help
python scripts/followup.py --help
python scripts/manage_agent.py --help
```

## License

MIT