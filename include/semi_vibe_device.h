/**
 * @file semi_vibe_device.h
 * @brief Header file for the Semi-Vibe-Device simulator
 */

#ifndef SEMI_VIBE_DEVICE_H
#define SEMI_VIBE_DEVICE_H

#define EXPORT __declspec(dllexport)

#include <stdbool.h>
#include <stdint.h>

/**
 * @brief Callback function type for logging messages from the device
 */
typedef void (*LogCallback)(const char *message);

/**
 * @brief Memory map structure for the Semi-Vibe-Device
 */
typedef struct {
  // MAIN (base address 1)
  uint8_t connected_device; // 0x00
  uint8_t reserved_main;    // 0x01
  uint8_t power_state;      // 0x02
  uint8_t error_state;      // 0x03

  // SENSOR (base address 2)
  uint8_t sensor_a_id;      // 0x10
  uint8_t sensor_a_reading; // 0x11
  uint8_t sensor_b_id;      // 0x20
  uint8_t sensor_b_reading; // 0x21

  // ACTUATOR (base address 3)
  uint8_t actuator_a; // 0x10 (LED)
  uint8_t actuator_b; // 0x20 (fan)
  uint8_t actuator_c; // 0x30 (heater)
  uint8_t actuator_d; // 0x40 (doors)

  // CONTROL (base address 4)
  uint8_t power_sensors;   // 0xFB
  uint8_t power_actuators; // 0xFC
  uint8_t reset_sensors;   // 0xFD
  uint8_t reset_actuators; // 0xFE
} DeviceMemory;

/**
 * @brief Initialize the Semi-Vibe-Device simulator
 *
 * @param log_callback Callback function for logging messages
 * @return EXPORT true if initialization was successful, false otherwise
 */
EXPORT bool device_init(LogCallback log_callback);

/**
 * @brief Start the Semi-Vibe-Device simulator
 *
 * @return EXPORT true if the device was started successfully, false otherwise
 */
EXPORT bool device_start();

/**
 * @brief Stop the Semi-Vibe-Device simulator
 *
 * @return EXPORT true if the device was stopped successfully, false otherwise
 */
EXPORT bool device_stop();

/**
 * @brief Get the current state of the device memory
 *
 * @param memory Pointer to a DeviceMemory structure to fill with the current
 * state
 * @return EXPORT true if the memory was successfully retrieved, false otherwise
 */
EXPORT bool device_get_memory(DeviceMemory *memory);

/**
 * @brief Process a command manually (for testing without socket connection)
 *
 * @param command The command to process (6 hex digits)
 * @param response Buffer to store the response (should be at least 7 bytes)
 * @return EXPORT true if the command was processed successfully, false
 * otherwise
 */
EXPORT bool device_process_command(const char *command, char *response);

#endif /* SEMI_VIBE_DEVICE_H */