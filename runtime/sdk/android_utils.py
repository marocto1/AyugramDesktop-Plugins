"""Small Android compatibility shim for portable helpers.

There is no Android runtime on Desktop. Helpers which have a meaningful Qt
analogue are forwarded to the native bridge; other Android-only operations are
reported as unsupported when called.
"""

from __future__ import annotations

from functools import partial
from typing import Any, Callable

import _bridge


def run_on_ui_thread(
    callback: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> Any:
    return _bridge.run_on_ui_thread(callback, *args, **kwargs)


def __getattr__(name: str) -> Callable[..., Any]:
    if name.startswith("_"):
        raise AttributeError(name)
    return partial(_bridge.hook_call, f"android_utils.{name}")
