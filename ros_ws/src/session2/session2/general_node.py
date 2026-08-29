import rclpy
from rclpy.node import Node

class GeneralNode(Node):
    def __init__(self):
        super().__init__("general_node")
        # -------------------------------------------------------------
        # 1. DECLARE PARAMETERS (with default values matching types)
        # -------------------------------------------------------------
        # String
        self.declare_parameter('robot_name', 'default_name')
        
        # Numbers (Float & Integer)
        self.declare_parameter('max_speed', 0.0)
        self.declare_parameter('target_id', 0)
        
        # Boolean
        self.declare_parameter('enable_safety', False)
        
        # Arrays / Lists
        self.declare_parameter('waypoints', [0.0])
        self.declare_parameter('sensor_names', [''])
        
        # Nested parameters (Dot notation for sub-namespaces)
        self.declare_parameter('pid_gains.kp', 0.0)
        self.declare_parameter('pid_gains.ki', 0.0)
        self.declare_parameter('pid_gains.kd', 0.0)

        # -------------------------------------------------------------
        # 2. RETRIEVE PARAMETER VALUES
        # -------------------------------------------------------------
        # Using .value (Clean Pythonic extraction)
        robot_name = self.get_parameter('robot_name').value
        max_speed = self.get_parameter('max_speed').value
        target_id = self.get_parameter('target_id').value
        enable_safety = self.get_parameter('enable_safety').value
        waypoints = self.get_parameter('waypoints').value
        sensor_names = self.get_parameter('sensor_names').value

        # Sub-namespace values
        kp = self.get_parameter('pid_gains.kp').value
        ki = self.get_parameter('pid_gains.ki').value
        kd = self.get_parameter('pid_gains.kd').value

        # -------------------------------------------------------------
        # 3. DISPLAY PARAMETERS IN TERMINAL
        # -------------------------------------------------------------
        self.get_logger().info("==========================================")
        self.get_logger().info(f"Robot Name     : {robot_name}")
        self.get_logger().info(f"Max Speed      : {max_speed} m/s")
        self.get_logger().info(f"Target ID      : {target_id}")
        self.get_logger().info(f"Safety Enabled : {enable_safety}")
        self.get_logger().info(f"Waypoints      : {waypoints}")
        self.get_logger().info(f"Sensors        : {sensor_names}")
        self.get_logger().info(f"PID Gains      : Kp={kp}, Ki={ki}, Kd={kd}")
        self.get_logger().info("==========================================")

def main():
    rclpy.init()
    node = GeneralNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()