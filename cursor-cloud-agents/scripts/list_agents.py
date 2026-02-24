#!/usr/bin/env python3
"""
List all Cursor Cloud Agents.

Usage:
    python list_agents.py --api-key YOUR_API_KEY [--limit 50] [--pr-url https://...]

Environment Variables:
    CURSOR_API_KEY: Your Cursor API key (alternative to --api-key)
"""

import argparse
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def parse_args():
    parser = argparse.ArgumentParser(
        description="List Cursor Cloud Agents"
    )
    
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.environ.get("CURSOR_API_KEY"),
        help="Cursor API key (or set CURSOR_API_KEY env var)"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Number of agents to return (default: 20, max: 100)"
    )
    
    parser.add_argument(
        "--pr-url",
        type=str,
        help="Filter by PR URL"
    )
    
    parser.add_argument(
        "--status",
        type=str,
        choices=["RUNNING", "FINISHED", "CREATING", "STOPPED"],
        help="Filter by status"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON response"
    )
    
    parser.add_argument(
        "--all-pages",
        action="store_true",
        help="Fetch all pages (auto-paginate)"
    )
    
    return parser.parse_args()


def list_agents(args):
    """List cloud agents."""
    
    # Validate API key
    if not args.api_key:
        print("Error: API key required. Use --api-key or set CURSOR_API_KEY env var.")
        sys.exit(1)
    
    # Validate limit
    if args.limit > 100:
        print("Warning: Limit capped at 100")
        args.limit = 100
    
    all_agents = []
    cursor = None
    page = 1
    
    while True:
        # Build URL with query parameters
        url = f"https://api.cursor.com/v0/agents?limit={args.limit}"
        
        if args.pr_url:
            url += f"&prUrl={args.pr_url}"
        
        if cursor:
            url += f"&cursor={cursor}"
        
        req = Request(
            url,
            headers={
                "Authorization": f"Basic {base64.b64encode(f'{args.api_key}:'.encode()).decode()}"
            },
            method="GET"
        )
        
        try:
            with urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                agents = result.get('agents', [])
                all_agents.extend(agents)
                
                if not args.all_pages:
                    break
                
                cursor = result.get('nextCursor')
                if not cursor:
                    break
                
                page += 1
                
        except HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"Error: HTTP {e.code}")
            print(f"Response: {error_body}")
            sys.exit(1)
        except URLError as e:
            print(f"Error: Failed to connect: {e.reason}")
            sys.exit(1)
    
    # Filter by status if specified
    if args.status:
        all_agents = [a for a in all_agents if a.get('status') == args.status]
    
    # Output
    if args.json:
        print(json.dumps({"agents": all_agents}, indent=2))
    else:
        if not all_agents:
            print("No agents found.")
            return
        
        print(f"Found {len(all_agents)} agent(s)\n")
        print("=" * 80)
        
        for agent in all_agents:
            status_icon = {
                "RUNNING": "🔄",
                "FINISHED": "✅",
                "CREATING": "⏳",
                "STOPPED": "⏸️"
            }.get(agent.get('status'), "•")
            
            print(f"\n{status_icon} {agent.get('name', 'Unnamed')}")
            print(f"   ID:     {agent.get('id')}")
            print(f"   Status: {agent.get('status')}")
            print(f"   Branch: {agent.get('target', {}).get('branchName', 'N/A')}")
            
            if agent.get('target', {}).get('prUrl'):
                print(f"   PR:     {agent['target']['prUrl']}")
            
            if agent.get('summary'):
                summary = agent['summary'][:100] + "..." if len(agent['summary']) > 100 else agent['summary']
                print(f"   Summary: {summary}")
            
            print(f"   Created: {agent.get('createdAt')}")
            print("-" * 80)
    
    return all_agents


def main():
    import base64
    args = parse_args()
    list_agents(args)


if __name__ == "__main__":
    main()
