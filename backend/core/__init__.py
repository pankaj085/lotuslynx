# backend/core/__init__.py

# Expose main configuration
from .config import settings

# Expose authentication utilities
from .auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_tokens,
    get_current_user,
    get_current_active_user,
    validate_token,
    Token,
    TokenData
)

# Optional: Explicit exports control
__all__ = [
    'settings',
    'get_password_hash',
    'verify_password',
    'create_access_token',
    'create_refresh_token',
    'create_tokens',
    'get_current_user',
    'get_current_active_user',
    'validate_token',
    'Token',
    'TokenData'
]