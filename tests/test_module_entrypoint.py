import subprocess
import sys
from pathlib import Path


def write_csv(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8", newline="")


def test_python_module_entrypoint_runs_cli(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.csv"
    output_path = tmp_path / "results.txt"
    write_csv(
        file_path,
        "id,status,notes\n"
        "1213131,AAA,needle\n"
        "9,BBB,hay\n",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rowlens",
            "--file",
            str(file_path),
            "--keyword",
            "1213131",
            "--filter",
            "AAA",
            "--output",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "rowlens v1.0.1" in result.stdout
    assert "row 2" in result.stdout
    assert "1213131" in output_path.read_text(encoding="utf-8")
