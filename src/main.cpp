#include "plugin_engine.h"

#include <filesystem>
#include <iostream>

int main(int argc, char **argv) {
    const std::filesystem::path sdkDir = argc > 1 ? argv[1] : "sdk";
    const std::filesystem::path pluginDir = argc > 2 ? argv[2] : "examples";

    PluginEngine engine(sdkDir, pluginDir);
    if (!engine.initialize()) {
        return 1;
    }

    const auto loaded = engine.loadAll();
    if (loaded < 0) {
        return 2;
    }

    std::cout << "[plugin-host] runtime smoke test completed\n";
    return 0;
}
