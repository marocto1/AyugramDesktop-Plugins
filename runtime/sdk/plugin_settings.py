"""Compatibility shim for the Android plugin_settings module."""

from __future__ import annotations

from typing import Any

import _bridge


def get_setting(plugin_id: str, key: str, default: Any = None) -> Any:
    return _bridge.get_setting(plugin_id, key, default)


def set_setting(plugin_id: str, key: str, value: Any) -> Any:
    return _bridge.set_setting(plugin_id, key, value, False)


def clear_settings(plugin_id: str) -> Any:
    return _bridge.client_call("clear_plugin_settings", plugin_id)


def get_all_settings(plugin_id: str) -> Any:
    return _bridge.client_call("get_all_plugin_settings", plugin_id)


def set_all_settings(plugin_id: str, settings: dict[str, Any]) -> Any:
    return _bridge.client_call("set_all_plugin_settings", plugin_id, settings)
