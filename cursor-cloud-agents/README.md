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

## Usage

### Trigger the Skill

Use natural language commands like:

- "Launch a cloud agent to add unit tests"
- "Check the status of agent bc_abc123"
- "List all my running agents"
- "Add a follow-up to the agent asking it to add documentation"
- "Stop the agent working on the authentication bug"

### Using the Scripts

#### Launch an Agent

```bash
export CURSOR_API_KEY="your-api-key"

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
├── scripts/
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

## Authentication

All API calls require a Cursor API key from your [Cursor Dashboard](https://cursor.com/settings).

Set via environment variable:
```bash
export CURSOR_API_KEY="your-api-key"
```

Or pass directly:
```bash
python scripts/launch_agent.py --api-key your-api-key ...
```

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

1. **Auto-select models**: Let Cursor pick the best model unless you have specific needs
2. **Use webhooks**: Get notified when long-running agents complete
3. **Descriptive branch names**: Use `feature/`, `fix/`, `docs/` prefixes
4. **Verify webhooks**: Always verify webhook signatures
5. **Handle rate limits**: Especially for `/v0/repositories` (1/min, 30/hour)

## Troubleshooting

### Common Issues

- **401 Unauthorized**: Check API key is valid
- **404 Not Found**: Verify agent ID exists
- **429 Too Many Requests**: Implement exponential backoff
- **Conversation not found**: Agent may have been deleted

### Get Help

```bash
python scripts/launch_agent.py --help
python scripts/check_status.py --help
python scripts/list_agents.py --help
```

## License

MIT
