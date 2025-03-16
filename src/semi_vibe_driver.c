/**
 * @file semi_vibe_driver.c
 * @brief Implementation of the Semi-Vibe-Driver
 */

#include "../include/semi_vibe_driver.h"
#include "../include/semi_vibe_comm.h"
#include "../include/semi_vibe_protocol.h"

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>

#define BUFFER_SIZE 256
#define COMMAND_SIZE 7 // 6 hex digits + null terminator
#define ERROR_MESSAGE_SIZE 256
#define DEFAULT_TIMEOUT_MS 5000

// Map error codes to their corresponding values in the header file
#define DRIVER_ERROR_COMMUNICATION DRIVER_ERROR_COMMUNICATION_FAILED
#define DRIVER_ERROR_PROTOCOL DRIVER_ERROR_PROTOCOL_ERROR
#define DRIVER_ERROR_VERIFICATION DRIVER_ERROR_DEVICE_ERROR
#define DRIVER_ERROR_TIMEOUT 9 // Value from semi_vibe_driver.h

// Driver state structure (internal implementation of the opaque handle)
struct DriverHandle
{
    LogCallback log_callback;
    CommContext comm_context;
    bool initialized;
    int last_error;
    char last_error_message[ERROR_MESSAGE_SIZE];
    CRITICAL_SECTION lock;
    unsigned int timeout_ms;
};

// Forward declarations
static void driver_log_callback_wrapper(const char *message, void *user_data);
static bool read_register(struct DriverHandle *handle, uint8_t base, uint8_t offset, uint8_t *value);
static bool write_register(struct DriverHandle *handle, uint8_t base, uint8_t offset, uint8_t value);
static void set_last_error(struct DriverHandle *handle, int error_code, const char *format, ...);
static bool format_read_command(char *command, size_t command_size, uint8_t base, uint8_t offset);
static bool format_write_command(char *command, size_t command_size, uint8_t base, uint8_t offset, uint8_t value);
static bool parse_response(const char *response, uint8_t *value);

/**
 * @brief Wrapper for the log callback
 *
 * @param message Log message
 * @param user_data User data (driver handle)
 */
static void driver_log_callback_wrapper(const char *message, void *user_data)
{
    struct DriverHandle *handle = (struct DriverHandle *)user_data;
    if (handle && handle->log_callback)
    {
        handle->log_callback(message);
    }
}

/**
 * @brief Set the last error message and code
 *
 * @param handle Driver handle
 * @param error_code Error code
 * @param format Format string
 * @param ... Format arguments
 */
static void set_last_error(struct DriverHandle *handle, int error_code, const char *format, ...)
{
    if (!handle)
    {
        return;
    }

    handle->last_error = error_code;

    va_list args;
    va_start(args, format);

#ifdef _MSC_VER
    // Use secure vsnprintf_s on Windows
    vsnprintf_s(handle->last_error_message, ERROR_MESSAGE_SIZE, _TRUNCATE, format, args);
#else
    // Use standard vsnprintf with explicit null termination
    int result = vsnprintf(handle->last_error_message, ERROR_MESSAGE_SIZE, format, args);
    if (result < 0 || result >= ERROR_MESSAGE_SIZE)
    {
        // Ensure null termination in case of truncation or error
        handle->last_error_message[ERROR_MESSAGE_SIZE - 1] = '\0';
    }
#endif

    va_end(args);

    // Log the error if a callback is available
    if (handle->log_callback)
    {
        handle->log_callback(handle->last_error_message);
    }
}

