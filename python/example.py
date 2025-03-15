"""
Example usage of the 1:1 DLL wrappers.
This demonstrates how to use the wrappers with minimal additional logic.
"""

import ctypes
from device import DeviceDLL, DeviceMemory
from driver import DriverDLL, DeviceStatus, SensorData, ActuatorData


def device_log_callback(message):
    """Callback function for device logging."""
    print(f"Device: {message.decode('utf-8')}")


def driver_log_callback(message):
    """Callback function for driver logging."""
    print(f"Driver: {message.decode('utf-8')}")


def run_device_example():
    """Example of using the device DLL wrapper."""
    print("\n=== Device Example ===")

    # Initialize the device DLL
    device = DeviceDLL()

    # Initialize the device
    result = device.init(device_log_callback)
    print(f"Device init result: {result}")

    # Start the device
    result = device.start()
    print(f"Device start result: {result}")

    # Get device memory
    memory = DeviceMemory()
    result = device.get_memory(memory)
    print(f"Get memory result: {result}")

    if result:
        print(f"Temperature sensor ID: {memory.sensor_a_id}")
        print(f"Temperature value: {memory.sensor_a_reading}")
        print(f"Humidity sensor ID: {memory.sensor_b_id}")
        print(f"Humidity value: {memory.sensor_b_reading}")
        print(f"LED value: {memory.actuator_a}")

    # Set LED value
    memory.actuator_a = 255  # Set LED to max brightness
    result = device.set_memory(memory)
    print(f"Set memory result: {result}")

    # Process a command
    command = "310164"  # Set LED to 100 (0x64)
    response = ctypes.create_string_buffer(7)
    result = device.process_command(command, response)
    print(f"Process command result: {result}")
    print(f"Response: {response.value.decode('utf-8')}")

    # Stop the device
    result = device.stop()
    print(f"Device stop result: {result}")


def run_driver_example():
    """Example of using the driver DLL wrapper."""
    print("\n=== Driver Example ===")

    # Initialize the driver DLL
    driver = DriverDLL()

    # Initialize the driver
    result = driver.init(driver_log_callback)
    print(f"Driver init result: {result}")

    # Connect to the device
    result = driver.connect("localhost", 8989)
    print(f"Connect result: {result}")

    # Get device status
    status = DeviceStatus()
    result = driver.get_status(status)
    print(f"Get status result: {result}")

    if result:
        print(f"Connected: {status.connected}")
        print(f"Sensors powered: {status.sensors_powered}")
        print(f"Actuators powered: {status.actuators_powered}")
        print(f"Has errors: {status.has_errors}")

    # Get sensor data
    sensor_data = SensorData()
    result = driver.get_sensors(sensor_data)
    print(f"Get sensors result: {result}")

    if result:
        print(f"Temperature ID: {sensor_data.temperature_id}")
        print(f"Temperature value: {sensor_data.temperature_value}")
        print(f"Humidity ID: {sensor_data.humidity_id}")
        print(f"Humidity value: {sensor_data.humidity_value}")

    # Set LED value
    result = driver.set_led(128)  # Set LED to half brightness
    print(f"Set LED result: {result}")

    # Send a raw command
    command = "310180"  # Set LED to 128 (0x80)
    response = ctypes.create_string_buffer(7)
    result = driver.send_command(command, response)
    print(f"Send command result: {result}")
    print(f"Response: {response.value.decode('utf-8')}")

    # Disconnect from the device
    result = driver.disconnect()
    print(f"Disconnect result: {result}")


if __name__ == "__main__":
    # Run the device example first
    run_device_example()

    # Then run the driver example
    run_driver_example()
