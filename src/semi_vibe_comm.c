/**
 * @file semi_vibe_comm.c
 * @brief Implementation of the communication layer for the Semi-Vibe protocol
 */

#include "../include/semi_vibe_comm.h"

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#define close_socket closesocket

#define BUFFER_SIZE 256
#define DEFAULT_PORT 8989
#define DEFAULT_HOST "localhost"
#define DEFAULT_TIMEOUT_MS 5000

/**
 * @brief Log a message using the callback if set
 *
 * @param context Communication context
 * @param format Format string
 * @param ... Format arguments
 */
void comm_log(CommContext *context, const char *format, ...)
{
    if (context && context->log_callback)
    {
        char buffer[BUFFER_SIZE];
        va_list args;
        va_start(args, format);

#ifdef _MSC_VER
        // Use secure vsnprintf_s on Windows
        vsnprintf_s(buffer, BUFFER_SIZE, _TRUNCATE, format, args);
#else
        // Use standard vsnprintf with explicit null termination
        int result = vsnprintf(buffer, BUFFER_SIZE, format, args);
        if (result < 0 || result >= BUFFER_SIZE)
        {
            // Ensure null termination in case of truncation or error
            buffer[BUFFER_SIZE - 1] = '\0';
        }
#endif

        va_end(args);

        context->log_callback(buffer, context->user_data);
    }
}

/**
 * @brief Set the operation timeout
 *
 * @param context Communication context
 * @param timeout_ms Timeout in milliseconds
 * @return true if successful, false otherwise
 */
bool comm_set_timeout(CommContext *context, unsigned int timeout_ms)
{
    if (!context)
    {
        return false;
    }

    context->timeout_ms = timeout_ms;

    // If socket is already connected, update its timeout
    if (context->connected && context->socket != SOCKET_ERROR_VALUE)
    {
        DWORD timeout = (DWORD)timeout_ms;
        if (setsockopt(context->socket, SOL_SOCKET, SO_RCVTIMEO, (const char *)&timeout, sizeof(timeout)) < 0)
        {
            comm_log(context, "Failed to set receive timeout");
            return false;
        }
        if (setsockopt(context->socket, SOL_SOCKET, SO_SNDTIMEO, (const char *)&timeout, sizeof(timeout)) < 0)
        {
            comm_log(context, "Failed to set send timeout");
            return false;
        }
    }

    return true;
}

/**
 * @brief Initialize the communication layer
 *
 * @param context Communication context to initialize
 * @param log_callback Optional callback for logging
 * @param user_data User data to pass to the callback
 * @return true if initialization was successful
 */
bool comm_init(CommContext *context, CommLogCallback log_callback, void *user_data)
{
    if (!context)
    {
        return false;
    }

    // Initialize Winsock
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0)
    {
        return false;
    }

    // Initialize context
    memset(context, 0, sizeof(CommContext));
    context->socket = SOCKET_ERROR_VALUE;
    context->initialized = true;
    context->connected = false;
    context->log_callback = log_callback;
    context->user_data = user_data;
    context->host = NULL;
    context->port = 0;
    context->timeout_ms = DEFAULT_TIMEOUT_MS;
    context->last_error = COMM_ERROR_NONE;

    comm_log(context, "Communication layer initialized");
    return true;
}

/**
 * @brief Connect to a server
 *
 * @param context Communication context
 * @param host Hostname or IP address (defaults to localhost if NULL)
 * @param port Port number (defaults to 8989 if <= 0)
 * @return true if connection was successful
 */
