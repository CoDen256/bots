#!/usr/bin/env python3
"""
Sports Court Booking Telegram Bot
Commands: /book  — start the booking flow
"""
import logging
from datetime import date, timedelta

import requests
import telebot
import yaml
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
with open("config.yaml", "r", encoding="utf-8") as _f:
    _cfg = yaml.safe_load(_f)

BOT_TOKEN      = _cfg["bot_token"]
API_BASE_URL   = _cfg["api_base_url"].rstrip("/")
EMAIL_TEMPLATE = _cfg["email_template"]
SPORTS_CFG     = _cfg["sports"]

# ── Constants ─────────────────────────────────────────────────────────────────
# 45-minute slots starting at 08:15, stopping before 23:00
# → 08:15, 09:00, 09:45 … 22:30   (20 slots total, 3 pages of 7)
def _gen_slots(start_h: int = 8, start_m: int = 15,
               interval: int = 45, end_h: int = 23) -> list[str]:
    slots, t = [], start_h * 60 + start_m
    while t < end_h * 60:
        slots.append(f"{t // 60:02d}{t % 60:02d}")
        t += interval
    return slots

ALL_SLOTS      = _gen_slots()   # ["0815", "0900", "0945", …, "2230"]
SLOTS_PER_PAGE = 7              # 3 pages: 7 + 7 + 6
DATES_PER_PAGE = 7

SPORT_EMOJI = {"badminton": "🏸", "squash": "🎾"}

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")


# ── API helpers ───────────────────────────────────────────────────────────────

def fetch_booked(sport: str, start_date: str) -> list:
    """
    Call the facility API and return the raw list of *booked* slot objects
    for the given sport and week starting at start_date (YYYY-MM-DD).
    """
    cfg      = SPORTS_CFG[sport]
    court_qs = "&".join(f"courts[]={c}" for c in cfg["courts"])
    url = (
        f"{API_BASE_URL}/widget/api/slot"
        f"?facilityId={cfg['facility_id']}"
        f"&sport={sport}"
        f"&startDate={start_date}"
        f"&{court_qs}"
    )
    log.info("GET %s", url)
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json().get("slots", [])


def build_availability(sport: str, start_date: str) -> dict:
    """
    Build a nested dict  {date_iso: {time_str: set_of_free_court_ids}}
    covering DATES_PER_PAGE days from start_date.
    A time slot appears only when at least one court is still free.
    """
    all_courts = set(SPORTS_CFG[sport]["courts"])

    # booked[date][time] = {court_ids that are already taken}
    booked: dict = {}
    for slot in fetch_booked(sport, start_date):
        d, t, c = slot["date"], slot["start"], slot["court"]
        booked.setdefault(d, {}).setdefault(t, set()).add(c)

    start  = date.fromisoformat(start_date)
    result = {}
    for i in range(DATES_PER_PAGE):
        day_iso = (start + timedelta(days=i)).isoformat()
        result[day_iso] = {}
        for t in ALL_SLOTS:
            free = all_courts - booked.get(day_iso, {}).get(t, set())
            if free:
                result[day_iso][t] = free   # only store if ≥ 1 court available

    return result


# ── Formatting helpers ────────────────────────────────────────────────────────

def fmt_time(t: str) -> str:
    """'1200' → '12:00'"""
    return f"{t[:2]}:{t[2:]}"


def fmt_date(d: str) -> str:
    """'2026-04-29' → 'Wed 29 Apr'"""
    return date.fromisoformat(d).strftime("%a %d %b")


def date_to_key(d: str) -> str:
    """'2026-04-29' → '20260429'  (safe for callback_data)"""
    return d.replace("-", "")


def key_to_date(k: str) -> str:
    """'20260429' → '2026-04-29'"""
    return f"{k[:4]}-{k[4:6]}-{k[6:]}"


