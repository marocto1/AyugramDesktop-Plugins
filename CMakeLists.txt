cmake_minimum_required(VERSION 3.21)

project(AyuGramDesktopPluginsPrototype LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Python3 3.11 EXACT REQUIRED COMPONENTS Development)

add_executable(ayu_plugin_host
    src/main.cpp
    src/plugin_engine.cpp
)

target_include_directories(ayu_plugin_host PRIVATE src)
target_link_libraries(ayu_plugin_host PRIVATE Python3::Python)

if(MSVC)
    target_compile_options(ayu_plugin_host PRIVATE /W4 /permissive-)
else()
    target_compile_options(ayu_plugin_host PRIVATE -Wall -Wextra -Wpedantic)
endif()
