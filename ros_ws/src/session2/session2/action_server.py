import time
import rclpy
from rclpy.node import Node
from example_interfaces.action import Fibonacci
from rclpy.action.server import ActionServer

"""
order = 5
0
1 + 0 = 1
1 + 1 = 2
2 + 1 = 3
3 + 2 = 5

1 1 3 4 5
"""

class MyActionServer(Node):
    def __init__(self):
        super().__init__("action_server")
        self.get_logger().info("Action Server Node Started!!")
        self.action_server = ActionServer(
            self,
            Fibonacci,
            "fibonacci",
            self.execute_callback
        )

    def execute_callback(self, goal_handle):
        self.get_logger().info("Executing Goal...")
        feedback_msg = Fibonacci.Feedback()
        feedback_msg.sequence = [0, 1]

        for i in range(1, goal_handle.request.order):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info("Goal Canceled")
                return Fibonacci.Result()

            feedback_msg.sequence.append(feedback_msg.sequence[i] + feedback_msg.sequence[i-1])
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(f"Feedback: {feedback_msg.sequence}")
            time.sleep(1)

        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = feedback_msg.sequence
        self.get_logger().info(f"Result: {result.sequence}")
        return result

def main():
    rclpy.init()
    node = MyActionServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()