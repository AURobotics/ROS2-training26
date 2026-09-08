import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool

# How long to wait (in seconds) after this node starts before it calls
# the go_to_goal node's 'start_movement' service.
STARTUP_DELAY_SEC = 5.0



class GoToGoalClient(Node):
    def __init__(self):
        super().__init__('go_to_goal_client')

        self.declare_parameter('delay_sec', STARTUP_DELAY_SEC)
        self.delay_sec = self.get_parameter('delay_sec').value

        self.client = self.create_client(SetBool, 'start_movement')

        # One-shot timer: fires once after delay_sec, then cancels itself.
        # This keeps the delay logic out of the service callback pattern
        # entirely - it lives in the client, not the server.
        self.delay_timer = self.create_timer(self.delay_sec, self.on_delay_elapsed)

        self.get_logger().info(
            f'go_to_goal_client ready. Will call the service in {self.delay_sec:.1f}s.'
        )

    def on_delay_elapsed(self):
        # Only fire once.
        self.delay_timer.cancel()

        if not self.client.service_is_ready():
            self.get_logger().warn(
                "'start_movement' service not available yet, waiting..."
            )
            self.client.wait_for_service(timeout_sec=10.0)

        request = SetBool.Request()
        request.data = True

        self.get_logger().info("Calling 'start_movement' service with data=True.")
        future = self.client.call_async(request)
        future.add_done_callback(self.on_response)

    def on_response(self, future):
        try:
            response = future.result()
        except Exception as exc:
            self.get_logger().error(f'Service call failed: {exc}')
            return

        if response.success:
            self.get_logger().info(f'Service call succeeded: {response.message}')
        else:
            self.get_logger().warn(f'Service call was not accepted: {response.message}')


def main(args=None):
    rclpy.init(args=args)
    node = GoToGoalClient()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
