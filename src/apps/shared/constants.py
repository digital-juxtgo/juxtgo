# ============================================================
# Pagination
# ============================================================
PAGE_SIZE = 20
PAGE_SIZE_LARGE = 50

# ============================================================
# Token Lifetimes (in minutes)
# ============================================================
ACCESS_TOKEN_LIFETIME = 15
REFRESH_TOKEN_LIFETIME = 7 * 24 * 60  # 7 days

# ============================================================
# File Upload Limits
# ============================================================
MAX_AVATAR_SIZE_MB = 2

# ============================================================
# Default Roles (used by seed command)
# ============================================================
DEFAULT_ROLES = [
    {"name": "admin", "display_name": "Admin", "description": "Full access"},
    {"name": "manager", "display_name": "Manager", "description": "Manage users"},
    {"name": "support", "display_name": "Support", "description": "Customer support"},
]

# ============================================================
# Organization Roles
# ============================================================
ORG_ROLE_OWNER = "owner"
ORG_ROLE_ADMIN = "admin"
ORG_ROLE_MEMBER = "member"
