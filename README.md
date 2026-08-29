# AyuGram Desktop Plugins

Experimental compatibility layer for running exteraGram / AyuGram Android `.plugin` files on AyuGram Desktop.

## Goal

Keep existing `.plugin` files unchanged where they use the portable plugin API, and bridge that API to AyuGram Desktop's C++/Qt internals.

The Android implementation uses Python 3.11 and exposes APIs such as `BasePlugin`, `client_utils`, request/update/message hooks, plugin settings, menu items, alerts and bulletins. This project reimplements that contract for Desktop rather than copying Android runtime binaries.

## Target architecture

```text
.plugin
  -> CPython 3.11
  -> compatibility SDK (base_plugin / client_utils / ui / hooks)
  -> C++/Qt bridge
  -> AyuGram Desktop / Telegram Desktop internals
```

## Current prototype

The first vertical slice now contains:

- a C++17 host embedding CPython 3.11;
- `.plugin` discovery from a directory;
- static metadata parsing via Python AST before plugin execution;
- validation of `__id__` and `__name__`;
- loading `.plugin` files with `SourceFileLoader`;
- discovery and construction of one `BasePlugin` subclass;
- `on_plugin_load()` / `on_plugin_unload()` lifecycle;
- an in-memory `get_setting()` / `set_setting()` placeholder;
- registration placeholders for request and outgoing-message hooks;
- a smoke-test plugin in `examples/hello.plugin`;
- unit tests for loading and metadata validation.

This is still a standalone prototype. It is not wired into AyuGram Desktop's UI, MTProto request pipeline, message sending pipeline, or persistent settings yet.

## Build the prototype

Requirements:

- CMake 3.21+
- a C++17 compiler
- CPython 3.11 development headers/libraries

```bash
cmake -S . -B build
cmake --build build
./build/ayu_plugin_host sdk examples
```

On Windows, run the generated `ayu_plugin_host.exe` with the same two arguments if your working directory is not the repository root.

Run the Python-side tests with:

```bash
python3.11 -m unittest discover -s tests -v
```

Expected smoke-test output includes:

```text
[plugin:hello_world] loaded
[plugin-runtime] loaded hello_world v0.1.0 from hello.plugin
[plugin-host] loaded 1 plugin(s)
[plugin:hello_world] unloaded
```

## MVP

- [x] `.plugin` discovery and metadata parsing
- [ ] plugin enable/disable state
- [x] embedded CPython 3.11 runtime prototype
- [x] `BasePlugin` lifecycle prototype
- [ ] persistent `get_setting` / `set_setting`
- [ ] `create_settings()` mapped to Desktop UI
- [ ] `on_send_message_hook` wired to Desktop
- [ ] request hooks (`pre_request_hook`, `post_request_hook`) wired to Desktop
- [ ] minimal `client_utils`

## Compatibility

Portable high-level plugin APIs are the first target. A `.plugin` is treated as Python source with literal top-level metadata and a `BasePlugin` subclass, matching current exteraGram/AyuGram plugin conventions.

Android-specific Java, Android View and arbitrary Xposed/LSPlant hooks cannot map 1:1 to Telegram Desktop and will require explicit compatibility adapters where feasible.

## Next integration step

Move the host/runtime into the AyuGram Desktop tree and bridge plugin lifecycle to the application session. After that, wire `on_send_message_hook` into the outgoing message path before implementing request hooks and Desktop settings UI.

## Upstream

Development targets the `dev` branch of [AyuGram/AyuGramDesktop](https://github.com/AyuGram/AyuGramDesktop).

Status: early development; standalone runtime prototype implemented.
