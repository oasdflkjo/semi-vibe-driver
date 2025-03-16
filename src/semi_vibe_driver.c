/**
 * @file semi_vibe_driver.c
 * @brief Implementation of the Semi-Vibe-Driver
 *
 * @copyright Copyright (c) 2024 Semi-Vibe Technologies, Inc.
 * @license MIT License with Attribution Requirement. See LICENSE.md for details.
 */

#include "../include/semi_vibe_driver.h"
#include "../include/semi_vibe_comm.h"
#include "../include/semi_vibe_protocol.h"

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BUFFER_SIZE 256
#define COMMAND_SIZE 7 // 6 hex digits + null terminator

// Driver state
typedef struct
{
    LogCallback log_callback;
    CommContext comm_context;
    bool initialized;
} DriverState;

// Global driver state
static DriverState g_driver = {.log_callback = NULL, .initialized = false};

// Forward declarations
static void driver_log_callback(const char *message);
static bool read_register(uint8_t base, uint8_t offset, uint8_t *value);
static bool write_register(uint8_t base, uint8_t offset, uint8_t value);

/**
 * @brief Callback function for communication layer logging
 *
 * @param message Log message
 */
static void driver_log_callback(const char *message)
{
    if (g_driver.log_callback)
    {
        g_driver.log_callback(message);
    }
}

/**
 * @brief Initialize the driver
 *
 * @param log_callback Optional callback for logging
 * @return true if initialization was successful
 */
EXPORT bool driver_init(LogCallback log_callback)
{
    if (g_driver.initialized)
    {
        if (g_driver.log_callback)
        {
            g_driver.log_callback("Driver is already initialized");
        }
        return true;
    }

    g_driver.log_callback = log_callback;

    // Initialize communication layer
    if (!comm_init(&g_driver.comm_context, driver_log_callback))
    {
        if (g_driver.log_callback)
        {
            g_driver.log_callback("Failed to initialize communication layer");
        }
        return false;
    }

    g_driver.initialized = true;
    if (g_driver.log_callback)
    {
        g_driver.log_callback("Semi-Vibe-Driver initialized");
    }
    return true;
}

/**
 * @brief Connect to the device
 *
 * @param host Hostname or IP address (defaults to localhost)
 * @param port Port number (defaults to 8989)
 * @return true if connection was successful
 */
EXPORT bool driver_connect(const char *host, int port)
{
    if (!g_driver.initialized)
    {
        if (g_driver.log_callback)
        {
            g_driver.log_callback("Driver is not initialized");
        }
        return false;
    }

    if (g_driver.comm_context.connected)
    {
        if (g_driver.log_callback)
        {
            g_driver.log_callback("Driver is already connected");
        }
        return true;
    }

    // Connect to device
    return comm_connect(&g_driver.comm_context, host, port);
}

/**
 * @brief Disconnect from the device
 *
 * @return true if disconnection was successful
 */
EXPORT bool driver_disconnect()
{
    if (!g_driver.comm_context.connected)
    {
        if (g_driver.log_callback)
        {
            g_driver.log_callback("Driver is not connected");
        }
        return true;
    }

    // Disconnect from device
    return comm_disconnect(&g_driver.comm_context, true);
}

/**
 * @brief Get the device status
 *
 * @param status Pointer to DeviceStatus structure to be filled
 * @return true if status was retrieved successfully
 */
EXPORT bool driver_get_status(DeviceStatus *status)
{
    if (!g_driver.comm_context.connected || !status)
    {
        return false;
    }

    uint8_t connected_device = 0;
    uint8_t power_state = 0;
    uint8_t error_state = 0;

    // Read status registers
    if (!read_register(BASE_MAIN, OFFSET_CONNECTED_DEVICE, &connected_device) ||
        !read_register(BASE_MAIN, OFFSET_POWER_STATE, &power_state) || !read_register(BASE_MAIN, OFFSET_ERROR_STATE, &error_state))
    {
        return false;
    }

    // Fill status structure
    status->connected = (connected_device != 0);
    status->sensors_powered = ((power_state & (MASK_TEMP_SENSOR | MASK_HUMID_SENSOR)) != 0);
    status->actuators_powered = ((power_state & (MASK_LED | MASK_FAN | MASK_HEATER | MASK_DOORS)) != 0);
    status->has_errors = (error_state != 0);

    return true;
}

/**
 * @brief Get humidity value
 *
 * @param value Pointer to store the humidity value (0-100)
 * @return true if value was retrieved successfully
 */
EXPORT bool driver_get_humidity(uint8_t *value)
{
    if (!g_driver.comm_context.connected || !value)
    {
        return false;
    }

    return read_register(BASE_SENSOR, OFFSET_HUMID_VALUE, value);
}

