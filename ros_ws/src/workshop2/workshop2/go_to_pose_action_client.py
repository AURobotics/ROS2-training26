"""
CANCELLED TASK
"""

import rclpy
from rclpy.action.client import ActionClient
from rclpy.node import Node

from turtle_interfaces.action import GoToPose


class GoToPoseActionClient(Node):
    """Sends a single goal coordinate to the GoToPose action server."""

    def __init__(self):
        super().__init__('go_to_pose_action_client')
        self._action_client = ActionClient(self, GoToPose, 'go_to_pose')

        self.declare_parameter('x', 0.0)
        self.declare_parameter('y', 0.0)

        self.x = self.get_parameter('x').value
        self.y = self.get_parameter('y').value

        if self.x is not None and self.y is not None:
            self.send_goal(self.x, self.y)
        else:
            self.get_logger().error('Parameters x and y must be set.')

    def send_goal(self, x: float, y: float):
        goal_msg = GoToPose.Goal()
        goal_msg.x = x
        goal_msg.y = y

        self._action_client.wait_for_server()
        self.get_logger().info(f'Sending goal: ({x:.2f}, {y:.2f})')

        send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback
        )
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn('Goal rejected by server.')
            rclpy.shutdown()
            return

        self.get_logger().info('Goal accepted by server.')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Result: success={result.success}')
        rclpy.shutdown()

    def feedback_callback(self, feedback_msg):
        pose = feedback_msg.feedback.current_pose
        self.get_logger().info(
            f'Feedback -> x={pose.x:.2f}, y={pose.y:.2f}, theta={pose.theta:.2f}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = GoToPoseActionClient()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