def page_start(page: int) -> str:
    """ISO date string for the first day of a given 7-day page (0-indexed)."""
    return (date.today() + timedelta(days=page * DATES_PER_PAGE)).isoformat()


# ── Keyboards & messages ──────────────────────────────────────────────────────

def kb_sports() -> InlineKeyboardMarkup:
    m = InlineKeyboardMarkup()
    m.row(
        InlineKeyboardButton("🏸 Badminton", callback_data="sport|badminton"),
        InlineKeyboardButton("🎾 Squash",    callback_data="sport|squash"),
    )
    return m


def kb_dates(sport: str, page: int):
    """Keyboard listing each date for the 7-day window with available-slot counts."""
    start = page_start(page)
    avail = build_availability(sport, start)
    emoji = SPORT_EMOJI[sport]

    m = InlineKeyboardMarkup()
    for d, slots in avail.items():
        n     = len(slots)
        label = f"{fmt_date(d)}  ·  {n} slot{'s' if n != 1 else ''}"
        m.row(InlineKeyboardButton(
            label,
            callback_data=f"date|{sport}|{date_to_key(d)}|{page}",
        ))

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀ Prev week", callback_data=f"dates|{sport}|{page - 1}"))
    nav.append(InlineKeyboardButton("Next week ▶", callback_data=f"dates|{sport}|{page + 1}"))
    m.row(*nav)
    m.row(InlineKeyboardButton("« Back to sports", callback_data="back_sport"))

    text = f"{emoji} *{sport.capitalize()}* — pick a date (week {page + 1}):"
    return m, text


def kb_slots(sport: str, date_key: str, dates_page: int, slot_page: int):
    """Keyboard with one row per hour in the current page; free = ✅, booked = 🔴."""
    d     = key_to_date(date_key)
    avail = build_availability(sport, d)   # API covers d … d+6
    day   = avail.get(d, {})
    emoji = SPORT_EMOJI[sport]

    m     = InlineKeyboardMarkup()
    chunk = ALL_SLOTS[slot_page * SLOTS_PER_PAGE: (slot_page + 1) * SLOTS_PER_PAGE]

    for t in chunk:
        if t in day:
            court = min(day[t])            # pick lowest court id as default
            m.row(InlineKeyboardButton(
                f"✅ {fmt_time(t)}",
                callback_data=f"time|{sport}|{date_key}|{t}|{court}|{dates_page}",
            ))
        else:
            m.row(InlineKeyboardButton(
                f"🔴 {fmt_time(t)} — occupied",
                callback_data="noop",
            ))

    # Slot pagination row
    nav = []
    if slot_page > 0:
        nav.append(InlineKeyboardButton(
            "◀", callback_data=f"slotpg|{sport}|{date_key}|{dates_page}|{slot_page - 1}",
        ))
    if (slot_page + 1) * SLOTS_PER_PAGE < len(ALL_SLOTS):
        nav.append(InlineKeyboardButton(
            "▶", callback_data=f"slotpg|{sport}|{date_key}|{dates_page}|{slot_page + 1}",
        ))
    if nav:
        m.row(*nav)

    m.row(InlineKeyboardButton("« Back to dates", callback_data=f"dates|{sport}|{dates_page}"))

    free_count = len(day)
    text = (
        f"{emoji} *{sport.capitalize()}* — {fmt_date(d)}\n"
        f"{free_count} available slot(s). Pick a time:"
    )
    return m, text


def kb_time(sport: str, date_key: str, t: str, court: str, dates_page: str):
    """Confirmation card with Preview and Back buttons."""
    d     = key_to_date(date_key)
    emoji = SPORT_EMOJI[sport]

    m = InlineKeyboardMarkup()
    m.row(
        InlineKeyboardButton(
            "📧 Preview email",
            callback_data=f"preview|{sport}|{date_key}|{t}|{court}",
        ),
        InlineKeyboardButton(
            "« Back",
            callback_data=f"date|{sport}|{date_key}|{dates_page}",
        ),
    )
    text = (
        f"{emoji} *Booking details*\n\n"
        f"🏟 Sport  ›  *{sport.capitalize()}*\n"
        f"📅 Date   ›  *{fmt_date(d)}*\n"
        f"🕐 Time   ›  *{fmt_time(t)}*\n"
        f"🎯 Court  ›  *#{court}*"
    )
    return m, text


