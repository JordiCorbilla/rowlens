from pathlib import Path

from rowlens.cli import main


def write_csv(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8", newline="")


def test_cli_writes_output_report(tmp_path: Path, capsys) -> None:
    file_path = tmp_path / "sample.csv"
    output_path = tmp_path / "results.txt"
    write_csv(
        file_path,
        "id,status,notes\n"
        "1213131,AAA,needle\n"
        "9,BBB,hay\n",
    )

    exit_code = main(
        [
            "--file",
            str(file_path),
            "--keyword",
            "1213131",
            "--filter",
            "AAA",
            "--output",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()
    report_text = output_path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert "rowlens v1.0.0" in captured.out
    assert "row 2" in captured.out
    assert "1213131" in report_text
    assert str(output_path) in report_text
