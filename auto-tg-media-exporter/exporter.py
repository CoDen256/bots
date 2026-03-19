import asyncio
import logging
import re
import signal
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from telethon import TelegramClient
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.rule import Rule
from rich.table import Table

try:
    import cryptg  # noqa: F401 — just checking presence
    _CRYPTG = True
except ImportError:
    _CRYPTG = False

from state import StateManager
from media import (
    ITER_FILTERS,
    extension_for,
    file_size_of,
    fmt_size,
    is_fwd_public_channel,
    is_link_preview,
    media_type_of,
    original_filename,
    resolve_datetime,
)

_SAFE_RE = re.compile(r"[^\w\- ]")


def _safe_name(name: str, limit: int = 28) -> str:
    return _SAFE_RE.sub("_", name)[:limit].strip("_ ")


class ChatExporter:
    """Downloads supported media from a single chat, updating state after each file."""

    def __init__(
            self,
            client:   TelegramClient,
            target:   Path,
            state:    StateManager,
            progress: Progress,
            log:      logging.Logger,
    ) -> None:
        self._client   = client
        self._target   = target
        self._state    = state
        self._progress = progress
        self._log      = log

    async def count_total(
            self,
            entity,
            iter_end: Optional[datetime],
    ) -> int:
        """
        Fetch the server-side message count for every filter in one round-trip each.
        Used to pre-populate the progress-bar total. Approximate for documents
        (server count includes all doc types; we filter to images only locally).
        """
        total = 0
        for f in ITER_FILTERS:
            try:
                result = await self._client.get_messages(
                    entity, filter=f, limit=1, offset_date=iter_end
                )
                total += result.total
            except Exception:
                pass   # count is best-effort
        return total

    async def run(
            self,
            chat_cfg:     dict,
            start:        Optional[datetime],
            end:          Optional[datetime],
            chat_task,
            overall_task,
            stop:         asyncio.Event,
    ) -> tuple[int, int, int]:
        """Return (saved, skipped, errors)."""
        cid   = str(chat_cfg["id"])
        cname = chat_cfg["name"]
        done  = self._state.downloaded_ids(cid)
        saved = skipped = errs = filtered = 0

        # Cache for public-channel resolution: channel_id → is_public
        pub_channel_cache: dict[int, bool] = {}

        try:
            entity = await self._client.get_entity(int(cid))
        except Exception as exc:
            self._log.error(f"[{cname}] Cannot resolve entity: {exc}")
            return 0, 0, 1

        iter_end = (end + timedelta(days=1)) if end else None

        # ── Set approximate total on progress tasks ────────────────────────
        total = await self.count_total(entity, iter_end)
        already_done = len(done)
        self._progress.update(chat_task,    total=total)
        self._progress.update(overall_task, total=(
                (self._progress.tasks[overall_task].total or 0) + total
        ))
        self._log.info(
            f"Chat '{cname}': starting  "
            f"(server total≈{total}, already downloaded: {already_done})"
        )

        # ── Multi-pass: one Telethon filter per media category ─────────────
        #
        # Why not iter_messages(filter=None)?
        #   • Pulling ALL messages consumes O(n_messages) RAM — every message
        #     object is allocated even if it carries no media.
        #   • Unfiltered full-history scans trigger GetFileRequest timeouts on
        #     large chats because Telegram rate-limits the file-location lookups
        #     that Telethon issues internally during iteration.
        #   • Server-side filters let Telegram pre-index and stream only the
        #     relevant subset, keeping both RAM and round-trips low.
        #
        seen_in_pass: set[str] = set()   # de-duplicate across filter passes

        for tg_filter in ITER_FILTERS:
            if stop.is_set():
                break

            async for msg in self._client.iter_messages(
                    entity,
                    filter=tg_filter,
                    offset_date=iter_end,
                    reverse=False,
            ):
                if stop.is_set():
                    break
                if start and msg.date < start:
                    break

                mid = str(msg.id)

                # ── Skip duplicates between filter passes ──────────────────
                # Do NOT advance progress — the dupe was already counted in
                # the pass that first saw it.
                if mid in seen_in_pass:
                    continue
                seen_in_pass.add(mid)

                # ── Local filters — advance + count, but don't download ────
                # The server-side total includes these messages, so we must
                # advance to keep completed in sync with total.
                def _advance_filtered(reason: str) -> None:
                    nonlocal filtered
                    filtered += 1
                    self._progress.advance(overall_task)
                    self._progress.advance(chat_task)
                    self._log.debug(f"[{cname}] Filtered ({reason}): msg {mid}")

                if is_link_preview(msg):
                    _advance_filtered("link preview")
                    continue
                if await is_fwd_public_channel(msg, self._client, pub_channel_cache):
                    _advance_filtered("fwd public channel")
                    continue

                mtype = media_type_of(msg)
                if not mtype:
                    _advance_filtered("unsupported type")
                    continue

                # ── Already downloaded ─────────────────────────────────────
                if mid in done:
                    skipped += 1
                    self._progress.advance(overall_task)
                    self._progress.advance(chat_task)
                    continue

                ext       = extension_for(msg, mtype)
                orig_name = original_filename(msg, mtype)
                tmp_path  = self._target / f"_tmp_{mid}{ext}"

                display_name = (orig_name or f"msg_{mid}{ext}")[:34]
                display_size = fmt_size(file_size_of(msg, mtype))
                self._progress.update(
                    chat_task,
                    current_file=f"{display_name}  ({display_size})",
                )

                try:
                    await self._client.download_media(msg, file=tmp_path)

                    self._log.debug(f"Downloaded [{mtype}]: {tmp_path}")
                    msg_utc = msg.date.astimezone(timezone.utc)
                    # resolve_datetime does file I/O (EXIF/hachoir) — run in a
                    # thread so it doesn't block the asyncio event loop and
                    # stall other pending network operations mid-download.
                    dt = await asyncio.to_thread(
                        resolve_datetime, tmp_path, orig_name, mtype, msg_utc
                    )

                    dest_dir = self._target / f"{dt.year}" / f"{dt.month:02d}"
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    fpath = dest_dir / (
                        f"{_safe_name(cname)}"
                        f"_{dt.strftime('%Y%m%d_%H%M%S')}"
                        f"_{mid}{ext}"
                    )
                    tmp_path.rename(fpath)

                    self._state.mark_downloaded(cid, cname, mid)
                    done.add(mid)
                    saved += 1
                    self._log.debug(f"Saved [{mtype}]: {fpath}")

                except Exception as exc:
                    errs += 1
                    self._log.error(f"[{cname}] Download failed (msg {mid}): {exc}")
                    if tmp_path.exists():
                        tmp_path.unlink(missing_ok=True)

                finally:
                    self._progress.update(chat_task, current_file="")

                self._progress.advance(overall_task)
                self._progress.advance(chat_task)

        self._log.info(
            f"Chat '{cname}': done  saved={saved}  "
            f"skipped={skipped}  filtered={filtered}  errors={errs}"
        )
        return saved, skipped, errs