/**
 * @brief Create a new driver instance
 *
 * @param handle Pointer to store the created driver handle
 * @param log_callback Callback function for logging (can be NULL)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_create(DriverHandle *handle, LogCallback log_callback, int *error_code)
{
    if (!handle)
    {
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    // Allocate memory for the driver handle
    struct DriverHandle *new_handle = (struct DriverHandle *)malloc(sizeof(struct DriverHandle));
    if (!new_handle)
    {
        if (error_code)
        {
            *error_code = DRIVER_ERROR_RESOURCE_UNAVAILABLE;
        }
        return false;
    }

    // Initialize the driver handle
    memset(new_handle, 0, sizeof(struct DriverHandle));
    new_handle->log_callback = log_callback;
    new_handle->initialized = false;
    new_handle->last_error = DRIVER_ERROR_NONE;
    new_handle->timeout_ms = DEFAULT_TIMEOUT_MS;

    // Initialize the critical section for thread safety
    InitializeCriticalSection(&new_handle->lock);

    // Initialize the communication layer
    if (!comm_init(&new_handle->comm_context, driver_log_callback_wrapper, new_handle))
    {
        set_last_error(new_handle, DRIVER_ERROR_INTERNAL, "Failed to initialize communication layer");
        DeleteCriticalSection(&new_handle->lock);
        free(new_handle);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INTERNAL;
        }
        return false;
    }

    new_handle->initialized = true;
    if (new_handle->log_callback)
    {
        new_handle->log_callback("Semi-Vibe-Driver instance created");
    }

    *handle = new_handle;
    if (error_code)
    {
        *error_code = DRIVER_ERROR_NONE;
    }
    return true;
}

/**
 * @brief Destroy a driver instance
 *
 * @param handle Driver handle
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_destroy(DriverHandle handle, int *error_code)
{
    if (!handle)
    {
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    struct DriverHandle *driver = (struct DriverHandle *)handle;

    // Acquire lock
    EnterCriticalSection(&driver->lock);

    // Disconnect if connected
    if (driver->comm_context.connected)
    {
        comm_disconnect(&driver->comm_context, true);
    }

    // Release lock before deleting it
    LeaveCriticalSection(&driver->lock);

    // Delete critical section
    DeleteCriticalSection(&driver->lock);

    // Free memory
    free(driver);

    if (error_code)
    {
        *error_code = DRIVER_ERROR_NONE;
    }
    return true;
}

/**
 * @brief Get the last error message
 *
 * @param handle Driver handle
 * @param buffer Buffer to store the error message
 * @param buffer_size Size of the buffer
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_last_error_message(DriverHandle handle, char *buffer, size_t buffer_size)
{
    if (!handle || !buffer || buffer_size == 0)
    {
        return false;
    }

    struct DriverHandle *driver = (struct DriverHandle *)handle;

    // Acquire lock
    EnterCriticalSection(&driver->lock);

    // Copy error message
#ifdef _MSC_VER
    strncpy_s(buffer, buffer_size, driver->last_error_message, buffer_size - 1);
#else
    strncpy(buffer, driver->last_error_message, buffer_size - 1);
#endif
    buffer[buffer_size - 1] = '\0';

    // Release lock
    LeaveCriticalSection(&driver->lock);

    return true;
}

/**
 * @brief Set the operation timeout
 *
 * @param handle Driver handle
 * @param timeout_ms Timeout in milliseconds
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_set_timeout(DriverHandle handle, unsigned int timeout_ms, int *error_code)
{
    if (!handle)
    {
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    struct DriverHandle *driver = (struct DriverHandle *)handle;

    // Acquire lock
    EnterCriticalSection(&driver->lock);

    // Set timeout in driver
    driver->timeout_ms = timeout_ms;

    // Update timeout in communication layer if initialized
    bool result = true;
    if (driver->initialized)
    {
        result = comm_set_timeout(&driver->comm_context, timeout_ms);
        if (!result)
        {
            set_last_error(driver, DRIVER_ERROR_INTERNAL, "Failed to set timeout in communication layer");
            if (error_code)
            {
                *error_code = DRIVER_ERROR_INTERNAL;
            }
        }
    }

    // Release lock
    LeaveCriticalSection(&driver->lock);

    if (error_code && result)
    {
        *error_code = DRIVER_ERROR_NONE;
    }
    return result;
}

/**
 * @brief Connect to the device
 *
 * @param handle Driver handle
 * @param host Hostname or IP address (defaults to localhost)
 * @param port Port number (defaults to 8989)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if connection was successful
 */
EXPORT bool driver_connect(DriverHandle handle, const char *host, int port, int *error_code)
{
    if (!handle)
    {
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    struct DriverHandle *driver = (struct DriverHandle *)handle;

    // Acquire lock
    EnterCriticalSection(&driver->lock);

    if (!driver->initialized)
    {
        set_last_error(driver, DRIVER_ERROR_NOT_INITIALIZED, "Driver is not initialized");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_NOT_INITIALIZED;
        }
        return false;
    }

    if (driver->comm_context.connected)
    {
        if (driver->log_callback)
        {
            driver->log_callback("Driver is already connected");
        }
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_NONE;
        }
        return true;
    }

    // Set timeout for the connection
    comm_set_timeout(&driver->comm_context, driver->timeout_ms);

    // Connect to device
    bool result = comm_connect(&driver->comm_context, host, port);
    if (!result)
    {
        set_last_error(driver, DRIVER_ERROR_CONNECTION_FAILED, "Failed to connect to device at %s:%d", host, port);
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_CONNECTION_FAILED;
        }
        return false;
    }

    // Release lock
    LeaveCriticalSection(&driver->lock);

    if (error_code)
    {
        *error_code = DRIVER_ERROR_NONE;
    }
    return true;
}

/**
 * @brief Disconnect from the device
 *
 * @param handle Driver handle
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if disconnection was successful
 */
EXPORT bool driver_disconnect(DriverHandle handle, int *error_code)
{
    if (!handle)
    {
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    struct DriverHandle *driver = (struct DriverHandle *)handle;

    // Acquire lock
    EnterCriticalSection(&driver->lock);

    if (!driver->comm_context.connected)
    {
        if (driver->log_callback)
        {
            driver->log_callback("Driver is not connected");
        }
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_NONE;
        }
        return true;
    }

    // Disconnect from device
    bool result = comm_disconnect(&driver->comm_context, true);
    if (!result)
    {
        set_last_error(driver, DRIVER_ERROR_COMMUNICATION, "Failed to disconnect from device");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_COMMUNICATION;
        }
        return false;
    }

    // Release lock
    LeaveCriticalSection(&driver->lock);

    if (error_code)
    {
        *error_code = DRIVER_ERROR_NONE;
    }
    return true;
}

/**
 * @brief Get the device status
 *
 * @param handle Driver handle
 * @param status Pointer to DeviceStatus structure to be filled
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if status was retrieved successfully
 */
