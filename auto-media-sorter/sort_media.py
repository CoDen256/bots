#!/usr/bin/env python3
"""
sort_media.py — Recursively sorts photos/videos into target/{year}/{month} folders.

Usage:
    python sort_media.py <source_dir> <target_dir>

Features:
    - Extracts year/month from filenames using multiple patterns
    - Falls back to EXIF data if available (requires Pillow)
    - Copies files (never moves originals)
    - Skips already-copied files (size + mtime check) to allow resuming
    - Live progress bar showing bytes processed / total
    - Logs all activity to both console and a logfile in the target directory
"""

import os
import re
import sys
import shutil
import hashlib
import logging
from pathlib import Path
from datetime import datetime

# Optional EXIF support
try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MEDIA_EXTENSIONS = {
    # Images
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif",
    ".webp", ".heic", ".heif", ".raw", ".cr2", ".nef", ".arw",
    ".dng", ".orf", ".rw2", ".pef", ".srw",
    # Videos
    ".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm",
    ".m4v", ".3gp", ".3g2", ".mts", ".m2ts", ".ts", ".vob",
    ".mpg", ".mpeg", ".divx", ".xvid",
}

DATE_PATTERNS = [
    re.compile(r"(?<!\d)(?P<year>20\d{2})[-_]?(?P<month>0[1-9]|1[0-2])[-_]?\d{2}(?!\d)"),
    re.compile(r"[A-Za-z_-]*(?P<year>20\d{2})(?P<month>0[1-9]|1[0-2])\d{2}"),
    re.compile(r"(?P<year>20\d{2})-(?P<month>0[1-9]|1[0-2])-\d{2}"),
    re.compile(r"(?<!\d)(?P<year>20\d{2})(?!\d)"),
]

# ---------------------------------------------------------------------------
# Progress bar
# ---------------------------------------------------------------------------

def fmt_bytes(n: int) -> str:
    """Human-readable byte size."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


class Progress:
    """
    Sticky single-line progress bar printed to stderr.

    Each time a log line is about to be printed to stdout, call
    clear() first, then let the line print, then call redraw().
    This keeps the bar visually "pinned" below all log output.

    Example bar:
      [████████████░░░░░░░░]  62.3%  4.2 GB / 6.7 GB  (312 / 500 files)
    """
    BAR_WIDTH = 20

    def __init__(self, total_bytes: int, total_files: int):
        self.total_bytes = total_bytes
        self.total_files = total_files
        self.done_bytes = 0
        self.done_files = 0
        self._drawn = False          # is the bar currently on screen?
        self._bar_len = 0

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def update(self, file_bytes: int):
        """Call after each file is processed (copied or skipped)."""
        self.done_bytes += file_bytes
        self.done_files += 1
        self.redraw()

    def clear(self):
        """Erase the bar line so a log line can be printed cleanly above it."""
        if self._drawn:
            sys.stderr.write(f"\r{' ' * self._bar_len}\r")
            sys.stderr.flush()
            self._drawn = False

    def redraw(self):
        """(Re)print the bar at the current position."""
        pct = self.done_bytes / self.total_bytes if self.total_bytes else 1.0
        filled = int(self.BAR_WIDTH * pct)
        bar = "█" * filled + "░" * (self.BAR_WIDTH - filled)
        line = (
            f"[{bar}] {pct * 100:5.1f}%  "
            f"{fmt_bytes(self.done_bytes)} / {fmt_bytes(self.total_bytes)}  "
            f"({self.done_files} / {self.total_files} files)"
        )
        self._bar_len = len(line)
        sys.stderr.write(f"\r{line}")
        sys.stderr.flush()
        self._drawn = True

    def finish(self):
        """Print the completed bar and move to a new line."""
        self.redraw()
        sys.stderr.write("\n")
        sys.stderr.flush()
        self._drawn = False


# ---------------------------------------------------------------------------
# Logging setup — handler that clears/redraws the bar around each log line
# ---------------------------------------------------------------------------

class ProgressAwareHandler(logging.StreamHandler):
    """
    StreamHandler that clears the progress bar before emitting a log record
    and redraws it immediately after, so log lines scroll normally above the
    bar without stomping on it.
    """
    def __init__(self, stream, progress: Progress):
        super().__init__(stream)
        self.progress = progress

    def emit(self, record):
        self.progress.clear()
        super().emit(record)
        self.progress.redraw()


def setup_logging(target_dir: Path, progress: Progress) -> logging.Logger:
    log_path = target_dir / "sort_media.log"
    logger = logging.getLogger("sort_media")
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")

    # File handler — full DEBUG log, append mode for resume support
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    # Console handler — INFO and above, clears/redraws bar around each line
    ch = ProgressAwareHandler(sys.stdout, progress)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


# ---------------------------------------------------------------------------
# Date extraction
# ---------------------------------------------------------------------------

def extract_date_from_name(filename: str):
    stem = Path(filename).stem
    for pattern in DATE_PATTERNS:
        m = pattern.search(stem)
        if m:
            year = m.group("year")
            month = m.groupdict().get("month")
            return year, month
    return None, None


def extract_date_from_exif(filepath: Path):
    if not PILLOW_AVAILABLE:
        return None, None
    try:
        img = Image.open(filepath)
        exif_data = img._getexif()
        if not exif_data:
            return None, None
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag in ("DateTimeOriginal", "DateTime", "DateTimeDigitized"):
                dt = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                return str(dt.year), f"{dt.month:02d}"
    except Exception:
        pass
    return None, None


def get_date(filepath: Path):
    year, month = extract_date_from_name(filepath.name)
    if year:
        return year, month
    if filepath.suffix.lower() in {".jpg", ".jpeg", ".tiff", ".tif", ".heic"}:
        year, month = extract_date_from_exif(filepath)
        if year:
            return year, month
    return None, None


# ---------------------------------------------------------------------------
# Resume: fast size + mtime check (copy2 preserves mtime)
# ---------------------------------------------------------------------------

def file_checksum(path: Path, chunk=65536) -> str:
    """MD5 of file contents — used to skip identical already-copied files."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            data = f.read(chunk)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


