"""Qt-backed replacement surface for Android BulletinHelper."""

from __future__ import annotations

from typing import Any

import _bridge


class BulletinHelper:
    @staticmethod
    def _show(kind: str, *args: Any, **kwargs: Any) -> Any:
        return _bridge.ui_call(f"bulletin.{kind}", *args, **kwargs)

    @staticmethod
    def show_info(*args: Any, **kwargs: Any) -> Any:
        return BulletinHelper._show("info", *args, **kwargs)

    @staticmethod
    def show_error(*args: Any, **kwargs: Any) -> Any:
        return BulletinHelper._show("error", *args, **kwargs)

    @staticmethod
    def show_success(*args: Any, **kwargs: Any) -> Any:
        return BulletinHelper._show("success", *args, **kwargs)

    @staticmethod
    def show_simple(*args: Any, **kwargs: Any) -> Any:
        return BulletinHelper._show("simple", *args, **kwargs)

    @staticmethod
    def show_two_line(*args: Any, **kwargs: Any) -> Any:
        return BulletinHelper._show("two_line", *args, **kwargs)

    @staticmethod
    def show_with_button(*args: Any, **kwargs: Any) -> Any:
        return BulletinHelper._show("with_button", *args, **kwargs)

    @staticmethod
    def show_undo(*args: Any, **kwargs: Any) -> Any:
        return BulletinHelper._show("undo", *args, **kwargs)

    @staticmethod
    def show_copy(*args: Any, **kwargs: Any) -> Any:
        return BulletinHelper._show("copy", *args, **kwargs)
