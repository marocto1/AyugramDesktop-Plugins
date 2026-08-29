option(
    AYUGRAM_ENABLE_PYTHON_PLUGINS
    "Enable exteraGram/AyuGram-compatible Python .plugin runtime"
    OFF
)

function(ayugram_configure_python_plugins target source_root)
    if (NOT AYUGRAM_ENABLE_PYTHON_PLUGINS)
        return()
    endif()

    find_package(Python3 3.11 REQUIRED COMPONENTS Development.Embed)

    target_sources(${target} PRIVATE
        ${source_root}/ayu/plugins/plugin_manager.cpp
        ${source_root}/ayu/plugins/plugin_manager.h
        ${source_root}/ayu/plugins/python_bridge.cpp
        ${source_root}/ayu/plugins/python_bridge.h
        ${source_root}/ayu/plugins/python_runtime.cpp
        ${source_root}/ayu/plugins/python_runtime.h
    )

    target_compile_definitions(${target} PRIVATE
        AYUGRAM_ENABLE_PYTHON_PLUGINS=1
    )

    target_link_libraries(${target} PRIVATE
        Python3::Python
    )
endfunction()
