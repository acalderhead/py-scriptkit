"""
Purpose
───────
    Optional Azure helpers (seam; fill in as scripts need them). azure-identity
    is imported lazily inside the helpers, so importing this module never
    requires the Azure SDK to be installed.

Public API
──────────
    get_credential : Return a DefaultAzureCredential (lazily imported)

Usage
─────
    from scriptkit.azure import get_credential

Notes
─────
    Conventions for scripts that build on these helpers:
    - Auth    : azure-identity `DefaultAzureCredential` (never hardcode keys).
    - Secrets : Azure Key Vault; never pass secrets as CLI args (they leak into
                process lists, shell history, and CI logs) — prefer env vars.
    - Retries : rely on the Azure SDK's built-in retry policy, or `tenacity`
                for your own network calls.
"""

from __future__ import annotations

from typing import Any

__all__ = ["get_credential"]


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def get_credential(**kwargs: Any):
    """
    Return a ``DefaultAzureCredential`` (lazily importing azure-identity).

    kwargs : Passed straight through to ``DefaultAzureCredential``.

    Raises ImportError with an actionable message if azure-identity is missing.
    """
    try:
        from azure.identity import DefaultAzureCredential  # pyright: ignore[reportMissingImports]
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise ImportError(
            "azure-identity is not installed. Add it to your script's PEP 723 "
            "dependencies, e.g. \"azure-identity>=1.16\"."
        ) from exc
    return DefaultAzureCredential(**kwargs)
