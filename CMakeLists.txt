cmake_minimum_required(VERSION 2.8.12)
project(clib)
set (CMAKE_CXX_STANDARD 14)

find_package(pybind11 REQUIRED)
pybind11_add_module(clib ./c_src/export.cpp)
if(MSVC)
  target_compile_options(env PRIVATE /utf-8)
endif()