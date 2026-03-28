from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from rich import box
from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from rowlens import __version__
from rowlens.search import MatchResult, SearchConfig, SearchSummary


@dataclass(frozen=True)
class RenderBundle:
    renderable: RenderableType
    text: str


def render_report(
    summary: SearchSummary,
    matches: list[MatchResult],
    config: SearchConfig,
    started_at: float,
    output_path: Path | None,
) -> RenderBundle:
    elapsed_seconds = perf_counter() - started_at
    renderable = _build_renderable(summary, matches, config, elapsed_seconds, output_path)

    text_console = Console(record=True, force_terminal=False, width=160)
    with text_console.capture() as capture:
        text_console.print(renderable)

    return RenderBundle(
        renderable=renderable,
        text=capture.get(),
    )


def print_report(bundle: RenderBundle) -> None:
    console = Console()
    console.print(bundle.renderable)


def _build_renderable(
    summary: SearchSummary,
    matches: list[MatchResult],
    config: SearchConfig,
    elapsed_seconds: float,
    output_path: Path | None,
) -> RenderableType:
    summary_table = Table.grid(padding=(0, 2))
    summary_table.add_column(style="bold cyan", no_wrap=True)
    summary_table.add_column()

    summary_table.add_row("file", str(summary.file_path))
    summary_table.add_row("keywords", _join_or_dash(config.keywords))
    summary_table.add_row("filters", _join_or_dash(config.filters))
    summary_table.add_row("delimiter", repr(config.delimiter))
    summary_table.add_row("ignore_case", "yes" if config.ignore_case else "no")
    summary_table.add_row("rows_scanned", f"{summary.total_rows_scanned:,}")
    summary_table.add_row("matched_rows", f"{summary.matched_rows:,}")
    summary_table.add_row("elapsed", f"{elapsed_seconds:.2f}s")
    if config.max_results is not None:
        summary_table.add_row("max_results", f"{config.max_results:,}")
    if output_path is not None:
        summary_table.add_row("output", str(output_path))

    sections: list[RenderableType] = [summary_table]

    if matches:
        for index, match in enumerate(matches, start=1):
            sections.append(_build_match_table(index, match))
    else:
        sections.append(Text("No matching rows found.", style="yellow"))

    return Panel(
        Group(*sections),
        title=f"rowlens v{__version__}",
        border_style="bright_blue",
        box=box.ROUNDED,
        padding=(1, 2),
    )


def _build_match_table(index: int, match: MatchResult) -> Table:
    table = Table(
        title=f"match {index}  row {match.row_number}",
        title_style="bold white",
        box=box.SIMPLE_HEAVY,
        header_style="bold magenta",
        expand=True,
    )
    table.add_column("#", justify="right", style="cyan", width=4)
    table.add_column("Column", style="bold")
    table.add_column("Value", overflow="fold")

    for row_index, (column_name, value) in enumerate(match.values.items(), start=1):
        table.add_row(str(row_index), column_name, value if value != "" else "[dim]<empty>[/dim]")

    return table


def _join_or_dash(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "-"
