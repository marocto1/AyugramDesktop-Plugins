"""Clean-room Desktop implementation of the portable BasePlugin API."""

from __future__ import annotations

import sys
from typing import Any

import _bridge


def _plugin_id(instance: object) -> str:
    module = sys.modules.get(instance.__class__.__module__)
    value = getattr(module, "__id__", None) if module is not None else None
    if isinstance(value, str) and value:
        return value
    return instance.__class__.__module__


class BasePlugin:
    """Base class exposed to existing exteraGram/AyuGram `.plugin` files.

    Lifecycle and event methods intentionally default to no-ops. Registration,
    settings and client operations are delegated to the native Desktop bridge.
    """

    def on_plugin_load(self) -> None:
        pass

    def on_plugin_unload(self) -> None:
        pass

    def create_settings(self) -> list[Any]:
        return []

    def on_app_event(self, event_type: Any) -> Any:
        return None

    def pre_request_hook(
        self,
        request_name: str,
        account: Any,
        request: Any,
    ) -> Any:
        return None

    def post_request_hook(
        self,
        request_name: str,
        account: Any,
        response: Any,
        error: Any,
    ) -> Any:
        return None

    def on_update_hook(
        self,
        update_name: str,
        account: Any,
        update: Any,
    ) -> Any:
        return None

    def on_updates_hook(
        self,
        container_name: str,
        account: Any,
        updates: Any,
    ) -> Any:
        return None

    def on_send_message_hook(self, account: Any, params: Any) -> Any:
        return None

    def add_hook(
        self,
        name: str,
        match_substring: str | None = None,
        priority: int = 0,
    ) -> Any:
        return _bridge.register_hook(
            _plugin_id(self),
            name,
            match_substring,
            priority,
        )

    def add_on_send_message_hook(self, priority: int = 0) -> Any:
        return _bridge.register_send_message_hook(_plugin_id(self), priority)

    def remove_hook(self, name: str) -> Any:
        return _bridge.remove_hook(_plugin_id(self), name)

    def get_setting(self, key: str, default: Any = None) -> Any:
        return _bridge.get_setting(_plugin_id(self), key, default)

    def set_setting(
        self,
        key: str,
        value: Any,
        reload_settings: bool = False,
    ) -> Any:
        return _bridge.set_setting(
            _plugin_id(self),
            key,
            value,
            reload_settings,
        )

    def export_settings(self) -> Any:
        return _bridge.client_call("export_plugin_settings", _plugin_id(self))

    def import_settings(
        self,
        settings: Any,
        reload_settings: bool = False,
    ) -> Any:
        return _bridge.client_call(
            "import_plugin_settings",
            _plugin_id(self),
            settings,
            reload_settings,
        )

    def hook_method(self, *args: Any, **kwargs: Any) -> Any:
        return _bridge.hook_call("hook_method", *args, **kwargs)

    def hook_all_methods(self, *args: Any, **kwargs: Any) -> Any:
        return _bridge.hook_call("hook_all_methods", *args, **kwargs)

    def hook_all_constructors(self, *args: Any, **kwargs: Any) -> Any:
        return _bridge.hook_call("hook_all_constructors", *args, **kwargs)

    def unhook_method(self, *args: Any, **kwargs: Any) -> Any:
        return _bridge.hook_call("unhook_method", *args, **kwargs)

    def add_menu_item(self, menu_item_data: Any) -> Any:
        return _bridge.add_menu_item(_plugin_id(self), menu_item_data)

    def remove_menu_item(self, item_id: str) -> Any:
        return _bridge.remove_menu_item(_plugin_id(self), item_id)

    def log(self, message: object) -> None:
        _bridge.log(_plugin_id(self), message)
