from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any


class HookStrategy(IntEnum):
    DEFAULT = 0
    CANCEL = 1
    MODIFY = 2
    MODIFY_FINAL = 3


@dataclass(slots=True)
class HookResult:
    strategy: HookStrategy = HookStrategy.DEFAULT
    request: Any = None
    response: Any = None
    update: Any = None
    updates: Any = None
    params: Any = None


class BasePlugin:
    """Minimal desktop-compatible subset of the exteraGram/AyuGram plugin API."""

    def __init__(self) -> None:
        self._settings: dict[str, Any] = {}
        self._request_hooks: set[str] = set()
        self._send_message_hook_priority: int | None = None
        self._metadata: dict[str, Any] = {}

    def on_plugin_load(self) -> None:
        pass

    def on_plugin_unload(self) -> None:
        pass

    def create_settings(self) -> list[Any]:
        return []

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        self._settings[key] = value

    def add_hook(self, request_name: str) -> None:
        self._request_hooks.add(request_name)

    def add_on_send_message_hook(self, priority: int = 0) -> None:
        self._send_message_hook_priority = int(priority)

    def log(self, message: Any) -> None:
        plugin_id = self._metadata.get("__id__", self.__class__.__name__)
        print(f"[plugin:{plugin_id}] {message}")
