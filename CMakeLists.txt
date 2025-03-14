cmake_minimum_required(VERSION 3.10)
project(SemiVibeDevice C)

# Set C standard
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Set output directories
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# Add include directories
include_directories(include)

# Define source files
set(SOURCES
    src/semi_vibe_device.c
)

# Define header files
set(HEADERS
    include/semi_vibe_device.h
)

# Create shared library
add_library(semi_vibe_device SHARED ${SOURCES} ${HEADERS})

# Set library properties
set_target_properties(semi_vibe_device PROPERTIES
    VERSION 1.0.0
    SOVERSION 1
    PUBLIC_HEADER "include/semi_vibe_device.h"
)

# Link with required libraries
if(WIN32)
    target_link_libraries(semi_vibe_device ws2_32)
endif()

# Install targets
install(TARGETS semi_vibe_device
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    PUBLIC_HEADER DESTINATION include
)

# Add test executable
add_executable(test_device tests/test_device.c)
target_link_libraries(test_device semi_vibe_device) 