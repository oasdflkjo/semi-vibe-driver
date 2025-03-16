/**
 * @file semi_vibe_comm.h
 * @brief Communication layer for the Semi-Vibe protocol
 */

#ifndef SEMI_VIBE_COMM_H
#define SEMI_VIBE_COMM_H

#include <stdbool.h>
#include <stdint.h>
#include <winsock2.h>

#ifdef __cplusplus
extern "C" {
#endif

// Error codes
#define COMM_ERROR_NONE 0
#define COMM_ERROR_TIMEOUT 1
#define COMM_ERROR_SEND_FAILED 2
#define COMM_ERROR_RECEIVE_FAILED 3
#define COMM_ERROR_INVALID_PARAMETER 4
#define COMM_ERROR_NOT_INITIALIZED 5
#define COMM_ERROR_ALREADY_CONNECTED 6
#define COMM_ERROR_NOT_CONNECTED 7
#define COMM_ERROR_CONNECTION_FAILED 8

// Callback function type for logging
typedef void (*CommLogCallback)(const char *message, void *user_data);

// Socket handle type
typedef SOCKET socket_t;
#define SOCKET_ERROR_VALUE INVALID_SOCKET

// Communication context
typedef struct
{
    socket_t socket;
    bool initialized;
    bool connected;
    CommLogCallback log_callback;
    void *user_data;
    char *host;
    int port;
    unsigned int timeout_ms;
    int last_error;
} CommContext;

/**
 * @brief Initialize the communication layer
 *
 * @param context Communication context to initialize
 * @param log_callback Optional callback for logging
 * @param user_data User data to pass to the callback
 * @return true if initialization was successful
 */
bool comm_init(CommContext *context, CommLogCallback log_callback, void *user_data);

/**
 * @brief Connect to a server
 *
 * @param context Communication context
 * @param host Hostname or IP address (defaults to localhost if NULL)
 * @param port Port number (defaults to 8989 if <= 0)
 * @return true if connection was successful
 */
bool comm_connect(CommContext *context, const char *host, int port);

/**
 * @brief Disconnect from the server
 *
 * @param context Communication context
 * @param send_exit Whether to send an exit command before disconnecting
 * @return true if disconnection was successful
 */
bool comm_disconnect(CommContext *context, bool send_exit);

/**
 * @brief Send a message and receive a response
 *
 * @param context Communication context
 * @param message Message to send
 * @param response Buffer to store the response (must be at least 7 bytes)
 * @param response_size Size of the response buffer
 * @return true if message was sent and response received successfully
 */
bool comm_send_receive(CommContext *context, const char *message, char *response, size_t response_size);

/**
 * @brief Log a message using the callback if set
 *
 * @param context Communication context
 * @param format Format string
 * @param ... Format arguments
 */
void comm_log(CommContext *context, const char *format, ...);

/**
 * @brief Clean up the communication context
 *
 * @param context Communication context
 */
void comm_cleanup(CommContext *context);

/**
 * @brief Set the operation timeout
 *
 * @param context Communication context
 * @param timeout_ms Timeout in milliseconds
 * @return true if successful, false otherwise
 */
bool comm_set_timeout(CommContext *context, unsigned int timeout_ms);

/**
 * @brief Get the last error code
 *
 * @param context Communication context
 * @return int Error code (COMM_ERROR_*)
 */
int comm_get_last_error(CommContext *context);

#ifdef __cplusplus
}
#endif

#endif /* SEMI_VIBE_COMM_H */