def build_email(sport: str, date_key: str, t: str, court: str) -> str:
    """Render the email template from config."""
    d = key_to_date(date_key)
    return EMAIL_TEMPLATE.format(
        sport    = sport.capitalize(),
        date     = fmt_date(d),
        date_iso = d,
        time     = fmt_time(t),
        court    = court,
    )


# ── Bot handlers ──────────────────────────────────────────────────────────────

def _edit(call, text: str, kb: InlineKeyboardMarkup) -> None:
    """Helper: edit the current message in-place."""
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=kb,
    )


@bot.message_handler(commands=["start", "book"])
def cmd_book(msg):
    bot.send_message(msg.chat.id, "🏅 *Select a sport to book a court:*",
                     reply_markup=kb_sports())


@bot.callback_query_handler(func=lambda c: True)
def on_callback(call):
    data = call.data

    try:
        # ── Tapped an occupied slot (no-op) ─────────────────────────────
        if data == "noop":
            bot.answer_callback_query(call.id, "⛔ This slot is fully booked.")
            return

        # ── Delete the preview message ───────────────────────────────────
        elif data == "delete":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return

        # ── Back to sport selection ──────────────────────────────────────
        elif data == "back_sport":
            _edit(call, "🏅 *Select a sport to book a court:*", kb_sports())

        # ── Sport chosen → show date list (page 0) ───────────────────────
        elif data.startswith("sport|"):
            _, sport = data.split("|", 1)
            kb, text = kb_dates(sport, 0)
            _edit(call, text, kb)

        # ── Navigate between date pages ──────────────────────────────────
        elif data.startswith("dates|"):
            _, sport, page = data.split("|")
            kb, text = kb_dates(sport, int(page))
            _edit(call, text, kb)

        # ── Date chosen → show time slots (slot page 0) ──────────────────
        elif data.startswith("date|"):
            _, sport, date_key, dates_page = data.split("|")
            kb, text = kb_slots(sport, date_key, int(dates_page), 0)
            _edit(call, text, kb)

        # ── Navigate between slot pages ──────────────────────────────────
        elif data.startswith("slotpg|"):
            _, sport, date_key, dates_page, slot_page = data.split("|")
            kb, text = kb_slots(sport, date_key, int(dates_page), int(slot_page))
            _edit(call, text, kb)

        # ── Time slot chosen → show booking card ─────────────────────────
        elif data.startswith("time|"):
            _, sport, date_key, t, court, dates_page = data.split("|")
            kb, text = kb_time(sport, date_key, t, court, dates_page)
            _edit(call, text, kb)

        # ── Preview → send email text as a new message ───────────────────
        elif data.startswith("preview|"):
            _, sport, date_key, t, court = data.split("|")
            email_body = build_email(sport, date_key, t, court)

            del_kb = InlineKeyboardMarkup()
            del_kb.row(InlineKeyboardButton("🗑 Delete this message", callback_data="delete"))

            bot.send_message(
                call.message.chat.id,
                f"📧 *Copy and send this email:*\n\n```\n{email_body}\n```",
                parse_mode="Markdown",
                reply_markup=del_kb,
            )

    except Exception as exc:
        log.exception("Error handling callback %r: %s", data, exc)
        bot.answer_callback_query(call.id, "❌ Something went wrong — please try again.")
        return

    bot.answer_callback_query(call.id)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log.info("Bot is running — press Ctrl+C to stop.")
    bot.infinity_polling(timeout=30, long_polling_timeout=20)