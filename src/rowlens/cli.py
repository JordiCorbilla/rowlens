from __future__ import annotations

import argparse
from pathlib import Path
from time import perf_counter

from rowlens.render import print_report, render_report
from rowlens.search import SearchConfig, search_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rowlens",
        description="Stream a CSV file, find exact row matches, and print the result as a readable CLI report.",
    )
    parser.add_argument("--file", required=True, dest="file_path", help="CSV file to search.")
    parser.add_argument(
        "--keyword",
        action="append",
        default=[],
        help="Exact cell value to match. Repeat the flag to require multiple values.",
    )
    parser.add_argument(
        "--filter",
        action="append",
        default=[],
        help="Substring that must appear in the row. Repeat the flag to require multiple filters.",
    )
    parser.add_argument("--delimiter", default=",", help="CSV delimiter. Defaults to ','.")
    parser.add_argument("--encoding", default="utf-8-sig", help="File encoding. Defaults to utf-8-sig.")
    parser.add_argument("--ignore-case", action="store_true", help="Case-insensitive matching.")
    parser.add_argument("--max-results", type=int, default=None, help="Stop after this many matches.")
    parser.add_argument("--output", default=None, help="Optional text file to write the rendered report to.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    file_path = Path(args.file_path)
    if not file_path.is_file():
        parser.error(f"File not found: {file_path}")

    if args.max_results is not None and args.max_results <= 0:
        parser.error("--max-results must be greater than zero.")

    if not args.keyword and not args.filter:
        parser.error("Provide at least one --keyword or --filter value.")

    started_at = perf_counter()
    config = SearchConfig(
        file_path=file_path,
        keywords=tuple(args.keyword),
        filters=tuple(args.filter),
        delimiter=args.delimiter,
        encoding=args.encoding,
        ignore_case=args.ignore_case,
        max_results=args.max_results,
    )
    summary, matches = search_csv(config)

    output_path = Path(args.output) if args.output else None
    bundle = render_report(summary, matches, config, started_at, output_path)
    print_report(bundle)

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(bundle.text, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