class ExportOrchestrator:
    """Coordinates the full export run across all configured chats."""

    def __init__(
            self,
            client:  TelegramClient,
            target:  Path,
            state:   StateManager,
            console: Console,
            log:     logging.Logger,
    ) -> None:
        self._client  = client
        self._target  = target
        self._state   = state
        self._console = console
        self._log     = log

    async def run(self, cfg: dict) -> None:
        dr    = cfg.get("date_range", {})
        start = datetime.fromisoformat(dr["start"]) if dr.get("start") else None
        end   = datetime.fromisoformat(dr["end"])   if dr.get("end")   else None
        chats = cfg["chats"]

        stop = asyncio.Event()
        self._setup_interrupt(stop)
        self._print_header(chats, start, end)

        total_saved = total_skipped = total_errs = 0

        with Progress(
                SpinnerColumn(spinner_name="dots2"),
                TextColumn("[bold]{task.description:<42}"),
                BarColumn(bar_width=28, complete_style="cyan", finished_style="green"),
                TextColumn("[cyan]{task.completed}[/cyan][dim]/[/dim][white]{task.total}[/white] [dim]files[/dim]"),
                TextColumn("[dim]|[/dim]"),
                TimeElapsedColumn(),
                TextColumn("[dim]{task.fields[current_file]}[/dim]"),
                console=self._console,
                refresh_per_second=8,
                transient=False,
        ) as prog:
            # total=None until count_total() fills it in per-chat
            overall_task = prog.add_task("[bold cyan]Total progress", total=None, current_file="")
            exporter = ChatExporter(
                self._client, self._target, self._state, prog, self._log
            )

            for chat_cfg in chats:
                if stop.is_set():
                    break

                label     = chat_cfg["name"][:40]
                chat_task = prog.add_task(f"[white]{label}", total=None, current_file="")

                saved, skipped, errs = await exporter.run(
                    chat_cfg, start, end, chat_task, overall_task, stop
                )
                total_saved   += saved
                total_skipped += skipped
                total_errs    += errs

                status = "[green]✓[/green]" if errs == 0 else "[yellow]⚠[/yellow]"
                prog.update(chat_task, description=f"{status} [dim]{label}[/dim]")

        self._print_summary(stop.is_set(), total_saved, total_skipped, total_errs)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _setup_interrupt(self, stop: asyncio.Event) -> None:
        loop = asyncio.get_running_loop()

        def _on_sigint(*_):
            self._console.print(
                "\n  [yellow]⚡  Interrupt received — finishing current download…"
                "[/yellow]"
            )
            stop.set()

        try:
            loop.add_signal_handler(signal.SIGINT, _on_sigint)
        except (NotImplementedError, AttributeError):
            signal.signal(signal.SIGINT, _on_sigint)

    def _print_header(
            self,
            chats: list[dict],
            start: Optional[datetime],
            end:   Optional[datetime],
    ) -> None:
        self._console.print()
        if not _CRYPTG:
            self._console.print(
                "  [yellow]⚡  cryptg not installed — downloads may be slow.\n"
                "     Run: [bold]pip install cryptg[/bold]  for native AES decryption.[/yellow]\n"
            )
        self._console.print(
            Rule("[bold cyan]Export Starting[/bold cyan]", style="cyan")
        )
        self._console.print()

        range_str = (
            f"{start.date() if start else '∞'}  →  {end.date() if end else '∞'}"
        )
        already = self._state.already_downloaded_count(chats)

        tbl = Table(box=box.SIMPLE, padding=(0, 1), show_header=False, expand=False)
        tbl.add_column(style="dim", width=14)
        tbl.add_column(style="bold white")
        tbl.add_row("Date range",   range_str)
        tbl.add_row("Chats",        str(len(chats)))
        tbl.add_row("Destination",  str(self._target))
        tbl.add_row("Media types",  "photos · videos · round videos · image files")
        tbl.add_row("Skipping",     "link previews · forwards from public channels")
        tbl.add_row("Already done", f"{already} files (will be skipped)")
        self._console.print(tbl)
        self._console.print()

    def _print_summary(
            self,
            interrupted:   bool,
            total_saved:   int,
            total_skipped: int,
            total_errs:    int,
    ) -> None:
        self._console.print()

        if interrupted:
            self._console.print(Panel(
                "[yellow bold]Export paused — progress has been saved.[/yellow bold]\n\n"
                f"  [dim]Saved so far:[/dim] [bold white]{total_saved}[/bold white] files\n\n"
                "[dim]Run the script again with the same arguments to resume "
                "from where you left off.[/dim]",
                border_style="yellow", padding=(1, 2),
            ))
            self._log.warning(
                f"Export paused. saved={total_saved}, "
                f"skipped={total_skipped}, errors={total_errs}"
            )
        else:
            self._console.print(Panel(
                "[green bold]✓  Export complete![/green bold]\n\n"
                f"  Saved     [bold]{total_saved}[/bold] new files\n"
                f"  Skipped   [bold]{total_skipped}[/bold] (already downloaded)\n"
                f"  Errors    [bold]{total_errs}[/bold]\n\n"
                f"  [dim]Location: {self._target}[/dim]",
                border_style="green", padding=(1, 2),
            ))
            self._log.info(
                f"Export complete. saved={total_saved}, "
                f"skipped={total_skipped}, errors={total_errs}"
            )