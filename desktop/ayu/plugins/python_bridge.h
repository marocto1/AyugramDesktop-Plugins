#pragma once

namespace Ayu::Plugins {

class PluginManager;

// Must be called before CPython initialization. Registers the built-in
// `_ayugram_desktop` module consumed by runtime/sdk/_bridge.py.
bool registerPythonBridgeModule();

// The bridge never owns this pointer. PluginManager clears it on shutdown.
void setBridgePluginManager(PluginManager *manager);

} // namespace Ayu::Plugins
