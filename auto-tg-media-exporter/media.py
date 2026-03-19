"""
Media-type detection, filtering, and datetime resolution for Telegram messages.

Optional dependencies (graceful fallback if missing):
    pip install Pillow          # EXIF datetime from photos
    pip install hachoir         # creation_date from video containers
"""

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from telethon.tl.types import (
    InputMessagesFilterDocument,
    InputMessagesFilterPhotoVideo,
    InputMessagesFilterRoundVideo,
    MessageMediaWebPage,
    PeerChannel,
)

# ── Optional deps ─────────────────────────────────────────────────────────────

try:
    from PIL import Image
    from PIL.ExifTags import TAGS as _EXIF_TAGS
    _PILLOW = True
except ImportError:
    _PILLOW = False

try:
    import hachoir.metadata
    import hachoir.parser
    _HACHOIR = True
except ImportError:
    _HACHOIR = False

# ── Telethon iteration filters (one pass each) ────────────────────────────────
#
# Using server-side filters instead of iterating all messages:
#   • drastically cuts RAM  — only matching message objects are transferred
#   • prevents GetFileRequest timeouts — Telegram doesn't time out filtered requests
#     the same way it does on unfiltered full-history scans
#
ITER_FILTERS = [
    InputMessagesFilterPhotoVideo(),   # native photos + video files
    InputMessagesFilterRoundVideo(),   # circle / video-note messages
    InputMessagesFilterDocument(),     # documents — further filtered by MIME below
]

# ── MIME → extension map ──────────────────────────────────────────────────────

_MIME_EXT: dict[str, str] = {
    "image/jpeg":       ".jpg",
    "image/png":        ".png",
    "image/gif":        ".gif",
    "image/webp":       ".webp",
    "video/mp4":        ".mp4",
    "video/mpeg":       ".mpeg",
    "video/quicktime":  ".mov",
    "video/x-matroska": ".mkv",
    "video/webm":       ".webm",
}

# ── Date patterns (most- to least-specific) ───────────────────────────────────

_DATE_PATTERNS = [
    re.compile(r"(\d{4})[._-](\d{2})[._-](\d{2})[_T ](\d{2})[._:-](\d{2})[._:-](\d{2})"),
    re.compile(r"(\d{4})(\d{2})(\d{2})[_-](\d{2})(\d{2})(\d{2})"),
    re.compile(r"(\d{4})[._-](\d{2})[._-](\d{2})"),
]


# ═════════════════════════════════════════════════════════════════════════════
# Public API — type detection
# ═════════════════════════════════════════════════════════════════════════════

def media_type_of(msg) -> Optional[str]:
    """
    Return one of:
        'photo'       — native Telegram photo
        'video'       — video file / GIF
        'round_video' — circular video note
        'image_doc'   — image sent as a document (file)
    or None if the message carries no supported media.
    """
    if msg.photo:
        return "photo"
    if getattr(msg, "video", None):
        return "video"
    if getattr(msg, "video_note", None):
        return "round_video"
    if msg.document:
        mime = getattr(msg.document, "mime_type", "") or ""
        if mime.startswith("image/"):
            return "image_doc"
    return None


def extension_for(msg, media_type: str) -> str:
    if media_type == "photo":
        return ".jpg"
    if media_type == "round_video":
        return ".mp4"
    doc = msg.document
    for attr in getattr(doc, "attributes", []):
        fname = getattr(attr, "file_name", None)
        if fname:
            suffix = Path(fname).suffix
            if suffix:
                return suffix
    return _MIME_EXT.get(getattr(doc, "mime_type", "") or "", "")


def file_size_of(msg, media_type: str) -> Optional[int]:
    """Return the file size in bytes, or None if unavailable."""
    if media_type == "photo" and msg.photo:
        # PhotoSize variants: PhotoSize has .size, PhotoSizeProgressive has .sizes
        for s in reversed(msg.photo.sizes):
            sz = getattr(s, "size", None)
            if sz:
                return sz
            sizes = getattr(s, "sizes", None)
            if sizes:
                return sizes[-1]
        return None
    if msg.document:
        return getattr(msg.document, "size", None)
    return None


