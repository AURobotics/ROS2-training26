"""
CANCELLED TASK
"""

import math

import rclpy
from rclpy.action.server import ActionServer, CancelResponse, GoalResponse
from rclpy.node import Node
from rclpy.task import Future

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

from turtle_interfaces.action import GoToPose

# turtlesim's default window is roughly 0.0 to 11.0 on both axes.
MIN_BOUND = 0.0
MAX_BOUND = 11.0

CONTROL_PERIOD = 0.05  # 20 Hz, matches Workshop 1's control timer


class GoToPoseActionServer(Node):
    """
    Action server wrapping the Workshop 1 proportional control loop.

    Goal validation happens in goal_callback() (reject anything outside the
    turtlesim window) so invalid goals never reach execute_callback().
    execute_callback() runs the same proportional logic as go_to_goal.py,
    but publishes Feedback each tick and returns a Result instead of just
    stopping silently.
    """

    def __init__(self):
        super().__init__('go_to_pose_action_server')

        # Proportional gains (same values as Workshop 1, Task 2)
        self.kp_linear = 1.5
        self.kp_angular = 6.0

        # Tolerances
        self.distance_tolerance = 0.1
        self.angle_tolerance = 0.05

        self.current_pose = None

        self.cmd_vel_publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_subscriber = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10
        )

        self._action_server = ActionServer(
            self,
            GoToPose,
            'go_to_pose',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
        )

        self.get_logger().info('GoToPose action server ready (single-threaded).')

    def pose_callback(self, msg: Pose):
        self.current_pose = msg

    def normalize_angle(self, angle: float) -> float:
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle

    def goal_callback(self, goal_request: GoToPose.Goal):
        """Reject goals outside turtlesim's drawable window before execution starts."""
        x, y = goal_request.x, goal_request.y
        if not (MIN_BOUND <= x <= MAX_BOUND and MIN_BOUND <= y <= MAX_BOUND):
            self.get_logger().warn(
                f'Rejecting goal ({x:.2f}, {y:.2f}): outside bounds '
                f'[{MIN_BOUND}, {MAX_BOUND}].'
            )
            return GoalResponse.REJECT

        self.get_logger().info(f'Accepted goal: ({x:.2f}, {y:.2f})')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Received cancel request.')
        return CancelResponse.ACCEPT

    def _sleep(self, duration: float) -> Future:
        """
        Non-blocking sleep for use inside an async callback.

        Returns a Future that resolves after `duration` seconds via a
        one-shot timer. Awaiting it suspends the coroutine and returns
        control to the executor -- unlike time.sleep() or Rate.sleep(),
        it never blocks the thread, so other callbacks keep running while
        we "wait".
        """
        future = Future()

        def _on_timer():
            timer.cancel()
            timer.destroy()
            if not future.done():
                future.set_result(None)

        timer = self.create_timer(duration, _on_timer)
        return future

    async def execute_callback(self, goal_handle):
        goal_x = goal_handle.request.x
        goal_y = goal_handle.request.y

        feedback_msg = GoToPose.Feedback()
        result_msg = GoToPose.Result()

        while rclpy.ok():
            if self.current_pose is None:
                await self._sleep(CONTROL_PERIOD)
                continue

            if goal_handle.is_cancel_requested:
                self._stop_turtle()
                goal_handle.canceled()
                result_msg.success = False
                self.get_logger().info('Goal canceled.')
                return result_msg

            dx = goal_x - self.current_pose.x
            dy = goal_y - self.current_pose.y
            distance_error = math.sqrt(dx ** 2 + dy ** 2)
            target_angle = math.atan2(dy, dx)
            heading_error = self.normalize_angle(target_angle - self.current_pose.theta)

            if distance_error < self.distance_tolerance:
                self._stop_turtle()
                goal_handle.succeed()
                result_msg.success = True
                self.get_logger().info('Goal reached successfully!')
                return result_msg

            twist = Twist()
            if abs(heading_error) > self.angle_tolerance:
                twist.linear.x = 0.0
                twist.angular.z = self.kp_angular * heading_error
            else:
                twist.linear.x = min(self.kp_linear * distance_error, 2.0)
                twist.angular.z = self.kp_angular * heading_error
            self.cmd_vel_publisher.publish(twist)

            feedback_msg.current_pose = self.current_pose
            goal_handle.publish_feedback(feedback_msg)

            await self._sleep(CONTROL_PERIOD)

        result_msg.success = False
        return result_msg

    def _stop_turtle(self):
        self.cmd_vel_publisher.publish(Twist())


def main(args=None):
    rclpy.init(args=args)
    node = GoToPoseActionServer()
    try:
        rclpy.spin(node)  # default SingleThreadedExecutor -- no threading needed
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
