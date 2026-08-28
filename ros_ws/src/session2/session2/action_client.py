import rclpy
from rclpy.node import Node
from example_interfaces.action import Fibonacci
from rclpy.action.client import ActionClient

class MyActionClient(Node):
    def __init__(self):
        super().__init__("action_client")
        self.get_logger().info("Action Client Node Started!!")
        self._action_client = ActionClient(self, Fibonacci, "fibonacci")
        self.send_goal(5)  # Send a goal with order 5

    def send_goal(self, order):
        goal_msg = Fibonacci.Goal()
        goal_msg.order = order

        self.get_logger().info("Waiting for action server...")
        self._action_client.wait_for_server()

        self.get_logger().info(f"Sending goal request for order: {order}")
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f"Received feedback: {feedback.sequence}")

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info("Goal rejected :(")
            return

        self.get_logger().info("Goal accepted :)")
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f"Result: {result.sequence}")

def main():
    rclpy.init()
    node = MyActionClient()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()