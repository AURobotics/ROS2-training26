import rclpy
from rclpy.node import Node
from turtle_interfaces.srv import SetTarget

# Defaults; all overridable via ROS 2 parameters at launch time.
STARTUP_DELAY_SEC = 5.0
DEFAULT_TARGET_X = 10.0
DEFAULT_TARGET_Y = 10.0


class GoToGoalClient(Node):
    def __init__(self):
        super().__init__('go_to_goal_client_bonus')

        self.declare_parameter('delay_sec', STARTUP_DELAY_SEC)
        self.declare_parameter('target_x', DEFAULT_TARGET_X)
        self.declare_parameter('target_y', DEFAULT_TARGET_Y)

        self.delay_sec = self.get_parameter('delay_sec').value
        self.target_x = self.get_parameter('target_x').value
        self.target_y = self.get_parameter('target_y').value

        self.client = self.create_client(SetTarget, 'set_target')

        # One-shot timer: fires once after delay_sec, then cancels itself.
        self.delay_timer = self.create_timer(self.delay_sec, self.on_delay_elapsed)

        self.get_logger().info(
            f'go_to_goal_client_bonus ready. Will call the service in {self.delay_sec:.1f}s '
            f'with target ({self.target_x}, {self.target_y}).'
        )

    def on_delay_elapsed(self):
        # Only fire once.
        self.delay_timer.cancel()

        if not self.client.service_is_ready():
            self.get_logger().warn("'set_target' service not available yet, waiting...")
            self.client.wait_for_service(timeout_sec=10.0)

        request = SetTarget.Request()
        request.x = self.target_x
        request.y = self.target_y

        self.get_logger().info(
            f'Calling go_to_goal with x={request.x}, y={request.y}.'
        )
        future = self.client.call_async(request)
        future.add_done_callback(self.on_response)

    def on_response(self, future):
        try:
            response = future.result()
        except Exception as exc:
            self.get_logger().error(f'Service call failed: {exc}')
            return

        if response.success:
            self.get_logger().info(f'Request accepted: {response.message}')
        else:
            self.get_logger().warn(f'Request rejected: {response.message}')


def main(args=None):
    rclpy.init(args=args)
    node = GoToGoalClient()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
