import json
import logging
import os
from pathlib import Path

from telethon import TelegramClient, errors
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt


class CredentialsManager:
    """Loads or interactively prompts for Telegram API credentials, then persists them."""

    def __init__(self, creds_path: Path, console: Console) -> None:
        self._path    = creds_path
        self._console = console

    def load_or_prompt(self) -> tuple[int, str]:
        if self._path.exists():
            with open(self._path, encoding="utf-8") as f:
                data = json.load(f)
            self._console.print(
                f"  [green]✓[/green] Loaded API credentials from "
                f"[dim]{self._path.name}[/dim]"
            )
            return int(data["api_id"]), data["api_hash"]

        self._console.print(Panel(
            "[bold]Telegram API Credentials[/bold]\n"
            "[dim]Get yours at [link=https://my.telegram.org]my.telegram.org[/link]  "
            "→  API Development Tools  →  Create app[/dim]",
            border_style="blue", padding=(0, 2),
        ))
        api_id   = int(Prompt.ask("  [cyan]API ID[/cyan]"))
        api_hash =     Prompt.ask("  [cyan]API Hash[/cyan]")

        self._save(api_id, api_hash)
        self._console.print(
            f"  [green]✓[/green] Credentials saved to [dim]{self._path.name}[/dim]"
        )
        return api_id, api_hash

    def _save(self, api_id: int, api_hash: str) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump({"api_id": api_id, "api_hash": api_hash}, f)
        try:
            os.chmod(self._path, 0o600)
        except OSError:
            pass


class Authenticator:
    """Handles Telegram sign-in, reusing an existing session when available."""

    def __init__(self, client: TelegramClient, console: Console, log: logging.Logger) -> None:
        self._client  = client
        self._console = console
        self._log     = log

    async def ensure_authenticated(self) -> None:
        if await self._client.is_user_authorized():
            me = await self._client.get_me()
            self._console.print(
                f"  [green]✓[/green] Already signed in as [bold]{me.first_name}[/bold] "
                f"([dim]+{me.phone}[/dim])"
            )
            self._log.info(f"Reusing session: {me.first_name} (+{me.phone})")
            return

        self._console.print()
        self._console.print(Panel(
            "[bold]Sign in to Telegram[/bold]\n"
            "[dim]Credentials are only used to authenticate locally.\n"
            "The session token is stored in the target folder.[/dim]",
            border_style="blue", padding=(0, 2),
        ))

        phone = Prompt.ask(
            "  [cyan]Phone number[/cyan] [dim](e.g. +49 123 456 789)[/dim]"
        ).replace(" ", "")

        await self._client.send_code_request(phone)
        self._console.print("  [green]✓[/green] One-time code sent.")

        otp = Prompt.ask("  [cyan]OTP code[/cyan]")

        try:
            await self._client.sign_in(phone, otp)
        except errors.SessionPasswordNeededError:
            pwd = Prompt.ask("  [cyan]2FA password[/cyan]", password=True)
            await self._client.sign_in(password=pwd)

        me = await self._client.get_me()
        self._console.print(f"  [green]✓[/green] Signed in as [bold]{me.first_name}[/bold]")
        self._log.info(f"Authenticated as {me.first_name} (+{me.phone})")