EXPORT bool driver_get_status(DriverHandle handle, DeviceStatus *status, int *error_code)
{
    if (!handle || !status)
    {
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    struct DriverHandle *driver = (struct DriverHandle *)handle;

    // Acquire lock
    EnterCriticalSection(&driver->lock);

    if (!driver->comm_context.connected)
    {
        set_last_error(driver, DRIVER_ERROR_NOT_CONNECTED, "Driver is not connected");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_NOT_CONNECTED;
        }
        return false;
    }

    uint8_t connected_device = 0;
    uint8_t power_state = 0;
    uint8_t error_state = 0;

    // Read status registers
    bool result = true;
    if (!read_register(driver, BASE_MAIN, OFFSET_CONNECTED_DEVICE, &connected_device) ||
        !read_register(driver, BASE_MAIN, OFFSET_POWER_STATE, &power_state) ||
        !read_register(driver, BASE_MAIN, OFFSET_ERROR_STATE, &error_state))
    {
        // Error already set by read_register
        result = false;
    }
    else
    {
        // Fill status structure
        status->connected = (connected_device != 0);
        status->sensors_powered = ((power_state & (MASK_TEMP_SENSOR | MASK_HUMID_SENSOR)) != 0);
        status->actuators_powered = ((power_state & (MASK_LED | MASK_FAN | MASK_HEATER | MASK_DOORS)) != 0);
        status->has_errors = (error_state != 0);
    }

    // Release lock
    LeaveCriticalSection(&driver->lock);

    if (error_code)
    {
        *error_code = result ? DRIVER_ERROR_NONE : driver->last_error;
    }
    return result;
}

/**
 * @brief Get humidity value
 *
 * @param handle Driver handle
 * @param value Pointer to store the humidity value (0-100)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if value was retrieved successfully
 */
EXPORT bool driver_get_humidity(DriverHandle handle, uint8_t *value, int *error_code)
{
    if (!handle || !value)
    {
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    struct DriverHandle *driver = (struct DriverHandle *)handle;

    // Acquire lock
    EnterCriticalSection(&driver->lock);

    if (!driver->comm_context.connected)
    {
        set_last_error(driver, DRIVER_ERROR_NOT_CONNECTED, "Driver is not connected");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_NOT_CONNECTED;
        }
        return false;
    }

    bool result = read_register(driver, BASE_SENSOR, OFFSET_HUMID_VALUE, value);

    // Release lock
    LeaveCriticalSection(&driver->lock);

    if (error_code)
    {
        *error_code = result ? DRIVER_ERROR_NONE : driver->last_error;
    }
    return result;
}

/**
 * @brief Get temperature value
 *
 * @param handle Driver handle
 * @param value Pointer to store the temperature value (0-255)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if value was retrieved successfully
 */
EXPORT bool driver_get_temperature(DriverHandle handle, uint8_t *value, int *error_code)
{
    if (!handle || !value)
    {
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    struct DriverHandle *driver = (struct DriverHandle *)handle;

    // Acquire lock
    EnterCriticalSection(&driver->lock);

    if (!driver->comm_context.connected)
    {
        set_last_error(driver, DRIVER_ERROR_NOT_CONNECTED, "Driver is not connected");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_NOT_CONNECTED;
        }
        return false;
    }

    bool result = read_register(driver, BASE_SENSOR, OFFSET_TEMP_VALUE, value);

    // Release lock
    LeaveCriticalSection(&driver->lock);

    if (error_code)
    {
        *error_code = result ? DRIVER_ERROR_NONE : driver->last_error;
    }
    return result;
}

/**
 * @brief Set LED value
 *
 * @param handle Driver handle
 * @param value LED brightness (0-255)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if value was set successfully
 */
EXPORT bool driver_set_led(DriverHandle handle, uint8_t value, int *error_code)
{
    if (!handle)
    {
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    struct DriverHandle *driver = (struct DriverHandle *)handle;

    // Acquire lock
    EnterCriticalSection(&driver->lock);

    if (!driver->comm_context.connected)
    {
        set_last_error(driver, DRIVER_ERROR_NOT_CONNECTED, "Driver is not connected");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_NOT_CONNECTED;
        }
        return false;
    }

    bool result = write_register(driver, BASE_ACTUATOR, OFFSET_LED, value);

    // Release lock
    LeaveCriticalSection(&driver->lock);

    if (error_code)
    {
        *error_code = result ? DRIVER_ERROR_NONE : driver->last_error;
    }
    return result;
}

/**
 * @brief Get LED value
 *
 * @param handle Driver handle
 * @param value Pointer to store the LED brightness (0-255)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if value was retrieved successfully
 */
EXPORT bool driver_get_led(DriverHandle handle, uint8_t *value, int *error_code)
{
    if (!handle || !value)
    {
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    struct DriverHandle *driver = (struct DriverHandle *)handle;

    // Acquire lock
    EnterCriticalSection(&driver->lock);

    if (!driver->comm_context.connected)
    {
        set_last_error(driver, DRIVER_ERROR_NOT_CONNECTED, "Driver is not connected");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_NOT_CONNECTED;
        }
        return false;
    }

    bool result = read_register(driver, BASE_ACTUATOR, OFFSET_LED, value);

    // Release lock
    LeaveCriticalSection(&driver->lock);

    if (error_code)
    {
        *error_code = result ? DRIVER_ERROR_NONE : driver->last_error;
    }
    return result;
}

/**
 * @brief Set fan value
 *
 * @param handle Driver handle
 * @param value Fan speed (0-255)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if value was set successfully
 */
