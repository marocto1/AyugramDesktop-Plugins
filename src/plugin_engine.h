#pragma once

#include <filesystem>

class PluginEngine final {
public:
    PluginEngine(std::filesystem::path sdkDir, std::filesystem::path pluginDir);
    ~PluginEngine();

    PluginEngine(const PluginEngine &) = delete;
    PluginEngine &operator=(const PluginEngine &) = delete;

    bool initialize();
    int loadAll();
    void shutdown();

private:
    std::filesystem::path _sdkDir;
    std::filesystem::path _pluginDir;
    bool _initialized = false;
};
