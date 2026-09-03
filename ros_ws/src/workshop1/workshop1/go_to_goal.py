import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

TARGET_X = 10.0  # Target X coordinate for the turtle to reach
TARGET_Y = 10.0  # Target Y coordinate for the turtle to reach

class GoToGoal(Node):
    def __init__(self):
        super().__init__('go_to_goal')

        # Target Goal Coordinates
        self.goal_x = TARGET_X
        self.goal_y = TARGET_Y

        # Proportional Gains (K_p)
        self.kp_linear = 1.5
        self.kp_angular = 6.0

        # Tolerances
        self.distance_tolerance = 0.1  # Distance error limit to consider goal reached
        self.angle_tolerance = 0.05    # Heading alignment threshold before moving forward

        # State Variables
        self.current_pose = None
        self.goal_reached = False

        # ROS 2 Publisher & Subscriber
        self.cmd_vel_publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_subscriber = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10
        )

        # Control Loop running at 20 Hz
        self.timer = self.create_timer(0.05, self.control_loop)

        self.get_logger().info(f'Navigating turtle to target goal: ({self.goal_x}, {self.goal_y})')

    def pose_callback(self, msg: Pose):
        """Update current position and heading from /turtle1/pose stream."""
        self.current_pose = msg

    def normalize_angle(self, angle: float) -> float:
        """Keep heading angle within [-pi, pi] to avoid unnecessary 360-degree turns."""
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle

    def control_loop(self):
        """Proportional Control Loop."""
        if self.current_pose is None or self.goal_reached:
            return

        # 1. Calculate Cartesian Errors
        dx = self.goal_x - self.current_pose.x
        dy = self.goal_y - self.current_pose.y

        # Euclidean Distance Error: sqrt((x_g - x)^2 + (y_g - y)^2)
        distance_error = math.sqrt(dx**2 + dy**2)

        # Desired Heading Angle: atan2(dy, dx)
        target_angle = math.atan2(dy, dx)
        heading_error = self.normalize_angle(target_angle - self.current_pose.theta)

        msg = Twist()

        # 2. Check if Goal is Reached
        if distance_error < self.distance_tolerance:
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.cmd_vel_publisher.publish(msg)
            self.goal_reached = True
            self.get_logger().info('Goal Reached Successfully!')
            return

        # 3. Proportional Control Logic
        # If heading error is large, align facing direction first before moving forward
        if abs(heading_error) > self.angle_tolerance:
            msg.linear.x = 0.0
            msg.angular.z = self.kp_angular * heading_error
        else:
            # Scale forward speed and heading alignment concurrently
            msg.linear.x = min(self.kp_linear * distance_error, 2.0)  # Cap speed at 2.0 m/s
            msg.angular.z = self.kp_angular * heading_error

        self.cmd_vel_publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = GoToGoal()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
