Semi-Vibe-Driver
===============
Semi-Vibe-Device is an imaginary device consisting of two sensors and four actuators.

Technical details
-----------------
As this device is just a mock up running only on code and not a physical device, the connection to it is simulated via a socket connection.  
Semi-Vibe-Device listens to a socket with port 8989. When a driver connects to this socket, connection has been established and Semi-Vibe-Device sends an "ACK" message as a signal for this. All of this is done in localhost.

Data is stored in 8 bits per address.

Communication
-------------
After establishing connection, communication is carried out with messages that consist of 6 hex numbers.  
These numbers represent base address, offset address, read/write and data.  
The format of these messages is explained in more detail below.  
There is one exception to this and that is `exit`. When Semi-Vibe-Device receives `exit`, the connection is cut and the device turns off.

Semi-Vibe-Device also responds to messages with 6 hex numbers.  
The response message is the same as the received one except when receiving a read command, the data part has the requested data.

If the command is wrong in some way, the response message consists of an error number and `FFFFF`.

|number|description
|------|-----------
|1     |forbidden
|2     |invalid
|3     |error

#### Reading and writing
R/W bit determines if the command message sent to Semi-Vibe-Driver is read or write.  
`0` means read and `1` means write. This bit takes one whole hex number from the message and giving anything else than `0` or `1` for that number results in an error. 

When sending a read message, the data numbers do not matter, although they have to be valid hex numbers.  
However in the response message the data numbers hold the requested data.

When sending a write message, the data numbers determine what should be written to the given register.  
Some registers are read-only aka you can't write to them. Trying this leads to an error.  
Writing to a valid register that has reserved bits in it just skips those bits. Trying to write to those bits does nothing.

#### Message format
Example message: 0x340141

|hex|base|offset|r/w|data
|---|----|------|---|----
|0x |3   |40    |1  |41  

Base: 1-4  
Offset: check tables below  
R/W: 0-1
Data: read or write data, 00-FF

Address map
-----------

|baseaddr       | name          | R/W?  | description
|---------------|---------------|-------|-------------
| 0             | `RESERVED`    | -     | -
| 1             | `MAIN`        | R     | Read the status of components
| 2             | `SENSOR`      | R     | Read IDs and readings of sensors
| 3             | `ACTUATOR`    | R\W   | Control actuators
| 4             | `CONTROL`     | R\W   | Control power and reset components

#### `MAIN`
Contains the current status of different on-board components.

#### `SENSOR`
Contains the IDs and readings of the connected sensors.  


For this example the sensors get random values everytime the Semi-Vibe-Driver receives a message.   
They have ~1% chance to raise an error flag on `MAIN` 0x03 register. 
We intentianally left these two out from the device implementation!!!!!!!!!!

Examples what these sensors could be:  
A: Temperature. Reads the temperature and gives a value between 0 (freezing) and 255 (melting).  
B: Humidity. Reads the moisture and gives a value between 0 (dry as heck) and 255 (monsoon).

#### `ACTUATOR`
Control the connected actuators.

Examples what these actuators could be:  
A: LED. You can control how bright the LED is from 0 (off) to 255 (brightest).  
B: Fan. You can control how fast the fan spins from 0 (off) to 255 (fastest).  
C: Heater. You can control the heater levels from 0 (off) to 15 (hot).  
D: Doors. You can control four different doors with 0 (open) and 1 (closed).

#### `CONTROL`
Controls the power of connected components. Can also be used to reset the components.  
Writing `0` to the power registers will shutdown the corresponding component. It can't be operated until turned back on by writing `1` to the register.  
Writing `1` to the reset registers will return the corresponding component to default value and clears error flag from `MAIN` 0x03. The reset register automatically then clears itself and sets it back to `0`.

Tables
------

|symbol|description
|------|-----------
|0     | reserved, stays 0
|x     | value changes or can be changed
|sa/sb | corresponds to the sensor A or B, value changes or can be changed
|aa-ad | corresponds to the actuator A, B, C or D, value changes or can be changed

### `MAIN`
|addr|bit7|bit6|bit5|bit4|bit3|bit2|bit1|bit0|description
|----|----|----|----|----|----|----|----|----|-----------
|0x00| ad | ac | ab | aa |  0 | sb |  0 | sa | connected_device
|0x01|  0 |  0 |  0 |  0 |  0 |  0 |  0 |  0 | reserved
|0x02| ad | ac | ab | aa |  0 | sb |  0 | sa | power_state
|0x03| ad | ac | ab | aa |  0 | sb |  0 | sa | error_state

### `SENSOR`
|addr|bit7|bit6|bit5|bit4|bit3|bit2|bit1|bit0|description
|----|----|----|----|----|----|----|----|----|-----------
|0x10|  x |  x |  x |  x |  x |  x |  x |  x | sensor_a_id (temperature)
|0x11|  x |  x |  x |  x |  x |  x |  x |  x | sensor_a_reading
|0x20|  x |  x |  x |  x |  x |  x |  x |  x | sensor_b_id (humidity)
|0x21|  x |  x |  x |  x |  x |  x |  x |  x | sensor_b_reading

### `ACTUATOR`
|addr|bit7|bit6|bit5|bit4|bit3|bit2|bit1|bit0|description
|----|----|----|----|----|----|----|----|----|-------------
|0x10|  x |  x |  x |  x |  x |  x |  x |  x | actuator_a (LED)
|0x20|  x |  x |  x |  x |  x |  x |  x |  x | actuator_b (fan)
|0x30|  0 |  0 |  0 |  0 |  x |  x |  x |  x | actuator_c (heater)
|0x40|  0 |  x |  0 |  x |  0 |  x |  0 |  x | actuator_d (doors)

### `CONTROL`
|addr|bit7|bit6|bit5|bit4|bit3|bit2|bit1|bit0|description
|----|----|----|----|----|----|----|----|----|-----------
|0xFB|  0 |  0 |  0 | sb |  0 |  0 |  0 | sa | power_sensors
|0xFC|  0 | ad |  0 | ac |  0 | ab |  0 | aa | power_actuators
|0xFD|  0 |  0 |  0 | sb |  0 |  0 |  0 | sa | reset_sensors
|0xFE|  0 | ad |  0 | ac |  0 | ab |  0 | aa | reset_actuators


Few notes:
- connected_device values are not specked here and we assume 0 is not connected and !0 is connected
- error state values are not specked here and we assume 0 is no error and !0 is error
- power_state values are not specked here and we assume 0 is off and !0 is on
- should we return error if we make a write to a device that is not connected?
- can some of the devices be unconnected?
- what is the difference between reset and power? typically reset is soft reset by grounding mcu software reset pin and power toggles Vdd.

