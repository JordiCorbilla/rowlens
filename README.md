# rowlens

`rowlens` is a streaming CSV search CLI for very large files. It scans row by row, keeps memory usage flat, and prints matches in a readable terminal report with column names beside each value.

## Why it exists

When a CSV is 17 GB, the usual "open it in a spreadsheet" workflow is already dead. `rowlens` is built for the needle-in-a-haystack case:

- Match one or more exact cell values with repeated `--keyword`
- Require one or more substring filters with repeated `--filter`
- Stream the file without loading it into memory
- Print each matching row in a bordered, columnar CLI layout
- Optionally save the same report to a text file with `--output`

## Install

```bash
poetry install
```

## Usage

```bash
poetry run rowlens --file "data.csv" --keyword "1213131" --filter "AAA"
```

```bash
poetry run rowlens \
  --file "huge.csv" \
  --keyword "1213131" \
  --keyword "YYYY" \
  --filter "AAA" \
  --filter "needle" \
  --ignore-case \
  --max-results 5 \
  --output "output/results.txt"
```

## Matching rules

- Every `--keyword` must match a full cell value in the row.
- Every `--filter` must appear as a substring in at least one cell in the row.
- A row is returned only if it satisfies all supplied criteria.
- Reported row numbers are CSV record numbers, so the header is row `1` and the first data row is row `2`.

## Options

```text
--file         CSV file to search
--keyword      Exact cell value to match; repeatable
--filter       Substring to require; repeatable
--delimiter    CSV delimiter, default ","
--encoding     File encoding, default "utf-8-sig"
--ignore-case  Case-insensitive matching
--max-results  Stop after N matches
--output       Write the rendered report to a text file
```

## Packaging

The project uses Poetry and exposes a console script named `rowlens`, so it is ready to publish to PyPI after you set the final author metadata and repository URLs in `pyproject.toml`.

## Tests

```bash
poetry run pytest
```
