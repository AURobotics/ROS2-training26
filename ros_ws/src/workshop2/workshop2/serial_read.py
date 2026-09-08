#!/usr/bin/env python3
"""
ROS 2 node that reads sensor data from a microcontroller (e.g. Arduino)
over a serial port and logs it.

Expects newline-terminated ASCII lines of the form:

    TEMP:23.45

This matches what mock_sensor_source.py writes, so the two can be tested
together via a socat pty pair:

    socat -d -d pty,raw,echo=0 pty,raw,echo=0
    # ex output: -> /dev/pts/3 and /dev/pts/4

    python3 mock_sensor_source.py /dev/pts/3 9600
    ros2 run workshop2 serial_read --ros-args -p serial_port:=/dev/pts/4 -p baud_rate:=9600

Usage (standalone):
    python3 serial_read.py
    ros2 run <package> serial_read
"""
import rclpy
from rclpy.node import Node

import serial


class SerialSensorReader(Node):
    def __init__(self):
        super().__init__('serial_reader')

        self.declare_parameter('serial_port', '/dev/serial/by-id/usb-STMicroelectronics_STM32_Virtual_ComPort_20483076314E-if00')
        self.declare_parameter('baud_rate', 115200)
        self.declare_parameter('poll_period_sec', 0.1)

        port = self.get_parameter('serial_port').get_parameter_value().string_value
        baud = self.get_parameter('baud_rate').get_parameter_value().integer_value
        poll_period = self.get_parameter('poll_period_sec').get_parameter_value().double_value

        try:
            self.conn = serial.Serial(port, baud, timeout=1.0)
        except serial.SerialException as exc:
            self.get_logger().error(f'Could not open serial port {port}: {exc}')
            raise

        self.get_logger().info(f'Listening for sensor data on {port} at {baud} baud.')

        self.timer = self.create_timer(poll_period, self.poll_serial)

    def poll_serial(self):
        try:
            if self.conn.in_waiting == 0:
                return
            raw_line = self.conn.readline()
        except serial.SerialException as exc:
            self.get_logger().error(f'Serial read error: {exc}')
            return

        if not raw_line:
            return

        try:
            line = raw_line.decode('utf-8').strip()
        except UnicodeDecodeError:
            self.get_logger().warn(f'Received undecodable bytes: {raw_line!r}')
            return

        if not line:
            return

        reading = self.parse_line(line)
        if reading is None:
            self.get_logger().warn(f'Unrecognized line: {line!r}')
            return

        key, value = reading
        self.get_logger().info(f'{key}: {value}')

    @staticmethod
    def parse_line(line: str):
        """Parse a 'KEY:value' line into (key, float value), or None if malformed."""
        if ':' not in line:
            return None
        key, _, value_str = line.partition(':')
        try:
            value = float(value_str)
        except ValueError:
            return None
        return key.strip(), value

    def destroy_node(self):
        if hasattr(self, 'conn') and self.conn.is_open:
            self.conn.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = SerialSensorReader()
        rclpy.spin(node)
    except (KeyboardInterrupt, serial.SerialException):
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.shutdown()
        