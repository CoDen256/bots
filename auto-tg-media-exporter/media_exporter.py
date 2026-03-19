"""
tg_photo_export — entry point.

Usage:
    python -m tg_photo_export <target_folder>
    python -m tg_photo_export <target_folder> --config path/to/config.json

Requirements:
    pip install telethon rich
"""

import asyncio
import sys
from typing import Optional

from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.rule import Rule
from telethon import TelegramClient, errors

from auth     import Authenticator, CredentialsManager
from cli      import parse_args, print_banner
from config   import ConfigManager
from dialogs  import DialogBrowser
from exporter import ExportOrchestrator
from logger   import setup_logging
from state    import StateManager
from cli import VERSION

# ── File-name constants ───────────────────────────────────────────────────────
SESSION_FILE = "me"
CONFIG_FILE  = "export_config.json"
STATE_FILE   = "export_state.json"
LOG_FILE     = "export.log"
CREDS_FILE   = ".tg_creds.json"


async def main() -> None:
    args   = parse_args()
    target = args.target.resolve()
    target.mkdir(parents=True, exist_ok=True)

    config_path = (args.config or target / CONFIG_FILE).resolve()
    log_path    = (target / LOG_FILE).resolve()
    creds_path  = (target / CREDS_FILE).resolve()
    state_path  = (target / STATE_FILE).resolve()
    session_str = str(target / SESSION_FILE)

    console = Console()
    log     = setup_logging(log_path, console)

    print_banner(console)
    log.info(f"tg-media-exporter v{VERSION}")
    log.info(f"Target: {target}")
    log.info(f"Log:    {log_path}")

    # ── Credentials & connection ──────────────────────────────────────────────
    creds_mgr         = CredentialsManager(creds_path, console)
    api_id, api_hash  = creds_mgr.load_or_prompt()

    client = TelegramClient(session_str, api_id, api_hash)
    await client.connect()

    # ── Authentication ────────────────────────────────────────────────────────
    try:
        await Authenticator(client, console, log).ensure_authenticated()
    except errors.FloodWaitError as exc:
        console.print(f"[red]Rate limited — try again in {exc.seconds}s.[/red]")
        log.error(f"FloodWaitError during auth: {exc.seconds}s")
        await client.disconnect()
        return
    except Exception as exc:
        console.print(f"[red]Authentication failed: {exc}[/red]")
        log.exception("Authentication failed")
        await client.disconnect()
        return

    # ── Export config ─────────────────────────────────────────────────────────
    console.print()
    config_mgr = ConfigManager(config_path, console)
    cfg: Optional[dict] = None

    if config_mgr.exists():
        console.print(
            f"  [green]✓[/green] Found config: [bold]{config_path.name}[/bold]"
        )
        existing = config_mgr.load()
        config_mgr.show_summary(existing)
        console.print()

        action = Prompt.ask(
            "  [cyan]What would you like to do?[/cyan]\n"
            "    [dim][U][/dim] Use this config\n"
            "    [dim][E][/dim] Create a new config (replaces existing)\n"
            "  ❯ ",
            choices=["u", "U", "e", "E"],
            default="u",
            show_choices=False,
        ).lower()

        if action == "u":
            cfg = existing
            log.info(f"Using config: {config_path}")

    if cfg is None:
        console.print()
        console.print(Rule("[bold]Chat Selection[/bold]", style="blue"))
        console.print()

        browser    = DialogBrowser(client, console, log)
        all_items  = await browser.fetch_and_display()

        if not all_items:
            console.print("[red]No chats found.[/red]")
            await client.disconnect()
            return

        console.print()
        chosen = browser.prompt_selection(all_items)

        console.print()
        start, end = config_mgr.prompt_date_range()

        cfg = config_mgr.build(chosen, start, end)
        config_mgr.save(cfg)
        log.info(f"Config created: {config_path}  chats={len(cfg['chats'])}")

    # ── Confirm & run ─────────────────────────────────────────────────────────
    console.print()
    if not Confirm.ask("  [cyan]Start export now?[/cyan]", default=True):
        console.print("  [yellow]Export cancelled.[/yellow]")
        log.info("Export cancelled by user.")
        await client.disconnect()
        return

    state        = StateManager(state_path)
    orchestrator = ExportOrchestrator(client, target, state, console, log)
    await orchestrator.run(cfg)

    await client.disconnect()
    log.info("Session disconnected. Exiting.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        Console().print("\n[yellow]Aborted.[/yellow]")
        sys.exit(0)