bool comm_connect(CommContext *context, const char *host, int port)
{
    if (!context || !context->initialized)
    {
        return false;
    }

    if (context->connected)
    {
        comm_log(context, "Already connected");
        return true;
    }

    // Use default values if not provided
    const char *host_to_use = (host != NULL) ? host : DEFAULT_HOST;
    int port_to_use = (port > 0) ? port : DEFAULT_PORT;

    // Store connection info
    if (context->host)
    {
        free(context->host);
        context->host = NULL;
    }

    // Safely duplicate the host string
    size_t host_len = strlen(host_to_use) + 1; // +1 for null terminator
#ifdef _MSC_VER
    context->host = (char *)malloc(host_len);
    if (context->host)
    {
        strncpy_s(context->host, host_len, host_to_use, _TRUNCATE);
    }
#else
    context->host = (char *)malloc(host_len);
    if (context->host)
    {
        strncpy(context->host, host_to_use, host_len - 1);
        context->host[host_len - 1] = '\0'; // Ensure null termination
    }
#endif

    if (context->host == NULL)
    {
        comm_log(context, "Failed to allocate memory for host name");
        close_socket(context->socket);
        context->socket = SOCKET_ERROR_VALUE;
        return false;
    }

    context->port = port_to_use;

    // Create socket
    context->socket = socket(AF_INET, SOCK_STREAM, 0);
    if (context->socket == SOCKET_ERROR_VALUE)
    {
        comm_log(context, "Failed to create socket");
        return false;
    }

    // Set socket timeouts
    DWORD timeout = (DWORD)context->timeout_ms;
    if (setsockopt(context->socket, SOL_SOCKET, SO_RCVTIMEO, (const char *)&timeout, sizeof(timeout)) < 0)
    {
        comm_log(context, "Failed to set receive timeout");
        close_socket(context->socket);
        context->socket = SOCKET_ERROR_VALUE;
        return false;
    }
    if (setsockopt(context->socket, SOL_SOCKET, SO_SNDTIMEO, (const char *)&timeout, sizeof(timeout)) < 0)
    {
        comm_log(context, "Failed to set send timeout");
        close_socket(context->socket);
        context->socket = SOCKET_ERROR_VALUE;
        return false;
    }

    // Connect to server
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port_to_use);

    // Convert hostname to IP address using getaddrinfo instead of deprecated gethostbyname
    struct addrinfo hints, *result = NULL;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET;       // IPv4
    hints.ai_socktype = SOCK_STREAM; // TCP

    int status = getaddrinfo(host_to_use, NULL, &hints, &result);
    if (status != 0 || result == NULL)
    {
        comm_log(context, "Failed to resolve hostname: %s", gai_strerror(status));
        close_socket(context->socket);
        context->socket = SOCKET_ERROR_VALUE;
        return false;
    }

    // Copy the resolved address
    memcpy(&server_addr.sin_addr, &((struct sockaddr_in *)result->ai_addr)->sin_addr, sizeof(server_addr.sin_addr));

    // Free the address info
    freeaddrinfo(result);

    if (connect(context->socket, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    {
        comm_log(context, "Connection failed");
        close_socket(context->socket);
        context->socket = SOCKET_ERROR_VALUE;
        return false;
    }

    // Wait for ACK message
    char buffer[BUFFER_SIZE];
    memset(buffer, 0, BUFFER_SIZE);
    int bytes_received = recv(context->socket, buffer, BUFFER_SIZE - 1, 0);
    if (bytes_received <= 0)
    {
        comm_log(context, "Failed to receive ACK message");
        close_socket(context->socket);
        context->socket = SOCKET_ERROR_VALUE;
        return false;
    }

    buffer[bytes_received] = '\0';
    if (strcmp(buffer, "ACK") != 0)
    {
        comm_log(context, "Invalid ACK message: %s", buffer);
        close_socket(context->socket);
        context->socket = SOCKET_ERROR_VALUE;
        return false;
    }

    context->connected = true;
    comm_log(context, "Connected to device at %s:%d", host_to_use, port_to_use);
    return true;
}

/**
 * @brief Disconnect from the server
 *
 * @param context Communication context
 * @param send_exit Whether to send an exit command before disconnecting
 * @return true if disconnection was successful
 */
bool comm_disconnect(CommContext *context, bool send_exit)
{
    if (!context || !context->connected)
    {
        return true; // Already disconnected
    }

    bool result = true;

    // Send exit command if requested
    if (send_exit)
    {
        comm_log(context, "Sending exit command to device");

        // Send the exit command
        const char *exit_cmd = "exit";
        if (send(context->socket, exit_cmd, 4, 0) < 0)
        {
            int error = WSAGetLastError();
            comm_log(context, "Failed to send exit command (error code: %d)", error);
            // Continue with disconnection even if exit command fails
            result = false;
        }
        else
        {
            // Wait a short time for the device to process the exit command
            Sleep(100);
        }
    }

    // Close the socket
    if (context->socket != SOCKET_ERROR_VALUE)
    {
        comm_log(context, "Closing socket connection");
        shutdown(context->socket, SD_BOTH);
        close_socket(context->socket);
        context->socket = SOCKET_ERROR_VALUE;
    }

    // Update connection state
    context->connected = false;

    // Free host string if allocated
    if (context->host)
    {
        free(context->host);
        context->host = NULL;
    }

    comm_log(context, "Disconnected from device");
    return result;
}

/**
 * @brief Send a message and receive a response
 *
 * @param context Communication context
 * @param message Message to send
 * @param response Buffer to store the response (must be at least 7 bytes)
 * @param response_size Size of the response buffer
 * @return true if message was sent and response received successfully
 */
bool comm_send_receive(CommContext *context, const char *message, char *response, size_t response_size)
{
    if (!context || !context->connected || !message || !response || response_size < 7)
    {
        return false;
    }

    // Validate message length to prevent buffer overflows
    size_t message_len = strlen(message);
    if (message_len == 0 || message_len > BUFFER_SIZE - 1)
    {
        comm_log(context, "Invalid message length: %zu", message_len);
        return false;
    }

    // Log the message being sent
    comm_log(context, "Sending message: %s", message);

    // Send message
    if (send(context->socket, message, (int)message_len, 0) < 0)
    {
        int error = WSAGetLastError();
        if (error == WSAETIMEDOUT)
        {
            comm_log(context, "Send operation timed out");
            context->last_error = COMM_ERROR_TIMEOUT;
        }
        else
        {
            comm_log(context, "Failed to send message (error code: %d)", error);
            context->last_error = COMM_ERROR_SEND_FAILED;
        }
        return false;
    }

    // Receive response
    memset(response, 0, response_size);
    int bytes_received = recv(context->socket, response, response_size - 1, 0);
    if (bytes_received <= 0)
    {
        int error = WSAGetLastError();
        if (error == WSAETIMEDOUT)
        {
            comm_log(context, "Receive operation timed out");
            context->last_error = COMM_ERROR_TIMEOUT;
        }
        else
        {
            comm_log(context, "Failed to receive response (error code: %d)", error);
            context->last_error = COMM_ERROR_RECEIVE_FAILED;
        }
        return false;
    }

    // Ensure null termination
    if ((size_t)bytes_received >= response_size)
    {
        response[response_size - 1] = '\0';
        comm_log(context, "Response truncated to fit buffer");
    }
    else
    {
        response[bytes_received] = '\0';
    }

    comm_log(context, "Received response: %s", response);
    context->last_error = COMM_ERROR_NONE;
    return true;
}

/**
 * @brief Clean up the communication context
 *
 * @param context Communication context
 */
void comm_cleanup(CommContext *context)
{
    if (!context)
    {
        return;
    }

    // Disconnect if still connected
    if (context->connected)
    {
        comm_disconnect(context, true);
    }

    // Free allocated memory
    if (context->host)
    {
        free(context->host);
        context->host = NULL;
    }

    // Cleanup Winsock
    if (context->initialized)
    {
        WSACleanup();
    }

    context->initialized = false;
    comm_log(context, "Communication layer cleaned up");
}

/**
 * @brief Get the last error code
 *
 * @param context Communication context
 * @return int Error code (COMM_ERROR_*)
 */
int comm_get_last_error(CommContext *context)
{
    if (!context)
    {
        return COMM_ERROR_INVALID_PARAMETER;
    }

    return context->last_error;
}