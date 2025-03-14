/**
 * @file semi_vibe_driver.c
 * @brief Implementation of the Semi-Vibe-Driver
 */

#include "../include/semi_vibe_driver.h"

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

// Driver state
typedef struct {
  LogCallback log_callback;
  socket_t socket;
  bool initialized;
  bool connected;
} DriverState;

// Global driver state
static DriverState g_driver = {.log_callback = NULL,
                               .socket = SOCKET_ERROR_VALUE,
                               .initialized = false,
                               .connected = false};

// Forward declarations
static void log_message(const char *format, ...);
static bool build_command(char *buffer, uint8_t base, uint8_t offset,
                          uint8_t rw, uint8_t data);
static bool send_and_receive(const char *command, char *response,
                             size_t response_size);
static bool read_register(uint8_t base, uint8_t offset, uint8_t *value);
static bool write_register(uint8_t base, uint8_t offset, uint8_t value);

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

  if (connect(g_driver.socket, (struct sockaddr *)&server_addr,
              sizeof(server_addr)) < 0) {
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

EXPORT bool driver_get_status(DeviceStatus *status) {
  if (!g_driver.connected || !status) {
    return false;
  }

  uint8_t connected_device = 0;
  uint8_t power_state = 0;
  uint8_t error_state = 0;

  // Read status registers
  if (!read_register(BASE_MAIN, OFFSET_CONNECTED_DEVICE, &connected_device) ||
      !read_register(BASE_MAIN, OFFSET_POWER_STATE, &power_state) ||
      !read_register(BASE_MAIN, OFFSET_ERROR_STATE, &error_state)) {
    return false;
  }

  // Fill status structure
  status->connected = (connected_device != 0);
  status->sensors_powered =
      ((power_state & (MASK_TEMP_SENSOR | MASK_HUMID_SENSOR)) != 0);
  status->actuators_powered =
      ((power_state & (MASK_LED | MASK_FAN | MASK_HEATER | MASK_DOORS)) != 0);
  status->has_errors = (error_state != 0);

  return true;
}

EXPORT bool driver_get_sensors(SensorData *data) {
  if (!g_driver.connected || !data) {
    return false;
  }

  // Read sensor registers
  if (!read_register(BASE_SENSOR, OFFSET_TEMP_ID, &data->temperature_id) ||
      !read_register(BASE_SENSOR, OFFSET_TEMP_VALUE,
                     &data->temperature_value) ||
      !read_register(BASE_SENSOR, OFFSET_HUMID_ID, &data->humidity_id) ||
      !read_register(BASE_SENSOR, OFFSET_HUMID_VALUE, &data->humidity_value)) {
    return false;
  }

  return true;
}

EXPORT bool driver_get_actuators(ActuatorData *data) {
  if (!g_driver.connected || !data) {
    return false;
  }

  // Read actuator registers
  if (!read_register(BASE_ACTUATOR, OFFSET_LED, &data->led_value) ||
      !read_register(BASE_ACTUATOR, OFFSET_FAN, &data->fan_value) ||
      !read_register(BASE_ACTUATOR, OFFSET_HEATER, &data->heater_value) ||
      !read_register(BASE_ACTUATOR, OFFSET_DOORS, &data->doors_value)) {
    return false;
  }

  return true;
}

EXPORT bool driver_set_led(uint8_t value) {
  return write_register(BASE_ACTUATOR, OFFSET_LED, value);
}

EXPORT bool driver_set_fan(uint8_t value) {
  return write_register(BASE_ACTUATOR, OFFSET_FAN, value);
}

EXPORT bool driver_set_heater(uint8_t value) {
  // Heater only uses lower 4 bits
  return write_register(BASE_ACTUATOR, OFFSET_HEATER,
                        value & MASK_HEATER_VALUE);
}

EXPORT bool driver_set_doors(uint8_t value) {
  // Doors only use bits 0, 2, 4, 6
  return write_register(BASE_ACTUATOR, OFFSET_DOORS, value & MASK_DOORS_VALUE);
}

EXPORT bool driver_power_sensors(bool temperature_on, bool humidity_on) {
  uint8_t value = 0;
  if (temperature_on)
    value |= MASK_TEMP_SENSOR;
  if (humidity_on)
    value |= MASK_HUMID_SENSOR;

  return write_register(BASE_CONTROL, OFFSET_POWER_SENSORS, value);
}

EXPORT bool driver_power_actuators(bool led_on, bool fan_on, bool heater_on,
                                   bool doors_on) {
  uint8_t value = 0;
  if (led_on)
    value |= MASK_LED;
  if (fan_on)
    value |= MASK_FAN;
  if (heater_on)
    value |= MASK_HEATER;
  if (doors_on)
    value |= MASK_DOORS;

  return write_register(BASE_CONTROL, OFFSET_POWER_ACTUATORS, value);
}

EXPORT bool driver_reset_sensors(bool reset_temperature, bool reset_humidity) {
  uint8_t value = 0;
  if (reset_temperature)
    value |= MASK_TEMP_SENSOR;
  if (reset_humidity)
    value |= MASK_HUMID_SENSOR;

  return write_register(BASE_CONTROL, OFFSET_RESET_SENSORS, value);
}

EXPORT bool driver_reset_actuators(bool reset_led, bool reset_fan,
                                   bool reset_heater, bool reset_doors) {
  uint8_t value = 0;
  if (reset_led)
    value |= MASK_LED;
  if (reset_fan)
    value |= MASK_FAN;
  if (reset_heater)
    value |= MASK_HEATER;
  if (reset_doors)
    value |= MASK_DOORS;

  return write_register(BASE_CONTROL, OFFSET_RESET_ACTUATORS, value);
}

EXPORT bool driver_send_command(const char *command, char *response) {
  if (!g_driver.connected || !command || !response) {
    return false;
  }

  return send_and_receive(command, response, BUFFER_SIZE);
}

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

static bool build_command(char *buffer, uint8_t base, uint8_t offset,
                          uint8_t rw, uint8_t data) {
  if (!buffer) {
    return false;
  }

  // Format: <base><offset><rw><data>
  snprintf(buffer, COMMAND_SIZE, "%1X%02X%1X%02X", base, offset, rw, data);
  return true;
}

static bool send_and_receive(const char *command, char *response,
                             size_t response_size) {
  if (!g_driver.connected || !command || !response || response_size < 7) {
    return false;
  }

  // Send command
  if (send(g_driver.socket, command, (int)strlen(command), 0) < 0) {
    log_message("Failed to send command");
    return false;
  }

  // Receive response
  memset(response, 0, response_size);
  int bytes_received = recv(g_driver.socket, response, response_size - 1, 0);
  if (bytes_received <= 0) {
    log_message("Failed to receive response");
    return false;
  }

  response[bytes_received] = '\0';

  // Log error responses but don't treat them as failures
  if (response[0] >= '1' && response[0] <= '3' && bytes_received >= 6 &&
      strcmp(response + 1, "FFFFF") == 0) {
    log_message("Error response: %s", response);
  }

  return true;
}

static bool read_register(uint8_t base, uint8_t offset, uint8_t *value) {
  if (!g_driver.connected || !value) {
    return false;
  }

  char command[COMMAND_SIZE];
  char response[BUFFER_SIZE];

  // Build read command (RW=0, data=00)
  if (!build_command(command, base, offset, CMD_READ, 0x00)) {
    return false;
  }

  // Send command and receive response
  if (!send_and_receive(command, response, BUFFER_SIZE)) {
    return false;
  }

  // Parse response (last 2 characters are the data)
  if (strlen(response) >= 6) {
    *value = (uint8_t)strtol(response + 4, NULL, 16);
    return true;
  }

  return false;
}

static bool write_register(uint8_t base, uint8_t offset, uint8_t value) {
  if (!g_driver.connected) {
    return false;
  }

  char command[COMMAND_SIZE];
  char response[BUFFER_SIZE];

  // Build write command (RW=1, data=value)
  if (!build_command(command, base, offset, CMD_WRITE, value)) {
    return false;
  }

  // Send command and receive response
  if (!send_and_receive(command, response, BUFFER_SIZE)) {
    return false;
  }

  // Check if response matches command (write operations echo back the command)
  return (strcmp(command, response) == 0);
}