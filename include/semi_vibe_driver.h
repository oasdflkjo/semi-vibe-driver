/**
 * @file semi_vibe_driver.h
 * @brief Header file for the Semi-Vibe-Driver
 */

#ifndef SEMI_VIBE_DRIVER_H
#define SEMI_VIBE_DRIVER_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

// Component types
#define COMPONENT_TEMPERATURE 0
#define COMPONENT_HUMIDITY 1
#define COMPONENT_LED 2
#define COMPONENT_FAN 3
#define COMPONENT_HEATER 4
#define COMPONENT_DOORS 5

// Door identifiers
#define DOOR_1 1
#define DOOR_2 2
#define DOOR_3 3
#define DOOR_4 4

// Door states
#define DOOR_CLOSED 0
#define DOOR_OPEN 1

// Error codes
#define DRIVER_ERROR_NONE 0
#define DRIVER_ERROR_NOT_INITIALIZED 1
#define DRIVER_ERROR_ALREADY_INITIALIZED 2
#define DRIVER_ERROR_CONNECTION_FAILED 3
#define DRIVER_ERROR_NOT_CONNECTED 4
#define DRIVER_ERROR_INVALID_PARAMETER 5
#define DRIVER_ERROR_COMMUNICATION_FAILED 6
#define DRIVER_ERROR_PROTOCOL_ERROR 7
#define DRIVER_ERROR_DEVICE_ERROR 8
#define DRIVER_ERROR_TIMEOUT 9
#define DRIVER_ERROR_RESOURCE_UNAVAILABLE 10
#define DRIVER_ERROR_INTERNAL 11

// Callback function type for driver logging
typedef void (*LogCallback)(const char *message);

// Device sensor data structure
typedef struct
{
    uint8_t temperature_id;
    uint8_t temperature_value;
    uint8_t humidity_id;
    uint8_t humidity_value;
} SensorData;

// Device actuator data structure
typedef struct
{
    uint8_t led_value;
    uint8_t fan_value;
    uint8_t heater_value;
    uint8_t doors_value;
} ActuatorData;

// Device status structure
typedef struct
{
    bool connected;
    bool sensors_powered;
    bool actuators_powered;
    bool has_errors;
} DeviceStatus;

// Opaque driver handle
typedef struct DriverHandle *DriverHandle;

