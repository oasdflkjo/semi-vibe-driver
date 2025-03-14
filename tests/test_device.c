/**
 * @file test_device.c
 * @brief Test program for the Semi-Vibe-Device simulator
 */

#include "../include/semi_vibe_device.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Callback function for logging
void log_callback(const char *message) { printf("[DEVICE] %s\n", message); }

int main() {
  printf("Semi-Vibe-Device Test Program\n");
  printf("-----------------------------\n");

  // Initialize device
  if (!device_init(log_callback)) {
    printf("Failed to initialize device\n");
    return 1;
  }

  // Start device
  if (!device_start()) {
    printf("Failed to start device\n");
    return 1;
  }

  // Process some test commands
  const char *test_commands[] = {
      "100000", // Read MAIN connected_device
      "102000", // Read MAIN power_state
      "103000", // Read MAIN error_state
      "210000", // Read SENSOR_A ID
      "211000", // Read SENSOR_A reading
      "220000", // Read SENSOR_B ID
      "221000", // Read SENSOR_B reading
      "310180", // Write ACTUATOR_A value 0x80
      "310000", // Read ACTUATOR_A value
      "320140", // Write ACTUATOR_B value 0x40
      "320000", // Read ACTUATOR_B value
      "330108", // Write ACTUATOR_C value 0x08
      "330000", // Read ACTUATOR_C value
      "340155", // Write ACTUATOR_D value 0x55
      "340000", // Read ACTUATOR_D value
      "4FB111", // Write CONTROL power_sensors
      "4FB000", // Read CONTROL power_sensors
      "4FC155", // Write CONTROL power_actuators
      "4FC000", // Read CONTROL power_actuators
  };

  char response[7];
  for (int i = 0; i < sizeof(test_commands) / sizeof(test_commands[0]); i++) {
    printf("Command: %s\n", test_commands[i]);
    if (device_process_command(test_commands[i], response)) {
      printf("Response: %s\n", response);
    } else {
      printf("Failed to process command\n");
    }
    printf("\n");
  }

  // Get device memory
  DeviceMemory memory;
  if (device_get_memory(&memory)) {
    printf("Device Memory:\n");
    printf("  Connected Device: 0x%02X\n", memory.connected_device);
    printf("  Power State: 0x%02X\n", memory.power_state);
    printf("  Error State: 0x%02X\n", memory.error_state);
    printf("  Sensor A ID: 0x%02X\n", memory.sensor_a_id);
    printf("  Sensor A Reading: 0x%02X\n", memory.sensor_a_reading);
    printf("  Sensor B ID: 0x%02X\n", memory.sensor_b_id);
    printf("  Sensor B Reading: 0x%02X\n", memory.sensor_b_reading);
    printf("  Actuator A: 0x%02X\n", memory.actuator_a);
    printf("  Actuator B: 0x%02X\n", memory.actuator_b);
    printf("  Actuator C: 0x%02X\n", memory.actuator_c);
    printf("  Actuator D: 0x%02X\n", memory.actuator_d);
  } else {
    printf("Failed to get device memory\n");
  }

  // Stop device
  if (!device_stop()) {
    printf("Failed to stop device\n");
    return 1;
  }

  printf("Test completed successfully\n");
  return 0;
}