EXPORT bool driver_set_fan(DriverHandle handle, uint8_t value, int *error_code)
{
    if (!handle)
    {
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    struct DriverHandle *driver = (struct DriverHandle *)handle;

    // Acquire lock
    EnterCriticalSection(&driver->lock);

    if (!driver->comm_context.connected)
    {
        set_last_error(driver, DRIVER_ERROR_NOT_CONNECTED, "Driver is not connected");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_NOT_CONNECTED;
        }
        return false;
    }

    bool result = write_register(driver, BASE_ACTUATOR, OFFSET_FAN, value);

    // Release lock
    LeaveCriticalSection(&driver->lock);

    if (error_code)
    {
        *error_code = result ? DRIVER_ERROR_NONE : driver->last_error;
    }
    return result;
}

/**
 * @brief Get fan value
 *
 * @param handle Driver handle
 * @param value Pointer to store the fan speed (0-255)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if value was retrieved successfully
 */
EXPORT bool driver_get_fan(DriverHandle handle, uint8_t *value, int *error_code)
{
    if (!handle || !value)
    {
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    struct DriverHandle *driver = (struct DriverHandle *)handle;

    // Acquire lock
    EnterCriticalSection(&driver->lock);

    if (!driver->comm_context.connected)
    {
        set_last_error(driver, DRIVER_ERROR_NOT_CONNECTED, "Driver is not connected");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_NOT_CONNECTED;
        }
        return false;
    }

    bool result = read_register(driver, BASE_ACTUATOR, OFFSET_FAN, value);

    // Release lock
    LeaveCriticalSection(&driver->lock);

    if (error_code)
    {
        *error_code = result ? DRIVER_ERROR_NONE : driver->last_error;
    }
    return result;
}

/**
 * @brief Set heater value
 *
 * @param handle Driver handle
 * @param value Heater level (0-15, only lower 4 bits used)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if value was set successfully
 */
EXPORT bool driver_set_heater(DriverHandle handle, uint8_t value, int *error_code)
{
    if (!handle)
    {
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    struct DriverHandle *driver = (struct DriverHandle *)handle;

    // Acquire lock
    EnterCriticalSection(&driver->lock);

    if (!driver->comm_context.connected)
    {
        set_last_error(driver, DRIVER_ERROR_NOT_CONNECTED, "Driver is not connected");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_NOT_CONNECTED;
        }
        return false;
    }

    // Only use lower 4 bits as per LAW.md (heater is 0-15)
    uint8_t heater_value = value & MASK_HEATER_VALUE;

    // Read current value to preserve reserved bits
    uint8_t current_value;
    if (!read_register(driver, BASE_ACTUATOR, OFFSET_HEATER, &current_value))
    {
        // Error already set by read_register
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = driver->last_error;
        }
        return false;
    }

    // Preserve the reserved bits (upper 4 bits)
    uint8_t new_value = (current_value & ~MASK_HEATER_VALUE) | heater_value;

    bool result = write_register(driver, BASE_ACTUATOR, OFFSET_HEATER, new_value);

    // Release lock
    LeaveCriticalSection(&driver->lock);

    if (error_code)
    {
        *error_code = result ? DRIVER_ERROR_NONE : driver->last_error;
    }
    return result;
}

/**
 * @brief Get heater value
 *
 * @param handle Driver handle
 * @param value Pointer to store the heater level (0-15)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if value was retrieved successfully
 */
EXPORT bool driver_get_heater(DriverHandle handle, uint8_t *value, int *error_code)
{
    if (!handle || !value)
    {
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    struct DriverHandle *driver = (struct DriverHandle *)handle;

    // Acquire lock
    EnterCriticalSection(&driver->lock);

    if (!driver->comm_context.connected)
    {
        set_last_error(driver, DRIVER_ERROR_NOT_CONNECTED, "Driver is not connected");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_NOT_CONNECTED;
        }
        return false;
    }

    bool result = read_register(driver, BASE_ACTUATOR, OFFSET_HEATER, value);
    if (result)
    {
        // Ensure only lower 4 bits are returned
        *value &= 0x0F;
    }

    // Release lock
    LeaveCriticalSection(&driver->lock);

    if (error_code)
    {
        *error_code = result ? DRIVER_ERROR_NONE : driver->last_error;
    }
    return result;
}

