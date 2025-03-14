/**
 * @file semi_vibe_protocol.h
 * @brief Protocol definitions for the Semi-Vibe-Device
 */

#ifndef SEMI_VIBE_PROTOCOL_H
#define SEMI_VIBE_PROTOCOL_H

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


// Protocol constants
#define BASE_RESERVED 0x0
#define BASE_MAIN 0x1
#define BASE_SENSOR 0x2
#define BASE_ACTUATOR 0x3
#define BASE_CONTROL 0x4

// Main register offsets
#define OFFSET_CONNECTED_DEVICE 0x00
#define OFFSET_RESERVED_MAIN 0x01
#define OFFSET_POWER_STATE 0x02
#define OFFSET_ERROR_STATE 0x03

// Sensor register offsets
#define OFFSET_TEMP_ID 0x10
#define OFFSET_TEMP_VALUE 0x11
#define OFFSET_HUMID_ID 0x20
#define OFFSET_HUMID_VALUE 0x21

// Actuator register offsets
#define OFFSET_LED 0x10
#define OFFSET_FAN 0x20
#define OFFSET_HEATER 0x30
#define OFFSET_DOORS 0x40

// Control register offsets
#define OFFSET_POWER_SENSORS 0xFB
#define OFFSET_POWER_ACTUATORS 0xFC
#define OFFSET_RESET_SENSORS 0xFD
#define OFFSET_RESET_ACTUATORS 0xFE

// Command types
#define CMD_READ 0x0
#define CMD_WRITE 0x1

// Error codes
#define ERROR_FORBIDDEN 0x1
#define ERROR_INVALID 0x2
#define ERROR_GENERAL 0x3

// Bit masks
#define MASK_TEMP_SENSOR 0x01
#define MASK_HUMID_SENSOR 0x10
#define MASK_LED 0x01
#define MASK_FAN 0x04
#define MASK_HEATER 0x10
#define MASK_DOORS 0x40
#define MASK_HEATER_VALUE 0x0F
#define MASK_DOORS_VALUE 0x55

// Bit positions
#define BIT_TEMP_SENSOR 0
#define BIT_HUMID_SENSOR 4
#define BIT_LED 0
#define BIT_FAN 2
#define BIT_HEATER 4
#define BIT_DOORS 6

/**
 * @brief Message structure for the Semi-Vibe-Device protocol
 */
typedef struct {
  uint8_t base;   // Base address (1 hex digit)
  uint8_t offset; // Offset address (2 hex digits)
  uint8_t rw;     // Read/Write flag (0=read, 1=write)
  uint8_t data;   // Data value (2 hex digits)
  uint8_t error;  // Error code (0=no error, 1-3=error)
} SemiVibeMessage;

/**
 * @brief Parse a command string into a message structure
 *
 * @param command Command string (6 hex digits)
 * @param message Pointer to message structure to fill
 * @return int 1 if successful, 0 if invalid format
 */
static inline int parse_message(const char *command, SemiVibeMessage *message) {
  // Validate command format (6 hex digits)
  if (!command || !message || strlen(command) != 6) {
    return 0;
  }

  for (int i = 0; i < 6; i++) {
    if (!((command[i] >= '0' && command[i] <= '9') || (command[i] >= 'A' && command[i] <= 'F') ||
          (command[i] >= 'a' && command[i] <= 'f'))) {
      return 0;
    }
  }

  // Parse command
  char base_str[2] = {command[0], '\0'};
  char offset_str[3] = {command[1], command[2], '\0'};
  char rw_str[2] = {command[3], '\0'};
  char data_str[3] = {command[4], command[5], '\0'};

  message->base = (uint8_t)strtol(base_str, NULL, 16);
  message->offset = (uint8_t)strtol(offset_str, NULL, 16);
  message->rw = (uint8_t)strtol(rw_str, NULL, 16);
  message->data = (uint8_t)strtol(data_str, NULL, 16);
  message->error = 0;

  return 1;
}

/**
 * @brief Format a message structure into a command string
 *
 * @param message Message structure
 * @param command Buffer to store the command string (must be at least 7 bytes)
 * @return int 1 if successful, 0 if invalid message
 */
static inline int format_message(const SemiVibeMessage *message, char *command) {
  if (!message || !command) {
    return 0;
  }

  if (message->error > 0) {
    // Format error response
    sprintf(command, "%1X%s", message->error, "FFFFF");
  } else {
    // Format normal command/response
    sprintf(command, "%1X%02X%1X%02X", message->base, message->offset, message->rw, message->data);
  }

  return 1;
}

/**
 * @brief Create an error message
 *
 * @param error_code Error code (1-3)
 * @param message Pointer to message structure to fill
 * @return int 1 if successful, 0 if invalid error code
 */
static inline int create_error_message(uint8_t error_code, SemiVibeMessage *message) {
  if (!message || error_code < 1 || error_code > 3) {
    return 0;
  }

  message->error = error_code;
  return 1;
}

#endif /* SEMI_VIBE_PROTOCOL_H */