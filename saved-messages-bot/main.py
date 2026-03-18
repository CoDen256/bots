"""
Telegram Notes Manager
Listens for commands you send to yourself in any chat within a configured
Telegram folder, and manages notes by moving messages between chats.

Requirements:
    pip install telethon

Commands (send from any managed chat):
    /help       — list all commands
    /chats      — list all managed chats in the folder
    #tag_name   — (as a reply) move the replied-to message to that chat
    #saved      — (as a reply) move the replied-to message back to Saved Messages
"""
import argparse
import asyncio
import configparser
import logging
import os
import re
import sys

from telethon import TelegramClient, events, utils
from telethon.errors import (
    ChannelPrivateError,
    ChatWriteForbiddenError,
    SessionPasswordNeededError,
    UserBannedInChannelError,
)
from telethon.tl.functions.channels import CreateChannelRequest
from telethon.tl.functions.messages import (
    GetDialogFiltersRequest,
    SendMessageRequest,
    UpdateDialogFilterRequest,
)
from telethon.tl.types import DialogFilter, InputReplyToMessage

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

CONTROL_CHAT = "#control"
SAVED_MESSAGES_CHAT = "#saved"
TAG_RE       = re.compile(r"^#([\w-]+)$", re.IGNORECASE)
def parse_args() -> str:
    p = argparse.ArgumentParser(description="Telegram Notes Manager")
    p.add_argument(
        "workdir",
        nargs="?",
        default=os.path.dirname(__file__),
        help="Directory containing config.ini and session file (default: cwd)",
    )
    return os.path.abspath(p.parse_args().workdir)

DIR = parse_args()

# ══════════════════════════════════════════════════════════════════════════════
#  Config
# ══════════════════════════════════════════════════════════════════════════════

class Config:
    def __init__(self, path: str = os.path.join(DIR, "config.ini")):
        if not os.path.exists(path):
            sys.exit(f"[ERROR] Config file not found: {path}")
        cfg = configparser.ConfigParser()
        cfg.read(path)
        t = cfg["telegram"]
        self.api_id      = int(t["api_id"])
        self.api_hash    = t["api_hash"]
        self.folder_name = t["folder_name"]
        raw = t.get("saved_messages_backlink", "off").strip().lower()
        if raw not in ("off", "reply", "forward"):
            sys.exit(f"[ERROR] saved_messages_backlink must be 'off', 'reply', or 'forward', got: '{raw}'")
        self.backlink = raw


# ══════════════════════════════════════════════════════════════════════════════
#  Auth
# ══════════════════════════════════════════════════════════════════════════════

class Auth:
    def __init__(self, client: TelegramClient):
        self.client = client

    async def ensure(self):
        if await self.client.is_user_authorized():
            return
        phone = input("Phone number (e.g. +49123456789): ")
        await self.client.send_code_request(phone)
        otp = input("OTP code: ")
        try:
            await self.client.sign_in(phone, otp)
        except SessionPasswordNeededError:
            await self.client.sign_in(password=input("2FA password: "))


# ══════════════════════════════════════════════════════════════════════════════
#  Folder manager
# ══════════════════════════════════════════════════════════════════════════════

