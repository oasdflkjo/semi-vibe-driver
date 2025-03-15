/**
 * @file semi_vibe_driver.c
 * @brief Implementation of the Semi-Vibe-Driver
 */

#include "../include/semi_vibe_driver.h"
#include "../include/semi_vibe_protocol.h"

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
typedef SOCKET socket_t;
#define SOCKET_ERROR_VALUE INVALID_SOCKET
#define close_socket closesocket

#define BUFFER_SIZE 256
#define DEFAULT_PORT 8989
#define DEFAULT_HOST "localhost"
#define COMMAND_SIZE 7 // 6 hex digits + null terminator

// Protocol constants
#define BASE_MAIN 0x1
#define BASE_SENSOR 0x2
#define BASE_ACTUATOR 0x3
#define BASE_CONTROL 0x4

#define OFFSET_CONNECTED_DEVICE 0x00
#define OFFSET_POWER_STATE 0x02
#define OFFSET_ERROR_STATE 0x03

#define OFFSET_TEMP_ID 0x10
#define OFFSET_TEMP_VALUE 0x11
#define OFFSET_HUMID_ID 0x20
#define OFFSET_HUMID_VALUE 0x21

#define OFFSET_LED 0x10
#define OFFSET_FAN 0x20
#define OFFSET_HEATER 0x30
#define OFFSET_DOORS 0x40

#define OFFSET_POWER_SENSORS 0xFB
#define OFFSET_POWER_ACTUATORS 0xFC
#define OFFSET_RESET_SENSORS 0xFD
#define OFFSET_RESET_ACTUATORS 0xFE

#define CMD_READ 0x0
#define CMD_WRITE 0x1

// Bit masks
#define MASK_TEMP_SENSOR 0x01
#define MASK_HUMID_SENSOR 0x10
#define MASK_LED 0x01
#define MASK_FAN 0x04
#define MASK_HEATER 0x10
#define MASK_DOORS 0x40
#define MASK_HEATER_VALUE 0x0F
#define MASK_DOORS_VALUE 0x55

// Bit positions for better readability
#define BIT_TEMP_SENSOR 0
#define BIT_HUMID_SENSOR 4
#define BIT_LED 0
#define BIT_FAN 2
#define BIT_HEATER 4
#define BIT_DOORS 6

// Driver state
typedef struct {
  LogCallback log_callback;
  socket_t socket;
  bool initialized;
  bool connected;
} DriverState;

// Global driver state
static DriverState g_driver = {.log_callback = NULL, .socket = SOCKET_ERROR_VALUE, .initialized = false, .connected = false};

// Forward declarations
static void log_message(const char *format, ...);
static bool send_and_receive(const SemiVibeMessage *request, SemiVibeMessage *response);
static bool read_register(uint8_t base, uint8_t offset, uint8_t *value);
static bool write_register(uint8_t base, uint8_t offset, uint8_t value);

/**
 * @brief Initialize the driver
 *
 * @param log_callback Optional callback for logging
 * @return true if initialization was successful
 */
EXPORT bool driver_init(LogCallback log_callback) {
  if (g_driver.initialized) {
    log_message("Driver is already initialized");
    return true;
  }

  g_driver.log_callback = log_callback;

  // Initialize Winsock
  WSADATA wsaData;
  if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
    log_message("WSAStartup failed");
    return false;
  }

  g_driver.initialized = true;
  log_message("Semi-Vibe-Driver initialized");
  return true;
}

/**
 * @brief Connect to the device
 *
 * @param host Hostname or IP address (defaults to localhost)
 * @param port Port number (defaults to 8989)
 * @return true if connection was successful
 */
