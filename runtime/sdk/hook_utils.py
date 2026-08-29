"""Compatibility facade for hook_utils.

Portable event hooks are handled by BasePlugin. Java/Xposed-style hooks are
kept import-compatible but require an explicit Desktop adapter.
"""

from __future__ import annotations

from functools import partial
from typing import Any, Callable

import _bridge


def _call(name: str, *args: Any, **kwargs: Any) -> Any:
    return _bridge.hook_call(name, *args, **kwargs)


def find_class(*args: Any, **kwargs: Any) -> Any:
    return _call("find_class", *args, **kwargs)


def hook_method(*args: Any, **kwargs: Any) -> Any:
    return _call("hook_method", *args, **kwargs)


def hook_all_methods(*args: Any, **kwargs: Any) -> Any:
    return _call("hook_all_methods", *args, **kwargs)


def hook_all_constructors(*args: Any, **kwargs: Any) -> Any:
    return _call("hook_all_constructors", *args, **kwargs)


def __getattr__(name: str) -> Callable[..., Any]:
    if name.startswith("_"):
        raise AttributeError(name)
    return partial(_call, name)
