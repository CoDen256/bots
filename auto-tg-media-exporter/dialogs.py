import logging

from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, User
from rich import box
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table


# (icon, label, colour)
CATEGORIES: dict[str, tuple[str, str, str]] = {
    "bot":             ("🤖", "Bots",             "red"),
    "private":         ("💬", "Private Chats",    "green"),
    "group":           ("👥", "Groups",           "yellow"),
    "pub_group":    ("🌐", "Public Groups",    "blue"),
    "priv_channel": ("🔒", "Private Channels", "magenta"),
    "pub_channel":  ("📢", "Public Channels",  "cyan"),
}


def _categorise(dialog) -> str:
    e = dialog.entity
    if isinstance(e, User):
        return "bot" if e.bot else "private"
    if isinstance(e, Chat):
        return "group"
    if isinstance(e, Channel):
        has_username = bool(getattr(e, "username", None))
        if e.megagroup:
            return "pub_group" if has_username else "group"
        return "pub_channel" if has_username else "priv_channel"
    return "group"


def _parse_selection(raw: str, max_idx: int) -> set[int]:
    """Convert '1, 3-5, 7' → {1, 3, 4, 5, 7}."""
    result: set[int] = set()
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            result.update(range(int(a), int(b) + 1))
        else:
            result.add(int(part))
    return {i for i in result if 1 <= i <= max_idx}


class DialogBrowser:
    """Fetches dialogs from Telegram, displays them in categorised tables,
    and lets the user interactively select which chats to export."""

    def __init__(
            self,
            client:  TelegramClient,
            console: Console,
            log:     logging.Logger,
    ) -> None:
        self._client  = client
        self._console = console
        self._log     = log

    async def fetch_and_display(self) -> list[dict]:
        """Return a flat indexed list of all dialogs after printing the tables."""
        with self._console.status("[cyan]Fetching your chats…[/cyan]", spinner="dots"):
            dialogs = await self._client.get_dialogs(limit=None)
        self._log.info(f"Fetched {len(dialogs)} dialogs")

        buckets: dict[str, list] = {k: [] for k in CATEGORIES}
        for d in dialogs:
            cat = _categorise(d)
            if cat in buckets:
                buckets[cat].append(d)

        all_items: list[dict] = []
        idx = 1

        for cat, (icon, label, colour) in CATEGORIES.items():
            items = buckets[cat]
            if not items:
                continue

            tbl = Table(
                title=f"{icon}  {label}",
                title_style=f"bold {colour}",
                header_style=f"bold {colour}",
                border_style=colour,
                box=box.SIMPLE_HEAVY,
                padding=(0, 1),
                show_lines=False,
                expand=False,
            )
            tbl.add_column("#",           style="dim",        width=5,   justify="right")
            tbl.add_column("Name",        style="bold white", min_width=24)
            tbl.add_column("Handle / ID", style="dim",        min_width=18)
            tbl.add_column("Category",    style=colour,       width=14)

            for d in items:
                e      = d.entity
                handle = (
                    f"@{e.username}" if getattr(e, "username", None)
                    else str(e.id)
                )
                tbl.add_row(str(idx), d.name or "(unnamed)", handle,
                            cat.replace("_", " "))
                all_items.append({"idx": idx, "dialog": d, "category": cat})
                idx += 1

            self._console.print(tbl)
            self._console.print()

        return all_items

    def prompt_selection(self, all_items: list[dict]) -> list[dict]:
        """Interactively ask the user which chats to export."""
        if not all_items:
            self._console.print("[red]No chats available.[/red]")
            raise SystemExit(1)

        from rich.panel import Panel
        max_idx = max(i["idx"] for i in all_items)
        self._console.print(Panel(
            "[bold]Select Chats to Export[/bold]\n"
            "[dim]Enter numbers, comma-separated or as ranges\n"
            "Examples:  [cyan]3[/cyan]   [cyan]1, 4, 7[/cyan]   [cyan]2-6[/cyan]   "
            "[cyan]1-3, 8, 12-15[/cyan][/dim]",
            border_style="blue", padding=(0, 2),
        ))

        while True:
            raw = Prompt.ask("  [cyan]Selection[/cyan]").strip()
            try:
                indices = _parse_selection(raw, max_idx)
            except ValueError:
                self._console.print(
                    "  [red]Invalid format — use numbers, commas, and dashes.[/red]"
                )
                continue

            chosen = [i for i in all_items if i["idx"] in indices]
            if not chosen:
                self._console.print("  [red]Nothing selected. Try again.[/red]")
                continue

            self._console.print(f"\n  [green]Selected {len(chosen)} chat(s):[/green]")
            for c in chosen:
                self._console.print(f"    [dim]·[/dim] {c['dialog'].name or '(unnamed)'}")

            if Confirm.ask("\n  [cyan]Confirm selection?[/cyan]", default=True):
                return chosen
            self._console.print("  [yellow]Let's try again.[/yellow]\n")