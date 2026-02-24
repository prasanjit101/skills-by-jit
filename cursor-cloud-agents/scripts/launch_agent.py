#!/usr/bin/env python3
"""
Launch a Cursor Cloud Agent with configurable options.

Usage:
    python launch_agent.py \
        --api-key YOUR_API_KEY \
        --repo https://github.com/your-org/your-repo \
        --prompt "Add a README.md file with installation instructions" \
        --ref main \
        --auto-create-pr \
        --branch-name feature/add-readme

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
        description="Launch a Cursor Cloud Agent"
    )
    
    # Required
    parser.add_argument(
        "--repo",
        type=str,
        help="GitHub repository URL (e.g., https://github.com/org/repo)"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="Instruction text for the agent"
    )
    
    # Authentication
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.environ.get("CURSOR_API_KEY"),
        help="Cursor API key (or set CURSOR_API_KEY env var)"
    )
    
    # Source options
    parser.add_argument(
        "--ref",
        type=str,
        default="main",
        help="Git ref (branch, tag, or commit hash). Default: main"
    )
    parser.add_argument(
        "--pr-url",
        type=str,
        help="PR URL to work on (overrides --repo and --ref)"
    )
    
    # Target options
    parser.add_argument(
        "--auto-create-pr",
        action="store_true",
        help="Automatically create a pull request"
    )
    parser.add_argument(
        "--branch-name",
        type=str,
        help="Custom branch name for the agent"
    )
    parser.add_argument(
        "--open-as-cursor-app",
        action="store_true",
        help="Open PR as Cursor GitHub App (requires --auto-create-pr)"
    )
    parser.add_argument(
        "--skip-reviewer",
        action="store_true",
        help="Skip adding user as reviewer (requires --auto-create-pr and --open-as-cursor-app)"
    )
    parser.add_argument(
        "--auto-branch",
        action="store_true",
        default=True,
        help="Create new branch (default: true). Use --no-auto-branch to disable"
    )
    
    # Model
    parser.add_argument(
        "--model",
        type=str,
        help="LLM model to use (e.g., claude-4-sonnet). Default: auto-select"
    )
    
    # Webhook
    parser.add_argument(
        "--webhook-url",
        type=str,
        help="Webhook URL for status notifications"
    )
    parser.add_argument(
        "--webhook-secret",
        type=str,
        help="Webhook secret for signature verification (min 32 chars)"
    )
    
    # Image (optional)
    parser.add_argument(
        "--image",
        type=str,
        help="Path to image file to include (base64 encoded)"
    )
    
    # Output
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON response"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output (only agent ID and URL)"
    )
    
    return parser.parse_args()


def encode_image(image_path: str) -> dict:
    """Encode image file to base64 with dimensions."""
    try:
        from PIL import Image
    except ImportError:
        print("Warning: Pillow not installed. Image dimensions will not be available.")
        with open(image_path, "rb") as f:
            data = base64.b64encode(f.read()).decode('utf-8')
        return {"data": data}
    
    with Image.open(image_path) as img:
        width, height = img.size
    
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    
    return {
        "data": data,
        "dimension": {"width": width, "height": height}
    }


def launch_agent(args):
    """Launch the cloud agent."""
    
    # Validate API key
    if not args.api_key:
        print("Error: API key required. Use --api-key or set CURSOR_API_KEY env var.")
        sys.exit(1)
    
    # Validate repo or pr-url
    if not args.repo and not args.pr_url:
        print("Error: Either --repo or --pr-url is required.")
        sys.exit(1)
    
    # Build request body
    body = {
        "prompt": {
            "text": args.prompt
        },
        "source": {}
    }
    
    # Add image if provided
    if args.image:
        try:
            body["prompt"]["images"] = [encode_image(args.image)]
        except Exception as e:
            print(f"Warning: Failed to encode image: {e}")
    
    # Source configuration
    if args.pr_url:
        body["source"]["prUrl"] = args.pr_url
        if args.auto_branch is False:
            body["target"] = body.get("target", {})
            body["target"]["autoBranch"] = False
    else:
        body["source"]["repository"] = args.repo
        body["source"]["ref"] = args.ref
    
    # Target configuration
    if any([args.auto_create_pr, args.branch_name, args.open_as_cursor_app, args.skip_reviewer]):
        body["target"] = {}
        
        if args.auto_create_pr:
            body["target"]["autoCreatePr"] = True
        
        if args.branch_name:
            body["target"]["branchName"] = args.branch_name
        
        if args.open_as_cursor_app:
            if not args.auto_create_pr:
                print("Warning: --open-as-cursor-app requires --auto-create-pr")
            body["target"]["openAsCursorGithubApp"] = True
        
        if args.skip_reviewer:
            if not (args.auto_create_pr and args.open_as_cursor_app):
                print("Warning: --skip-reviewer requires --auto-create-pr and --open-as-cursor-app")
            body["target"]["skipReviewerRequest"] = True
    
    # Model
    if args.model:
        body["model"] = args.model
    
    # Webhook
    if args.webhook_url:
        body["webhook"] = {"url": args.webhook_url}
        if args.webhook_secret:
            if len(args.webhook_secret) < 32:
                print("Warning: Webhook secret should be at least 32 characters")
            body["webhook"]["secret"] = args.webhook_secret
    
    # Make request
    url = "https://api.cursor.com/v0/agents"
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
            elif args.quiet:
                print(f"Agent ID: {result['id']}")
                print(f"URL: {result['target']['url']}")
            else:
                print("✓ Agent launched successfully!")
                print(f"\nAgent ID:   {result['id']}")
                print(f"Name:       {result['name']}")
                print(f"Status:     {result['status']}")
                print(f"Branch:     {result['target']['branchName']}")
                print(f"URL:        {result['target']['url']}")
                
                if result['target'].get('prUrl'):
                    print(f"PR URL:     {result['target']['prUrl']}")
                
                print(f"\nMonitor:    curl -u {args.api_key}: https://api.cursor.com/v0/agents/{result['id']}")
            
            return result
            
    except HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"Error: HTTP {e.code}")
        print(f"Response: {error_body}")
        sys.exit(1)
    except URLError as e:
        print(f"Error: Failed to connect: {e.reason}")
        sys.exit(1)


def main():
    args = parse_args()
    launch_agent(args)


if __name__ == "__main__":
    main()
