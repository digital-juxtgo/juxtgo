"""
Environment configuration loader for JuxtGo OS.

Purpose:
- Centralize environment variable access
- Avoid hardcoding secrets
- Support Docker + local dev

Future:
- Replace with django-environ if needed
"""

import os


def get_env(key: str, default=None, required: bool = False):
    value = os.getenv(key, default)
    if required and value is None:
        raise Exception(f"Missing required environment variable: {key}")
    return value