/**
 * @brief Set the state of a specific door
 *
 * @param handle Driver handle
 * @param door_id Door identifier (DOOR_1, DOOR_2, DOOR_3, or DOOR_4)
 * @param state Door state (DOOR_OPEN or DOOR_CLOSED)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_set_door(DriverHandle handle, int door_id, int state, int *error_code)
{
    if (!handle)
    {
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    struct DriverHandle *driver = (struct DriverHandle *)handle;

    // Acquire lock
    EnterCriticalSection(&driver->lock);

    if (!driver->comm_context.connected)
    {
        set_last_error(driver, DRIVER_ERROR_NOT_CONNECTED, "Driver is not connected");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_NOT_CONNECTED;
        }
        return false;
    }

    if (door_id < DOOR_1 || door_id > DOOR_4 || (state != DOOR_OPEN && state != DOOR_CLOSED))
    {
        set_last_error(driver, DRIVER_ERROR_INVALID_PARAMETER, "Invalid door ID or state");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
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
    if (!read_register(driver, BASE_ACTUATOR, OFFSET_DOORS, &current_value))
    {
        // Error already set by read_register
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = driver->last_error;
        }
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

    // Ensure we only modify valid bits (bits 0,2,4,6) as per LAW.md
    // MASK_DOORS_VALUE is 0x55 (01010101 in binary) which masks bits 0,2,4,6
    new_value = (current_value & ~MASK_DOORS_VALUE) | (new_value & MASK_DOORS_VALUE);

    // Write the new value
    bool result = write_register(driver, BASE_ACTUATOR, OFFSET_DOORS, new_value);

    // Verify the write operation by reading back the value
    if (result)
    {
        uint8_t verify_value;
        if (read_register(driver, BASE_ACTUATOR, OFFSET_DOORS, &verify_value))
        {
            // Check if the bit was set/cleared as expected
            bool expected_bit_state = (state == DOOR_OPEN);
            bool actual_bit_state = (verify_value & (1 << bit_position)) != 0;

            if (expected_bit_state != actual_bit_state)
            {
                set_last_error(driver, DRIVER_ERROR_DEVICE_ERROR, "Door state verification failed");
                result = false;
            }
        }
    }

    // Release lock
    LeaveCriticalSection(&driver->lock);

    if (error_code)
    {
        *error_code = result ? DRIVER_ERROR_NONE : driver->last_error;
    }
    return result;
}

/**
 * @brief Get the state of a specific door
 *
 * @param handle Driver handle
 * @param door_id Door identifier (DOOR_1, DOOR_2, DOOR_3, or DOOR_4)
 * @param state Pointer to store the door state (DOOR_OPEN or DOOR_CLOSED)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_door_state(DriverHandle handle, int door_id, int *state, int *error_code)
{
    if (!handle || !state)
    {
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    struct DriverHandle *driver = (struct DriverHandle *)handle;

    // Acquire lock
    EnterCriticalSection(&driver->lock);

    if (!driver->comm_context.connected)
    {
        set_last_error(driver, DRIVER_ERROR_NOT_CONNECTED, "Driver is not connected");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_NOT_CONNECTED;
        }
        return false;
    }

    if (door_id < DOOR_1 || door_id > DOOR_4)
    {
        set_last_error(driver, DRIVER_ERROR_INVALID_PARAMETER, "Invalid door ID");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    /* IMPORTANT: This function always reads the current door state directly from the hardware.
     * This ensures we always have the most up-to-date state, which is critical for functional
     * safety elements like doors.
     */
    uint8_t door_value;
    bool result = read_register(driver, BASE_ACTUATOR, OFFSET_DOORS, &door_value);
    if (result)
    {
        // Calculate bit position (DOOR_1->0, DOOR_2->2, DOOR_3->4, DOOR_4->6)
        int bit_position = (door_id - 1) * 2;

        // Check if the bit is set (door open) or clear (door closed)
        *state = (door_value & (1 << bit_position)) ? DOOR_OPEN : DOOR_CLOSED;
    }

    // Release lock
    LeaveCriticalSection(&driver->lock);

    if (error_code)
    {
        *error_code = result ? DRIVER_ERROR_NONE : driver->last_error;
    }
    return result;
}

/**
 * @brief Send a command and receive a response
 *
 * @param handle Driver handle
 * @param request Message structure for the request
 * @param response Message structure for the response
 * @return true if command was sent and response received successfully
 */
static bool send_and_receive(struct DriverHandle *handle, const SemiVibeMessage *request, SemiVibeMessage *response)
{
    if (!handle || !handle->comm_context.connected || !request || !response)
    {
        if (handle)
        {
            set_last_error(handle, DRIVER_ERROR_INVALID_PARAMETER, "Invalid parameters for send_and_receive");
        }
        return false;
    }

    char command[COMMAND_SIZE];
    char response_str[BUFFER_SIZE];

    // Format the request message
    if (!protocol_format_message(request, command))
    {
        set_last_error(handle, DRIVER_ERROR_PROTOCOL, "Failed to format command");
        return false;
    }

    // Send command and receive response
    if (!comm_send_receive(&handle->comm_context, command, response_str, BUFFER_SIZE))
    {
        // Check if it was a timeout
        if (comm_get_last_error(&handle->comm_context) == COMM_ERROR_TIMEOUT)
        {
            set_last_error(handle, DRIVER_ERROR_TIMEOUT, "Communication timeout during operation");
        }
        else
        {
            set_last_error(handle, DRIVER_ERROR_COMMUNICATION, "Failed to send/receive command");
        }
        return false;
    }

    // Parse the response
    if (!protocol_parse_message(response_str, response))
    {
        set_last_error(handle, DRIVER_ERROR_PROTOCOL, "Failed to parse response: %s", response_str);
        return false;
    }

    // Log error responses but don't treat them as failures
    if (protocol_is_error(response))
    {
        set_last_error(handle, DRIVER_ERROR_DEVICE_ERROR, "Device returned error code %d", response->error);
    }

    return true;
}

/**
 * @brief Validate register access permissions
 *
 * @param base Base register address
 * @param offset Register offset
 * @param is_write Whether this is a write operation
 * @return true if access is allowed, false otherwise
 */
static bool validate_register_access(uint8_t base, uint8_t offset, bool is_write)
{
    // BASE_RESERVED (0x0) is not accessible
    if (base == BASE_RESERVED)
    {
        return false;
    }

    // BASE_MAIN (0x1) and BASE_SENSOR (0x2) are read-only
    if (is_write && (base == BASE_MAIN || base == BASE_SENSOR))
    {
        return false;
    }

    // BASE_ACTUATOR (0x3) and BASE_CONTROL (0x4) are read/write
    if (base == BASE_ACTUATOR)
    {
        // For heater, ensure we're only writing to the lower 4 bits
        if (is_write && offset == OFFSET_HEATER)
        {
            return true; // We mask the value in driver_set_heater
        }

        // For doors, ensure we're only writing to the valid bits (0,2,4,6)
        if (is_write && offset == OFFSET_DOORS)
        {
            return true; // We mask the value in driver_set_door
        }

        return true;
    }

    if (base == BASE_CONTROL)
    {
        // Only specific control registers are valid
        return (offset == OFFSET_POWER_SENSORS || offset == OFFSET_POWER_ACTUATORS || offset == OFFSET_RESET_SENSORS ||
                offset == OFFSET_RESET_ACTUATORS);
    }

    // Default to allowing access
    return true;
}

