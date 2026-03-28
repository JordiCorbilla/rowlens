import csv
from pathlib import Path

from rowlens.search import SearchConfig, search_csv


def generate_large_csv(path: Path, total_rows: int, target_row_index: int) -> str:
    target_id = "needle-1213131"

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["id", "status", "category", "payload"])

        for row_index in range(1, total_rows + 1):
            if row_index == target_row_index:
                writer.writerow(
                    [
                        target_id,
                        "AAA",
                        "priority",
                        "payload with unique-target-marker embedded for lookup",
                    ]
                )
                continue

            writer.writerow(
                [
                    f"id-{row_index:07d}",
                    "AAA" if row_index % 5 == 0 else "BBB",
                    f"group-{row_index % 17}",
                    f"payload-{row_index:07d}-noise",
                ]
            )

    return target_id


def test_search_csv_streams_large_generated_file(tmp_path: Path) -> None:
    total_rows = 250_000
    target_row_index = 187_654
    file_path = tmp_path / "large.csv"
    target_id = generate_large_csv(file_path, total_rows=total_rows, target_row_index=target_row_index)

    summary, matches = search_csv(
        SearchConfig(
            file_path=file_path,
            keywords=(target_id,),
            filters=("AAA", "unique-target-marker"),
        )
    )

    assert file_path.stat().st_size > 1_000_000
    assert summary.total_rows_scanned == total_rows
    assert summary.matched_rows == 1
    assert matches[0].row_number == target_row_index + 1
    assert matches[0].values["id"] == target_id
    assert matches[0].values["status"] == "AAA"
