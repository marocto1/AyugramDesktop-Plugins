#pragma once

#include <filesystem>
#include <optional>
#include <string>

struct SendMessageHookResult final {
    bool cancelled = false;
    std::string message;
};

class PluginEngine final {
public:
    PluginEngine(std::filesystem::path sdkDir, std::filesystem::path pluginDir);
    ~PluginEngine();

    PluginEngine(const PluginEngine &) = delete;
    PluginEngine &operator=(const PluginEngine &) = delete;

    bool initialize();
    int loadAll();
    std::optional<SendMessageHookResult> dispatchTextMessage(
        int account,
        std::string message);
    void shutdown();

private:
    std::filesystem::path _sdkDir;
    std::filesystem::path _pluginDir;
    bool _initialized = false;
};
