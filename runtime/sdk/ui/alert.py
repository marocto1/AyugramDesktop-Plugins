"""Desktop compatibility implementation of the alert builder surface."""

from __future__ import annotations

from typing import Any, Callable

import _bridge


class AlertDialogBuilder:
    """Records fluent builder calls and lets the Qt bridge render the dialog."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._init_args = args
        self._init_kwargs = kwargs
        self._calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    def _record(self, name: str, *args: Any, **kwargs: Any) -> "AlertDialogBuilder":
        self._calls.append((name, args, kwargs))
        return self

    def show(self) -> Any:
        return _bridge.ui_call(
            "alert.show",
            self._init_args,
            self._init_kwargs,
            self._calls,
        )

    def create(self) -> Any:
        return _bridge.ui_call(
            "alert.create",
            self._init_args,
            self._init_kwargs,
            self._calls,
        )

    def __getattr__(self, name: str) -> Callable[..., "AlertDialogBuilder"]:
        if name.startswith("_"):
            raise AttributeError(name)

        def method(*args: Any, **kwargs: Any) -> "AlertDialogBuilder":
            return self._record(name, *args, **kwargs)

        return method


def __getattr__(name: str) -> Callable[..., Any]:
    if name.startswith("_"):
        raise AttributeError(name)

    def proxy(*args: Any, **kwargs: Any) -> Any:
        return _bridge.ui_call(f"alert.{name}", *args, **kwargs)

    return proxy
