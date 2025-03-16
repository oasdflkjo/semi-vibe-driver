/**
 * @file semi_vibe_protocol.h
 * @brief Protocol definitions for the Semi-Vibe-Device
 *
 * @copyright Copyright (c) 2024 Semi-Vibe Technologies, Inc.
 * @license MIT License with Attribution Requirement. See LICENSE.md for details.
 */

#ifndef SEMI_VIBE_PROTOCOL_H
#define SEMI_VIBE_PROTOCOL_H

#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

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
typedef struct
{
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
 * @return bool true if successful, false if invalid format
 */
bool protocol_parse_message(const char *command, SemiVibeMessage *message);

/**
 * @brief Format a message structure into a command string
 *
 * @param message Message structure
 * @param command Buffer to store the command string (must be at least 7 bytes)
 * @return bool true if successful, false if invalid message
 */
bool protocol_format_message(const SemiVibeMessage *message, char *command);

/**
 * @brief Create an error message
 *
 * @param error_code Error code (1-3)
 * @param message Pointer to message structure to fill
 * @return bool true if successful, false if invalid error code
 */
bool protocol_create_error(uint8_t error_code, SemiVibeMessage *message);

/**
 * @brief Create a read message
 *
 * @param base Base address
 * @param offset Offset address
 * @param message Pointer to message structure to fill
 * @return bool true if successful
 */
bool protocol_create_read_message(uint8_t base, uint8_t offset, SemiVibeMessage *message);

/**
 * @brief Create a write message
 *
 * @param base Base address
 * @param offset Offset address
 * @param data Data to write
 * @param message Pointer to message structure to fill
 * @return bool true if successful
 */
bool protocol_create_write_message(uint8_t base, uint8_t offset, uint8_t data, SemiVibeMessage *message);

/**
 * @brief Check if a message is an error response
 *
 * @param message Message structure
 * @return bool true if message is an error response
 */
bool protocol_is_error(const SemiVibeMessage *message);

/**
 * @brief Create a bitmask from boolean values
 *
 * @param count Number of boolean parameters
 * @param ... Boolean values and their corresponding bit positions
 * @return uint8_t Resulting bitmask
 */
uint8_t protocol_create_bitmask(int count, ...);

#ifdef __cplusplus
}
#endif

#endif /* SEMI_VIBE_PROTOCOL_H */