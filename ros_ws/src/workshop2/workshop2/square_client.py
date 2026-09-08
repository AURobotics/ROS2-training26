"""
CANCELLED TASK
"""

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rcl_interfaces.msg import ParameterDescriptor

from turtle_interfaces.action import GoToPose


class SquareClient(Node):
    """
    Reads a list of (x, y) waypoints from parallel YAML array parameters
    and sends them to the GoToPose action server one at a time, moving to
    the next waypoint only after the previous one succeeds (or is rejected).
    """

    def __init__(self):
        super().__init__('square_client')

        self.declare_parameter(
            'waypoints_x', [0.0],
            ParameterDescriptor(description='X coordinates of the square waypoints'),
        )
        self.declare_parameter(
            'waypoints_y', [0.0],
            ParameterDescriptor(description='Y coordinates of the square waypoints'),
        )

        xs = self.get_parameter('waypoints_x').get_parameter_value().double_array_value
        ys = self.get_parameter('waypoints_y').get_parameter_value().double_array_value

        if len(xs) == 0 or len(xs) != len(ys):
            raise ValueError(
                'waypoints_x and waypoints_y must be non-empty and the same length. '
                f'Got {len(xs)} x-values and {len(ys)} y-values.'
            )

        self.waypoints = list(zip(xs, ys))
        self.current_index = 0

        self._action_client = ActionClient(self, GoToPose, 'go_to_pose')
        self.get_logger().info(f'Loaded {len(self.waypoints)} waypoints: {self.waypoints}')

        self._action_client.wait_for_server()
        self.send_next_goal()

    def send_next_goal(self):
        if self.current_index >= len(self.waypoints):
            self.get_logger().info('Square trajectory complete.')
            rclpy.shutdown()
            return

        x, y = self.waypoints[self.current_index]
        self.get_logger().info(
            f'Sending waypoint {self.current_index + 1}/{len(self.waypoints)}: '
            f'({x:.2f}, {y:.2f})'
        )

        goal_msg = GoToPose.Goal()
        goal_msg.x = x
        goal_msg.y = y

        send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback
        )
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn(
                f'Waypoint {self.current_index + 1} rejected by server, skipping.'
            )
            self.current_index += 1
            self.send_next_goal()
            return

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(
            f'Waypoint {self.current_index + 1} result: success={result.success}'
        )
        self.current_index += 1
        self.send_next_goal()

    def feedback_callback(self, feedback_msg):
        pose = feedback_msg.feedback.current_pose
        self.get_logger().debug(f'Feedback -> x={pose.x:.2f}, y={pose.y:.2f}')


def main(args=None):
    rclpy.init(args=args)
    node = SquareClient()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
