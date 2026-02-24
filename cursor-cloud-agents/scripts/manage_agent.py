#!/usr/bin/env python3
"""
Stop or delete a Cursor Cloud Agent.

Usage:
    python manage_agent.py --api-key YOUR_API_KEY --agent-id bc_abc123 --action stop
    python manage_agent.py --api-key YOUR_API_KEY --agent-id bc_abc123 --action delete

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
        description="Stop or delete a Cursor Cloud Agent"
    )
    
    parser.add_argument(
        "--agent-id",
        type=str,
        required=True,
        help="Agent ID (e.g., bc_abc123)"
    )
    
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.environ.get("CURSOR_API_KEY"),
        help="Cursor API key (or set CURSOR_API_KEY env var)"
    )
    
    parser.add_argument(
        "--action",
        type=str,
        choices=["stop", "delete"],
        required=True,
        help="Action to perform: stop or delete"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation for delete"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON response"
    )
    
    return parser.parse_args()


def manage_agent(args):
    """Stop or delete an agent."""
    
    # Validate API key
    if not args.api_key:
        print("Error: API key required. Use --api-key or set CURSOR_API_KEY env var.")
        sys.exit(1)
    
    # Confirm delete
    if args.action == "delete" and not args.force:
        confirm = input(f"⚠️  Are you sure you want to DELETE agent {args.agent_id}? This cannot be undone. (y/N): ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
    
    # Build URL
    if args.action == "stop":
        url = f"https://api.cursor.com/v0/agents/{args.agent_id}/stop"
        action_name = "Stop"
    else:
        url = f"https://api.cursor.com/v0/agents/{args.agent_id}"
        action_name = "Delete"
    
    req = Request(
        url,
        headers={
            "Authorization": f"Basic {base64.b64encode(f'{args.api_key}:'.encode()).decode()}"
        },
        method="POST" if args.action == "stop" else "DELETE"
    )
    
    try:
        with urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if args.action == "stop":
                    print("✓ Agent stopped successfully!")
                    print(f"\nAgent ID: {result['id']}")
                    print("\nThe agent has been paused. Send a follow-up to restart it.")
                else:
                    print("✓ Agent deleted successfully!")
                    print(f"\nAgent ID: {result['id']}")
                    print("\n⚠️  This action is permanent. The agent and its conversation history are gone.")
            
            return result
            
    except HTTPError as e:
        if e.code == 404:
            print(f"Error: Agent {args.agent_id} not found.")
        elif e.code == 400:
            error_body = e.read().decode('utf-8')
            if args.action == "stop":
                print(f"Error: Can only stop running agents. {error_body}")
            else:
                print(f"Error: {error_body}")
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
    manage_agent(args)


if __name__ == "__main__":
    main()
