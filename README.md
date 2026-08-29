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

## MVP

- `.plugin` discovery and metadata parsing
- plugin enable/disable state
- embedded CPython 3.11 runtime
- `BasePlugin` lifecycle
- `get_setting` / `set_setting`
- `create_settings()` mapped to Desktop UI
- `on_send_message_hook`
- request hooks (`pre_request_hook`, `post_request_hook`)
- minimal `client_utils`

## Compatibility

Portable high-level plugin APIs are the first target. Android-specific Java, Android View and arbitrary Xposed/LSPlant hooks cannot map 1:1 to Telegram Desktop and will require explicit compatibility adapters where feasible.

## Upstream

Development targets the `dev` branch of [AyuGram/AyuGramDesktop](https://github.com/AyuGram/AyuGramDesktop).

Status: early development.
