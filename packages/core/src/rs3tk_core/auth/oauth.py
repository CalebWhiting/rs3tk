"""OAuth2 PKCE flow for Jagex authentication."""

# OAuth2 is an authorization framework that lets third-party apps obtain
# limited access to a user's account without exposing passwords.  The
# client redirects the user to the authorization server, which authenticates
# the user and returns an authorization code.  The client then exchanges
# this code for tokens (access, refresh, ID) by calling the token endpoint.
#
# PKCE (Proof Key for Code Exchange) adds a code_verifier / code_challenge
# pair to prevent authorization code interception attacks.  The client
# generates a random verifier, derives a challenge (SHA-256 + base64url),
# sends only the challenge in the auth request, and later proves possession
# of the verifier when exchanging the code for tokens.

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
