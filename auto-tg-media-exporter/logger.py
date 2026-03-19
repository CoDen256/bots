import logging
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler


def setup_logging(log_path: Path, console: Console) -> logging.Logger:
    logger = logging.getLogger("tgexport")
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))

    ch = RichHandler(
        console=console,
        rich_tracebacks=True,
        show_path=False,
        markup=True,
        log_time_format="%H:%M:%S",
    )
    ch.setLevel(logging.INFO)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger