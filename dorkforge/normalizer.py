"""Normalization utilities for DorkForge."""

from __future__ import annotations

import re
import unicodedata


_WHITESPACE_PATTERN = re.compile(r"\s+")
_CONTROL_PATTERN = re.compile(
    r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]"
)


def normalize_target(value: str) -> str:
    """Normalize a target while preserving readable Unicode."""

    if not isinstance(value, str):
        raise TypeError("target must be a string")

    normalized = unicodedata.normalize(
        "NFKC",
        value,
    )

    normalized = _CONTROL_PATTERN.sub(
        "",
        normalized,
    )

    normalized = _WHITESPACE_PATTERN.sub(
        " ",
        normalized,
    ).strip()

    if not normalized:
        raise ValueError(
            "target must not be empty"
        )

    return normalized


def normalize_query(value: str) -> str:
    """Normalize generated query whitespace."""

    if not isinstance(value, str):
        raise TypeError("query must be a string")

    normalized = unicodedata.normalize(
        "NFKC",
        value,
    )

    normalized = _CONTROL_PATTERN.sub(
        "",
        normalized,
    )

    normalized = _WHITESPACE_PATTERN.sub(
        " ",
        normalized,
    ).strip()

    return normalized


def normalize_category(value: str) -> str:
    """Normalize a category name."""

    if not isinstance(value, str):
        raise TypeError(
            "category must be a string"
        )

    normalized = normalize_query(value).lower()
    normalized = normalized.replace("_", "-")
    normalized = normalized.replace(" ", "-")

    if not normalized:
        raise ValueError(
            "category must not be empty"
        )

    return normalized


def deduplication_key(value: str) -> str:
    """Build a stable key for duplicate query detection."""

    normalized = normalize_query(value)
    return normalized.casefold()


def quote_target(value: str) -> str:
    """Return a target safe for use inside search quotes."""

    normalized = normalize_target(value)

    normalized = normalized.replace(
        "\\",
        "\\\\",
    )

    normalized = normalized.replace(
        '"',
        '\\"',
    )

    return normalized