class FolderManager:
    def __init__(self, client: TelegramClient, folder_name: str, me):
        self.client      = client
        self.folder_name = folder_name
        self.me          = me
        self.chats: dict = {}   # title → entity
        self.folder: DialogFilter | None = None

    async def load(self):
        result  = await self.client(GetDialogFiltersRequest())
        filters = result.filters
        self.folder = next(
            (f for f in filters
             if isinstance(f, DialogFilter)
             and f.title.text.lower() == self.folder_name.lower()),
            None,
        )
        if self.folder is None:
            names = [f.title.text for f in filters if isinstance(f, DialogFilter)]
            sys.exit(f"[ERROR] Folder '{self.folder_name}' not found.\nAvailable: {names}")

        self.chats = {"#saved": self.me}
        for peer in self.folder.include_peers:
            try:
                entity = await self.client.get_entity(peer)
                self.chats[getattr(entity, "title", "unknown")] = entity
            except Exception as exc:
                log.warning("Could not resolve peer %s: %s", peer, exc)

    def peer_ids(self) -> set:
        ids = {self.me.id}
        for entity in self.chats.values():
            try:
                ids.add(utils.get_peer_id(entity))
            except Exception:
                pass
        return ids

    async def find_or_create(self, tag: str):
        """Return entity for *tag*, creating a group and adding to folder if needed."""
        key = tag.lower()
        for name, entity in self.chats.items():
            if name.lower() == key:
                return entity

        log.info("Creating new group: %s", tag)
        result = await self.client(CreateChannelRequest(
            title=tag, about=f"Notes — {tag}", megagroup=True,
        ))
        entity = result.chats[0]
        self.chats[tag] = entity

        input_peer = await self.client.get_input_entity(entity)
        self.folder.include_peers.append(input_peer)
        await self.client(UpdateDialogFilterRequest(id=self.folder.id, filter=self.folder))
        log.info("Added '%s' to folder '%s'", tag, self.folder_name)

        await self.client.send_message(entity, f"📁 Created notes folder **{tag}**")
        return entity


# ══════════════════════════════════════════════════════════════════════════════
#  Command handler
# ══════════════════════════════════════════════════════════════════════════════

class CommandHandler:
    def __init__(self, client: TelegramClient, folder: FolderManager, backlink: bool):
        self.client   = client
        self.folder   = folder
        self.backlink = backlink

    # ── helpers ───────────────────────────────────────────────────────────────

    async def _report_error(self, text: str):
        try:
            ctrl = await self.folder.find_or_create(CONTROL_CHAT)
            await self.client.send_message(ctrl, f"⚠️ **Error**\n{text}")
        except Exception as exc:
            log.error("Could not send to %s: %s", CONTROL_CHAT, exc)

    async def _copy_message(self, msg, target):
        """Forward-preserving copy. Returns the sent message."""
        if msg.forward:
            try:
                sent = await self.client.forward_messages(target, messages=msg)
                return sent[0] if isinstance(sent, list) else sent
            except Exception as exc:
                log.warning("Forward failed, falling back to copy: %s", exc)
        if msg.media:
            return await self.client.send_file(target, file=msg.media, caption=msg.text or "")
        if msg.text:
            return await self.client.send_message(target, msg.text)
        log.warning("Message %s has no text or media — skipping.", msg.id)
        return None

    async def _send_backlink(self, sent, target):
        """Backlink to *sent* (in *target*) from Saved Messages — reply or forward."""
        try:
            if self.backlink == "forward":
                await self.client.forward_messages("me", messages=sent, silent=True)
            elif self.backlink == "reply":
                target_peer = await self.client.get_input_entity(target)
                saved_peer  = await self.client.get_input_entity("me")
                await self.client(SendMessageRequest(
                    peer=saved_peer,
                    message="ㅤ",
                    reply_to=InputReplyToMessage(
                        reply_to_msg_id=sent.id,
                        reply_to_peer_id=target_peer,
                    ),
                    silent=True,
                    no_webpage=True,
                ))
        except Exception as exc:
            log.warning("Could not create backlink: %s", exc)

    # ── commands ──────────────────────────────────────────────────────────────

    async def help(self, event):
        chat = await event.get_chat()
        await self.client.send_message(chat, (
            "📋 **Notes Manager — Commands**\n\n"
            "`/help` — show this message\n"
            "`/chats` — list all managed chats\n\n"
            "**Moving a message:**\n"
            "Reply to any message with `#tag_name` to move it to that chat "
            "(created automatically if it doesn't exist).\n"
            "Reply with `#saved` to move a message back to Saved Messages.\n\n"
            f"Errors are reported to **{CONTROL_CHAT}**."
        ))
        await self.client.delete_messages(chat, event.message.id)

    async def chats(self, event):
        chat  = await event.get_chat()
        lines = [f"📁 **Chats in folder '{self.folder.folder_name}':**\n"]
        lines += [f"• `{name}`" for name in sorted(self.folder.chats)]
        await self.client.send_message(chat, "\n".join(lines))
        await self.client.delete_messages(chat, event.message.id)

    async def tag(self, event):
        text = (event.message.text or "").strip()
        m    = TAG_RE.match(text)
        if not m:
            return

        tag = "#" + m.group(1).lower()
        src_chat = await event.get_chat()

        if not event.message.reply_to_msg_id:
            await self.client.send_message(
                src_chat, f"⚠️ Reply to a message with `#{tag}` to move it."
            )
            await self.client.delete_messages(src_chat, event.message.id)
            return

        try:
            target = self.folder.me if tag == SAVED_MESSAGES_CHAT \
                else await self.folder.find_or_create(tag)

            # No-op if already in the target chat
            src_pid = utils.get_peer_id(src_chat)
            tgt_pid = self.folder.me.id if tag == SAVED_MESSAGES_CHAT \
                else utils.get_peer_id(target)
            if src_pid == tgt_pid:
                log.info("Tag matches source chat — deleting command only.")
                await self.client.delete_messages(src_chat, event.message.id)
                return

            original = await self.client.get_messages(
                src_chat, ids=event.message.reply_to_msg_id
            )
            if original is None:
                raise ValueError("Replied-to message not found.")

            # Send, retrying after evicting stale cache on permission errors
            try:
                sent = await self._copy_message(original, target)
            except (ChannelPrivateError, ChatWriteForbiddenError, UserBannedInChannelError) as exc:
                log.warning("No access to '%s' (%s) — evicting and recreating.", tag, exc)
                if tag in self.folder.chats:
                    del self.folder.chats[tag]
                target = await self.folder.find_or_create(tag)
                sent   = await self._copy_message(original, target)

            src_is_saved = (src_pid == self.folder.me.id)
            if self.backlink != "off" and src_is_saved and sent is not None:
                await self._send_backlink(sent, target)

            await self.client.delete_messages(src_chat, [original.id, event.message.id])
            log.info("Moved message %s → %s", original.id, tag)

        except Exception as exc:
            log.error("Move to %s failed: %s", tag, exc)
            await self._report_error(f"Move to **{tag}** failed: {exc}")


