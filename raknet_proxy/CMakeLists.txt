cmake_minimum_required(VERSION 3.16)
project(mn2mc_raknet_proxy LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)

# Use local SLikeNet clone
set(SLIKENET_ROOT "E:/TEMP_SHARE/SLikeNet")

# Collect SLikeNet source files
file(GLOB SLIKENET_SOURCES "${SLIKENET_ROOT}/Source/src/*.cpp")

add_executable(mn2mc_proxy
    src/main.cpp
    src/proxy.cpp
    src/backend_bridge.cpp
    ${SLIKENET_SOURCES}
)

target_include_directories(mn2mc_proxy PRIVATE
    ${SLIKENET_ROOT}/Source/include
    src
)

target_link_libraries(mn2mc_proxy PRIVATE
    ws2_32
    iphlpapi
)

target_compile_definitions(mn2mc_proxy PRIVATE
    _CRT_SECURE_NO_WARNINGS
    _RAKNET_LIB
    _RAKNET_SUPPORT_NatPunchthroughServer=1
    _RAKNET_SUPPORT_NatPunchthroughClient=1
    _RAKNET_SUPPORT_UDPProxyServer=1
    _RAKNET_SUPPORT_UDPProxyCoordinator=1
)
