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

// Global variables
static LogCallback g_log_callback = NULL;
static socket_t g_socket = SOCKET_ERROR_VALUE;
static bool g_initialized = false;
static bool g_connected = false;

// Forward declarations
static void log_message(const char *format, ...);
static bool send_and_receive(const char *command, char *response);

EXPORT bool driver_init(LogCallback log_callback) {
  if (g_initialized) {
    log_message("Driver is already initialized");
    return true;
  }

  g_log_callback = log_callback;

  // Initialize Winsock
  WSADATA wsaData;
  if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
    log_message("WSAStartup failed");
    return false;
  }

  g_initialized = true;
  log_message("Semi-Vibe-Driver initialized");
  return true;
}

EXPORT bool driver_connect(const char *host, int port) {
  if (!g_initialized) {
    log_message("Driver is not initialized");
    return false;
  }

  if (g_connected) {
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
  g_socket = socket(AF_INET, SOCK_STREAM, 0);
  if (g_socket == SOCKET_ERROR_VALUE) {
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
    close_socket(g_socket);
    g_socket = SOCKET_ERROR_VALUE;
    return false;
  }

  // Copy the IP address
  memcpy(&server_addr.sin_addr, he->h_addr_list[0], he->h_length);

  if (connect(g_socket, (struct sockaddr *)&server_addr, sizeof(server_addr)) <
      0) {
    log_message("Connection failed");
    close_socket(g_socket);
    g_socket = SOCKET_ERROR_VALUE;
    return false;
  }

  // Wait for ACK message
  char buffer[BUFFER_SIZE];
  memset(buffer, 0, BUFFER_SIZE);
  int bytes_received = recv(g_socket, buffer, BUFFER_SIZE - 1, 0);
  if (bytes_received <= 0) {
    log_message("Failed to receive ACK message");
    close_socket(g_socket);
    g_socket = SOCKET_ERROR_VALUE;
    return false;
  }

  buffer[bytes_received] = '\0';
  if (strcmp(buffer, "ACK") != 0) {
    log_message("Invalid ACK message: %s", buffer);
    close_socket(g_socket);
    g_socket = SOCKET_ERROR_VALUE;
    return false;
  }

  g_connected = true;
  log_message("Connected to device at %s:%d", host, port);
  return true;
}

EXPORT bool driver_disconnect() {
  if (!g_connected) {
    log_message("Driver is not connected");
    return true;
  }

  // Send exit command
  const char *exit_command = "exit";
  send(g_socket, exit_command, (int)strlen(exit_command), 0);

  // Close socket
  close_socket(g_socket);
  g_socket = SOCKET_ERROR_VALUE;
  g_connected = false;

  log_message("Disconnected from device");
  return true;
}

EXPORT bool driver_get_status(DeviceStatus *status) {
  if (!g_connected || !status) {
    return false;
  }

  char response[BUFFER_SIZE];

  // Get connected_device register
  if (!send_and_receive("100000", response)) {
    return false;
  }
  uint8_t connected_device = (uint8_t)strtol(response + 4, NULL, 16);

  // Get power_state register
  if (!send_and_receive("102000", response)) {
    return false;
  }
  uint8_t power_state = (uint8_t)strtol(response + 4, NULL, 16);

  // Get error_state register
  if (!send_and_receive("103000", response)) {
    return false;
  }
  uint8_t error_state = (uint8_t)strtol(response + 4, NULL, 16);

  // Fill status structure
  status->connected = (connected_device != 0);
  status->sensors_powered =
      ((power_state & 0x05) != 0); // Check if any sensor is powered
  status->actuators_powered =
      ((power_state & 0xF0) != 0); // Check if any actuator is powered
  status->has_errors = (error_state != 0);

  return true;
}

EXPORT bool driver_get_sensors(SensorData *data) {
  if (!g_connected || !data) {
    return false;
  }

  char response[BUFFER_SIZE];

  // Get temperature sensor ID
  if (!send_and_receive("210000", response)) {
    return false;
  }
  data->temperature_id = (uint8_t)strtol(response + 4, NULL, 16);

  // Get temperature sensor reading
  if (!send_and_receive("211000", response)) {
    return false;
  }
  data->temperature_value = (uint8_t)strtol(response + 4, NULL, 16);

  // Get humidity sensor ID
  if (!send_and_receive("220000", response)) {
    return false;
  }
  data->humidity_id = (uint8_t)strtol(response + 4, NULL, 16);

  // Get humidity sensor reading
  if (!send_and_receive("221000", response)) {
    return false;
  }
  data->humidity_value = (uint8_t)strtol(response + 4, NULL, 16);

  return true;
}

EXPORT bool driver_get_actuators(ActuatorData *data) {
  if (!g_connected || !data) {
    return false;
  }

  char response[BUFFER_SIZE];

  // Get LED value
  if (!send_and_receive("310000", response)) {
    return false;
  }
  data->led_value = (uint8_t)strtol(response + 4, NULL, 16);

  // Get fan value
  if (!send_and_receive("320000", response)) {
    return false;
  }
  data->fan_value = (uint8_t)strtol(response + 4, NULL, 16);

  // Get heater value
  if (!send_and_receive("330000", response)) {
    return false;
  }
  data->heater_value = (uint8_t)strtol(response + 4, NULL, 16);

  // Get doors value
  if (!send_and_receive("340000", response)) {
    return false;
  }
  data->doors_value = (uint8_t)strtol(response + 4, NULL, 16);

  return true;
}

EXPORT bool driver_set_led(uint8_t value) {
  if (!g_connected) {
    return false;
  }

  char command[7];
  char response[BUFFER_SIZE];

  sprintf(command, "3101%02X", value);
  return send_and_receive(command, response);
}

EXPORT bool driver_set_fan(uint8_t value) {
  if (!g_connected) {
    return false;
  }

  char command[7];
  char response[BUFFER_SIZE];

  sprintf(command, "3201%02X", value);
  return send_and_receive(command, response);
}

EXPORT bool driver_set_heater(uint8_t value) {
  if (!g_connected) {
    return false;
  }

  // Heater only uses lower 4 bits
  value &= 0x0F;

  char command[7];
  char response[BUFFER_SIZE];

  sprintf(command, "3301%02X", value);
  return send_and_receive(command, response);
}

EXPORT bool driver_set_doors(uint8_t value) {
  if (!g_connected) {
    return false;
  }

  // Doors only use bits 0, 2, 4, 6
  value &= 0x55;

  char command[7];
  char response[BUFFER_SIZE];

  sprintf(command, "3401%02X", value);
  return send_and_receive(command, response);
}

EXPORT bool driver_power_sensors(bool temperature_on, bool humidity_on) {
  if (!g_connected) {
    return false;
  }

  uint8_t value = 0;
  if (temperature_on) {
    value |= 0x01;
  }
  if (humidity_on) {
    value |= 0x10;
  }

  char command[7];
  char response[BUFFER_SIZE];

  sprintf(command, "4FB1%02X", value);
  return send_and_receive(command, response);
}

EXPORT bool driver_power_actuators(bool led_on, bool fan_on, bool heater_on,
                                   bool doors_on) {
  if (!g_connected) {
    return false;
  }

  uint8_t value = 0;
  if (led_on) {
    value |= 0x01;
  }
  if (fan_on) {
    value |= 0x04;
  }
  if (heater_on) {
    value |= 0x10;
  }
  if (doors_on) {
    value |= 0x40;
  }

  char command[7];
  char response[BUFFER_SIZE];

  sprintf(command, "4FC1%02X", value);
  return send_and_receive(command, response);
}

EXPORT bool driver_reset_sensors(bool reset_temperature, bool reset_humidity) {
  if (!g_connected) {
    return false;
  }

  uint8_t value = 0;
  if (reset_temperature) {
    value |= 0x01;
  }
  if (reset_humidity) {
    value |= 0x10;
  }

  char command[7];
  char response[BUFFER_SIZE];

  sprintf(command, "4FD1%02X", value);
  return send_and_receive(command, response);
}

EXPORT bool driver_reset_actuators(bool reset_led, bool reset_fan,
                                   bool reset_heater, bool reset_doors) {
  if (!g_connected) {
    return false;
  }

  uint8_t value = 0;
  if (reset_led) {
    value |= 0x01;
  }
  if (reset_fan) {
    value |= 0x04;
  }
  if (reset_heater) {
    value |= 0x10;
  }
  if (reset_doors) {
    value |= 0x40;
  }

  char command[7];
  char response[BUFFER_SIZE];

  sprintf(command, "4FE1%02X", value);
  return send_and_receive(command, response);
}

EXPORT bool driver_send_command(const char *command, char *response) {
  if (!g_connected || !command || !response) {
    return false;
  }

  return send_and_receive(command, response);
}

static void log_message(const char *format, ...) {
  if (g_log_callback) {
    char buffer[BUFFER_SIZE];
    va_list args;
    va_start(args, format);
    vsnprintf(buffer, BUFFER_SIZE, format, args);
    va_end(args);

    g_log_callback(buffer);
  }
}

static bool send_and_receive(const char *command, char *response) {
  if (!g_connected || !command || !response) {
    return false;
  }

  // Send command
  if (send(g_socket, command, (int)strlen(command), 0) < 0) {
    log_message("Failed to send command");
    return false;
  }

  // Receive response
  memset(response, 0, BUFFER_SIZE);
  int bytes_received = recv(g_socket, response, BUFFER_SIZE - 1, 0);
  if (bytes_received <= 0) {
    log_message("Failed to receive response");
    return false;
  }

  response[bytes_received] = '\0';

  // Check for error response
  if (response[0] >= '1' && response[0] <= '3' &&
      strcmp(response + 1, "FFFFF") == 0) {
    log_message("Error response: %s", response);
    return false;
  }

  return true;
}