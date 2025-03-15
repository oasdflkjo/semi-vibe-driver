#include <stdio.h>
#include <stdlib.h>
#include <windows.h>

// Define the callback function type
typedef void (*LogCallback)(const char *message);

// Define the callback function
void log_callback(const char *message) { printf("DLL: %s\n", message); }

int main() {
  printf("Testing DLL loading...\n");

  // Load the DLL
  HMODULE dll = LoadLibrary("build/bin/Debug/semi_vibe_device.dll");
  if (!dll) {
    printf("Failed to load DLL: %d\n", GetLastError());
    return 1;
  }
  printf("DLL loaded successfully\n");

  // Get function pointers
  typedef int (*DeviceInitFunc)(LogCallback callback);
  typedef int (*DeviceStartFunc)();
  typedef int (*DeviceStopFunc)();

  DeviceInitFunc device_init = (DeviceInitFunc)GetProcAddress(dll, "device_init");
  DeviceStartFunc device_start = (DeviceStartFunc)GetProcAddress(dll, "device_start");
  DeviceStopFunc device_stop = (DeviceStopFunc)GetProcAddress(dll, "device_stop");

  if (!device_init || !device_start || !device_stop) {
    printf("Failed to get function pointers:\n");
    printf("  device_init: %p\n", device_init);
    printf("  device_start: %p\n", device_start);
    printf("  device_stop: %p\n", device_stop);
    printf("Error: %d\n", GetLastError());
    FreeLibrary(dll);
    return 1;
  }
  printf("Function pointers obtained successfully\n");

  // Initialize the device
  printf("Initializing device...\n");
  int init_result = device_init(log_callback);
  printf("Initialization result: %d\n", init_result);

  if (init_result) {
    // Start the device
    printf("Starting device...\n");
    int start_result = device_start();
    printf("Start result: %d\n", start_result);

    if (start_result) {
      printf("Device started successfully\n");

      // Wait for a moment
      printf("Waiting for 5 seconds...\n");
      Sleep(5000);

      // Stop the device
      printf("Stopping device...\n");
      int stop_result = device_stop();
      printf("Stop result: %d\n", stop_result);
    }
  }

  // Unload the DLL
  FreeLibrary(dll);
  printf("DLL unloaded\n");

  return 0;
}