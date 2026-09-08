## Workshop 2 - Task 4: Services and serial communication

```bash
ros2 run workshop2 serial_service_server --ros-args -p serial_port:=/dev/ttyUSB0 -p baud_rate:=9600
```
Start reading:
```bash
ros2 service call /toggle_serial_reading std_srvs/srv/SetBool "{data: true}"
```
Stop reading:
```bash
ros2 service call /toggle_serial_reading std_srvs/srv/SetBool "{data: false}"
```

### No Arduino on hand?

Requires `pip install pyserial` and `socat` (`sudo apt install socat`).

```bash
socat -d -d pty,raw,echo=0 pty,raw,echo=0
# prints two devices, e.g. /dev/pts/3 and /dev/pts/4

# Terminal A -- feed fake sensor data into one end:
ros2 run workshop2 mock_sensor_source /dev/pts/3 9600

# Terminal B -- point the service server at the other end:
ros2 run workshop2 serial_service_server --ros-args -p serial_port:=/dev/pts/4
```
