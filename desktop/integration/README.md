# AyuGram Desktop integration (MVP)

This directory describes how to wire the plugin runtime into the current
`AyuGram/AyuGramDesktop` `dev` branch without making Python a mandatory build
dependency.

## 1. Copy native sources

Copy `desktop/ayu/plugins/*` to:

```text
Telegram/SourceFiles/ayu/plugins/
```

Copy `desktop/cmake/ayu_python_plugins.cmake` to:

```text
Telegram/cmake/ayu_python_plugins.cmake
```

## 2. CMake

In `Telegram/CMakeLists.txt`, after `src_loc` is defined and after the Telegram
target exists, add:

```cmake
include(cmake/ayu_python_plugins.cmake)
ayugram_configure_python_plugins(Telegram ${src_loc})
```

Configure the build with:

```text
-DAYUGRAM_ENABLE_PYTHON_PLUGINS=ON
```

The MVP uses CMake's `Python3::Python` embed target and requires Python 3.11 or
newer development/embed files. The default remains OFF, so normal AyuGram
builds are unaffected.

## 3. Runtime files

For the first milestone, copy this repository's `runtime/` directory next to
AyuGram's plugin data as:

```text
<tdata>/ayu_plugins/runtime/
    loader.py
    sdk/
```

Place plugin files in:

```text
<tdata>/ayu_plugins/plugins/*.plugin
```

`settings.json` is created automatically inside the plugins directory.

## 4. AyuInfra startup

Add the following include to `Telegram/SourceFiles/ayu/ayu_infra.cpp`:

```cpp
#include "ayu/plugins/plugin_manager.h"
```

Add this helper in `namespace AyuInfra`:

```cpp
void initPlugins() {
#if defined(AYUGRAM_ENABLE_PYTHON_PLUGINS)
    const auto root = cWorkingDir() + u"tdata/ayu_plugins/"_q;
    Ayu::Plugins::PluginManager::instance().initialize(
        root + u"runtime"_q,
        root + u"plugins"_q);
#endif
}
```

Then call `initPlugins();` near the end of `AyuInfra::init()` after the core Ayu
services are initialized.

## First milestone acceptance check

With `examples/hello.plugin` copied to the plugins directory, starting AyuGram
should produce a log entry similar to:

```text
[AyuPlugin:desktop_hello] loaded
```

The plugin must also be able to persist a setting through `BasePlugin.set_setting`
and read it again through `BasePlugin.get_setting`.

## Deliberately not implemented yet

- Telegram request/update hooks.
- send-message hooks.
- plugin enable/disable UI.
- installation from a Telegram document.
- automatic dependency installation.
- bundling an embeddable Python distribution with release packages.

Those are layered on top of the working loader/bridge rather than being mixed
into interpreter startup.
