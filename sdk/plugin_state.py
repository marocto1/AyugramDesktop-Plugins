from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class PluginStateError(RuntimeError):
    pass


class PluginStateStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._data: dict[str, Any] = {
            "enabled": {},
            "settings": {},
        }
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return

        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PluginStateError(f"failed to read plugin state: {self.path}") from exc

        if not isinstance(raw, dict):
            raise PluginStateError(f"plugin state root must be an object: {self.path}")

        enabled = raw.get("enabled", {})
        settings = raw.get("settings", {})
        if not isinstance(enabled, dict) or not isinstance(settings, dict):
            raise PluginStateError(f"invalid plugin state structure: {self.path}")

        self._data = {
            "enabled": enabled,
            "settings": settings,
        }

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_name(f"{self.path.name}.tmp")
        try:
            temp_path.write_text(
                json.dumps(self._data, ensure_ascii=False, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            os.replace(temp_path, self.path)
        except OSError as exc:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise PluginStateError(f"failed to write plugin state: {self.path}") from exc

    def is_enabled(self, plugin_id: str) -> bool:
        value = self._data["enabled"].get(plugin_id, True)
        return bool(value)

    def set_enabled(self, plugin_id: str, enabled: bool) -> None:
        self._data["enabled"][plugin_id] = bool(enabled)
        self._save()

    def get_setting(self, plugin_id: str, key: str, default: Any = None) -> Any:
        plugin_settings = self._data["settings"].get(plugin_id)
        if not isinstance(plugin_settings, dict):
            return default
        return plugin_settings.get(key, default)

    def set_setting(self, plugin_id: str, key: str, value: Any) -> None:
        try:
            json.dumps(value)
        except (TypeError, ValueError) as exc:
            raise PluginStateError(
                f"setting {plugin_id}.{key} is not JSON-serializable"
            ) from exc

        settings = self._data["settings"]
        plugin_settings = settings.setdefault(plugin_id, {})
        if not isinstance(plugin_settings, dict):
            plugin_settings = {}
            settings[plugin_id] = plugin_settings
        plugin_settings[key] = value
        self._save()
