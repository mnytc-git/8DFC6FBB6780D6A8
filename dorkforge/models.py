"""Data models used by DorkForge."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar


SUPPORTED_ENGINES = frozenset(
    {
        "google",
        "duckduckgo",
    }
)

SUPPORTED_TARGET_TYPES = frozenset(
    {
        "general",
        "person",
        "username",
        "organization",
        "company",
        "domain",
        "document",
        "academic",
        "developer",
        "product",
    }
)

SUPPORTED_RISK_LEVELS = frozenset(
    {
        "public",
        "restricted",
        "rejected",
    }
)


@dataclass(frozen=True, slots=True)
class Template:
    """Represent one query template from the local database."""

    REQUIRED_FIELDS: ClassVar[frozenset[str]] = frozenset(
        {
            "id",
            "category",
            "target_types",
            "engines",
            "template",
        }
    )

    id: str
    category: str
    target_types: tuple[str, ...]
    engines: tuple[str, ...]
    template: str
    risk: str = "public"
    quality: int = 50
    source: str = "builtin"
    tags: tuple[str, ...] = field(default_factory=tuple)
    description: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Template":
        """Create a validated template object from a dictionary."""

        if not isinstance(data, dict):
            raise TypeError("template entry must be a dictionary")

        missing = cls.REQUIRED_FIELDS.difference(data)

        if missing:
            missing_text = ", ".join(sorted(missing))
            raise ValueError(
                f"template entry is missing fields: {missing_text}"
            )

        template_id = _required_string(data["id"], "id")
        category = _required_string(
            data["category"],
            "category",
        )
        template_text = _required_string(
            data["template"],
            "template",
        )

        target_types = _string_tuple(
            data["target_types"],
            "target_types",
        )
        engines = _string_tuple(
            data["engines"],
            "engines",
        )
        tags = _string_tuple(
            data.get("tags", []),
            "tags",
            allow_empty=True,
        )

        risk = _required_string(
            data.get("risk", "public"),
            "risk",
        ).lower()

        source = _required_string(
            data.get("source", "builtin"),
            "source",
        )

        description_value = data.get("description", "")

        if not isinstance(description_value, str):
            raise TypeError(
                "description must be a string"
            )

        quality_value = data.get("quality", 50)

        if isinstance(quality_value, bool):
            raise TypeError(
                "quality must be an integer"
            )

        try:
            quality = int(quality_value)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                "quality must be an integer"
            ) from exc

        template = cls(
            id=template_id,
            category=category.lower(),
            target_types=tuple(
                item.lower()
                for item in target_types
            ),
            engines=tuple(
                item.lower()
                for item in engines
            ),
            template=template_text,
            risk=risk,
            quality=quality,
            source=source,
            tags=tuple(
                item.lower()
                for item in tags
            ),
            description=description_value.strip(),
        )

        template.validate()
        return template

    def validate(self) -> None:
        """Validate this template and raise ValueError on failure."""

        if "{{target}}" not in self.template:
            raise ValueError(
                f"template {self.id!r} does not contain "
                "{{target}}"
            )

        invalid_target_types = (
            set(self.target_types)
            .difference(SUPPORTED_TARGET_TYPES)
        )

        if invalid_target_types:
            invalid_text = ", ".join(
                sorted(invalid_target_types)
            )
            raise ValueError(
                f"template {self.id!r} has unsupported "
                f"target types: {invalid_text}"
            )

        invalid_engines = (
            set(self.engines)
            .difference(SUPPORTED_ENGINES)
        )

        if invalid_engines:
            invalid_text = ", ".join(
                sorted(invalid_engines)
            )
            raise ValueError(
                f"template {self.id!r} has unsupported "
                f"engines: {invalid_text}"
            )

        if self.risk not in SUPPORTED_RISK_LEVELS:
            raise ValueError(
                f"template {self.id!r} has unsupported "
                f"risk level: {self.risk}"
            )

        if not 0 <= self.quality <= 100:
            raise ValueError(
                f"template {self.id!r} quality must be "
                "between 0 and 100"
            )

    def supports_engine(self, engine: str) -> bool:
        """Return whether the template supports an engine."""

        normalized_engine = engine.strip().lower()

        if normalized_engine == "both":
            return bool(self.engines)

        return normalized_engine in self.engines

    def supports_target_type(
        self,
        target_type: str,
    ) -> bool:
        """Return whether the template supports a target type."""

        normalized_type = target_type.strip().lower()

        return (
            "general" in self.target_types
            or normalized_type in self.target_types
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert this model into a JSON-compatible dictionary."""

        return {
            "id": self.id,
            "category": self.category,
            "target_types": list(self.target_types),
            "engines": list(self.engines),
            "template": self.template,
            "risk": self.risk,
            "quality": self.quality,
            "source": self.source,
            "tags": list(self.tags),
            "description": self.description,
        }


@dataclass(frozen=True, slots=True)
class GeneratedQuery:
    """Represent one rendered query."""

    query: str
    template_id: str
    category: str
    engines: tuple[str, ...]
    quality: int

    def to_dict(self) -> dict[str, Any]:
        """Convert the generated query to a dictionary."""

        return {
            "query": self.query,
            "template_id": self.template_id,
            "category": self.category,
            "engines": list(self.engines),
            "quality": self.quality,
        }


def _required_string(
    value: Any,
    field_name: str,
) -> str:
    """Validate and normalize a required string."""

    if not isinstance(value, str):
        raise TypeError(
            f"{field_name} must be a string"
        )

    normalized = value.strip()

    if not normalized:
        raise ValueError(
            f"{field_name} must not be empty"
        )

    return normalized


def _string_tuple(
    value: Any,
    field_name: str,
    *,
    allow_empty: bool = False,
) -> tuple[str, ...]:
    """Convert a string list or tuple into a normalized tuple."""

    if not isinstance(value, (list, tuple)):
        raise TypeError(
            f"{field_name} must be a list or tuple"
        )

    result: list[str] = []

    for item in value:
        normalized = _required_string(
            item,
            field_name,
        )

        if normalized not in result:
            result.append(normalized)

    if not result and not allow_empty:
        raise ValueError(
            f"{field_name} must not be empty"
        )

    return tuple(result)