/**
 * @brief Get temperature value
 *
 * @param value Pointer to store the temperature value (0-255)
 * @return true if value was retrieved successfully
 */
EXPORT bool driver_get_temperature(uint8_t *value)
{
    if (!g_driver.comm_context.connected || !value)
    {
        return false;
    }

    return read_register(BASE_SENSOR, OFFSET_TEMP_VALUE, value);
}

/**
 * @brief Set LED value
 *
 * @param value LED brightness (0-255)
 * @return true if value was set successfully
 */
EXPORT bool driver_set_led(uint8_t value)
{
    return write_register(BASE_ACTUATOR, OFFSET_LED, value);
}

/**
 * @brief Get LED value
 *
 * @param value Pointer to store the LED brightness (0-255)
 * @return true if value was retrieved successfully
 */
EXPORT bool driver_get_led(uint8_t *value)
{
    if (!g_driver.comm_context.connected || !value)
    {
        return false;
    }

    return read_register(BASE_ACTUATOR, OFFSET_LED, value);
}

/**
 * @brief Set fan value
 *
 * @param value Fan speed (0-255)
 * @return true if value was set successfully
 */
EXPORT bool driver_set_fan(uint8_t value)
{
    return write_register(BASE_ACTUATOR, OFFSET_FAN, value);
}

/**
 * @brief Get fan value
 *
 * @param value Pointer to store the fan speed (0-255)
 * @return true if value was retrieved successfully
 */
EXPORT bool driver_get_fan(uint8_t *value)
{
    if (!g_driver.comm_context.connected || !value)
    {
        return false;
    }

    return read_register(BASE_ACTUATOR, OFFSET_FAN, value);
}

/**
 * @brief Set heater value
 *
 * @param value Heater level (0-15, only lower 4 bits used)
 * @return true if value was set successfully
 */
EXPORT bool driver_set_heater(uint8_t value)
{
    // Heater only uses lower 4 bits
    return write_register(BASE_ACTUATOR, OFFSET_HEATER, value & MASK_HEATER_VALUE);
}

/**
 * @brief Get heater value
 *
 * @param value Pointer to store the heater level (0-15)
 * @return true if value was retrieved successfully
 */
EXPORT bool driver_get_heater(uint8_t *value)
{
    if (!g_driver.comm_context.connected || !value)
    {
        return false;
    }

    uint8_t raw_value;
    if (!read_register(BASE_ACTUATOR, OFFSET_HEATER, &raw_value))
    {
        return false;
    }

    // Ensure only the lower 4 bits are returned (0-15)
    *value = raw_value & MASK_HEATER_VALUE;
    return true;
}

/**
 * @brief Set the state of a specific door
 *
 * @param door_id Door identifier (DOOR_1, DOOR_2, DOOR_3, or DOOR_4)
 * @param state Door state (DOOR_OPEN or DOOR_CLOSED)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_set_door(int door_id, int state)
{
    if (!g_driver.comm_context.connected || door_id < DOOR_1 || door_id > DOOR_4 || (state != DOOR_OPEN && state != DOOR_CLOSED))
    {
        return false;
    }

    /* IMPORTANT: This function intentionally uses a read-modify-write approach for functional safety.
     *
     * 1. We first read the current door register value to ensure we have the most up-to-date state.
     *    This is critical for functional safety elements like doors where multiple clients might
     *    control the same device simultaneously.
     *
     * 2. We then modify only the specific door bit while preserving the state of other doors.
     *
     * 3. Finally, we write the new value back to the register.
     *
     * While this approach generates more messages (2 per door operation), it ensures:
     * - We always operate on the current state of the hardware
     * - We don't inadvertently change the state of other doors
     * - We avoid race conditions and synchronization issues that could occur with cached values
     *
     * For functional safety elements like doors, this additional communication overhead
     * is an acceptable trade-off for increased reliability and safety.
     */
    uint8_t current_value;
    if (!read_register(BASE_ACTUATOR, OFFSET_DOORS, &current_value))
    {
        return false;
    }

    // Calculate bit position (DOOR_1->0, DOOR_2->2, DOOR_3->4, DOOR_4->6)
    int bit_position = (door_id - 1) * 2;

    // Set or clear the bit based on state
    uint8_t new_value;
    if (state == DOOR_OPEN)
    {
        new_value = current_value | (1 << bit_position); // Set bit
    }
    else
    {
        new_value = current_value & ~(1 << bit_position); // Clear bit
    }

    // Write the new value (ensuring only valid bits are set)
    return write_register(BASE_ACTUATOR, OFFSET_DOORS, new_value & MASK_DOORS_VALUE);
}

