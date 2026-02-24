# Webhooks Guide

Configure webhooks to receive notifications when cloud agent status changes.

---

## Table of Contents

1. [Overview](#overview)
2. [Configuration](#configuration)
3. [Webhook Payload](#webhook-payload)
4. [Signature Verification](#signature-verification)
5. [Best Practices](#best-practices)
6. [Example Implementation](#example-implementation)

---

## Overview

Webhooks allow you to receive real-time notifications when a cloud agent's status changes. This is useful for:

- Tracking long-running agents
- Integrating with CI/CD pipelines
- Sending notifications to Slack, email, or other channels
- Triggering downstream workflows

---

## Configuration

When launching an agent, include the `webhook` object in your request:

```json
{
  "prompt": {
    "text": "Add comprehensive tests for the authentication module"
  },
  "source": {
    "repository": "https://github.com/your-org/your-repo",
    "ref": "main"
  },
  "webhook": {
    "url": "https://your-server.com/webhook",
    "secret": "your-secret-key-minimum-32-characters-long"
  }
}
```

### Webhook Properties

| Property | Type   | Required | Description                              |
|----------|--------|----------|------------------------------------------|
| url      | string | Yes      | URL to receive webhook notifications     |
| secret   | string | No       | Secret for payload verification (min 32 chars) |

### Requirements

- **URL**: Must be a publicly accessible HTTPS endpoint
- **Secret**: Minimum 32 characters recommended for security
- **Response**: Your endpoint should return `200 OK` for successful receipt

---

## Webhook Payload

When an agent's status changes, Cursor sends a POST request to your webhook URL with the following payload:

```typescript
{
  id: string;           // Agent ID (e.g., "bc_abc123")
  name: string;         // Agent name
  status: string;       // New status (e.g., "RUNNING", "FINISHED")
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
  summary?: string;     // Present when status is "FINISHED"
  createdAt: string;    // ISO 8601 timestamp
  event: {
    type: "status_change";
    timestamp: string;  // ISO 8601 timestamp
    previousStatus?: string;
  };
}
```

### Example Payload

```json
{
  "id": "bc_abc123",
  "name": "Add Unit Tests",
  "status": "FINISHED",
  "source": {
    "repository": "https://github.com/your-org/your-repo",
    "ref": "main"
  },
  "target": {
    "branchName": "feature/add-tests",
    "url": "https://cursor.com/agents?id=bc_abc123",
    "prUrl": "https://github.com/your-org/your-repo/pull/456",
    "autoCreatePr": true,
    "openAsCursorGithubApp": false,
    "skipReviewerRequest": false
  },
  "summary": "Created comprehensive unit tests for authentication module with 95% coverage",
  "createdAt": "2024-01-15T10:30:00Z",
  "event": {
    "type": "status_change",
    "timestamp": "2024-01-15T11:45:00Z",
    "previousStatus": "RUNNING"
  }
}
```

---

## Signature Verification

To verify that webhooks are from Cursor, use the `X-Cursor-Signature` header.

### Signature Algorithm

Cursor signs each webhook payload with HMAC-SHA256 using your secret:

```
signature = HMAC-SHA256(secret, payload_body)
```

The signature is sent as a hex string in the `X-Cursor-Signature` header.

### Verification Example (Node.js)

```javascript
const crypto = require('crypto');

function verifyWebhookSignature(payload, signature, secret) {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload, 'utf8')
    .digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(signature, 'hex'),
    Buffer.from(expectedSignature, 'hex')
  );
}

// Express middleware example
app.post('/webhook', (req, res) => {
  const signature = req.headers['x-cursor-signature'];
  const payload = JSON.stringify(req.body);
  const secret = process.env.CURSOR_WEBHOOK_SECRET;
  
  if (!verifyWebhookSignature(payload, signature, secret)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }
  
  // Process webhook
  console.log('Webhook received:', req.body);
  res.status(200).json({ received: true });
});
```

### Verification Example (Python/Flask)

```python
from flask import Flask, request, abort
import hmac
import hashlib
import json

app = Flask(__name__)

def verify_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)

@app.route('/webhook', methods=['POST'])
def webhook():
    signature = request.headers.get('X-Cursor-Signature')
    payload = request.get_data(as_text=True)
    secret = os.environ['CURSOR_WEBHOOK_SECRET']
    
    if not verify_signature(payload, signature, secret):
        abort(401)
    
    data = json.loads(payload)
    print(f"Webhook received: {data}")
    return json.dumps({'received': True})
```

---

## Best Practices

### 1. Endpoint Requirements

- **Return 200 OK**: Acknowledge receipt quickly (within 5 seconds)
- **Process asynchronously**: Move heavy processing to background jobs
- **Idempotency**: Handle duplicate webhooks gracefully (use agent ID + timestamp)

### 2. Security

- **Use HTTPS**: Always use HTTPS for webhook URLs
- **Verify signatures**: Always verify the `X-Cursor-Signature` header
- **Use strong secrets**: Minimum 32 characters, randomly generated
- **Rotate secrets**: Periodically rotate webhook secrets

### 3. Reliability

- **Handle retries**: Cursor may retry failed webhooks
- **Log everything**: Log all webhook events for debugging
- **Monitor failures**: Set up alerts for webhook delivery failures
- **Timeout handling**: Process webhooks quickly to avoid timeouts

### 4. Status Transitions

Common status transitions:

```
CREATING → RUNNING → FINISHED
                    → FAILED (if error occurs)
                    
RUNNING → STOPPED (via API)
STOPPED → RUNNING (via follow-up)
```

---

## Example Implementation

### Full Node.js/Express Example

```javascript
const express = require('express');
const crypto = require('crypto');
const app = express();

app.use(express.json());

const WEBHOOK_SECRET = process.env.CURSOR_WEBHOOK_SECRET;

function verifySignature(payload, signature, secret) {
  const expected = crypto
    .createHmac('sha256', secret)
    .update(payload, 'utf8')
    .digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(signature, 'hex'),
    Buffer.from(expected, 'hex')
  );
}

app.post('/webhook/cursor', (req, res) => {
  const signature = req.headers['x-cursor-signature'];
  const payload = JSON.stringify(req.body);
  
  // Verify signature
  if (!verifySignature(payload, signature, WEBHOOK_SECRET)) {
    console.error('Invalid webhook signature');
    return res.status(401).json({ error: 'Invalid signature' });
  }
  
  const event = req.body;
  console.log(`Agent ${event.id} status: ${event.previousStatus} → ${event.status}`);
  
  // Process based on status
  switch (event.status) {
    case 'FINISHED':
      handleAgentFinished(event);
      break;
    case 'FAILED':
      handleAgentFailed(event);
      break;
    case 'RUNNING':
      handleAgentRunning(event);
      break;
  }
  
  res.status(200).json({ received: true });
});

function handleAgentFinished(event) {
  // Send notification, update database, trigger CI/CD, etc.
  console.log(`Agent completed: ${event.summary}`);
  if (event.target.prUrl) {
    console.log(`PR created: ${event.target.prUrl}`);
  }
}

function handleAgentFailed(event) {
  // Alert team, log error, etc.
  console.error(`Agent failed: ${event.id}`);
}

function handleAgentRunning(event) {
  // Update status in dashboard, etc.
  console.log(`Agent is running: ${event.id}`);
}

app.listen(3000, () => {
  console.log('Webhook server listening on port 3000');
});
```

### Python/FastAPI Example

```python
from fastapi import FastAPI, Request, HTTPException, Header
import hmac
import hashlib
import os
from typing import Optional

app = FastAPI()

WEBHOOK_SECRET = os.environ.get("CURSOR_WEBHOOK_SECRET")

def verify_signature(payload: str, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)

@app.post("/webhook/cursor")
async def cursor_webhook(
    request: Request,
    x_cursor_signature: Optional[str] = Header(None)
):
    body = await request.body()
    payload = body.decode('utf-8')
    
    if not verify_signature(payload, x_cursor_signature, WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    event = await request.json()
    agent_id = event.get("id")
    status = event.get("status")
    previous_status = event.get("event", {}).get("previousStatus")
    
    print(f"Agent {agent_id}: {previous_status} → {status}")
    
    # Process event
    if status == "FINISHED":
        await handle_finished(event)
    elif status == "FAILED":
        await handle_failed(event)
    
    return {"received": True}

async def handle_finished(event: dict):
    print(f"Agent completed: {event.get('summary')}")
    if event.get("target", {}).get("prUrl"):
        print(f"PR: {event['target']['prUrl']}")

async def handle_failed(event: dict):
    print(f"Agent failed: {event.get('id')}")
```

---

## Testing Webhooks

### Local Testing with ngrok

1. Install ngrok: `npm install -g ngrok`
2. Start your local server: `node server.js`
3. Expose to internet: `ngrok http 3000`
4. Use the ngrok URL as your webhook URL

### Test Payload

Use this sample payload to test your endpoint:

```json
{
  "id": "bc_test123",
  "name": "Test Agent",
  "status": "FINISHED",
  "source": {
    "repository": "https://github.com/test/test-repo",
    "ref": "main"
  },
  "target": {
    "branchName": "test/branch",
    "url": "https://cursor.com/agents?id=bc_test123",
    "autoCreatePr": false,
    "openAsCursorGithubApp": false,
    "skipReviewerRequest": false
  },
  "createdAt": "2024-01-15T10:30:00Z",
  "event": {
    "type": "status_change",
    "timestamp": "2024-01-15T11:00:00Z",
    "previousStatus": "RUNNING"
  }
}
```

### Generate Test Signature

```bash
# Using OpenSSL
echo -n '{"id":"bc_test123",...}' | openssl dgst -sha256 -hmac "your-secret-key"
```

---

## Troubleshooting

### Webhook Not Received

1. **Check URL accessibility**: Ensure your endpoint is publicly accessible
2. **Verify firewall rules**: Allow inbound HTTPS traffic
3. **Check DNS**: Ensure your domain resolves correctly
4. **Test with curl**: `curl -X POST https://your-server.com/webhook`

### Signature Verification Fails

1. **Check secret match**: Ensure webhook secret matches your verification code
2. **Verify encoding**: Use UTF-8 encoding for payload
3. **Check header name**: Header is `X-Cursor-Signature` (case-insensitive)
4. **Raw payload**: Use raw request body, not parsed JSON

### Multiple Webhooks Received

- **Expected behavior**: Cursor may retry on non-200 responses
- **Solution**: Implement idempotency using agent ID + timestamp

### Slow Response Times

- **Process asynchronously**: Return 200 immediately, process in background
- **Use queues**: Move webhook processing to a job queue
- **Timeout**: Cursor may timeout after 30 seconds