EXPORT bool driver_connect(const char *host, int port) {
  if (!g_driver.initialized) {
    log_message("Driver is not initialized");
    return false;
  }

  if (g_driver.connected) {
    log_message("Driver is already connected");
    return true;
  }

  // Use default values if not provided
  if (host == NULL) {
    host = DEFAULT_HOST;
  }
  if (port <= 0) {
    port = DEFAULT_PORT;
  }

  // Create socket
  g_driver.socket = socket(AF_INET, SOCK_STREAM, 0);
  if (g_driver.socket == SOCKET_ERROR_VALUE) {
    log_message("Failed to create socket");
    return false;
  }

  // Connect to server
  struct sockaddr_in server_addr;
  server_addr.sin_family = AF_INET;
  server_addr.sin_port = htons(port);

  // Convert hostname to IP address
  struct hostent *he;
  if ((he = gethostbyname(host)) == NULL) {
    log_message("Failed to resolve hostname");
    close_socket(g_driver.socket);
    g_driver.socket = SOCKET_ERROR_VALUE;
    return false;
  }

  // Copy the IP address
  memcpy(&server_addr.sin_addr, he->h_addr_list[0], he->h_length);

  if (connect(g_driver.socket, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
    log_message("Connection failed");
    close_socket(g_driver.socket);
    g_driver.socket = SOCKET_ERROR_VALUE;
    return false;
  }

  // Wait for ACK message
  char buffer[BUFFER_SIZE];
  memset(buffer, 0, BUFFER_SIZE);
  int bytes_received = recv(g_driver.socket, buffer, BUFFER_SIZE - 1, 0);
  if (bytes_received <= 0) {
    log_message("Failed to receive ACK message");
    close_socket(g_driver.socket);
    g_driver.socket = SOCKET_ERROR_VALUE;
    return false;
  }

  buffer[bytes_received] = '\0';
  if (strcmp(buffer, "ACK") != 0) {
    log_message("Invalid ACK message: %s", buffer);
    close_socket(g_driver.socket);
    g_driver.socket = SOCKET_ERROR_VALUE;
    return false;
  }

  g_driver.connected = true;
  log_message("Connected to device at %s:%d", host, port);
  return true;
}

/**
 * @brief Disconnect from the device
 *
 * @return true if disconnection was successful
 */
EXPORT bool driver_disconnect() {
  if (!g_driver.connected) {
    log_message("Driver is not connected");
    return true;
  }

  // Send exit command
  const char *exit_command = "exit";
  send(g_driver.socket, exit_command, (int)strlen(exit_command), 0);

  // Close socket
  close_socket(g_driver.socket);
  g_driver.socket = SOCKET_ERROR_VALUE;
  g_driver.connected = false;

  log_message("Disconnected from device");
  return true;
}

/**
 * @brief Get the device status
 *
 * @param status Pointer to DeviceStatus structure to be filled
 * @return true if status was retrieved successfully
 */
EXPORT bool driver_get_status(DeviceStatus *status) {
  if (!g_driver.connected || !status) {
    return false;
  }

  uint8_t connected_device = 0;
  uint8_t power_state = 0;
  uint8_t error_state = 0;

  // Read status registers
  if (!read_register(BASE_MAIN, OFFSET_CONNECTED_DEVICE, &connected_device) ||
      !read_register(BASE_MAIN, OFFSET_POWER_STATE, &power_state) || !read_register(BASE_MAIN, OFFSET_ERROR_STATE, &error_state)) {
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
EXPORT bool driver_get_humidity(uint8_t *value) {
  if (!g_driver.connected || !value) {
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
EXPORT bool driver_get_temperature(uint8_t *value) {
  if (!g_driver.connected || !value) {
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
EXPORT bool driver_set_led(uint8_t value) { return write_register(BASE_ACTUATOR, OFFSET_LED, value); }

/**
 * @brief Get LED value
 *
 * @param value Pointer to store the LED brightness (0-255)
 * @return true if value was retrieved successfully
 */
EXPORT bool driver_get_led(uint8_t *value) {
  if (!g_driver.connected || !value) {
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
EXPORT bool driver_set_fan(uint8_t value) { return write_register(BASE_ACTUATOR, OFFSET_FAN, value); }

/**
 * @brief Get fan value
 *
 * @param value Pointer to store the fan speed (0-255)
 * @return true if value was retrieved successfully
 */
EXPORT bool driver_get_fan(uint8_t *value) {
  if (!g_driver.connected || !value) {
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
EXPORT bool driver_set_heater(uint8_t value) {
  // Heater only uses lower 4 bits
  return write_register(BASE_ACTUATOR, OFFSET_HEATER, value & MASK_HEATER_VALUE);
}

/**
 * @brief Get heater value
 *
 * @param value Pointer to store the heater level (0-15)
 * @return true if value was retrieved successfully
 */
EXPORT bool driver_get_heater(uint8_t *value) {
  if (!g_driver.connected || !value) {
    return false;
  }

  uint8_t raw_value;
  if (!read_register(BASE_ACTUATOR, OFFSET_HEATER, &raw_value)) {
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
EXPORT bool driver_set_door(int door_id, int state) {
  if (!g_driver.connected || door_id < DOOR_1 || door_id > DOOR_4 || (state != DOOR_OPEN && state != DOOR_CLOSED)) {
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
  if (!read_register(BASE_ACTUATOR, OFFSET_DOORS, &current_value)) {
    return false;
  }

  // Calculate bit position (DOOR_1->0, DOOR_2->2, DOOR_3->4, DOOR_4->6)
  int bit_position = (door_id - 1) * 2;

  // Set or clear the bit based on state
  uint8_t new_value;
  if (state == DOOR_OPEN) {
    new_value = current_value | (1 << bit_position); // Set bit
  } else {
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
EXPORT bool driver_get_door_state(int door_id, int *state) {
  if (!g_driver.connected || door_id < DOOR_1 || door_id > DOOR_4 || state == NULL) {
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
  if (!read_register(BASE_ACTUATOR, OFFSET_DOORS, &current_value)) {
    return false;
  }

  // Calculate bit position (DOOR_1->0, DOOR_2->2, DOOR_3->4, DOOR_4->6)
  int bit_position = (door_id - 1) * 2;

  // Check if the bit is set
  *state = (current_value & (1 << bit_position)) ? DOOR_OPEN : DOOR_CLOSED;

  return true;
}

/**
 * @brief Helper function to create a bitmask from boolean values
 *
 * @param count Number of boolean parameters
 * @param ... Boolean values and their corresponding bit positions
 * @return uint8_t Resulting bitmask
 */
static uint8_t create_bitmask(int count, ...) {
  va_list args;
  uint8_t mask = 0;

  va_start(args, count);
  for (int i = 0; i < count; i++) {
    bool value = va_arg(args, int); // bool is promoted to int in varargs
    int bit_position = va_arg(args, int);
    if (value) {
      mask |= (1 << bit_position);
    }
  }
  va_end(args);

  return mask;
}

/**
 * @brief Power sensors on/off
 *
 * @param temperature_on Whether temperature sensor should be powered
 * @param humidity_on Whether humidity sensor should be powered
 * @return true if power state was set successfully
 */
EXPORT bool driver_power_sensors(bool temperature_on, bool humidity_on) {
  uint8_t value = create_bitmask(2, temperature_on, BIT_TEMP_SENSOR, humidity_on, BIT_HUMID_SENSOR);
  return write_register(BASE_CONTROL, OFFSET_POWER_SENSORS, value);
}

/**
 * @brief Power actuators on/off
 *
 * @param led_on Whether LED should be powered
 * @param fan_on Whether fan should be powered
 * @param heater_on Whether heater should be powered
 * @param doors_on Whether doors should be powered
 * @return true if power state was set successfully
 */
EXPORT bool driver_power_actuators(bool led_on, bool fan_on, bool heater_on, bool doors_on) {
  uint8_t value = create_bitmask(4, led_on, BIT_LED, fan_on, BIT_FAN, heater_on, BIT_HEATER, doors_on, BIT_DOORS);
  return write_register(BASE_CONTROL, OFFSET_POWER_ACTUATORS, value);
}

/**
 * @brief Reset sensors
 *
 * @param reset_temperature Whether to reset temperature sensor
 * @param reset_humidity Whether to reset humidity sensor
 * @return true if reset was successful
 */
EXPORT bool driver_reset_sensors(bool reset_temperature, bool reset_humidity) {
  uint8_t value = create_bitmask(2, reset_temperature, BIT_TEMP_SENSOR, reset_humidity, BIT_HUMID_SENSOR);
  return write_register(BASE_CONTROL, OFFSET_RESET_SENSORS, value);
}

/**
 * @brief Reset actuators
 *
 * @param reset_led Whether to reset LED
 * @param reset_fan Whether to reset fan
 * @param reset_heater Whether to reset heater
 * @param reset_doors Whether to reset doors
 * @return true if reset was successful
 */
EXPORT bool driver_reset_actuators(bool reset_led, bool reset_fan, bool reset_heater, bool reset_doors) {
  uint8_t value = create_bitmask(4, reset_led, BIT_LED, reset_fan, BIT_FAN, reset_heater, BIT_HEATER, reset_doors, BIT_DOORS);
  return write_register(BASE_CONTROL, OFFSET_RESET_ACTUATORS, value);
}

/**
 * @brief Send a command and receive a response
 *
 * @param request Message structure for the request
 * @param response Message structure for the response
 * @return true if command was sent and response received successfully
 */
static bool send_and_receive(const SemiVibeMessage *request, SemiVibeMessage *response) {
  if (!g_driver.connected || !request || !response) {
    return false;
  }

  char command[COMMAND_SIZE];
  char response_str[BUFFER_SIZE];

  // Format the request message
  if (!format_message(request, command)) {
    log_message("Failed to format command");
    return false;
  }

  // Log the command being sent
  log_message("Sending command: %s", command);

  // Send command
  if (send(g_driver.socket, command, (int)strlen(command), 0) < 0) {
    log_message("Failed to send command");
    return false;
  }

  // Receive response
  memset(response_str, 0, BUFFER_SIZE);
  int bytes_received = recv(g_driver.socket, response_str, BUFFER_SIZE - 1, 0);
  if (bytes_received <= 0) {
    log_message("Failed to receive response");
    return false;
  }

  response_str[bytes_received] = '\0';

  // Parse the response
  if (!parse_message(response_str, response)) {
    log_message("Failed to parse response: %s", response_str);
    return false;
  }

  // Log error responses but don't treat them as failures
  if (response->error > 0) {
    log_message("Error response: %s", response_str);
  }

  log_message("Received response: %s", response_str);
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
static bool read_register(uint8_t base, uint8_t offset, uint8_t *value) {
  if (!g_driver.connected || !value) {
    return false;
  }

  // Create request message
  SemiVibeMessage request = {.base = base, .offset = offset, .rw = CMD_READ, .data = 0, .error = 0};

  // Create response message
  SemiVibeMessage response = {0};

  // Send request and receive response
  if (!send_and_receive(&request, &response)) {
    return false;
  }

  // Check for errors
  if (response.error > 0) {
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
static bool write_register(uint8_t base, uint8_t offset, uint8_t value) {
  if (!g_driver.connected) {
    return false;
  }

  // Create request message
  SemiVibeMessage request = {.base = base, .offset = offset, .rw = CMD_WRITE, .data = value, .error = 0};

  // Create response message
  SemiVibeMessage response = {0};

  // Send request and receive response
  if (!send_and_receive(&request, &response)) {
    return false;
  }

  // Check for errors
  if (response.error > 0) {
    return false;
  }

  // Check if response matches request (write operations echo back the command)
  return (response.base == request.base && response.offset == request.offset && response.rw == request.rw && response.data == request.data);
}

/**
 * @brief Send a raw command to the device
 *
 * @param command Command string
 * @param response Buffer to store response
 * @return true if command was sent successfully
 */
EXPORT bool driver_send_command(const char *command, char *response) {
  if (!g_driver.connected || !command || !response) {
    return false;
  }

  // Parse the command
  SemiVibeMessage request = {0};
  if (!parse_message(command, &request)) {
    log_message("Failed to parse command: %s", command);
    return false;
  }

  // Create response message
  SemiVibeMessage response_msg = {0};

  // Send request and receive response
  if (!send_and_receive(&request, &response_msg)) {
    return false;
  }

  // Format the response
  if (!format_message(&response_msg, response)) {
    log_message("Failed to format response");
    return false;
  }

  return true;
}

/**
 * @brief Log a message using the callback if set
 *
 * @param format Format string
 * @param ... Format arguments
 */
static void log_message(const char *format, ...) {
  if (g_driver.log_callback) {
    char buffer[BUFFER_SIZE];
    va_list args;
    va_start(args, format);
    vsnprintf(buffer, BUFFER_SIZE, format, args);
    va_end(args);

    g_driver.log_callback(buffer);
  }
}