import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table


def _parse_date(s: str) -> Optional[datetime]:
    if not s.strip():
        return None
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s.strip(), fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date '{s}' — use YYYY-MM-DD or DD.MM.YYYY")


class ConfigManager:
    """Builds, persists, loads, and displays the export configuration."""

    def __init__(self, config_path: Path, console: Console) -> None:
        self._path    = config_path
        self._console = console

    # ── I/O ──────────────────────────────────────────────────────────────────

    def exists(self) -> bool:
        return self._path.exists()

    def load(self) -> dict:
        with open(self._path, encoding="utf-8") as f:
            return json.load(f)

    def save(self, cfg: dict) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        self._console.print(
            f"  [green]✓[/green] Config saved → [bold]{self._path}[/bold]"
        )

    def build(
            self,
            chosen: list[dict],
            start:  Optional[datetime],
            end:    Optional[datetime],
    ) -> dict:
        return {
            "version":    1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "date_range": {
                "start": start.isoformat() if start else None,
                "end":   end.isoformat()   if end   else None,
            },
            "chats": [
                {
                    "id":       c["dialog"].entity.id,
                    "name":     c["dialog"].name or "(unnamed)",
                    "category": c["category"],
                    "username": getattr(c["dialog"].entity, "username", None),
                }
                for c in chosen
            ],
        }

    # ── Display ───────────────────────────────────────────────────────────────

    def show_summary(self, cfg: dict) -> None:
        dr    = cfg.get("date_range", {})
        start = dr.get("start") or "∞"
        end   = dr.get("end")   or "∞"

        tbl = Table(box=box.SIMPLE, padding=(0, 1), show_header=False, expand=False)
        tbl.add_column(style="dim", width=12)
        tbl.add_column(style="bold white")
        tbl.add_row("Date range", f"{start}  →  {end}")
        tbl.add_row("Chats",      str(len(cfg["chats"])))
        self._console.print(tbl)

        for c in cfg["chats"]:
            handle = f"@{c['username']}" if c.get("username") else str(c["id"])
            self._console.print(f"    [dim]·[/dim] {c['name']}  [dim]{handle}[/dim]")

    # ── Prompt ────────────────────────────────────────────────────────────────

    def prompt_date_range(self) -> tuple[Optional[datetime], Optional[datetime]]:
        self._console.print(Panel(
            "[bold]Set Date Range[/bold]\n"
            "[dim]Accepted formats: [cyan]YYYY-MM-DD[/cyan]  or  [cyan]DD.MM.YYYY[/cyan]\n"
            "Leave blank for no limit (export all photos).[/dim]",
            border_style="blue", padding=(0, 2),
        ))

        while True:
            try:
                start = _parse_date(
                    Prompt.ask(
                        "  [cyan]Start date[/cyan] [dim](blank = no limit)[/dim]",
                        default="",
                    )
                )
                end = _parse_date(
                    Prompt.ask(
                        "  [cyan]End date  [/cyan] [dim](blank = no limit)[/dim]",
                        default="",
                    )
                )
            except ValueError as exc:
                self._console.print(f"  [red]{exc}[/red]")
                continue

            if start and end and start > end:
                self._console.print(
                    "  [red]Start date must be before end date.[/red]"
                )
                continue

            return start, end