from pathlib import Path

from rowlens.search import SearchConfig, search_csv


def write_csv(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8", newline="")


def test_search_csv_matches_keywords_and_filters(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.csv"
    write_csv(
        file_path,
        "id,status,notes\n"
        "1,AAA,alpha marker\n"
        "1213131,AAA,exact target\n"
        "1213131,BBB,wrong filter\n",
    )

    summary, matches = search_csv(
        SearchConfig(
            file_path=file_path,
            keywords=("1213131",),
            filters=("AAA", "target"),
        )
    )

    assert summary.total_rows_scanned == 3
    assert summary.matched_rows == 1
    assert matches[0].row_number == 3
    assert matches[0].values["status"] == "AAA"


def test_search_csv_supports_ignore_case_and_extra_cells(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.csv"
    write_csv(
        file_path,
        "id,status\n"
        "10,Closed,EXTRA\n",
    )

    summary, matches = search_csv(
        SearchConfig(
            file_path=file_path,
            keywords=("closed",),
            filters=("extra",),
            ignore_case=True,
        )
    )

    assert summary.matched_rows == 1
    assert matches[0].values["extra_column_3"] == "EXTRA"


def test_search_csv_honors_max_results(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.csv"
    write_csv(
        file_path,
        "id,status\n"
        "1,AAA\n"
        "2,AAA\n"
        "3,AAA\n",
    )

    summary, matches = search_csv(
        SearchConfig(
            file_path=file_path,
            filters=("AAA",),
            max_results=2,
        )
    )

    assert summary.total_rows_scanned == 2
    assert summary.matched_rows == 2
    assert [match.row_number for match in matches] == [2, 3]