/**
 * @brief Read a register value
 *
 * @param handle Driver handle
 * @param base Base register address
 * @param offset Register offset
 * @param value Pointer to store the register value
 * @return true if successful, false otherwise
 */
static bool read_register(struct DriverHandle *handle, uint8_t base, uint8_t offset, uint8_t *value)
{
    if (!handle || !value)
    {
        return false;
    }

    // Check if connected
    if (!handle->comm_context.connected)
    {
        set_last_error(handle, DRIVER_ERROR_NOT_CONNECTED, "Not connected to device");
        return false;
    }

    // Validate register access
    if (!validate_register_access(base, offset, false))
    {
        set_last_error(handle, DRIVER_ERROR_INVALID_PARAMETER, "Invalid register access (read)");
        return false;
    }

    // Format the read command
    char command[COMMAND_SIZE];
    if (!format_read_command(command, COMMAND_SIZE, base, offset))
    {
        set_last_error(handle, DRIVER_ERROR_INTERNAL, "Failed to format read command");
        return false;
    }

    // Send command and receive response
    char response[BUFFER_SIZE];
    if (!comm_send_receive(&handle->comm_context, command, response, BUFFER_SIZE))
    {
        // Check if it was a timeout
        if (comm_get_last_error(&handle->comm_context) == COMM_ERROR_TIMEOUT)
        {
            set_last_error(handle, DRIVER_ERROR_TIMEOUT, "Communication timeout during read operation");
        }
        else
        {
            set_last_error(handle, DRIVER_ERROR_COMMUNICATION, "Failed to communicate with device");
        }
        return false;
    }

    // Parse the response
    uint8_t parsed_value;
    if (!parse_response(response, &parsed_value))
    {
        set_last_error(handle, DRIVER_ERROR_PROTOCOL, "Failed to parse response: %s", response);
        return false;
    }

    *value = parsed_value;
    return true;
}

/**
 * @brief Write a value to a register
 *
 * @param handle Driver handle
 * @param base Base register address
 * @param offset Register offset
 * @param value Value to write
 * @return true if successful, false otherwise
 */
static bool write_register(struct DriverHandle *handle, uint8_t base, uint8_t offset, uint8_t value)
{
    if (!handle)
    {
        return false;
    }

    // Check if connected
    if (!handle->comm_context.connected)
    {
        set_last_error(handle, DRIVER_ERROR_NOT_CONNECTED, "Not connected to device");
        return false;
    }

    // Validate register access
    if (!validate_register_access(base, offset, true))
    {
        set_last_error(handle, DRIVER_ERROR_INVALID_PARAMETER, "Invalid register access (write)");
        return false;
    }

    // Format the write command
    char command[COMMAND_SIZE];
    if (!format_write_command(command, COMMAND_SIZE, base, offset, value))
    {
        set_last_error(handle, DRIVER_ERROR_INTERNAL, "Failed to format write command");
        return false;
    }

    // Send command and receive response
    char response[BUFFER_SIZE];
    if (!comm_send_receive(&handle->comm_context, command, response, BUFFER_SIZE))
    {
        // Check if it was a timeout
        if (comm_get_last_error(&handle->comm_context) == COMM_ERROR_TIMEOUT)
        {
            set_last_error(handle, DRIVER_ERROR_TIMEOUT, "Communication timeout during write operation");
        }
        else
        {
            set_last_error(handle, DRIVER_ERROR_COMMUNICATION, "Failed to communicate with device");
        }
        return false;
    }

    // Parse the response
    uint8_t parsed_value;
    if (!parse_response(response, &parsed_value))
    {
        set_last_error(handle, DRIVER_ERROR_PROTOCOL, "Failed to parse response: %s", response);
        return false;
    }

    // Verify the write operation
    if (parsed_value != value)
    {
        set_last_error(handle, DRIVER_ERROR_VERIFICATION, "Write verification failed: expected 0x%02X, got 0x%02X", value, parsed_value);
        return false;
    }

    return true;
}