# ══════════════════════════════════════════════════════════════════════════════
#  Notes manager
# ══════════════════════════════════════════════════════════════════════════════

class NotesManager:
    def __init__(self, cfg: Config):
        self.cfg    = cfg
        self.client = TelegramClient(
            os.path.join(DIR, "me"), cfg.api_id, cfg.api_hash
        )

    async def run(self):
        await self.client.connect()
        await Auth(self.client).ensure()

        me      = await self.client.get_me()
        log.info("Logged in as %s (@%s)", me.first_name, me.username)

        folder  = FolderManager(self.client, self.cfg.folder_name, me)
        await folder.load()
        log.info("Watching %d chat(s) in folder '%s':", len(folder.chats), self.cfg.folder_name)
        for name in folder.chats:
            log.info("  • %s", name)

        handler = CommandHandler(self.client, folder, self.cfg.backlink)

        @self.client.on(events.NewMessage(outgoing=True))
        async def on_message(event):
            if event.chat_id not in folder.peer_ids():
                return
            text = (event.message.text or "").strip()
            if   text == "/help":    await handler.help(event)
            elif text == "/chats":   await handler.chats(event)
            elif TAG_RE.match(text): await handler.tag(event)

        print(f"\n✅  Notes manager running — folder: '{self.cfg.folder_name}'")
        print("    Send /help to any managed chat to get started.")
        print("    Ctrl+C to stop.\n")
        await self.client.run_until_disconnected()


# ══════════════════════════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    asyncio.run(NotesManager(Config()).run())