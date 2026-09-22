"""Command-line interface for DorkForge."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from . import __version__


DESCRIPTION = (
    "Offline query generator for Google and DuckDuckGo. "
    "DorkForge only generates text and never performs searches."
)

TARGET_TYPES = (
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
)

ENGINES = (
    "google",
    "duckduckgo",
    "both",
)


def positive_integer(value: str) -> int:
    """Return a positive integer parsed from user input."""

    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"invalid integer: {value!r}"
        ) from exc

    if number <= 0:
        raise argparse.ArgumentTypeError(
            "value must be greater than zero"
        )

    return number


def build_parser() -> argparse.ArgumentParser:
    """Build and return the main command-line parser."""

    parser = argparse.ArgumentParser(
        prog="dorkforge",
        description=DESCRIPTION,
        epilog=(
            "DorkForge does not contact search engines, "
            "open browsers, or scan targets."
        ),
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="show the installed version and exit",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        metavar="COMMAND",
    )

    generate_parser = subparsers.add_parser(
        "generate",
        help="generate search queries as text",
        description=(
            "Generate search-query text from the local "
            "template database."
        ),
    )

    generate_parser.add_argument(
        "target",
        help="target text used to fill query templates",
    )

    generate_parser.add_argument(
        "--type",
        dest="target_type",
        default="general",
        choices=TARGET_TYPES,
        help=(
            "target type used to select templates "
            "(default: general)"
        ),
    )

    generate_parser.add_argument(
        "--engine",
        choices=ENGINES,
        default="both",
        help=(
            "filter templates by search-engine "
            "compatibility"
        ),
    )

    generate_parser.add_argument(
        "--category",
        action="append",
        default=[],
        metavar="NAME",
        help=(
            "select a category; may be specified "
            "multiple times"
        ),
    )

    generate_parser.add_argument(
        "--limit",
        type=positive_integer,
        default=50,
        metavar="N",
        help=(
            "maximum number of generated queries "
            "(default: 50)"
        ),
    )

    generate_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="output format (default: text)",
    )

    generate_parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="write generated queries to a file",
    )

    subparsers.add_parser(
        "categories",
        help="list available template categories",
    )

    database_parser = subparsers.add_parser(
        "database",
        help="inspect or validate the local database",
    )

    database_subparsers = database_parser.add_subparsers(
        dest="database_command",
        title="database commands",
        metavar="COMMAND",
    )

    database_subparsers.add_parser(
        "stats",
        help="show local database statistics",
    )

    database_subparsers.add_parser(
        "validate",
        help="validate the local template database",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the DorkForge command-line application."""

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "generate":
        print(
            "The generator engine has not been enabled yet. "
            "Complete the database and engine stages first."
        )
        return 0

    if args.command == "categories":
        print(
            "The category database has not been enabled yet."
        )
        return 0

    if args.command == "database":
        if args.database_command is None:
            print(
                "Choose a database command: stats or validate."
            )
            return 0

        print(
            "The database subsystem has not been enabled yet."
        )
        return 0

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())