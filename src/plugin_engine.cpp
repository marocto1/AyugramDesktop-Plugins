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

PyObject *ImportRuntimeCallable(const char *name) {
    auto *runtime = PyImport_ImportModule("plugin_runtime");
    if (!runtime) {
        PrintPythonError("failed to import plugin_runtime");
        return nullptr;
    }

    auto *callable = PyObject_GetAttrString(runtime, name);
    Py_DECREF(runtime);
    if (!callable || !PyCallable_Check(callable)) {
        Py_XDECREF(callable);
        PrintPythonError("plugin_runtime callable is unavailable");
        return nullptr;
    }
    return callable;
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

    auto *sysPath = PySys_GetObject("path");
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

    auto *discover = ImportRuntimeCallable("discover_and_load");
    if (!discover) {
        return -1;
    }

    const auto pluginDirString = _pluginDir.string();
    auto *pluginDir = PyUnicode_DecodeFSDefault(pluginDirString.c_str());
    if (!pluginDir) {
        Py_DECREF(discover);
        PrintPythonError("failed to convert plugin directory");
        return -1;
    }

    auto *result = PyObject_CallFunctionObjArgs(discover, pluginDir, nullptr);
    Py_DECREF(pluginDir);
    Py_DECREF(discover);

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

std::optional<SendMessageHookResult> PluginEngine::dispatchTextMessage(
        int account,
        std::string message) {
    if (!_initialized) {
        return std::nullopt;
    }

    auto *dispatch = ImportRuntimeCallable("dispatch_text_message");
    if (!dispatch) {
        return std::nullopt;
    }

    auto *accountObject = PyLong_FromLong(account);
    auto *messageObject = PyUnicode_DecodeUTF8(
        message.data(),
        static_cast<Py_ssize_t>(message.size()),
        "strict");
    if (!accountObject || !messageObject) {
        Py_XDECREF(accountObject);
        Py_XDECREF(messageObject);
        Py_DECREF(dispatch);
        PrintPythonError("failed to build send hook arguments");
        return std::nullopt;
    }

    auto *result = PyObject_CallFunctionObjArgs(
        dispatch,
        accountObject,
        messageObject,
        nullptr);
    Py_DECREF(accountObject);
    Py_DECREF(messageObject);
    Py_DECREF(dispatch);
    if (!result) {
        PrintPythonError("send hook dispatch failed");
        return std::nullopt;
    }

    auto *cancelledObject = PyObject_GetAttrString(result, "cancelled");
    auto *paramsObject = PyObject_GetAttrString(result, "params");
    auto *textObject = paramsObject
        ? PyObject_GetAttrString(paramsObject, "message")
        : nullptr;

    if (!cancelledObject || !paramsObject || !textObject || !PyUnicode_Check(textObject)) {
        Py_XDECREF(cancelledObject);
        Py_XDECREF(paramsObject);
        Py_XDECREF(textObject);
        Py_DECREF(result);
        PrintPythonError("send hook returned an invalid result");
        return std::nullopt;
    }

    const auto cancelled = PyObject_IsTrue(cancelledObject);
    const auto *utf8 = PyUnicode_AsUTF8(textObject);
    if (cancelled < 0 || !utf8) {
        Py_DECREF(cancelledObject);
        Py_DECREF(paramsObject);
        Py_DECREF(textObject);
        Py_DECREF(result);
        PrintPythonError("failed to decode send hook result");
        return std::nullopt;
    }

    auto output = SendMessageHookResult();
    output.cancelled = (cancelled != 0);
    output.message = utf8;

    Py_DECREF(cancelledObject);
    Py_DECREF(paramsObject);
    Py_DECREF(textObject);
    Py_DECREF(result);
    return output;
}

void PluginEngine::shutdown() {
    if (!_initialized) {
        return;
    }

    auto *unload = ImportRuntimeCallable("unload_all");
    if (unload) {
        auto *result = PyObject_CallNoArgs(unload);
        if (!result) {
            PrintPythonError("plugin unload failed");
        }
        Py_XDECREF(result);
        Py_DECREF(unload);
    } else {
        PyErr_Clear();
    }

    Py_Finalize();
    _initialized = false;
}
