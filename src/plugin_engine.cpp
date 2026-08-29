#include "plugin_engine.h"

#include <Python.h>

#include <iostream>
#include <utility>

namespace {

void PrintPythonError(const char *context) {
    std::cerr << "[plugin-host] " << context << '\n';
    if (PyErr_Occurred()) {
        PyErr_Print();
    }
}

} // namespace

PluginEngine::PluginEngine(std::filesystem::path sdkDir, std::filesystem::path pluginDir)
: _sdkDir(std::move(sdkDir))
, _pluginDir(std::move(pluginDir)) {
}

PluginEngine::~PluginEngine() {
    shutdown();
}

bool PluginEngine::initialize() {
    if (_initialized) {
        return true;
    }

    Py_Initialize();
    if (!Py_IsInitialized()) {
        std::cerr << "[plugin-host] failed to initialize CPython\n";
        return false;
    }
    _initialized = true;

    auto *sysPath = PySys_GetObject("path"); // borrowed reference
    if (!sysPath || !PyList_Check(sysPath)) {
        PrintPythonError("sys.path is unavailable");
        shutdown();
        return false;
    }

    const auto sdkString = _sdkDir.string();
    auto *sdkPath = PyUnicode_DecodeFSDefault(sdkString.c_str());
    if (!sdkPath) {
        PrintPythonError("failed to convert SDK path");
        shutdown();
        return false;
    }

    const auto inserted = PyList_Insert(sysPath, 0, sdkPath);
    Py_DECREF(sdkPath);
    if (inserted != 0) {
        PrintPythonError("failed to add SDK directory to sys.path");
        shutdown();
        return false;
    }

    std::cout << "[plugin-host] CPython " << Py_GetVersion() << '\n';
    std::cout << "[plugin-host] SDK: " << _sdkDir << '\n';
    std::cout << "[plugin-host] plugins: " << _pluginDir << '\n';
    return true;
}

int PluginEngine::loadAll() {
    if (!_initialized && !initialize()) {
        return -1;
    }

    auto *runtime = PyImport_ImportModule("plugin_runtime");
    if (!runtime) {
        PrintPythonError("failed to import plugin_runtime");
        return -1;
    }

    auto *discover = PyObject_GetAttrString(runtime, "discover_and_load");
    if (!discover || !PyCallable_Check(discover)) {
        Py_XDECREF(discover);
        Py_DECREF(runtime);
        PrintPythonError("plugin_runtime.discover_and_load is unavailable");
        return -1;
    }

    const auto pluginDirString = _pluginDir.string();
    auto *pluginDir = PyUnicode_DecodeFSDefault(pluginDirString.c_str());
    if (!pluginDir) {
        Py_DECREF(discover);
        Py_DECREF(runtime);
        PrintPythonError("failed to convert plugin directory");
        return -1;
    }

    auto *result = PyObject_CallFunctionObjArgs(discover, pluginDir, nullptr);
    Py_DECREF(pluginDir);
    Py_DECREF(discover);
    Py_DECREF(runtime);

    if (!result) {
        PrintPythonError("plugin discovery failed");
        return -1;
    }

    const auto loadedCount = PyList_Check(result) ? PyList_Size(result) : -1;
    Py_DECREF(result);

    if (loadedCount < 0) {
        PrintPythonError("plugin_runtime returned an unexpected result");
        return -1;
    }

    std::cout << "[plugin-host] loaded " << loadedCount << " plugin(s)\n";
    return static_cast<int>(loadedCount);
}

void PluginEngine::shutdown() {
    if (!_initialized) {
        return;
    }

    auto *runtime = PyImport_ImportModule("plugin_runtime");
    if (runtime) {
        auto *unload = PyObject_GetAttrString(runtime, "unload_all");
        if (unload && PyCallable_Check(unload)) {
            auto *result = PyObject_CallNoArgs(unload);
            if (!result) {
                PrintPythonError("plugin unload failed");
            }
            Py_XDECREF(result);
        }
        Py_XDECREF(unload);
        Py_DECREF(runtime);
    } else {
        PyErr_Clear();
    }

    Py_Finalize();
    _initialized = false;
}
