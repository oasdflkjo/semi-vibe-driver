/**
 * @file semi_vibe_device.c
 * @brief Implementation of the Semi-Vibe-Device simulator
 */

#include "../include/semi_vibe_device.h"

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>


#ifdef _WIN32
#include <process.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
typedef SOCKET socket_t;
#define SOCKET_ERROR_VALUE INVALID_SOCKET
#define close_socket closesocket
#define THREAD_RETURN_TYPE unsigned __stdcall
#define THREAD_RETURN_VALUE 0
#else
#include <arpa/inet.h>
#include <netinet/in.h>
#include <pthread.h>
#include <sys/socket.h>
#include <unistd.h>
typedef int socket_t;
#define SOCKET_ERROR_VALUE -1
#define close_socket close
#define THREAD_RETURN_TYPE void *
#define THREAD_RETURN_VALUE NULL
#endif

#define PORT 8989
#define BUFFER_SIZE 256

// Global variables
static DeviceMemory g_memory;
static LogCallback g_log_callback = NULL;
static bool g_running = false;
static socket_t g_server_socket = SOCKET_ERROR_VALUE;
static socket_t g_client_socket = SOCKET_ERROR_VALUE;

#ifdef _WIN32
static HANDLE g_memory_mutex;
static HANDLE g_server_thread;
#else
static pthread_mutex_t g_memory_mutex;
static pthread_t g_server_thread;
#endif

// Forward declarations
static THREAD_RETURN_TYPE server_thread_func(void *arg);
static bool process_command(const char *command, char *response);
static void log_message(const char *format, ...);
static void update_sensors();

EXPORT bool device_init(LogCallback log_callback) {
  g_log_callback = log_callback;

  // Initialize random number generator
  srand((unsigned int)time(NULL));

  // Initialize memory
  memset(&g_memory, 0, sizeof(DeviceMemory));

  // Set initial values
  g_memory.connected_device = 0xFF; // All devices connected
  g_memory.power_state = 0xFF;      // All devices powered on
  g_memory.error_state = 0x00;      // No errors

  // Set sensor IDs
  g_memory.sensor_a_id = 0xA1; // Temperature sensor ID
  g_memory.sensor_b_id = 0xB2; // Humidity sensor ID

  // Set initial sensor readings
  g_memory.sensor_a_reading = (uint8_t)rand();
  g_memory.sensor_b_reading = (uint8_t)rand();

  // Set power control registers
  g_memory.power_sensors = 0x11;   // Both sensors powered on
  g_memory.power_actuators = 0x55; // All actuators powered on

  // Initialize mutex
#ifdef _WIN32
  g_memory_mutex = CreateMutex(NULL, FALSE, NULL);
  if (g_memory_mutex == NULL) {
    log_message("Failed to initialize mutex");
    return false;
  }
#else
  if (pthread_mutex_init(&g_memory_mutex, NULL) != 0) {
    log_message("Failed to initialize mutex");
    return false;
  }
#endif

  log_message("Semi-Vibe-Device simulator initialized");
  return true;
}

EXPORT bool device_start() {
  if (g_running) {
    log_message("Device is already running");
    return false;
  }

#ifdef _WIN32
  // Initialize Winsock
  WSADATA wsaData;
  if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
    log_message("WSAStartup failed");
    return false;
  }
#endif

  // Create socket
  g_server_socket = socket(AF_INET, SOCK_STREAM, 0);
  if (g_server_socket == SOCKET_ERROR_VALUE) {
    log_message("Failed to create socket");
#ifdef _WIN32
    WSACleanup();
#endif
    return false;
  }

  // Set socket options
  int opt = 1;
  if (setsockopt(g_server_socket, SOL_SOCKET, SO_REUSEADDR, (const char *)&opt,
                 sizeof(opt)) < 0) {
    log_message("Failed to set socket options");
    close_socket(g_server_socket);
#ifdef _WIN32
    WSACleanup();
#endif
    return false;
  }

  // Bind socket
  struct sockaddr_in server_addr;
  server_addr.sin_family = AF_INET;
  server_addr.sin_addr.s_addr = INADDR_ANY;
  server_addr.sin_port = htons(PORT);

  if (bind(g_server_socket, (struct sockaddr *)&server_addr,
           sizeof(server_addr)) < 0) {
    log_message("Failed to bind socket");
    close_socket(g_server_socket);
#ifdef _WIN32
    WSACleanup();
#endif
    return false;
  }

  // Listen for connections
  if (listen(g_server_socket, 1) < 0) {
    log_message("Failed to listen on socket");
    close_socket(g_server_socket);
#ifdef _WIN32
    WSACleanup();
#endif
    return false;
  }

  // Start server thread
  g_running = true;

