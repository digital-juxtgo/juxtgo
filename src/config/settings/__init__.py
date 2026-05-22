"""
Settings loader based on DJANGO_ENV environment variable.
"""

import os
from split_settings.tools import include, optional

ENV = os.getenv("DJANGO_ENV", "development")

include(
    "base.py",
    optional(f"{ENV}.py"),
)