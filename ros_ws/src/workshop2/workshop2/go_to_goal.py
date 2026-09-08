import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from std_srvs.srv import SetBool


class GoToGoal(Node):
    def __init__(self):
        super().__init__('go_to_goal')

        # Declare ROS 2 parameters with default values
        # (used if no YAML file or override is supplied at launch)
        self.declare_parameter('target_x', 10.0)
        self.declare_parameter('target_y', 10.0)
        self.declare_parameter('linear_gain', 1.5)
        self.declare_parameter('angular_gain', 6.0)
        self.declare_parameter('distance_tolerance', 0.1)
        self.declare_parameter('angle_tolerance', 0.05)
        self.declare_parameter('loop_rate_hz', 20.0)

        # Target Goal Coordinates
        self.goal_x = self.get_parameter('target_x').value
        self.goal_y = self.get_parameter('target_y').value

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
        self.goal_reached = False

        # Movement is now gated behind a service call instead of starting
        # automatically. The control loop only publishes cmd_vel once this
        # flag is set to True.
        self.movement_active = False

        # ROS 2 Publisher & Subscriber
        self.cmd_vel_publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_subscriber = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10
        )

        # SetBool Service Server: a client calling this with data=True
        # arms the node to start driving the turtle toward the goal.
        # The callback ONLY flips a flag and returns immediately - the
        # actual work happens in the timer-driven control_loop below.
        self.start_service = self.create_service(
            SetBool, 'start_movement', self.start_movement_callback
        )

        # Control Loop running at the configured rate
        self.timer = self.create_timer(1.0 / self.loop_rate_hz, self.control_loop)

        self.get_logger().info(
            f'go_to_goal ready. Target: ({self.goal_x}, {self.goal_y}). '
            f"Waiting for a 'start_movement' service call with data=True."
        )

    def start_movement_callback(self, request: SetBool.Request, response: SetBool.Response):
        """SetBool service callback - must return quickly.

        Only toggles the movement_active flag; all actual driving logic
        happens later in control_loop(), which runs on its own timer.
        """
        self.movement_active = request.data

        if request.data:
            self.goal_reached = False  # allow re-arming after a previous run
            response.success = True
            response.message = 'Movement started: turtle will drive to the goal.'
            self.get_logger().info('Service call received: starting movement toward goal.')
        else:
            response.success = True
            response.message = 'Movement stopped.'
            self.get_logger().info('Service call received: stopping movement.')

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
    