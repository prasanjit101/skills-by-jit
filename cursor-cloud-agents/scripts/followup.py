#!/usr/bin/env python3
"""
Add a follow-up instruction to a running Cursor Cloud Agent.

Usage:
    python followup.py --api-key YOUR_API_KEY --agent-id bc_abc123 --prompt "Add unit tests"

Environment Variables:
    CURSOR_API_KEY: Your Cursor API key (alternative to --api-key)
"""

import argparse
import json
import os
import sys
import base64
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def parse_args():
    parser = argparse.ArgumentParser(
        description="Add follow-up to Cursor Cloud Agent"
    )
    
    parser.add_argument(
        "--agent-id",
        type=str,
        required=True,
        help="Agent ID (e.g., bc_abc123)"
    )
    
    parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="Follow-up instruction text"
    )
    
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.environ.get("CURSOR_API_KEY"),
        help="Cursor API key (or set CURSOR_API_KEY env var)"
    )
    
    parser.add_argument(
        "--image",
        type=str,
        help="Path to image file to include"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON response"
    )
    
    return parser.parse_args()


def encode_image(image_path: str) -> dict:
    """Encode image file to base64."""
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    return {"data": data}


def add_followup(args):
    """Add follow-up to agent."""
    
    # Validate API key
    if not args.api_key:
        print("Error: API key required. Use --api-key or set CURSOR_API_KEY env var.")
        sys.exit(1)
    
    # Build request body
    body = {
        "prompt": {
            "text": args.prompt
        }
    }
    
    # Add image if provided
    if args.image:
        try:
            body["prompt"]["images"] = [encode_image(args.image)]
        except Exception as e:
            print(f"Error: Failed to encode image: {e}")
            sys.exit(1)
    
    # Make request
    url = f"https://api.cursor.com/v0/agents/{args.agent_id}/followup"
    data = json.dumps(body).encode('utf-8')
    
    req = Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Basic {base64.b64encode(f'{args.api_key}:'.encode()).decode()}"
        },
        method="POST"
    )
    
    try:
        with urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print("✓ Follow-up added successfully!")
                print(f"\nAgent ID: {result['id']}")
                print(f"Prompt:   {args.prompt}")
                print(f"\nNote: If the agent was stopped, it will now restart.")
            
            return result
            
    except HTTPError as e:
        if e.code == 404:
            print(f"Error: Agent {args.agent_id} not found.")
        elif e.code == 400:
            error_body = e.read().decode('utf-8')
            print(f"Error: Bad request - {error_body}")
        else:
            error_body = e.read().decode('utf-8')
            print(f"Error: HTTP {e.code}")
            print(f"Response: {error_body}")
        sys.exit(1)
    except URLError as e:
        print(f"Error: Failed to connect: {e.reason}")
        sys.exit(1)


def main():
    args = parse_args()
    add_followup(args)


if __name__ == "__main__":
    main()
