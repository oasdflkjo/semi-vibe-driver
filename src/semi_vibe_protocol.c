/**
 * @file semi_vibe_protocol.c
 * @brief Implementation of the Semi-Vibe protocol
 */

#include "../include/semi_vibe_protocol.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
 * @brief Parse a command string into a message structure
 *
 * @param command Command string (6 hex digits)
 * @param message Pointer to message structure to fill
 * @return bool true if successful, false if invalid format
 */
bool protocol_parse_message(const char *command, SemiVibeMessage *message)
{
    // Validate command format (6 hex digits)
    if (!command || !message || strlen(command) != 6)
    {
        return false;
    }

    for (int i = 0; i < 6; i++)
    {
        if (!((command[i] >= '0' && command[i] <= '9') || (command[i] >= 'A' && command[i] <= 'F') ||
                (command[i] >= 'a' && command[i] <= 'f')))
        {
            return false;
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

    return true;
}

/**
 * @brief Format a message structure into a command string
 *
 * @param message Message structure
 * @param command Buffer to store the command string (must be at least 7 bytes)
 * @return bool true if successful, false if invalid message
 */
bool protocol_format_message(const SemiVibeMessage *message, char *command)
{
    if (!message || !command)
    {
        return false;
    }

    if (message->error > 0)
    {
        // Format error response
        sprintf(command, "%1X%s", message->error, "FFFFF");
    }
    else
    {
        // Format normal command/response
        sprintf(command, "%1X%02X%1X%02X", message->base, message->offset, message->rw, message->data);
    }

    return true;
}

/**
 * @brief Create an error message
 *
 * @param error_code Error code (1-3)
 * @param message Pointer to message structure to fill
 * @return bool true if successful, false if invalid error code
 */
bool protocol_create_error(uint8_t error_code, SemiVibeMessage *message)
{
    if (!message || error_code < 1 || error_code > 3)
    {
        return false;
    }

    message->error = error_code;
    return true;
}

/**
 * @brief Create a read message
 *
 * @param base Base address
 * @param offset Offset address
 * @param message Pointer to message structure to fill
 * @return bool true if successful
 */
bool protocol_create_read_message(uint8_t base, uint8_t offset, SemiVibeMessage *message)
{
    if (!message)
    {
        return false;
    }

    message->base = base;
    message->offset = offset;
    message->rw = CMD_READ;
    message->data = 0;
    message->error = 0;

    return true;
}

/**
 * @brief Create a write message
 *
 * @param base Base address
 * @param offset Offset address
 * @param data Data to write
 * @param message Pointer to message structure to fill
 * @return bool true if successful
 */
bool protocol_create_write_message(uint8_t base, uint8_t offset, uint8_t data, SemiVibeMessage *message)
{
    if (!message)
    {
        return false;
    }

    message->base = base;
    message->offset = offset;
    message->rw = CMD_WRITE;
    message->data = data;
    message->error = 0;

    return true;
}

/**
 * @brief Check if a message is an error response
 *
 * @param message Message structure
 * @return bool true if message is an error response
 */
bool protocol_is_error(const SemiVibeMessage *message)
{
    return (message && message->error > 0);
}

/**
 * @brief Create a bitmask from boolean values
 *
 * @param count Number of boolean parameters
 * @param ... Boolean values and their corresponding bit positions
 * @return uint8_t Resulting bitmask
 */
uint8_t protocol_create_bitmask(int count, ...)
{
    va_list args;
    uint8_t mask = 0;

    va_start(args, count);
    for (int i = 0; i < count; i++)
    {
        bool value = va_arg(args, int); // bool is promoted to int in varargs
        int bit_position = va_arg(args, int);
        if (value)
        {
            mask |= (1 << bit_position);
        }
    }
    va_end(args);

    return mask;
}