/**
 * @brief Get the state of a specific door
 *
 * @param door_id Door identifier (DOOR_1, DOOR_2, DOOR_3, or DOOR_4)
 * @param state Pointer to store the door state (DOOR_OPEN or DOOR_CLOSED)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_door_state(int door_id, int *state)
{
    if (!g_driver.comm_context.connected || door_id < DOOR_1 || door_id > DOOR_4 || state == NULL)
    {
        return false;
    }

    /* IMPORTANT: This function always reads the current door state directly from the hardware.
     *
     * For functional safety elements like doors, it's critical to always have the most up-to-date
     * state from the hardware rather than relying on cached values. This ensures:
     * - We always report the actual state of the hardware
     * - We detect any changes made by other clients or external factors
     * - We avoid potential safety issues that could arise from stale or incorrect state information
     *
     * While this generates an additional message for each door state query, the safety
     * benefits outweigh the communication overhead.
     */
    uint8_t current_value;
    if (!read_register(BASE_ACTUATOR, OFFSET_DOORS, &current_value))
    {
        return false;
    }

    // Calculate bit position (DOOR_1->0, DOOR_2->2, DOOR_3->4, DOOR_4->6)
    int bit_position = (door_id - 1) * 2;

    // Check if the bit is set
    *state = (current_value & (1 << bit_position)) ? DOOR_OPEN : DOOR_CLOSED;

    return true;
}

/**
 * @brief Send a command and receive a response
 *
 * @param request Message structure for the request
 * @param response Message structure for the response
 * @return true if command was sent and response received successfully
 */
static bool send_and_receive(const SemiVibeMessage *request, SemiVibeMessage *response)
{
    if (!g_driver.comm_context.connected || !request || !response)
    {
        return false;
    }

    char command[COMMAND_SIZE];
    char response_str[BUFFER_SIZE];

    // Format the request message
    if (!protocol_format_message(request, command))
    {
        if (g_driver.log_callback)
        {
            g_driver.log_callback("Failed to format command");
        }
        return false;
    }

    // Send command and receive response
    if (!comm_send_receive(&g_driver.comm_context, command, response_str, BUFFER_SIZE))
    {
        return false;
    }

    // Parse the response
    if (!protocol_parse_message(response_str, response))
    {
        if (g_driver.log_callback)
        {
            g_driver.log_callback("Failed to parse response: %s");
        }
        return false;
    }

    // Log error responses but don't treat them as failures
    if (protocol_is_error(response))
    {
        if (g_driver.log_callback)
        {
            g_driver.log_callback("Error response");
        }
    }

    return true;
}

/**
 * @brief Read a register value
 *
 * @param base Base address
 * @param offset Offset address
 * @param value Pointer to store the read value
 * @return true if register was read successfully
 */
static bool read_register(uint8_t base, uint8_t offset, uint8_t *value)
{
    if (!g_driver.comm_context.connected || !value)
    {
        return false;
    }

    // Create request message
    SemiVibeMessage request;
    if (!protocol_create_read_message(base, offset, &request))
    {
        return false;
    }

    // Create response message
    SemiVibeMessage response = {0};

    // Send request and receive response
    if (!send_and_receive(&request, &response))
    {
        return false;
    }

    // Check for errors
    if (protocol_is_error(&response))
    {
        return false;
    }

    // Store the read value
    *value = response.data;
    return true;
}

/**
 * @brief Write a value to a register
 *
 * @param base Base address
 * @param offset Offset address
 * @param value Value to write
 * @return true if register was written successfully
 */
static bool write_register(uint8_t base, uint8_t offset, uint8_t value)
{
    if (!g_driver.comm_context.connected)
    {
        return false;
    }

    // Create request message
    SemiVibeMessage request;
    if (!protocol_create_write_message(base, offset, value, &request))
    {
        return false;
    }

    // Create response message
    SemiVibeMessage response = {0};

    // Send request and receive response
    if (!send_and_receive(&request, &response))
    {
        return false;
    }

    // Check for errors
    if (protocol_is_error(&response))
    {
        return false;
    }

    // Check if response matches request (write operations echo back the command)
    return (
        response.base == request.base && response.offset == request.offset && response.rw == request.rw && response.data == request.data);
}

