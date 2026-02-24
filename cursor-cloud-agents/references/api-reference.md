# API Reference

Complete API specification for the Cursor Cloud Agents API.

Base URL: `https://api.cursor.com/v0`

Authentication: Basic Auth with API key (`-u YOUR_API_KEY:`)

---

## Table of Contents

1. [List Agents](#list-agents)
2. [Agent Status](#agent-status)
3. [Agent Conversation](#agent-conversation)
4. [Launch an Agent](#launch-an-agent)
5. [Add Follow-up](#add-follow-up)
6. [Stop an Agent](#stop-an-agent)
7. [Delete an Agent](#delete-an-agent)
8. [API Key Info](#api-key-info)
9. [List Models](#list-models)
10. [List GitHub Repositories](#list-github-repositories)

---

## List Agents

**Endpoint:** `GET /v0/agents`

List all cloud agents for the authenticated user.

### Request

```bash
curl --request GET \
  --url https://api.cursor.com/v0/agents \
  -u YOUR_API_KEY:
```

### Query Parameters

| Parameter | Type   | Required | Description                                      |
|-----------|--------|----------|--------------------------------------------------|
| limit     | number | No       | Number of agents to return. Default: 20, Max: 100 |
| cursor    | string | No       | Pagination cursor from previous response         |
| prUrl     | string | No       | Filter agents by pull request URL                |

### Response Schema

```typescript
{
  agents: Array<{
    id: string;
    name: string;
    status: string;
    source: {
      repository: string;
      ref?: string;
      prUrl?: string;
    };
    target: {
      branchName: string;
      url: string;
      prUrl?: string;
      autoCreatePr: boolean;
      openAsCursorGithubApp: boolean;
      skipReviewerRequest: boolean;
    };
    summary?: string;
    createdAt: string; // ISO 8601
  }>;
  nextCursor?: string;
}
```

### Example Response

```json
{
  "agents": [
    {
      "id": "bc_abc123",
      "name": "Add README Documentation",
      "status": "FINISHED",
      "source": {
        "repository": "https://github.com/your-org/your-repo",
        "ref": "main"
      },
      "target": {
        "branchName": "cursor/add-readme-1234",
        "url": "https://cursor.com/agents?id=bc_abc123",
        "prUrl": "https://github.com/your-org/your-repo/pull/1234",
        "autoCreatePr": false,
        "openAsCursorGithubApp": false,
        "skipReviewerRequest": false
      },
      "summary": "Added README.md with installation instructions and usage examples",
      "createdAt": "2024-01-15T10:30:00Z"
    },
    {
      "id": "bc_def456",
      "name": "Fix authentication bug",
      "status": "RUNNING",
      "source": {
        "repository": "https://github.com/your-org/your-repo",
        "ref": "main"
      },
      "target": {
        "branchName": "cursor/fix-auth-5678",
        "url": "https://cursor.com/agents?id=bc_def456",
        "autoCreatePr": true,
        "openAsCursorGithubApp": true,
        "skipReviewerRequest": false
      },
      "createdAt": "2024-01-15T11:45:00Z"
    }
  ],
  "nextCursor": "bc_ghi789"
}
```

---

## Agent Status

**Endpoint:** `GET /v0/agents/{id}`

Retrieve the current status and results of a cloud agent.

### Request

```bash
curl --request GET \
  --url https://api.cursor.com/v0/agents/bc_abc123 \
  -u YOUR_API_KEY:
```

### Path Parameters

| Parameter | Type   | Required | Description                                    |
|-----------|--------|----------|------------------------------------------------|
| id        | string | Yes      | Unique identifier (e.g., `bc_abc123`)          |

### Response Schema

```typescript
{
  id: string;
  name: string;
  status: string;
  source: {
    repository: string;
    ref?: string;
  };
  target: {
    branchName: string;
    url: string;
    prUrl?: string;
    autoCreatePr: boolean;
    openAsCursorGithubApp: boolean;
    skipReviewerRequest: boolean;
  };
  summary?: string;
  createdAt: string; // ISO 8601
}
```

### Example Response

```json
{
  "id": "bc_abc123",
  "name": "Add README Documentation",
  "status": "FINISHED",
  "source": {
    "repository": "https://github.com/your-org/your-repo",
    "ref": "main"
  },
  "target": {
    "branchName": "cursor/add-readme-1234",
    "url": "https://cursor.com/agents?id=bc_abc123",
    "prUrl": "https://github.com/your-org/your-repo/pull/1234",
    "autoCreatePr": false,
    "openAsCursorGithubApp": false,
    "skipReviewerRequest": false
  },
  "summary": "Added README.md with installation instructions and usage examples",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

---

## Agent Conversation

**Endpoint:** `GET /v0/agents/{id}/conversation`

Retrieve the conversation history of a cloud agent, including all user prompts and assistant responses.

**Important:** You cannot access the conversation if the agent has been deleted.

### Request

```bash
curl --request GET \
  --url https://api.cursor.com/v0/agents/bc_abc123/conversation \
  -u YOUR_API_KEY:
```

### Path Parameters

| Parameter | Type   | Required | Description                           |
|-----------|--------|----------|---------------------------------------|
| id        | string | Yes      | Unique identifier (e.g., `bc_abc123`) |

### Response Schema

```typescript
{
  id: string;
  messages: Array<{
    id: string;
    type: "user_message" | "assistant_message";
    text: string;
  }>;
}
```

### Example Response

```json
{
  "id": "bc_abc123",
  "messages": [
    {
      "id": "msg_001",
      "type": "user_message",
      "text": "Add a README.md file with installation instructions"
    },
    {
      "id": "msg_002",
      "type": "assistant_message",
      "text": "I'll help you create a comprehensive README.md file with installation instructions. Let me start by analyzing your project structure..."
    },
    {
      "id": "msg_003",
      "type": "assistant_message",
      "text": "I've created a README.md file with the following sections:\n- Project overview\n- Installation instructions\n- Usage examples\n- Configuration options"
    },
    {
      "id": "msg_004",
      "type": "user_message",
      "text": "Also add a section about troubleshooting"
    },
    {
      "id": "msg_005",
      "type": "assistant_message",
      "text": "I've added a troubleshooting section to the README with common issues and solutions."
    }
  ]
}
```

---

## Launch an Agent

**Endpoint:** `POST /v0/agents`

Start a new cloud agent to work on your repository.

### Request

```bash
curl --request POST \
  --url https://api.cursor.com/v0/agents \
  -u YOUR_API_KEY: \
  --header 'Content-Type: application/json' \
  --data '{
  "prompt": {
    "text": "Add a README.md file with installation instructions",
    "images": [
      {
        "data": "iVBORw0KGgoAAAANSUhEUgAA...",
        "dimension": {
          "width": 1024,
          "height": 768
        }
      }
    ]
  },
  "source": {
    "repository": "https://github.com/your-org/your-repo",
    "ref": "main"
  },
  "target": {
    "autoCreatePr": true,
    "branchName": "feature/add-readme"
  }
}'
```

### Request Body Schema

```typescript
{
  prompt: {
    text: string;         // Required
    images?: Array<{      // Optional, max 5
      data: string;       // Base64 encoded image
      dimension: {
        width: number;
        height: number;
      };
    }>;
  };
  source: {
    repository?: string;  // Required unless prUrl is provided
    ref?: string;         // Git ref (branch, tag, commit hash)
    prUrl?: string;       // PR URL - overrides repository and ref
  };
  target?: {
    autoCreatePr?: boolean;           // Default: false
    openAsCursorGithubApp?: boolean;  // Default: false, requires autoCreatePr
    skipReviewerRequest?: boolean;    // Default: false, requires autoCreatePr + openAsCursorGithubApp
    branchName?: string;              // Custom branch name
    autoBranch?: boolean;             // Default: true, only when prUrl provided
  };
  model?: string;  // e.g., "claude-4-sonnet"
  webhook?: {
    url: string;    // Required if webhook provided
    secret: string; // Optional, min 32 characters
  };
}
```

### Response Schema

```typescript
{
  id: string;
  name: string;
  status: "CREATING" | "RUNNING" | "FINISHED" | ...;
  source: {
    repository: string;
    ref?: string;
  };
  target: {
    branchName: string;
    url: string;
    prUrl?: string;
    autoCreatePr: boolean;
    openAsCursorGithubApp: boolean;
    skipReviewerRequest: boolean;
  };
  createdAt: string; // ISO 8601
}
```

### Example Response

```json
{
  "id": "bc_abc123",
  "name": "Add README Documentation",
  "status": "CREATING",
  "source": {
    "repository": "https://github.com/your-org/your-repo",
    "ref": "main"
  },
  "target": {
    "branchName": "feature/add-readme",
    "url": "https://cursor.com/agents?id=bc_abc123",
    "prUrl": "https://github.com/your-org/your-repo/pull/123",
    "autoCreatePr": true,
    "openAsCursorGithubApp": false,
    "skipReviewerRequest": false
  },
  "createdAt": "2024-01-15T10:30:00Z"
}
```

---

## Add Follow-up

**Endpoint:** `POST /v0/agents/{id}/followup`

Add a follow-up instruction to an existing cloud agent.

### Request

```bash
curl --request POST \
  --url https://api.cursor.com/v0/agents/bc_abc123/followup \
  -u YOUR_API_KEY: \
  --header 'Content-Type: application/json' \
  --data '{
  "prompt": {
    "text": "Also add a section about troubleshooting",
    "images": [
      {
        "data": "iVBORw0KGgoAAAANSUhEUgAA...",
        "dimension": {
          "width": 1024,
          "height": 768
        }
      }
    ]
  }
}'
```

### Path Parameters

| Parameter | Type   | Required | Description                           |
|-----------|--------|----------|---------------------------------------|
| id        | string | Yes      | Unique identifier (e.g., `bc_abc123`) |

### Request Body Schema

```typescript
{
  prompt: {
    text: string;         // Required
    images?: Array<{      // Optional, max 5
      data: string;       // Base64 encoded image
      dimension: {
        width: number;
        height: number;
      };
    }>;
  };
}
```

### Response Schema

```typescript
{
  id: string;
}
```

### Example Response

```json
{
  "id": "bc_abc123"
}
```

### Notes

- Sending a follow-up to a stopped agent will restart it.
- The agent must exist and not be deleted.

---

## Stop an Agent

**Endpoint:** `POST /v0/agents/{id}/stop`

Stop a running cloud agent. This pauses the agent's execution without deleting it.

### Request

```bash
curl --request POST \
  --url https://api.cursor.com/v0/agents/bc_abc123/stop \
  -u YOUR_API_KEY:
```

### Path Parameters

| Parameter | Type   | Required | Description                           |
|-----------|--------|----------|---------------------------------------|
| id        | string | Yes      | Unique identifier (e.g., `bc_abc123`) |

### Response Schema

```typescript
{
  id: string;
}
```

### Example Response

```json
{
  "id": "bc_abc123"
}
```

### Notes

- You can only stop agents that are currently running.
- A stopped agent will restart if you send a follow-up prompt.

---

## Delete an Agent

**Endpoint:** `DELETE /v0/agents/{id}`

Delete a cloud agent. This action is permanent and cannot be undone.

### Request

```bash
curl --request DELETE \
  --url https://api.cursor.com/v0/agents/bc_abc123 \
  -u YOUR_API_KEY:
```

### Path Parameters

| Parameter | Type   | Required | Description                           |
|-----------|--------|----------|---------------------------------------|
| id        | string | Yes      | Unique identifier (e.g., `bc_abc123`) |

### Response Schema

```typescript
{
  id: string;
}
```

### Example Response

```json
{
  "id": "bc_abc123"
}
```

### Important

- **This action is permanent and cannot be undone.**
- After deletion, you cannot access the agent's conversation history.

---

## API Key Info

**Endpoint:** `GET /v0/me`

Retrieve information about the API key being used for authentication.

### Request

```bash
curl --request GET \
  --url https://api.cursor.com/v0/me \
  -u YOUR_API_KEY:
```

### Response Schema

```typescript
{
  apiKeyName: string;
  createdAt: string; // ISO 8601
  userEmail: string;
}
```

### Example Response

```json
{
  "apiKeyName": "Production API Key",
  "createdAt": "2024-01-15T10:30:00Z",
  "userEmail": "developer@example.com"
}
```

---

## List Models

**Endpoint:** `GET /v0/models`

Retrieve a list of recommended models for cloud agents.

### Request

```bash
curl --request GET \
  --url https://api.cursor.com/v0/models \
  -u YOUR_API_KEY:
```

### Response Schema

```typescript
{
  models: string[];
}
```

### Example Response

```json
{
  "models": [
    "claude-4-sonnet-thinking",
    "gpt-5.2",
    "claude-4.5-sonnet-thinking"
  ]
}
```

### Recommendation

Use "Auto" (don't provide a model name) to let Cursor pick the most appropriate model.

---

## List GitHub Repositories

**Endpoint:** `GET /v0/repositories`

Retrieve a list of GitHub repositories accessible to the authenticated user.

### Request

```bash
curl --request GET \
  --url https://api.cursor.com/v0/repositories \
  -u YOUR_API_KEY:
```

### Response Schema

```typescript
{
  repositories: Array<{
    owner: string;
    name: string;
    repository: string; // Full URL
  }>;
}
```

### Example Response

```json
{
  "repositories": [
    {
      "owner": "your-org",
      "name": "your-repo",
      "repository": "https://github.com/your-org/your-repo"
    },
    {
      "owner": "your-org",
      "name": "another-repo",
      "repository": "https://github.com/your-org/another-repo"
    },
    {
      "owner": "your-username",
      "name": "personal-project",
      "repository": "https://github.com/your-username/personal-project"
    }
  ]
}
```

### Rate Limits

**This endpoint has very strict rate limits:**

- **1 request per user per minute**
- **30 requests per user per hour**

Requests can take tens of seconds for users with access to many repositories. Handle unavailability gracefully.

---

## Error Handling

### Common HTTP Status Codes

| Code | Description | Handling |
|------|-------------|----------|
| 400  | Bad Request | Invalid request body or parameters |
| 401  | Unauthorized | Invalid or missing API key |
| 403  | Forbidden | Insufficient permissions |
| 404  | Not Found | Agent or resource doesn't exist |
| 429  | Too Many Requests | Rate limit exceeded |
| 500  | Server Error | Retry with exponential backoff |

### Rate Limiting

Most endpoints have standard rate limits. The `/v0/repositories` endpoint has especially strict limits (1/min, 30/hour).

Implement exponential backoff for 429 responses:

```python
import time
import requests

def make_request_with_retry(url, api_key, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url, auth=(api_key, ''))
        if response.status_code == 429:
            wait_time = (2 ** attempt) + random.random()
            time.sleep(wait_time)
            continue
        return response
    raise Exception("Max retries exceeded")
```
