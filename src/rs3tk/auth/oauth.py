"""OAuth2 PKCE flow for Jagex authentication."""

from __future__ import annotations

import hashlib
import secrets
from base64 import urlsafe_b64encode


def generate_pkce_pair() -> tuple[str, str]:
    """Generate a PKCE code verifier and S256 challenge.

    Returns:
        Tuple of (code_verifier, code_challenge).
    """
    code_verifier = secrets.token_urlsafe(32)
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return code_verifier, code_challenge


def generate_state() -> str:
    """Generate a random state parameter for CSRF protection."""
    return secrets.token_urlsafe(16)
