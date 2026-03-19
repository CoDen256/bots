import json
from pathlib import Path


class StateManager:
    """Persists downloaded message IDs so an interrupted export can be resumed."""

    def __init__(self, state_path: Path) -> None:
        self._path  = state_path
        self._state = self._load()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _load(self) -> dict:
        if self._path.exists():
            try:
                with open(self._path, encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return {}

    def _persist(self) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._state, f)

    # ── Public API ────────────────────────────────────────────────────────────

    def downloaded_ids(self, chat_id: str) -> set[str]:
        """Return the set of already-downloaded message IDs for *chat_id*."""
        return set(self._state.get(chat_id, {}).get("downloaded", []))

    def mark_downloaded(self, chat_id: str, chat_name: str, msg_id: str) -> None:
        """Record *msg_id* as downloaded and immediately flush to disk."""
        if chat_id not in self._state:
            self._state[chat_id] = {"name": chat_name, "downloaded": []}
        ids: list = self._state[chat_id]["downloaded"]
        if msg_id not in ids:
            ids.append(msg_id)
        self._persist()

    def already_downloaded_count(self, chats: list[dict]) -> int:
        return sum(
            len(self._state.get(str(c["id"]), {}).get("downloaded", []))
            for c in chats
        )