/**
 * @brief Get power state of a specific component
 *
 * @param component_type Type of component (0=TEMPERATURE, 1=HUMIDITY, 2=LED, 3=FAN, 4=HEATER, 5=DOORS)
 * @param powered Pointer to store the power state (true=powered, false=not powered)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_power_state(int component_type, bool *powered)
{
    if (!g_driver.comm_context.connected || !powered || component_type < COMPONENT_TEMPERATURE || component_type > COMPONENT_DOORS)
    {
        return false;
    }

    uint8_t power_state = 0;
    if (!read_register(BASE_MAIN, OFFSET_POWER_STATE, &power_state))
    {
        return false;
    }

    // Map component type to bit mask
    uint8_t mask = 0;
    switch (component_type)
    {
    case COMPONENT_TEMPERATURE:
        mask = MASK_TEMP_SENSOR;
        break;
    case COMPONENT_HUMIDITY:
        mask = MASK_HUMID_SENSOR;
        break;
    case COMPONENT_LED:
        mask = MASK_LED;
        break;
    case COMPONENT_FAN:
        mask = MASK_FAN;
        break;
    case COMPONENT_HEATER:
        mask = MASK_HEATER;
        break;
    case COMPONENT_DOORS:
        mask = MASK_DOORS;
        break;
    default:
        return false;
    }

    // Check if the bit is set
    *powered = (power_state & mask) != 0;
    return true;
}

/**
 * @brief Get error state of a specific component
 *
 * @param component_type Type of component (0=TEMPERATURE, 1=HUMIDITY, 2=LED, 3=FAN, 4=HEATER, 5=DOORS)
 * @param has_error Pointer to store the error state (true=has error, false=no error)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_error_state(int component_type, bool *has_error)
{
    if (!g_driver.comm_context.connected || !has_error || component_type < COMPONENT_TEMPERATURE || component_type > COMPONENT_DOORS)
    {
        return false;
    }

    uint8_t error_state = 0;
    if (!read_register(BASE_MAIN, OFFSET_ERROR_STATE, &error_state))
    {
        return false;
    }

    // Map component type to bit mask
    uint8_t mask = 0;
    switch (component_type)
    {
    case COMPONENT_TEMPERATURE:
        mask = MASK_TEMP_SENSOR;
        break;
    case COMPONENT_HUMIDITY:
        mask = MASK_HUMID_SENSOR;
        break;
    case COMPONENT_LED:
        mask = MASK_LED;
        break;
    case COMPONENT_FAN:
        mask = MASK_FAN;
        break;
    case COMPONENT_HEATER:
        mask = MASK_HEATER;
        break;
    case COMPONENT_DOORS:
        mask = MASK_DOORS;
        break;
    default:
        return false;
    }

    // Check if the bit is set
    *has_error = (error_state & mask) != 0;
    return true;
}

/**
 * @brief Send a raw command to the device
 *
 * @param command Command string
 * @param response Buffer to store response
 * @return true if command was sent successfully
 */
EXPORT bool driver_send_command(const char *command, char *response)
{
    if (!g_driver.comm_context.connected || !command || !response)
    {
        return false;
    }

    // Parse the command
    SemiVibeMessage request = {0};
    if (!protocol_parse_message(command, &request))
    {
        if (g_driver.log_callback)
        {
            g_driver.log_callback("Failed to parse command");
        }
        return false;
    }

    // Create response message
    SemiVibeMessage response_msg = {0};

    // Send request and receive response
    if (!send_and_receive(&request, &response_msg))
    {
        return false;
    }

    // Format the response
    if (!protocol_format_message(&response_msg, response))
    {
        if (g_driver.log_callback)
        {
            g_driver.log_callback("Failed to format response");
        }
        return false;
    }

    return true;
}

