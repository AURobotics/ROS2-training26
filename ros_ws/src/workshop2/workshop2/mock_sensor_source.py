#!/usr/bin/env python3
"""
Writes fake sensor readings to a serial port once per second.

Use this with `socat` to simulate a microcontroller when no Arduino is
available:

    socat -d -d pty,raw,echo=0 pty,raw,echo=0

That prints two linked devices, e.g. /dev/pts/3 and /dev/pts/4. Run this
script pointed at one of them, and set serial_service_server's 'serial_port'
parameter to the other.

Usage:
    ros2 run workshop2 mock_sensor_source /dev/pts/3 9600
"""
import random
import sys
import time

import serial


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/pts/1'
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 9600

    conn = serial.Serial(port, baud, timeout=1.0)
    print(f'Writing fake sensor data to {port} at {baud} baud. Ctrl+C to stop.')
    try:
        while True:
            reading = round(random.uniform(20.0, 30.0), 2)
            line = f'TEMP:{reading}\n'
            conn.write(line.encode('utf-8'))
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        conn.close()


if __name__ == '__main__':
    main()
