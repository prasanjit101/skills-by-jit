#!/usr/bin/env python3
"""
Check the status of a Cursor Cloud Agent.

Usage:
    python check_status.py --api-key YOUR_API_KEY --agent-id bc_abc123

Environment Variables:
    CURSOR_API_KEY: Your Cursor API key (alternative to --api-key)
"""

import argparse
import base64
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Load .env from the skill root directory into os.environ automatically.
# This must happen before parse_args() so that os.environ.get("CURSOR_API_KEY")
# picks up any value saved in the .env file.
import config  # noqa: E402  (local module in the same scripts/ directory)


def parse_args():
    parser = argparse.ArgumentParser(description="Check Cursor Cloud Agent status")

    parser.add_argument(
        "--agent-id", type=str, required=True, help="Agent ID (e.g., bc_abc123)"
    )

    parser.add_argument(
        "--api-key",
        type=str,
        default=os.environ.get("CURSOR_API_KEY"),
        help="Cursor API key (or set CURSOR_API_KEY env var)",
    )

    parser.add_argument(
        "--conversation",
        action="store_true",
        help="Fetch conversation history instead of status",
    )

    parser.add_argument("--json", action="store_true", help="Output raw JSON response")

    parser.add_argument(
        "--quiet", action="store_true", help="Minimal output (only status)"
    )

    return parser.parse_args()


def check_status(args):
    """Check agent status or conversation."""

    # Validate API key
    if not args.api_key:
        print("Error: API key required. Use --api-key or set CURSOR_API_KEY env var.")
        sys.exit(1)

    # Build URL
    if args.conversation:
        url = f"https://api.cursor.com/v0/agents/{args.agent_id}/conversation"
    else:
        url = f"https://api.cursor.com/v0/agents/{args.agent_id}"

    req = Request(
        url,
        headers={
            "Authorization": f"Basic {base64.b64encode(f'{args.api_key}:'.encode()).decode()}"
        },
        method="GET",
    )

    try:
        with urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))

            if args.json:
                print(json.dumps(result, indent=2))
                return result

            if args.conversation:
                # Display conversation
                if args.quiet:
                    print(f"Messages: {len(result.get('messages', []))}")
                else:
                    print(f"Conversation for Agent: {result['id']}\n")
                    print("=" * 60)

                    for msg in result.get("messages", []):
                        role = "USER" if msg["type"] == "user_message" else "ASSISTANT"
                        print(f"\n[{role}]")
                        print(msg["text"])
                        print("-" * 60)
            else:
                # Display status
                if args.quiet:
                    print(result["status"])
                else:
                    print(f"Agent: {result['name']}")
                    print(f"ID:     {result['id']}")
                    print(f"Status: {result['status']}")
                    print()

                    if result.get("source"):
                        print("Source:")
                        print(
                            f"  Repository: {result['source'].get('repository', 'N/A')}"
                        )
                        if result["source"].get("ref"):
                            print(f"  Ref:        {result['source']['ref']}")

                    if result.get("target"):
                        print("\nTarget:")
                        print(
                            f"  Branch:     {result['target'].get('branchName', 'N/A')}"
                        )
                        print(f"  URL:        {result['target'].get('url', 'N/A')}")
                        if result["target"].get("prUrl"):
                            print(f"  PR:         {result['target']['prUrl']}")
                        print(
                            f"  Auto PR:    {result['target'].get('autoCreatePr', False)}"
                        )

                    if result.get("summary"):
                        print(f"\nSummary:\n{result['summary']}")

                    print(f"\nCreated:  {result.get('createdAt', 'N/A')}")

            return result

    except HTTPError as e:
        if e.code == 404:
            print(f"Error: Agent {args.agent_id} not found.")
        else:
            error_body = e.read().decode("utf-8")
            print(f"Error: HTTP {e.code}")
            print(f"Response: {error_body}")
        sys.exit(1)
    except URLError as e:
        print(f"Error: Failed to connect: {e.reason}")
        sys.exit(1)


def main():
    args = parse_args()
    check_status(args)


if __name__ == "__main__":
    main()
