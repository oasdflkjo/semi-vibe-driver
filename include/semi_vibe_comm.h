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

// Callback function type for logging
typedef void (*CommLogCallback)(const char *message);

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
    char *host;
    int port;
} CommContext;

/**
 * @brief Initialize the communication layer
 *
 * @param context Communication context to initialize
 * @param log_callback Optional callback for logging
 * @return true if initialization was successful
 */
bool comm_init(CommContext *context, CommLogCallback log_callback);

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

#ifdef __cplusplus
}
#endif

#endif /* SEMI_VIBE_COMM_H */