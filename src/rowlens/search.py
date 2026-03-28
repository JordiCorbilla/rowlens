from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


@dataclass(frozen=True)
class MatchResult:
    row_number: int
    values: dict[str, str]


@dataclass(frozen=True)
class SearchConfig:
    file_path: Path
    keywords: tuple[str, ...] = ()
    filters: tuple[str, ...] = ()
    delimiter: str = ","
    encoding: str = "utf-8-sig"
    ignore_case: bool = False
    max_results: int | None = None


@dataclass(frozen=True)
class SearchSummary:
    file_path: Path
    total_rows_scanned: int
    matched_rows: int


def search_csv(config: SearchConfig) -> tuple[SearchSummary, list[MatchResult]]:
    matches: list[MatchResult] = []
    total_rows_scanned = 0
    _maximize_field_size_limit()

    with config.file_path.open("r", encoding=config.encoding, errors="replace", newline="") as handle:
        reader = csv.reader(handle, delimiter=config.delimiter)

        try:
            header = next(reader)
        except StopIteration as exc:
            raise ValueError("CSV file is empty.") from exc

        normalized_header = [column or f"column_{index}" for index, column in enumerate(header, start=1)]
        normalized_keywords = tuple(_normalize(value, config.ignore_case) for value in config.keywords)
        normalized_filters = tuple(_normalize(value, config.ignore_case) for value in config.filters)

        for record_index, row in enumerate(reader, start=2):
            total_rows_scanned += 1
            normalized_row = [_normalize(value, config.ignore_case) for value in row]

            if _row_matches(normalized_row, normalized_keywords, normalized_filters):
                matches.append(
                    MatchResult(
                        row_number=record_index,
                        values=_pair_columns(normalized_header, row),
                    )
                )

                if config.max_results is not None and len(matches) >= config.max_results:
                    break

    summary = SearchSummary(
        file_path=config.file_path,
        total_rows_scanned=total_rows_scanned,
        matched_rows=len(matches),
    )
    return summary, matches


def _pair_columns(header: Sequence[str], row: Sequence[str]) -> dict[str, str]:
    paired: dict[str, str] = {}

    for index, column_name in enumerate(header):
        paired[column_name] = row[index] if index < len(row) else ""

    if len(row) > len(header):
        for index in range(len(header), len(row)):
            paired[f"extra_column_{index + 1}"] = row[index]

    return paired


def _row_matches(
    row: Sequence[str],
    keywords: Iterable[str],
    filters: Iterable[str],
) -> bool:
    return _matches_exact_keywords(row, keywords) and _matches_filters(row, filters)


def _matches_exact_keywords(row: Sequence[str], keywords: Iterable[str]) -> bool:
    return all(any(cell == keyword for cell in row) for keyword in keywords)


def _matches_filters(row: Sequence[str], filters: Iterable[str]) -> bool:
    return all(any(filter_value in cell for cell in row) for filter_value in filters)


def _normalize(value: str, ignore_case: bool) -> str:
    return value.casefold() if ignore_case else value


def _maximize_field_size_limit() -> None:
    limit = sys.maxsize

    while True:
        try:
            csv.field_size_limit(limit)
            return
        except OverflowError:
            limit //= 10
