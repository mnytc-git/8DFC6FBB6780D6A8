"""Deterministic safety filters for local query templates."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .models import Template
from .normalizer import normalize_query


@dataclass(frozen=True, slots=True)
class SafetyResult:
    """Describe the result of a template safety check."""

    allowed: bool
    reasons: tuple[str, ...]


_BLOCKED_PATTERNS: tuple[
    tuple[str, re.Pattern[str]],
    ...,
] = (
    (
        "credential-discovery",
        re.compile(
            r"\b("
            r"password|passwd|credential|credentials|"
            r"api[_ -]?key|access[_ -]?token|"
            r"secret[_ -]?key|private[_ -]?key"
            r")\b",
            re.IGNORECASE,
        ),
    ),
    (
        "identity-document-discovery",
        re.compile(
            r"\b("
            r"passport|national[_ -]?id|identity[_ -]?card|"
            r"driver'?s?[_ -]?license"
            r")\b",
            re.IGNORECASE,
        ),
    ),
    (
        "financial-data-discovery",
        re.compile(
            r"\b("
            r"credit[_ -]?card|bank[_ -]?account|"
            r"cvv|cardholder|financial[_ -]?record"
            r")\b",
            re.IGNORECASE,
        ),
    ),
    (
        "private-location-discovery",
        re.compile(
            r"\b("
            r"home[_ -]?address|live[_ -]?location|"
            r"real[_ -]?time[_ -]?location"
            r")\b",
            re.IGNORECASE,
        ),
    ),
    (
        "medical-data-discovery",
        re.compile(
            r"\b("
            r"medical[_ -]?record|patient[_ -]?record|"
            r"health[_ -]?record"
            r")\b",
            re.IGNORECASE,
        ),
    ),
)


def check_template(template: Template) -> SafetyResult:
    """Check whether a template may be used by the generator."""

    reasons: list[str] = []

    if template.risk != "public":
        reasons.append(
            f"risk-level:{template.risk}"
        )

    normalized_template = normalize_query(
        template.template
    )

    searchable_text = " ".join(
        (
            normalized_template,
            template.category,
            " ".join(template.tags),
            template.description,
        )
    )

    for name, pattern in _BLOCKED_PATTERNS:
        if pattern.search(searchable_text):
            reasons.append(name)

    unique_reasons = tuple(
        dict.fromkeys(reasons)
    )

    return SafetyResult(
        allowed=not unique_reasons,
        reasons=unique_reasons,
    )


def is_template_allowed(template: Template) -> bool:
    """Return whether a template passes safety checks."""

    return check_template(template).allowed