def already_copied(src: Path, dst: Path) -> bool:
    if not dst.exists():
        return False
    if dst.stat().st_size != src.stat().st_size:
        return False
    # Full checksum only when sizes match
    return file_checksum(src) == file_checksum(dst)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def destination_path(target_dir: Path, year, month, filename: str) -> Path:
    if year is None:
        folder = target_dir / "unknown"
    elif month is None:
        folder = target_dir / year / "unknown_month"
    else:
        folder = target_dir / year / month
    return folder / filename


def resolve_conflict(dst: Path) -> Path:
    if not dst.exists():
        return dst
    stem, suffix, parent = dst.stem, dst.suffix, dst.parent
    counter = 2
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def process_directory(source_dir: Path, target_dir: Path, logger: logging.Logger,
                      progress: Progress):
    stats = {"copied": 0, "skipped": 0, "errors": 0,
             "bytes_copied": 0, "bytes_skipped": 0}

    progress.clear()
    print("Scanning source directory…", flush=True)
    all_files = sorted(
        p for p in source_dir.rglob("*")
        if p.is_file()
    )
    total_files = len(all_files)
    total_bytes = sum(p.stat().st_size for p in all_files)

    # Patch progress totals now that we know them
    progress.total_bytes = total_bytes
    progress.total_files = total_files

    logger.info("=" * 70)
    logger.info(f"Run started  —  source: {source_dir}  |  target: {target_dir}")
    logger.info(f"Found {total_files} media file(s)  ({fmt_bytes(total_bytes)} total)")
    if not PILLOW_AVAILABLE:
        logger.warning("Pillow not installed — EXIF fallback disabled. "
                       "Install with: pip install Pillow")
    logger.info("=" * 70)

    for src in all_files:
        rel = src.relative_to(source_dir)
        file_size = src.stat().st_size

        try:
            year, month = get_date(src)
            dst = destination_path(target_dir, year, month, src.name)

            if already_copied(src, dst):
                logger.info(f"  SKIP  {rel}  ->  {dst.relative_to(target_dir)}")
                stats["skipped"] += 1
                stats["bytes_skipped"] += file_size
                progress.update(file_size)
                continue

            dst = resolve_conflict(dst)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

            label = (f"{year}/{month}" if year and month
                     else f"{year}/unknown_month" if year
                     else "unknown")
            logger.info(f"  COPIED  {rel}  ->  {label}/{dst.name}")
            stats["copied"] += 1
            stats["bytes_copied"] += file_size

        except Exception as exc:
            logger.error(f"  ERROR  {rel}: {exc}", exc_info=True)
            stats["errors"] += 1

        progress.update(file_size)

    progress.finish()

    summary = (
        f"\nDone.\n"
        f"  Copied  : {stats['copied']} files  ({fmt_bytes(stats['bytes_copied'])})\n"
        f"  Skipped : {stats['skipped']} files  ({fmt_bytes(stats['bytes_skipped'])})  [already done]\n"
        f"  Errors  : {stats['errors']} files\n"
    )
    print(summary)
    logger.info(summary.strip())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 3:
        print(__doc__)
        print("Usage: python sort_media.py <source_dir> <target_dir>")
        sys.exit(1)

    source_dir = Path(sys.argv[1]).resolve()
    target_dir = Path(sys.argv[2]).resolve()

    if not source_dir.exists() or not source_dir.is_dir():
        print(f"ERROR: Source directory does not exist: {source_dir}")
        sys.exit(1)

    target_dir.mkdir(parents=True, exist_ok=True)

    # Progress is created with placeholder totals; process_directory fills them in
    # after scanning. It must exist before setup_logging so the console handler
    # can reference it.
    progress = Progress(total_bytes=1, total_files=0)
    logger = setup_logging(target_dir, progress)
    process_directory(source_dir, target_dir, logger, progress)


if __name__ == "__main__":
    main()