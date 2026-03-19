import argparse
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

VERSION = "1.0.0"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="tg_photo_export",
        description="Export & organise photos from Telegram chats by year/month.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m tg_photo_export ~/Photos/Telegram\n"
            "  python -m tg_photo_export ~/Photos/Telegram --config my_export.json\n"
        ),
    )
    p.add_argument(
        "target", type=Path,
        help="Destination folder — photos saved as <target>/YYYY/MM/",
    )
    p.add_argument(
        "--config", "-c", type=Path, default=None,
        help="Export config file (default: <target>/export_config.json)",
    )
    return p.parse_args()


def print_banner(console: Console) -> None:
    console.print()
    console.print(Panel.fit(
        Text.assemble(
            ("📷  Telegram Photo Exporter", "bold cyan"),
            ("  ", ""),
            (f"v{VERSION}", "dim"),
            ("\n", ""),
            ("Export photos from Telegram chats, organised by year / month", "dim"),
        ),
        border_style="cyan",
        padding=(1, 6),
    ))
    console.print()