#ifdef _WIN32
  g_server_thread =
      (HANDLE)_beginthreadex(NULL, 0, server_thread_func, NULL, 0, NULL);
  if (g_server_thread == NULL) {
    log_message("Failed to create server thread");
    close_socket(g_server_socket);
    WSACleanup();
    g_running = false;
    return false;
  }
#else
  if (pthread_create(&g_server_thread, NULL, server_thread_func, NULL) != 0) {
    log_message("Failed to create server thread");
    close_socket(g_server_socket);
    g_running = false;
    return false;
  }
#endif

  log_message("Semi-Vibe-Device simulator started on port %d", PORT);
  return true;
}

EXPORT bool device_stop() {
  if (!g_running) {
    log_message("Device is not running");
    return false;
  }

  g_running = false;

  // Close client socket if connected
  if (g_client_socket != SOCKET_ERROR_VALUE) {
    close_socket(g_client_socket);
    g_client_socket = SOCKET_ERROR_VALUE;
  }

  // Close server socket
  if (g_server_socket != SOCKET_ERROR_VALUE) {
    close_socket(g_server_socket);
    g_server_socket = SOCKET_ERROR_VALUE;
  }

  // Wait for server thread to finish
#ifdef _WIN32
  WaitForSingleObject(g_server_thread, INFINITE);
  CloseHandle(g_server_thread);

  // Destroy mutex
  CloseHandle(g_memory_mutex);

  WSACleanup();
#else
  pthread_join(g_server_thread, NULL);

  // Destroy mutex
  pthread_mutex_destroy(&g_memory_mutex);
#endif

  log_message("Semi-Vibe-Device simulator stopped");
  return true;
}

EXPORT bool device_get_memory(DeviceMemory *memory) {
  if (!memory) {
    return false;
  }

#ifdef _WIN32
  WaitForSingleObject(g_memory_mutex, INFINITE);
  memcpy(memory, &g_memory, sizeof(DeviceMemory));
  ReleaseMutex(g_memory_mutex);
#else
  pthread_mutex_lock(&g_memory_mutex);
  memcpy(memory, &g_memory, sizeof(DeviceMemory));
  pthread_mutex_unlock(&g_memory_mutex);
#endif

  return true;
}

EXPORT bool device_process_command(const char *command, char *response) {
  if (!command || !response) {
    return false;
  }

  return process_command(command, response);
}

static THREAD_RETURN_TYPE server_thread_func(void *arg) {
  log_message("Server thread started");

  while (g_running) {
    log_message("Waiting for connection...");

    // Accept connection
    struct sockaddr_in client_addr;
#ifdef _WIN32
    int client_addr_len = sizeof(client_addr);
#else
    socklen_t client_addr_len = sizeof(client_addr);
#endif
    g_client_socket = accept(g_server_socket, (struct sockaddr *)&client_addr,
                             &client_addr_len);

    if (g_client_socket == SOCKET_ERROR_VALUE) {
      if (g_running) {
        log_message("Failed to accept connection");
      }
      continue;
    }

    log_message("Client connected: %s", inet_ntoa(client_addr.sin_addr));

    // Send ACK message
    const char *ack_message = "ACK";
    send(g_client_socket, ack_message, (int)strlen(ack_message), 0);

    // Handle client communication
    char buffer[BUFFER_SIZE];
    char response[BUFFER_SIZE];

    while (g_running) {
      memset(buffer, 0, BUFFER_SIZE);
      int bytes_received = recv(g_client_socket, buffer, BUFFER_SIZE - 1, 0);

      if (bytes_received <= 0) {
        log_message("Client disconnected");
        break;
      }

      buffer[bytes_received] = '\0';
      log_message("Received: %s", buffer);

      // Check for exit command
      if (strcmp(buffer, "exit") == 0) {
        log_message("Exit command received");
        break;
      }

      // Process command
      if (process_command(buffer, response)) {
        send(g_client_socket, response, (int)strlen(response), 0);
        log_message("Sent response: %s", response);
      }
    }

    // Close client socket
    close_socket(g_client_socket);
    g_client_socket = SOCKET_ERROR_VALUE;
  }

  log_message("Server thread stopped");
  return THREAD_RETURN_VALUE;
}