/**
 * @brief Get power state of a specific component
 *
 * @param handle Driver handle
 * @param component_type Type of component (0=TEMPERATURE, 1=HUMIDITY, 2=LED, 3=FAN, 4=HEATER, 5=DOORS)
 * @param powered Pointer to store the power state (true=powered, false=not powered)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_power_state(DriverHandle handle, int component_type, bool *powered, int *error_code)
{
    if (!handle || !powered)
    {
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    struct DriverHandle *driver = (struct DriverHandle *)handle;

    // Acquire lock
    EnterCriticalSection(&driver->lock);

    if (!driver->comm_context.connected)
    {
        set_last_error(driver, DRIVER_ERROR_NOT_CONNECTED, "Driver is not connected");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_NOT_CONNECTED;
        }
        return false;
    }

    if (component_type < COMPONENT_TEMPERATURE || component_type > COMPONENT_DOORS)
    {
        set_last_error(driver, DRIVER_ERROR_INVALID_PARAMETER, "Invalid component type");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    uint8_t power_state = 0;
    bool result = read_register(driver, BASE_MAIN, OFFSET_POWER_STATE, &power_state);
    if (result)
    {
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
        }

        // Check if the bit is set
        *powered = (power_state & mask) != 0;
    }

    // Release lock
    LeaveCriticalSection(&driver->lock);

    if (error_code)
    {
        *error_code = result ? DRIVER_ERROR_NONE : driver->last_error;
    }
    return result;
}

/**
 * @brief Get error state of a specific component
 *
 * @param handle Driver handle
 * @param component_type Type of component (0=TEMPERATURE, 1=HUMIDITY, 2=LED, 3=FAN, 4=HEATER, 5=DOORS)
 * @param has_error Pointer to store the error state (true=has error, false=no error)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_error_state(DriverHandle handle, int component_type, bool *has_error, int *error_code)
{
    if (!handle || !has_error)
    {
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    struct DriverHandle *driver = (struct DriverHandle *)handle;

    // Acquire lock
    EnterCriticalSection(&driver->lock);

    if (!driver->comm_context.connected)
    {
        set_last_error(driver, DRIVER_ERROR_NOT_CONNECTED, "Driver is not connected");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_NOT_CONNECTED;
        }
        return false;
    }

    if (component_type < COMPONENT_TEMPERATURE || component_type > COMPONENT_DOORS)
    {
        set_last_error(driver, DRIVER_ERROR_INVALID_PARAMETER, "Invalid component type");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    uint8_t error_state = 0;
    bool result = read_register(driver, BASE_MAIN, OFFSET_ERROR_STATE, &error_state);
    if (result)
    {
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
        }

        // Check if the bit is set
        *has_error = (error_state & mask) != 0;
    }

    // Release lock
    LeaveCriticalSection(&driver->lock);

    if (error_code)
    {
        *error_code = result ? DRIVER_ERROR_NONE : driver->last_error;
    }
    return result;
}

/**
 * @brief Send a raw command to the device
 *
 * @param handle Driver handle
 * @param command Command string
 * @param response Buffer to store response
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if command was sent successfully
 */
EXPORT bool driver_send_command(DriverHandle handle, const char *command, char *response, int *error_code)
{
    if (!handle || !command || !response)
    {
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    struct DriverHandle *driver = (struct DriverHandle *)handle;

    // Acquire lock
    EnterCriticalSection(&driver->lock);

    if (!driver->comm_context.connected)
    {
        set_last_error(driver, DRIVER_ERROR_NOT_CONNECTED, "Driver is not connected");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_NOT_CONNECTED;
        }
        return false;
    }

    // Parse the command
    SemiVibeMessage request = {0};
    if (!protocol_parse_message(command, &request))
    {
        set_last_error(driver, DRIVER_ERROR_PROTOCOL, "Failed to parse command");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_PROTOCOL;
        }
        return false;
    }

    // Create response message
    SemiVibeMessage response_msg = {0};

    // Send request and receive response
    bool result = send_and_receive(driver, &request, &response_msg);
    if (!result)
    {
        // Error already set by send_and_receive
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = driver->last_error;
        }
        return false;
    }

    // Format the response
    if (!protocol_format_message(&response_msg, response))
    {
        set_last_error(driver, DRIVER_ERROR_PROTOCOL, "Failed to format response");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_PROTOCOL;
        }
        return false;
    }

    // Release lock
    LeaveCriticalSection(&driver->lock);

    if (error_code)
    {
        *error_code = DRIVER_ERROR_NONE;
    }
    return true;
}

