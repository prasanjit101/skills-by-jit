#!/usr/bin/env python3
"""
Shared configuration loader for Cursor Cloud Agents scripts.

Automatically loads a .env file from the skill root directory
(one level above this scripts/ folder) into os.environ so that
all scripts can read credentials without any extra dependencies.

Usage in any script:
    import config
    config.load_env()
    # os.environ["CURSOR_API_KEY"] is now available
"""

import os
import sys


def _find_env_file() -> str | None:
    """
    Locate the .env file.

    Search order:
    1. <skill_root>/.env   (i.e., one directory above this file)
    2. Current working directory .env (fallback)
    """
    # This file lives at: <skill_root>/scripts/config.py
    # So the skill root is one level up.
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    skill_root = os.path.dirname(scripts_dir)

    candidate = os.path.join(skill_root, ".env")
    if os.path.isfile(candidate):
        return candidate

    # Fallback: current working directory
    cwd_candidate = os.path.join(os.getcwd(), ".env")
    if os.path.isfile(cwd_candidate):
        return cwd_candidate

    return None


def _parse_env_file(path: str) -> dict[str, str]:
    """
    Parse a .env file into a dictionary.

    Supports:
    - KEY=VALUE
    - KEY="VALUE"  (double-quoted)
    - KEY='VALUE'  (single-quoted)
    - # comments (full-line or inline after a space)
    - blank lines (ignored)
    - Multiline values are NOT supported (not needed here)
    """
    pairs: dict[str, str] = {}

    with open(path, "r", encoding="utf-8") as fh:
        for lineno, raw_line in enumerate(fh, start=1):
            line = raw_line.strip()

            # Skip blank lines and full-line comments
            if not line or line.startswith("#"):
                continue

            # Must contain an = sign
            if "=" not in line:
                continue

            key, _, raw_value = line.partition("=")
            key = key.strip()

            if not key:
                continue

            # Strip inline comments (only if separated by whitespace)
            # e.g.  VALUE=abc  # comment
            value = raw_value.strip()

            # Strip surrounding quotes (matching pairs only)
            if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
                value = value[1:-1]
            else:
                # Remove inline comment that starts with ' #'
                for comment_marker in (" #", "\t#"):
                    idx = value.find(comment_marker)
                    if idx != -1:
                        value = value[:idx].strip()
                        break

            pairs[key] = value

    return pairs


def load_env(*, override: bool = False, verbose: bool = False) -> bool:
    """
    Load variables from the .env file into os.environ.

    Args:
        override: If True, existing environment variables are overwritten.
                  If False (default), existing values are preserved so that
                  shell-level exports always take precedence over .env.
        verbose:  If True, print which .env file was loaded and how many
                  variables were set.

    Returns:
        True  if a .env file was found and processed.
        False if no .env file was found (not an error — scripts still work
              via --api-key flag or a manually exported CURSOR_API_KEY).
    """
    env_path = _find_env_file()

    if env_path is None:
        if verbose:
            print(
                "config: No .env file found. "
                "Using environment variables or --api-key flag.",
                file=sys.stderr,
            )
        return False

    pairs = _parse_env_file(env_path)
    loaded = 0

    for key, value in pairs.items():
        if override or key not in os.environ:
            os.environ[key] = value
            loaded += 1

    if verbose:
        print(
            f"config: Loaded {loaded} variable(s) from {env_path}",
            file=sys.stderr,
        )

    return True


def get_api_key(args_api_key: str | None = None) -> str | None:
    """
    Resolve the Cursor API key with the following priority:

    1. Value passed directly via --api-key CLI flag  (highest)
    2. CURSOR_API_KEY in os.environ (set by shell or loaded from .env)
    3. None  (caller must handle the missing-key error)

    Call load_env() before this function to ensure the .env file
    has already been merged into os.environ.
    """
    if args_api_key:
        return args_api_key
    return os.environ.get("CURSOR_API_KEY")


# ---------------------------------------------------------------------------
# Auto-load on import
# ---------------------------------------------------------------------------
# Loading on import means every script only needs `import config` at the top —
# no explicit function call required.  The silent default (override=False,
# verbose=False) keeps things clean in normal operation.
load_env()
