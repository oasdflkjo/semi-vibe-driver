"""
Utility functions for working with the Semi-Vibe-Device and Semi-Vibe-Driver DLLs.
This module provides higher-level functions that build on top of the 1:1 wrappers.
"""

import ctypes
from device import DeviceDLL, DeviceMemory
from driver import DriverDLL, DeviceStatus, SensorData, ActuatorData


def get_device_state(device):
    """Get the current device state as a dictionary.

    Args:
        device: DeviceDLL instance

    Returns:
        dict: Device state or None if failed
    """
    memory = DeviceMemory()
    if not device.get_memory(memory):
        return None

    return {
        "status": {
            "connected": bool(memory.connected_device),
            "sensors_powered": bool(memory.power_sensors),
            "actuators_powered": bool(memory.power_actuators),
            "has_errors": bool(memory.error_state),
        },
        "sensors": {
            "temperature_id": memory.sensor_a_id,
            "temperature_value": memory.sensor_a_reading,
            "humidity_id": memory.sensor_b_id,
            "humidity_value": memory.sensor_b_reading,
        },
        "actuators": {
            "led_value": memory.actuator_a,
            "fan_value": memory.actuator_b,
            "heater_value": memory.actuator_c,
            "doors_value": memory.actuator_d,
        },
    }


def set_device_state(device, new_state):
    """Set the device state from a dictionary.

    Args:
        device: DeviceDLL instance
        new_state: Dictionary with state values to set

    Returns:
        bool: True if successful
    """
    # Get current memory
    memory = DeviceMemory()
    if not device.get_memory(memory):
        return False

    # Update memory with new state
    if "sensors" in new_state:
        sensors = new_state["sensors"]
        if "temperature_value" in sensors:
            memory.sensor_a_reading = sensors["temperature_value"]
        if "humidity_value" in sensors:
            memory.sensor_b_reading = sensors["humidity_value"]

    if "actuators" in new_state:
        actuators = new_state["actuators"]
        if "led_value" in actuators:
            memory.actuator_a = actuators["led_value"]
        if "fan_value" in actuators:
            memory.actuator_b = actuators["fan_value"]
        if "heater_value" in actuators:
            memory.actuator_c = actuators["heater_value"]
        if "doors_value" in actuators:
            memory.actuator_d = actuators["doors_value"]

    # Write memory back to device
    return device.set_memory(memory)


def get_driver_status(driver):
    """Get the device status as a dictionary.

    Args:
        driver: DriverDLL instance

    Returns:
        dict: Status dictionary or None if failed
    """
    status = DeviceStatus()
    if not driver.get_status(status):
        return None

    return {
        "connected": status.connected,
        "sensors_powered": status.sensors_powered,
        "actuators_powered": status.actuators_powered,
        "has_errors": status.has_errors,
    }


def get_driver_sensors(driver):
    """Get sensor data as a dictionary.

    Args:
        driver: DriverDLL instance

    Returns:
        dict: Sensor data dictionary or None if failed
    """
    data = SensorData()
    if not driver.get_sensors(data):
        return None

    return {
        "temperature_id": data.temperature_id,
        "temperature_value": data.temperature_value,
        "humidity_id": data.humidity_id,
        "humidity_value": data.humidity_value,
    }


def get_driver_actuators(driver):
    """Get actuator data as a dictionary.

    Args:
        driver: DriverDLL instance

    Returns:
        dict: Actuator data dictionary or None if failed
    """
    data = ActuatorData()
    if not driver.get_actuators(data):
        return None

    return {
        "led_value": data.led_value,
        "fan_value": data.fan_value,
        "heater_value": data.heater_value,
        "doors_value": data.doors_value,
    }


def set_led(device, value):
    """Set the LED value directly on the device.

    Args:
        device: DeviceDLL instance
        value: LED value (0-255)

    Returns:
        bool: True if successful
    """
    memory = DeviceMemory()
    if not device.get_memory(memory):
        return False

    memory.actuator_a = value
    return device.set_memory(memory)


def send_command(driver, command):
    """Send a raw command to the device.

    Args:
        driver: DriverDLL instance
        command: Command string (6 hex digits)

    Returns:
        str: Response from the device, or None if failed
    """
    if not command or len(command) != 6:
        return None

    response_buffer = ctypes.create_string_buffer(7)
    if not driver.send_command(command, response_buffer):
        return None

    return response_buffer.value.decode("utf-8")