/**
 * @brief Create a new driver instance
 * @param handle Pointer to store the created driver handle
 * @param log_callback Callback function for logging (can be NULL)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_create(DriverHandle *handle, LogCallback log_callback, int *error_code);

/**
 * @brief Destroy a driver instance
 * @param handle Driver handle
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_destroy(DriverHandle handle, int *error_code);

/**
 * @brief Connect to the device
 * @param handle Driver handle
 * @param host Hostname or IP address
 * @param port Port number
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_connect(DriverHandle handle, const char *host, int port, int *error_code);

/**
 * @brief Disconnect from the device
 * @param handle Driver handle
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_disconnect(DriverHandle handle, int *error_code);

/**
 * @brief Get device status
 * @param handle Driver handle
 * @param status Pointer to status structure to fill
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_status(DriverHandle handle, DeviceStatus *status, int *error_code);

/**
 * @brief Get humidity value
 * @param handle Driver handle
 * @param value Pointer to store the humidity value (0-100)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_humidity(DriverHandle handle, uint8_t *value, int *error_code);

/**
 * @brief Get temperature value
 * @param handle Driver handle
 * @param value Pointer to store the temperature value (0-255)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_temperature(DriverHandle handle, uint8_t *value, int *error_code);

/**
 * @brief Set LED value
 * @param handle Driver handle
 * @param value Value to set (0-255)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_set_led(DriverHandle handle, uint8_t value, int *error_code);

/**
 * @brief Get LED value
 * @param handle Driver handle
 * @param value Pointer to store the LED brightness (0-255)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_led(DriverHandle handle, uint8_t *value, int *error_code);

/**
 * @brief Set fan value
 * @param handle Driver handle
 * @param value Value to set (0-255)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_set_fan(DriverHandle handle, uint8_t value, int *error_code);

/**
 * @brief Get fan value
 * @param handle Driver handle
 * @param value Pointer to store the fan speed (0-255)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_fan(DriverHandle handle, uint8_t *value, int *error_code);

/**
 * @brief Set heater value
 * @param handle Driver handle
 * @param value Value to set (0-15)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_set_heater(DriverHandle handle, uint8_t value, int *error_code);

/**
 * @brief Get heater value
 * @param handle Driver handle
 * @param value Pointer to store the heater level (0-15)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_heater(DriverHandle handle, uint8_t *value, int *error_code);

/**
 * @brief Set the state of a specific door
 * @param handle Driver handle
 * @param door_id Door identifier (DOOR_1, DOOR_2, DOOR_3, or DOOR_4)
 * @param state Door state (DOOR_OPEN or DOOR_CLOSED)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_set_door(DriverHandle handle, int door_id, int state, int *error_code);

/**
 * @brief Get the state of a specific door
 * @param handle Driver handle
 * @param door_id Door identifier (DOOR_1, DOOR_2, DOOR_3, or DOOR_4)
 * @param state Pointer to store the door state (DOOR_OPEN or DOOR_CLOSED)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_door_state(DriverHandle handle, int door_id, int *state, int *error_code);

/**
 * @brief Get power state of a specific component
 * @param handle Driver handle
 * @param component_type Type of component (0=TEMPERATURE, 1=HUMIDITY, 2=LED, 3=FAN, 4=HEATER, 5=DOORS)
 * @param powered Pointer to store the power state (true=powered, false=not powered)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_power_state(DriverHandle handle, int component_type, bool *powered, int *error_code);

/**
 * @brief Get error state of a specific component
 * @param handle Driver handle
 * @param component_type Type of component (0=TEMPERATURE, 1=HUMIDITY, 2=LED, 3=FAN, 4=HEATER, 5=DOORS)
 * @param has_error Pointer to store the error state (true=has error, false=no error)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_error_state(DriverHandle handle, int component_type, bool *has_error, int *error_code);

/**
 * @brief Send a raw command to the device
 * @param handle Driver handle
 * @param command Command string (6 hex digits)
 * @param response Buffer to store response (must be at least 7 bytes)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 *
 * @note This function is not part of the official API and is only for testing purposes and should be dropped to null in production.
 */
EXPORT bool driver_send_command(DriverHandle handle, const char *command, char *response, int *error_code);

/**
 * @brief Set power state of a specific component
 * @param handle Driver handle
 * @param component_type Type of component (0=TEMPERATURE, 1=HUMIDITY, 2=LED, 3=FAN, 4=HEATER, 5=DOORS)
 * @param powered Power state to set (true=powered, false=not powered)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_set_power_state(DriverHandle handle, int component_type, bool powered, int *error_code);

/**
 * @brief Reset a specific component
 * @param handle Driver handle
 * @param component_type Type of component (0=TEMPERATURE, 1=HUMIDITY, 2=LED, 3=FAN, 4=HEATER, 5=DOORS)
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_reset_component(DriverHandle handle, int component_type, int *error_code);

/**
 * @brief Get the last error message
 * @param handle Driver handle
 * @param buffer Buffer to store the error message
 * @param buffer_size Size of the buffer
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_last_error_message(DriverHandle handle, char *buffer, size_t buffer_size);

/**
 * @brief Set the operation timeout
 * @param handle Driver handle
 * @param timeout_ms Timeout in milliseconds
 * @param error_code Pointer to store error code (can be NULL)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_set_timeout(DriverHandle handle, unsigned int timeout_ms, int *error_code);

#ifdef __cplusplus
}
#endif

#endif /* SEMI_VIBE_DRIVER_H */