/**
 * @brief Set power state of a specific component
 *
 * @param component_type Type of component (0=TEMPERATURE, 1=HUMIDITY, 2=LED, 3=FAN, 4=HEATER, 5=DOORS)
 * @param powered Power state to set (true=powered, false=not powered)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_set_power_state(int component_type, bool powered)
{
    if (!g_driver.comm_context.connected || component_type < COMPONENT_TEMPERATURE || component_type > COMPONENT_DOORS)
    {
        return false;
    }

    // For sensors
    if (component_type == COMPONENT_TEMPERATURE || component_type == COMPONENT_HUMIDITY)
    {
        // Read current power state to preserve the other sensor's state
        uint8_t current_power_state = 0;
        if (!read_register(BASE_CONTROL, OFFSET_POWER_SENSORS, &current_power_state))
        {
            return false;
        }

        bool temperature_on = (current_power_state & MASK_TEMP_SENSOR) != 0;
        bool humidity_on = (current_power_state & MASK_HUMID_SENSOR) != 0;

        // Update the requested component's state
        if (component_type == COMPONENT_TEMPERATURE)
        {
            temperature_on = powered;
        }
        else
        { // COMPONENT_HUMIDITY
            humidity_on = powered;
        }

        // Create bitmask and write to register
        uint8_t value = protocol_create_bitmask(2, temperature_on, BIT_TEMP_SENSOR, humidity_on, BIT_HUMID_SENSOR);
        return write_register(BASE_CONTROL, OFFSET_POWER_SENSORS, value);
    }
    // For actuators
    else
    {
        // Read current power state to preserve other actuators' states
        uint8_t current_power_state = 0;
        if (!read_register(BASE_CONTROL, OFFSET_POWER_ACTUATORS, &current_power_state))
        {
            return false;
        }

        bool led_on = (current_power_state & MASK_LED) != 0;
        bool fan_on = (current_power_state & MASK_FAN) != 0;
        bool heater_on = (current_power_state & MASK_HEATER) != 0;
        bool doors_on = (current_power_state & MASK_DOORS) != 0;

        // Update the requested component's state
        switch (component_type)
        {
        case COMPONENT_LED:
            led_on = powered;
            break;
        case COMPONENT_FAN:
            fan_on = powered;
            break;
        case COMPONENT_HEATER:
            heater_on = powered;
            break;
        case COMPONENT_DOORS:
            doors_on = powered;
            break;
        default:
            return false;
        }

        // Create bitmask and write to register
        uint8_t value = protocol_create_bitmask(4, led_on, BIT_LED, fan_on, BIT_FAN, heater_on, BIT_HEATER, doors_on, BIT_DOORS);
        return write_register(BASE_CONTROL, OFFSET_POWER_ACTUATORS, value);
    }
}

/**
 * @brief Reset a specific component
 *
 * @param component_type Type of component (0=TEMPERATURE, 1=HUMIDITY, 2=LED, 3=FAN, 4=HEATER, 5=DOORS)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_reset_component(int component_type)
{
    if (!g_driver.comm_context.connected || component_type < COMPONENT_TEMPERATURE || component_type > COMPONENT_DOORS)
    {
        return false;
    }

    // For sensors
    if (component_type == COMPONENT_TEMPERATURE || component_type == COMPONENT_HUMIDITY)
    {
        // Read current reset state to preserve the other sensor's state
        uint8_t current_reset_state = 0;
        if (!read_register(BASE_CONTROL, OFFSET_RESET_SENSORS, &current_reset_state))
        {
            return false;
        }

        bool reset_temperature = (current_reset_state & MASK_TEMP_SENSOR) != 0;
        bool reset_humidity = (current_reset_state & MASK_HUMID_SENSOR) != 0;

        // Update the requested component's state
        if (component_type == COMPONENT_TEMPERATURE)
        {
            reset_temperature = true;
            reset_humidity = false;
        }
        else
        { // COMPONENT_HUMIDITY
            reset_temperature = false;
            reset_humidity = true;
        }

        // Create bitmask and write to register
        uint8_t value = protocol_create_bitmask(2, reset_temperature, BIT_TEMP_SENSOR, reset_humidity, BIT_HUMID_SENSOR);
        return write_register(BASE_CONTROL, OFFSET_RESET_SENSORS, value);
    }
    // For actuators
    else
    {
        // Read current reset state to preserve other actuators' states
        uint8_t current_reset_state = 0;
        if (!read_register(BASE_CONTROL, OFFSET_RESET_ACTUATORS, &current_reset_state))
        {
            return false;
        }

        bool reset_led = (current_reset_state & MASK_LED) != 0;
        bool reset_fan = (current_reset_state & MASK_FAN) != 0;
        bool reset_heater = (current_reset_state & MASK_HEATER) != 0;
        bool reset_doors = (current_reset_state & MASK_DOORS) != 0;

        // Update the requested component's state
        switch (component_type)
        {
        case COMPONENT_LED:
            reset_led = true;
            reset_fan = false;
            reset_heater = false;
            reset_doors = false;
            break;
        case COMPONENT_FAN:
            reset_led = false;
            reset_fan = true;
            reset_heater = false;
            reset_doors = false;
            break;
        case COMPONENT_HEATER:
            reset_led = false;
            reset_fan = false;
            reset_heater = true;
            reset_doors = false;
            break;
        case COMPONENT_DOORS:
            reset_led = false;
            reset_fan = false;
            reset_heater = false;
            reset_doors = true;
            break;
        default:
            return false;
        }

        // Create bitmask and write to register
        uint8_t value =
            protocol_create_bitmask(4, reset_led, BIT_LED, reset_fan, BIT_FAN, reset_heater, BIT_HEATER, reset_doors, BIT_DOORS);
        return write_register(BASE_CONTROL, OFFSET_RESET_ACTUATORS, value);
    }
}