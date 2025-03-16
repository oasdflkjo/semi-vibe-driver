/**
 * @file semi_vibe_comm.c
 * @brief Implementation of the communication layer for the Semi-Vibe protocol
 *
 * @copyright Copyright (c) 2024 Semi-Vibe Technologies, Inc.
 * @license MIT License with Attribution Requirement. See LICENSE.md for details.
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
        vsnprintf(buffer, BUFFER_SIZE, format, args);
        va_end(args);

        context->log_callback(buffer);
    }
}

/**
 * @brief Initialize the communication layer
 *
 * @param context Communication context to initialize
 * @param log_callback Optional callback for logging
 * @return true if initialization was successful
 */
bool comm_init(CommContext *context, CommLogCallback log_callback)
{
    if (!context)
    {
        return false;
    }

    // Initialize context
    context->socket = SOCKET_ERROR_VALUE;
    context->initialized = false;
    context->connected = false;
    context->log_callback = log_callback;
    context->host = NULL;
    context->port = 0;

    // Initialize Winsock
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0)
    {
        comm_log(context, "WSAStartup failed");
        return false;
    }

    context->initialized = true;
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
    }
    context->host = _strdup(host_to_use);
    context->port = port_to_use;

    // Create socket
    context->socket = socket(AF_INET, SOCK_STREAM, 0);
    if (context->socket == SOCKET_ERROR_VALUE)
    {
        comm_log(context, "Failed to create socket");
        return false;
    }

    // Connect to server
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port_to_use);

    // Convert hostname to IP address
    struct hostent *he;
    if ((he = gethostbyname(host_to_use)) == NULL)
    {
        comm_log(context, "Failed to resolve hostname");
        close_socket(context->socket);
        context->socket = SOCKET_ERROR_VALUE;
        return false;
    }

    // Copy the IP address
    memcpy(&server_addr.sin_addr, he->h_addr_list[0], he->h_length);

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
        return true;
    }

    // Send exit command if requested
    if (send_exit)
    {
        const char *exit_command = "exit";
        send(context->socket, exit_command, (int)strlen(exit_command), 0);
    }

    // Close socket
    close_socket(context->socket);
    context->socket = SOCKET_ERROR_VALUE;
    context->connected = false;

    comm_log(context, "Disconnected from device");
    return true;
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

    // Log the message being sent
    comm_log(context, "Sending message: %s", message);

    // Send message
    if (send(context->socket, message, (int)strlen(message), 0) < 0)
    {
        comm_log(context, "Failed to send message");
        return false;
    }

    // Receive response
    memset(response, 0, response_size);
    int bytes_received = recv(context->socket, response, response_size - 1, 0);
    if (bytes_received <= 0)
    {
        comm_log(context, "Failed to receive response");
        return false;
    }

    response[bytes_received] = '\0';
    comm_log(context, "Received response: %s", response);
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