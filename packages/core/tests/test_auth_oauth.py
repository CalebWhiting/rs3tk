"""Test auth/oauth.py module — PKCE and CSRF state generation."""

from __future__ import annotations

import base64
import hashlib

from rs3tk_core.auth.oauth import generate_pkce_pair, generate_state


class TestGeneratePkcePair:
    def test_returns_tuple_of_two_strings(self) -> None:
        verifier, challenge = generate_pkce_pair()
        assert isinstance(verifier, str)
        assert isinstance(challenge, str)

    def test_verifier_has_expected_length(self) -> None:
        # secrets.token_urlsafe(32) yields 43 base64url characters
        verifier, _ = generate_pkce_pair()
        assert len(verifier) == 43

    def test_challenge_is_sha256_of_verifier_base64url_no_pad(self) -> None:
        verifier, challenge = generate_pkce_pair()
        digest = hashlib.sha256(verifier.encode("ascii")).digest()
        expected = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
        assert challenge == expected

    def test_challenge_has_no_padding(self) -> None:
        _, challenge = generate_pkce_pair()
        assert "=" not in challenge

    def test_challenge_uses_urlsafe_alphabet(self) -> None:
        # urlsafe base64 swaps '+' -> '-' and '/' -> '_'
        _, challenge = generate_pkce_pair()
        assert "+" not in challenge
        assert "/" not in challenge

    def test_returns_unique_pairs(self) -> None:
        seen_verifiers = set()
        for _ in range(10):
            verifier, _ = generate_pkce_pair()
            assert verifier not in seen_verifiers
            seen_verifiers.add(verifier)


class TestGenerateState:
    def test_returns_non_empty_string(self) -> None:
        state = generate_state()
        assert isinstance(state, str)
        assert len(state) > 0

    def test_returns_unique_values(self) -> None:
        states = {generate_state() for _ in range(10)}
        assert len(states) == 10

    def test_uses_urlsafe_alphabet(self) -> None:
        state = generate_state()
        assert "+" not in state
        assert "/" not in state
