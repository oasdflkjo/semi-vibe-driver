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

# Define device source files
set(DEVICE_SOURCES
    src/semi_vibe_device.c
)

# Define device header files
set(DEVICE_HEADERS
    include/semi_vibe_device.h
)

# Define driver source files
set(DRIVER_SOURCES
    src/semi_vibe_driver.c
)

# Define driver header files
set(DRIVER_HEADERS
    include/semi_vibe_driver.h
)

# Create device shared library
add_library(semi_vibe_device SHARED ${DEVICE_SOURCES} ${DEVICE_HEADERS})

# Set device library properties
set_target_properties(semi_vibe_device PROPERTIES
    VERSION 1.0.0
    PUBLIC_HEADER "include/semi_vibe_device.h"
)

# Link device with required libraries
target_link_libraries(semi_vibe_device ws2_32)

# Create driver shared library
add_library(semi_vibe_driver SHARED ${DRIVER_SOURCES} ${DRIVER_HEADERS})

# Set driver library properties
set_target_properties(semi_vibe_driver PROPERTIES
    VERSION 1.0.0
    PUBLIC_HEADER "include/semi_vibe_driver.h"
)

# Link driver with required libraries
target_link_libraries(semi_vibe_driver ws2_32)

# Install targets
install(TARGETS semi_vibe_device semi_vibe_driver
    RUNTIME DESTINATION bin
    ARCHIVE DESTINATION lib
    PUBLIC_HEADER DESTINATION include
) 