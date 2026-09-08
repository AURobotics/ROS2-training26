import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtle_interfaces.srv import SetTarget

# turtlesim's default field is roughly an 11x11 square (0.0 to 11.0 on
# each axis). Requests outside this range are rejected as out of bounds.
FIELD_MIN = 0.0
FIELD_MAX = 11.0


class GoToGoal(Node):
    def __init__(self):
        super().__init__('go_to_goal_bonus')

        # Note: target_x / target_y are intentionally NOT declared as
        # parameters anymore. With the SetTarget service, the goal
        # coordinates come from the request, not from the YAML file.
        self.declare_parameter('linear_gain', 1.5)
        self.declare_parameter('angular_gain', 6.0)
        self.declare_parameter('distance_tolerance', 0.1)
        self.declare_parameter('angle_tolerance', 0.05)
        self.declare_parameter('loop_rate_hz', 20.0)

        # Proportional Gains (K_p)
        self.kp_linear = self.get_parameter('linear_gain').value
        self.kp_angular = self.get_parameter('angular_gain').value

        # Tolerances
        self.distance_tolerance = self.get_parameter('distance_tolerance').value
        self.angle_tolerance = self.get_parameter('angle_tolerance').value

        # Loop Rate
        self.loop_rate_hz = self.get_parameter('loop_rate_hz').value

        # State Variables
        self.current_pose = None
        self.goal_reached = True   # nothing to do until a target is set
        self.movement_active = False
        self.goal_x = None
        self.goal_y = None

        # ROS 2 Publisher & Subscriber
        self.cmd_vel_publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_subscriber = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10
        )

        # SetTarget Service Server. The callback ONLY validates the
        # request, stores the new goal, and flips movement_active - it
        # does NOT wait for the turtle to arrive. Actual driving happens
        # in the timer-driven control_loop below, so the service returns
        # immediately regardless of how long the turtle takes to arrive.
        self.set_target_service = self.create_service(
            SetTarget, 'set_target', self.set_target_callback
        )

        # Control Loop running at the configured rate
        self.timer = self.create_timer(1.0 / self.loop_rate_hz, self.control_loop)

        self.get_logger().info(
            "go_to_goal ready. Waiting for a 'set_target' service call with x, y."
        )

    def set_target_callback(self, request: SetTarget.Request, response: SetTarget.Response):
        """SetTarget service callback - must return quickly.

        Validates the requested coordinates, stores them, and arms
        movement. It does not block waiting for the turtle to reach the
        goal; the timer-driven control_loop() does the actual driving.
        """
        x, y = request.x, request.y

        in_bounds = (FIELD_MIN <= x <= FIELD_MAX) and (FIELD_MIN <= y <= FIELD_MAX)

        if not in_bounds:
            response.success = False
            response.message = (
                f'Rejected: ({x}, {y}) is out of bounds '
                f'[{FIELD_MIN}, {FIELD_MAX}] on both axes.'
            )
            self.get_logger().warn(response.message)
            return response

        self.goal_x = x
        self.goal_y = y
        self.goal_reached = False
        self.movement_active = True

        response.success = True
        response.message = f'Accepted: driving to ({x}, {y}).'
        self.get_logger().info(response.message)
        return response

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
        """Proportional Control Loop. Only drives the turtle once movement_active is True."""
        if not self.movement_active:
            return

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
            self.movement_active = False
            self.get_logger().info(
                f'Goal Reached Successfully at ({self.goal_x}, {self.goal_y})!'
            )
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