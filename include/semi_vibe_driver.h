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

// Door identifiers
#define DOOR_1 1
#define DOOR_2 2
#define DOOR_3 3
#define DOOR_4 4

// Door states
#define DOOR_CLOSED 0
#define DOOR_OPEN 1

// Callback function type for driver logging
typedef void (*LogCallback)(const char *message);

// Device sensor data structure
typedef struct {
  uint8_t temperature_id;
  uint8_t temperature_value;
  uint8_t humidity_id;
  uint8_t humidity_value;
} SensorData;

// Device actuator data structure
typedef struct {
  uint8_t led_value;
  uint8_t fan_value;
  uint8_t heater_value;
  uint8_t doors_value;
} ActuatorData;

// Device status structure
typedef struct {
  bool connected;
  bool sensors_powered;
  bool actuators_powered;
  bool has_errors;
} DeviceStatus;

/**
 * @brief Initialize the driver
 * @param log_callback Callback function for logging
 * @return true if successful, false otherwise
 */
EXPORT bool driver_init(LogCallback log_callback);

/**
 * @brief Connect to the device
 * @param host Hostname or IP address
 * @param port Port number
 * @return true if successful, false otherwise
 */
EXPORT bool driver_connect(const char *host, int port);

/**
 * @brief Disconnect from the device
 * @return true if successful, false otherwise
 */
EXPORT bool driver_disconnect();

/**
 * @brief Get device status
 * @param status Pointer to status structure to fill
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_status(DeviceStatus *status);

/**
 * @brief Get sensor data
 * @param data Pointer to sensor data structure to fill
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_sensors(SensorData *data);

/**
 * @brief Get humidity value
 * @param value Pointer to store the humidity value (0-100)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_humidity(uint8_t *value);

/**
 * @brief Get temperature value
 * @param value Pointer to store the temperature value (0-255)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_temperature(uint8_t *value);

/**
 * @brief Get actuator data
 * @param data Pointer to actuator data structure to fill
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_actuators(ActuatorData *data);

/**
 * @brief Set LED value
 * @param value Value to set (0-255)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_set_led(uint8_t value);

/**
 * @brief Get LED value
 * @param value Pointer to store the LED brightness (0-255)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_led(uint8_t *value);

/**
 * @brief Set fan value
 * @param value Value to set (0-255)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_set_fan(uint8_t value);

/**
 * @brief Get fan value
 * @param value Pointer to store the fan speed (0-255)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_fan(uint8_t *value);

/**
 * @brief Set heater value
 * @param value Value to set (0-15)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_set_heater(uint8_t value);

/**
 * @brief Get heater value
 * @param value Pointer to store the heater level (0-15)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_heater(uint8_t *value);

/**
 * @brief Set the state of a specific door
 * @param door_id Door identifier (DOOR_1, DOOR_2, DOOR_3, or DOOR_4)
 * @param state Door state (DOOR_OPEN or DOOR_CLOSED)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_set_door(int door_id, int state);

/**
 * @brief Get the state of a specific door
 * @param door_id Door identifier (DOOR_1, DOOR_2, DOOR_3, or DOOR_4)
 * @param state Pointer to store the door state (DOOR_OPEN or DOOR_CLOSED)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_get_door_state(int door_id, int *state);

/**
 * @brief Power on/off sensors
 * @param temperature_on Power state for temperature sensor
 * @param humidity_on Power state for humidity sensor
 * @return true if successful, false otherwise
 */
EXPORT bool driver_power_sensors(bool temperature_on, bool humidity_on);

/**
 * @brief Power on/off actuators
 * @param led_on Power state for LED
 * @param fan_on Power state for fan
 * @param heater_on Power state for heater
 * @param doors_on Power state for doors
 * @return true if successful, false otherwise
 */
EXPORT bool driver_power_actuators(bool led_on, bool fan_on, bool heater_on, bool doors_on);

/**
 * @brief Reset sensors
 * @param reset_temperature Reset temperature sensor
 * @param reset_humidity Reset humidity sensor
 * @return true if successful, false otherwise
 */
EXPORT bool driver_reset_sensors(bool reset_temperature, bool reset_humidity);

/**
 * @brief Reset actuators
 * @param reset_led Reset LED
 * @param reset_fan Reset fan
 * @param reset_heater Reset heater
 * @param reset_doors Reset doors
 * @return true if successful, false otherwise
 */
EXPORT bool driver_reset_actuators(bool reset_led, bool reset_fan, bool reset_heater, bool reset_doors);

/**
 * @brief Send a raw command to the device
 * @param command Command string (6 hex digits)
 * @param response Buffer to store response (must be at least 7 bytes)
 * @return true if successful, false otherwise
 */
EXPORT bool driver_send_command(const char *command, char *response);

#ifdef __cplusplus
}
#endif

#endif /* SEMI_VIBE_DRIVER_H */