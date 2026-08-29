from __future__ import annotations

import ast
import importlib.machinery
import importlib.util
import inspect
import re
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

from base_plugin import BasePlugin
from plugin_state import PluginStateStore


_METADATA_KEYS = {
    "__id__",
    "__name__",
    "__description__",
    "__author__",
    "__version__",
    "__icon__",
    "__app_version__",
    "__sdk_version__",
    "__min_version__",
    "__requirements__",
}
_PLUGIN_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{1,31}$")


class PluginLoadError(RuntimeError):
    pass


@dataclass(slots=True)
class LoadedPlugin:
    path: Path
    module: ModuleType
    instance: BasePlugin
    metadata: dict[str, Any]


_loaded_plugins: list[LoadedPlugin] = []


def _read_metadata(path: Path) -> dict[str, Any]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    metadata: dict[str, Any] = {}

    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name) or target.id not in _METADATA_KEYS:
            continue
        try:
            metadata[target.id] = ast.literal_eval(node.value)
        except (ValueError, TypeError) as exc:
            raise PluginLoadError(
                f"{path.name}: metadata {target.id} must be a literal"
            ) from exc

    plugin_id = metadata.get("__id__")
    plugin_name = metadata.get("__name__")
    if not isinstance(plugin_id, str) or not _PLUGIN_ID_RE.fullmatch(plugin_id):
        raise PluginLoadError(
            f"{path.name}: __id__ must be 2-32 chars, start with a letter, "
            "and contain only latin letters, digits, '_' or '-'"
        )
    if not isinstance(plugin_name, str) or not plugin_name.strip():
        raise PluginLoadError(f"{path.name}: __name__ is required")

    metadata.setdefault("__version__", "1.0")
    return metadata


def _find_plugin_class(module: ModuleType) -> type[BasePlugin]:
    candidates: list[type[BasePlugin]] = []
    for value in vars(module).values():
        if not inspect.isclass(value) or value is BasePlugin:
            continue
        if value.__module__ != module.__name__:
            continue
        if issubclass(value, BasePlugin):
            candidates.append(value)

    if len(candidates) != 1:
        raise PluginLoadError(
            f"{module.__file__}: expected exactly one BasePlugin subclass, "
            f"found {len(candidates)}"
        )
    return candidates[0]


def _default_state_store(plugin_path: Path) -> PluginStateStore:
    return PluginStateStore(plugin_path.parent / ".ayu_plugin_state.json")


def load_plugin(
    path: str | Path,
    state_store: PluginStateStore | None = None,
) -> LoadedPlugin:
    plugin_path = Path(path).resolve()
    metadata = _read_metadata(plugin_path)
    store = state_store or _default_state_store(plugin_path)
    plugin_id = metadata["__id__"]
    module_name = f"ayu_plugin_{plugin_id.replace('-', '_')}"

    loader = importlib.machinery.SourceFileLoader(module_name, str(plugin_path))
    spec = importlib.util.spec_from_loader(module_name, loader)
    if spec is None:
        raise PluginLoadError(f"{plugin_path.name}: failed to create module spec")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        loader.exec_module(module)
        plugin_class = _find_plugin_class(module)
        instance = plugin_class()
        instance._bind_runtime(
            metadata,
            lambda key, default=None: store.get_setting(plugin_id, key, default),
            lambda key, value: store.set_setting(plugin_id, key, value),
        )
        instance.on_plugin_load()
    except Exception:
        sys.modules.pop(module_name, None)
        raise

    loaded = LoadedPlugin(
        path=plugin_path,
        module=module,
        instance=instance,
        metadata=metadata,
    )
    _loaded_plugins.append(loaded)
    return loaded


def discover_and_load(plugin_dir: str | Path) -> list[LoadedPlugin]:
    directory = Path(plugin_dir).resolve()
    if not directory.exists():
        raise PluginLoadError(f"plugin directory does not exist: {directory}")
    if not directory.is_dir():
        raise PluginLoadError(f"plugin path is not a directory: {directory}")

    state_store = PluginStateStore(directory / ".ayu_plugin_state.json")
    loaded_now: list[LoadedPlugin] = []
    for path in sorted(directory.glob("*.plugin")):
        try:
            metadata = _read_metadata(path)
            if not state_store.is_enabled(metadata["__id__"]):
                print(f"[plugin-runtime] skipped disabled plugin {metadata['__id__']}")
                continue

            loaded = load_plugin(path, state_store)
            loaded_now.append(loaded)
            print(
                f"[plugin-runtime] loaded {loaded.metadata['__id__']} "
                f"v{loaded.metadata['__version__']} from {path.name}"
            )
        except Exception as exc:
            print(f"[plugin-runtime] failed to load {path.name}: {exc}", file=sys.stderr)
            traceback.print_exc()

    return loaded_now


def set_plugin_enabled(plugin_dir: str | Path, plugin_id: str, enabled: bool) -> None:
    directory = Path(plugin_dir).resolve()
    store = PluginStateStore(directory / ".ayu_plugin_state.json")
    store.set_enabled(plugin_id, enabled)


def unload_all() -> None:
    while _loaded_plugins:
        loaded = _loaded_plugins.pop()
        try:
            loaded.instance.on_plugin_unload()
        except Exception:
            traceback.print_exc()
        finally:
            sys.modules.pop(loaded.module.__name__, None)