def fmt_size(n: Optional[int]) -> str:
    """Human-readable file size string, e.g. '4.2 MB'."""
    if not n:
        return "? B"
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024
    return f"{n:.1f} TB"


def original_filename(msg, media_type: str) -> str:
    if media_type in ("video", "image_doc") and msg.document:
        for attr in getattr(msg.document, "attributes", []):
            fname = getattr(attr, "file_name", None)
            if fname:
                return fname
    return ""


# ═════════════════════════════════════════════════════════════════════════════
# Public API — message-level filters
# ═════════════════════════════════════════════════════════════════════════════

def is_link_preview(msg) -> bool:
    """True when the media originates from a URL embed / web-page preview."""
    return isinstance(getattr(msg, "media", None), MessageMediaWebPage)


async def is_fwd_public_channel(msg, client, cache: dict[int, bool]) -> bool:
    """
    True when the message was forwarded from a public channel.

    Results are cached by channel ID so each channel is resolved at most once
    per chat export — no per-message API calls after the first occurrence.
    """
    fwd = getattr(msg, "fwd_from", None)
    if not fwd:
        return False
    fwd_id = getattr(fwd, "from_id", None)
    if not isinstance(fwd_id, PeerChannel):
        return False

    cid = fwd_id.channel_id
    if cid in cache:
        return cache[cid]

    try:
        entity = await client.get_entity(cid)
        is_pub = bool(getattr(entity, "username", None))
    except Exception:
        is_pub = False   # can't resolve → assume private, don't skip

    cache[cid] = is_pub
    return is_pub


# ═════════════════════════════════════════════════════════════════════════════
# Public API — datetime resolution
# ═════════════════════════════════════════════════════════════════════════════

def resolve_datetime(
        file_path:     Path,
        original_name: str,
        media_type:    str,
        msg_date:      datetime,
) -> datetime:
    """
    Priority:
        1. File metadata  — EXIF DateTimeOriginal (Pillow) or container
                            creation_date (hachoir)
        2. Original filename — common date-stamp patterns
        3. Telegram message datetime (fallback)
    """
    dt = _from_metadata(file_path, media_type)
    if dt:
        return dt
    dt = _from_filename(original_name or file_path.name)
    if dt:
        return dt
    return msg_date


# ═════════════════════════════════════════════════════════════════════════════
# Internal helpers
# ═════════════════════════════════════════════════════════════════════════════

def _from_metadata(path: Path, media_type: str) -> Optional[datetime]:
    if media_type in ("photo", "image_doc") and _PILLOW:
        return _exif_datetime(path)
    if media_type in ("video", "round_video") and _HACHOIR:
        return _hachoir_datetime(path)
    return None


def _exif_datetime(path: Path) -> Optional[datetime]:
    try:
        img  = Image.open(path)
        exif = img._getexif()
        if not exif:
            return None
        for tag_id, val in exif.items():
            if _EXIF_TAGS.get(tag_id) in (
                    "DateTimeOriginal", "DateTime", "DateTimeDigitized"
            ):
                return datetime.strptime(val, "%Y:%m:%d %H:%M:%S").replace(
                    tzinfo=timezone.utc
                )
    except Exception:
        pass
    return None


def _hachoir_datetime(path: Path) -> Optional[datetime]:
    try:
        parser = hachoir.parser.createParser(str(path))
        if not parser:
            return None
        with parser:
            meta = hachoir.metadata.extractMetadata(parser)
        if not meta:
            return None
        dt = meta.get("creation_date")
        if dt:
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        pass
    return None


def _from_filename(name: str) -> Optional[datetime]:
    stem = Path(name).stem
    for pat in _DATE_PATTERNS:
        m = pat.search(stem)
        if not m:
            continue
        groups = [int(g) for g in m.groups()]
        try:
            if len(groups) == 6:
                return datetime(*groups, tzinfo=timezone.utc)
            if len(groups) == 3:
                return datetime(*groups, tzinfo=timezone.utc)
        except ValueError:
            continue
    return None