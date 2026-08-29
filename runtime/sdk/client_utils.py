"""Portable client_utils facade for AyuGram Desktop plugins."""

from __future__ import annotations

from functools import partial
from typing import Any, Callable

import _bridge


def _call(name: str, *args: Any, **kwargs: Any) -> Any:
    return _bridge.client_call(name, *args, **kwargs)


def send_request(*args: Any, **kwargs: Any) -> Any:
    return _call("send_request", *args, **kwargs)


def send_message(*args: Any, **kwargs: Any) -> Any:
    return _call("send_message", *args, **kwargs)


def send_text(*args: Any, **kwargs: Any) -> Any:
    return _call("send_text", *args, **kwargs)


def send_photo(*args: Any, **kwargs: Any) -> Any:
    return _call("send_photo", *args, **kwargs)


def send_document(*args: Any, **kwargs: Any) -> Any:
    return _call("send_document", *args, **kwargs)


def send_video(*args: Any, **kwargs: Any) -> Any:
    return _call("send_video", *args, **kwargs)


def send_audio(*args: Any, **kwargs: Any) -> Any:
    return _call("send_audio", *args, **kwargs)


def edit_message(*args: Any, **kwargs: Any) -> Any:
    return _call("edit_message", *args, **kwargs)


def get_account_instance(*args: Any, **kwargs: Any) -> Any:
    return _call("get_account_instance", *args, **kwargs)


def get_messages_controller(*args: Any, **kwargs: Any) -> Any:
    return _call("get_messages_controller", *args, **kwargs)


def get_contacts_controller(*args: Any, **kwargs: Any) -> Any:
    return _call("get_contacts_controller", *args, **kwargs)


def get_connections_manager(*args: Any, **kwargs: Any) -> Any:
    return _call("get_connections_manager", *args, **kwargs)


def get_messages_storage(*args: Any, **kwargs: Any) -> Any:
    return _call("get_messages_storage", *args, **kwargs)


def get_send_messages_helper(*args: Any, **kwargs: Any) -> Any:
    return _call("get_send_messages_helper", *args, **kwargs)


def get_file_loader(*args: Any, **kwargs: Any) -> Any:
    return _call("get_file_loader", *args, **kwargs)


def get_notification_center(*args: Any, **kwargs: Any) -> Any:
    return _call("get_notification_center", *args, **kwargs)


def get_user_config(*args: Any, **kwargs: Any) -> Any:
    return _call("get_user_config", *args, **kwargs)


def __getattr__(name: str) -> Callable[..., Any]:
    # Preserve import compatibility for client_utils helpers which have not yet
    # received a dedicated Desktop wrapper. The native bridge decides whether a
    # particular operation is implemented.
    if name.startswith("_"):
        raise AttributeError(name)
    return partial(_call, name)