static bool process_command(const char *command, char *response) {
  // Validate command format (6 hex digits)
  if (strlen(command) != 6) {
    strcpy(response, "1FFFFF");
    return true;
  }

  for (int i = 0; i < 6; i++) {
    if (!((command[i] >= '0' && command[i] <= '9') ||
          (command[i] >= 'A' && command[i] <= 'F') ||
          (command[i] >= 'a' && command[i] <= 'f'))) {
      strcpy(response, "1FFFFF");
      return true;
    }
  }

  // Parse command
  char base_str[2] = {command[0], '\0'};
  char offset_str[3] = {command[1], command[2], '\0'};
  char rw_str[2] = {command[3], '\0'};
  char data_str[3] = {command[4], command[5], '\0'};

  int base = (int)strtol(base_str, NULL, 16);
  int offset = (int)strtol(offset_str, NULL, 16);
  int rw = (int)strtol(rw_str, NULL, 16);
  int data = (int)strtol(data_str, NULL, 16);

  // Validate R/W bit
  if (rw != 0 && rw != 1) {
    strcpy(response, "2FFFFF");
    return true;
  }

  // Process command based on base address
#ifdef _WIN32
  WaitForSingleObject(g_memory_mutex, INFINITE);
#else
  pthread_mutex_lock(&g_memory_mutex);
#endif

  uint8_t read_data = 0;
  bool valid_command = false;

  switch (base) {
  case 0:
    // RESERVED - always invalid
    strcpy(response, "1FFFFF");
    break;

  case 1:
    // MAIN - read only
    if (rw == 0) {
      switch (offset) {
      case 0x00:
        read_data = g_memory.connected_device;
        valid_command = true;
        break;
      case 0x01:
        read_data = g_memory.reserved_main;
        valid_command = true;
        break;
      case 0x02:
        read_data = g_memory.power_state;
        valid_command = true;
        break;
      case 0x03:
        read_data = g_memory.error_state;
        valid_command = true;
        break;
      default:
        strcpy(response, "2FFFFF");
        break;
      }
    } else {
      // Write to read-only register
      strcpy(response, "1FFFFF");
    }
    break;

  case 2:
    // SENSOR - read only
    if (rw == 0) {
      switch (offset) {
      case 0x10:
        read_data = g_memory.sensor_a_id;
        valid_command = true;
        break;
      case 0x11:
        read_data = g_memory.sensor_a_reading;
        valid_command = true;
        break;
      case 0x20:
        read_data = g_memory.sensor_b_id;
        valid_command = true;
        break;
      case 0x21:
        read_data = g_memory.sensor_b_reading;
        valid_command = true;
        break;
      default:
        strcpy(response, "2FFFFF");
        break;
      }
    } else {
      // Write to read-only register
      strcpy(response, "1FFFFF");
    }
    break;

  case 3:
    // ACTUATOR - read/write
    switch (offset) {
    case 0x10:
      if (rw == 0) {
        read_data = g_memory.actuator_a;
      } else {
        g_memory.actuator_a = (uint8_t)data;
      }
      valid_command = true;
      break;
    case 0x20:
      if (rw == 0) {
        read_data = g_memory.actuator_b;
      } else {
        g_memory.actuator_b = (uint8_t)data;
      }
      valid_command = true;
      break;
    case 0x30:
      if (rw == 0) {
        read_data = g_memory.actuator_c;
      } else {
        // Only lower 4 bits are writable
        g_memory.actuator_c = (uint8_t)(data & 0x0F);
      }
      valid_command = true;
      break;
    case 0x40:
      if (rw == 0) {
        read_data = g_memory.actuator_d;
      } else {
        // Only bits 0, 2, 4, 6 are writable
        g_memory.actuator_d = (uint8_t)(data & 0x55);
      }
      valid_command = true;
      break;
    default:
      strcpy(response, "2FFFFF");
      break;
    }
    break;

  case 4:
    // CONTROL - read/write
    switch (offset) {
    case 0xFB:
      if (rw == 0) {
        read_data = g_memory.power_sensors;
      } else {
        // Only bits 0 and 4 are writable
        g_memory.power_sensors = (uint8_t)(data & 0x11);

        // Update connected_device and power_state based on power_sensors
        if (data & 0x01) {
          g_memory.connected_device |= 0x01;
          g_memory.power_state |= 0x01;
        } else {
          g_memory.connected_device &= ~0x01;
          g_memory.power_state &= ~0x01;
        }

        if (data & 0x10) {
          g_memory.connected_device |= 0x04;
          g_memory.power_state |= 0x04;
        } else {
          g_memory.connected_device &= ~0x04;
          g_memory.power_state &= ~0x04;
        }
      }
      valid_command = true;
      break;
    case 0xFC:
      if (rw == 0) {
        read_data = g_memory.power_actuators;
      } else {
        // Only bits 0, 2, 4, 6 are writable
        g_memory.power_actuators = (uint8_t)(data & 0x55);

        // Update connected_device and power_state based on power_actuators
        if (data & 0x01) {
          g_memory.connected_device |= 0x10;
          g_memory.power_state |= 0x10;
        } else {
          g_memory.connected_device &= ~0x10;
          g_memory.power_state &= ~0x10;
        }

        if (data & 0x04) {
          g_memory.connected_device |= 0x20;
          g_memory.power_state |= 0x20;
        } else {
          g_memory.connected_device &= ~0x20;
          g_memory.power_state &= ~0x20;
        }

        if (data & 0x10) {
          g_memory.connected_device |= 0x40;
          g_memory.power_state |= 0x40;
        } else {
          g_memory.connected_device &= ~0x40;
          g_memory.power_state &= ~0x40;
        }

        if (data & 0x40) {
          g_memory.connected_device |= 0x80;
          g_memory.power_state |= 0x80;
        } else {
          g_memory.connected_device &= ~0x80;
          g_memory.power_state &= ~0x80;
        }
      }
      valid_command = true;
      break;
    case 0xFD:
      if (rw == 0) {
        read_data = g_memory.reset_sensors;
      } else {
        // Only bits 0 and 4 are writable
        g_memory.reset_sensors = (uint8_t)(data & 0x11);

        // Reset sensors if bit is set
        if (data & 0x01) {
          g_memory.error_state &= ~0x01;
          g_memory.reset_sensors &= ~0x01; // Auto-clear
        }

        if (data & 0x10) {
          g_memory.error_state &= ~0x04;
          g_memory.reset_sensors &= ~0x10; // Auto-clear
        }
      }
      valid_command = true;
      break;
    case 0xFE:
      if (rw == 0) {
        read_data = g_memory.reset_actuators;
      } else {
        // Only bits 0, 2, 4, 6 are writable
        g_memory.reset_actuators = (uint8_t)(data & 0x55);

        // Reset actuators if bit is set
        if (data & 0x01) {
          g_memory.error_state &= ~0x10;
          g_memory.actuator_a = 0;
          g_memory.reset_actuators &= ~0x01; // Auto-clear
        }

        if (data & 0x04) {
          g_memory.error_state &= ~0x20;
          g_memory.actuator_b = 0;
          g_memory.reset_actuators &= ~0x04; // Auto-clear
        }

        if (data & 0x10) {
          g_memory.error_state &= ~0x40;
          g_memory.actuator_c = 0;
          g_memory.reset_actuators &= ~0x10; // Auto-clear
        }

        if (data & 0x40) {
          g_memory.error_state &= ~0x80;
          g_memory.actuator_d = 0;
          g_memory.reset_actuators &= ~0x40; // Auto-clear
        }
      }
      valid_command = true;
      break;
    default:
      strcpy(response, "2FFFFF");
      break;
    }
    break;

  default:
    strcpy(response, "2FFFFF");
    break;
  }

  if (valid_command) {
    if (rw == 0) {
      // Read command - include read data in response
      sprintf(response, "%c%c%c%c%02X", command[0], command[1], command[2],
              command[3], read_data);
    } else {
      // Write command - echo back the command
      strcpy(response, command);
    }
  }

  // Update sensors
  update_sensors();

#ifdef _WIN32
  ReleaseMutex(g_memory_mutex);
#else
  pthread_mutex_unlock(&g_memory_mutex);
#endif

  return true;
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

static void update_sensors() {
  // Only update sensors if they are powered on
  if (g_memory.power_state & 0x01) {
    g_memory.sensor_a_reading = (uint8_t)rand();

    // 1% chance to raise error
    if (rand() % 100 == 0) {
      g_memory.error_state |= 0x01;
    }
  }

  if (g_memory.power_state & 0x04) {
    g_memory.sensor_b_reading = (uint8_t)rand();

    // 1% chance to raise error
    if (rand() % 100 == 0) {
      g_memory.error_state |= 0x04;
    }
  }
}