/**
 * @brief Set power state of a specific component
 *
 * @param handle Driver handle
 * @param component_type Type of component (0=TEMPERATURE, 1=HUMIDITY, 2=LED, 3=FAN, 4=HEATER, 5=DOORS)
 * @param powered Power state to set (true=powered, false=not powered)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_set_power_state(DriverHandle handle, int component_type, bool powered, int *error_code)
{
    if (!handle)
    {
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    struct DriverHandle *driver = (struct DriverHandle *)handle;

    // Acquire lock
    EnterCriticalSection(&driver->lock);

    if (!driver->comm_context.connected)
    {
        set_last_error(driver, DRIVER_ERROR_NOT_CONNECTED, "Driver is not connected");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_NOT_CONNECTED;
        }
        return false;
    }

    if (component_type < COMPONENT_TEMPERATURE || component_type > COMPONENT_DOORS)
    {
        set_last_error(driver, DRIVER_ERROR_INVALID_PARAMETER, "Invalid component type");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    bool result = false;

    // For sensors
    if (component_type == COMPONENT_TEMPERATURE || component_type == COMPONENT_HUMIDITY)
    {
        // Read current power state to preserve the other sensor's state
        uint8_t current_power_state = 0;
        if (!read_register(driver, BASE_CONTROL, OFFSET_POWER_SENSORS, &current_power_state))
        {
            // Error already set by read_register
            LeaveCriticalSection(&driver->lock);
            if (error_code)
            {
                *error_code = driver->last_error;
            }
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
        result = write_register(driver, BASE_CONTROL, OFFSET_POWER_SENSORS, value);
    }
    // For actuators
    else
    {
        // Read current power state to preserve other actuators' states
        uint8_t current_power_state = 0;
        if (!read_register(driver, BASE_CONTROL, OFFSET_POWER_ACTUATORS, &current_power_state))
        {
            // Error already set by read_register
            LeaveCriticalSection(&driver->lock);
            if (error_code)
            {
                *error_code = driver->last_error;
            }
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
        }

        // Create bitmask and write to register
        uint8_t value = protocol_create_bitmask(4, led_on, BIT_LED, fan_on, BIT_FAN, heater_on, BIT_HEATER, doors_on, BIT_DOORS);
        result = write_register(driver, BASE_CONTROL, OFFSET_POWER_ACTUATORS, value);
    }

    // Release lock
    LeaveCriticalSection(&driver->lock);

    if (error_code)
    {
        *error_code = result ? DRIVER_ERROR_NONE : driver->last_error;
    }
    return result;
}

/**
 * @brief Reset a specific component
 *
 * @param handle Driver handle
 * @param component_type Type of component (0=TEMPERATURE, 1=HUMIDITY, 2=LED, 3=FAN, 4=HEATER, 5=DOORS)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_reset_component(DriverHandle handle, int component_type, int *error_code)
{
    if (!handle)
    {
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    struct DriverHandle *driver = (struct DriverHandle *)handle;

    // Acquire lock
    EnterCriticalSection(&driver->lock);

    if (!driver->comm_context.connected)
    {
        set_last_error(driver, DRIVER_ERROR_NOT_CONNECTED, "Driver is not connected");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_NOT_CONNECTED;
        }
        return false;
    }

    if (component_type < COMPONENT_TEMPERATURE || component_type > COMPONENT_DOORS)
    {
        set_last_error(driver, DRIVER_ERROR_INVALID_PARAMETER, "Invalid component type");
        LeaveCriticalSection(&driver->lock);
        if (error_code)
        {
            *error_code = DRIVER_ERROR_INVALID_PARAMETER;
        }
        return false;
    }

    bool result = false;

    // For sensors
    if (component_type == COMPONENT_TEMPERATURE || component_type == COMPONENT_HUMIDITY)
    {
        // Read current reset state to preserve the other sensor's state
        uint8_t current_reset_state = 0;
        if (!read_register(driver, BASE_CONTROL, OFFSET_RESET_SENSORS, &current_reset_state))
        {
            // Error already set by read_register
            LeaveCriticalSection(&driver->lock);
            if (error_code)
            {
                *error_code = driver->last_error;
            }
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
        result = write_register(driver, BASE_CONTROL, OFFSET_RESET_SENSORS, value);
    }
    // For actuators
    else
    {
        // Read current reset state to preserve other actuators' states
        uint8_t current_reset_state = 0;
        if (!read_register(driver, BASE_CONTROL, OFFSET_RESET_ACTUATORS, &current_reset_state))
        {
            // Error already set by read_register
            LeaveCriticalSection(&driver->lock);
            if (error_code)
            {
                *error_code = driver->last_error;
            }
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
        result = write_register(driver, BASE_CONTROL, OFFSET_RESET_ACTUATORS, value);
    }

    // Release lock
    LeaveCriticalSection(&driver->lock);

    if (error_code)
    {
        *error_code = result ? DRIVER_ERROR_NONE : driver->last_error;
    }
    return result;
}

/**
 * @brief Format a read command
 *
 * @param command Buffer to store the formatted command
 * @param command_size Size of the command buffer
 * @param base Base register address
 * @param offset Register offset
 * @return true if successful, false otherwise
 */
static bool format_read_command(char *command, size_t command_size, uint8_t base, uint8_t offset)
{
    if (!command || command_size < COMMAND_SIZE)
    {
        return false;
    }

    // Validate parameters
    if (base > 0xF || offset > 0xFF)
    {
        return false;
    }

    // Create a message structure
    SemiVibeMessage message = {0};
    message.base = base;
    message.offset = offset;
    message.rw = 0; // Read
    message.data = 0;

    // Format the message
    return protocol_format_message(&message, command);
}

/**
 * @brief Format a write command
 *
 * @param command Buffer to store the formatted command
 * @param command_size Size of the command buffer
 * @param base Base register address
 * @param offset Register offset
 * @param value Value to write
 * @return true if successful, false otherwise
 */
static bool format_write_command(char *command, size_t command_size, uint8_t base, uint8_t offset, uint8_t value)
{
    if (!command || command_size < COMMAND_SIZE)
    {
        return false;
    }

    // Validate parameters
    if (base > 0xF || offset > 0xFF)
    {
        return false;
    }

    // Create a message structure
    SemiVibeMessage message = {0};
    message.base = base;
    message.offset = offset;
    message.rw = 1; // Write
    message.data = value;

    // Format the message
    return protocol_format_message(&message, command);
}

/**
 * @brief Parse a response string
 *
 * @param response Response string
 * @param value Pointer to store the parsed value
 * @return true if successful, false otherwise
 */
static bool parse_response(const char *response, uint8_t *value)
{
    if (!response || !value)
    {
        return false;
    }

    // Validate response length
    size_t response_len = strlen(response);
    if (response_len < 6 || response_len >= BUFFER_SIZE)
    {
        return false;
    }

    // Parse the response
    SemiVibeMessage message = {0};
    if (!protocol_parse_message(response, &message))
    {
        return false;
    }

    // Check for error
    if (protocol_is_error(&message))
    {
        return false;
    }

    // Store the value
    *value = message.data;
    return true;
}