import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

class TurtleController(Node):
    def __init__(self):
        super().__init__('turtle_controller')
        
        # Publisher: Sends linear and angular velocity to move the turtle
        self.cmd_vel_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        
        # Subscriber: Receives continuous pose updates from turtlesim
        self.pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10)
        
        # Timer: Publishes velocity commands at 2 Hz (every 0.5 sec)
        self.timer = self.create_timer(0.5, self.publish_velocity)

    def pose_callback(self, msg: Pose):
        # Log live telemetry coordinates received from turtlesim
        self.get_logger().info(f'Turtle Pose -> X: {msg.x:.2f}, Y: {msg.y:.2f}, Theta: {msg.theta:.2f}')

    def publish_velocity(self):
        msg = Twist()
        msg.linear.x = 2.0   # Drive forward at 2.0 m/s
        msg.angular.z = 1.0  # Turn counter-clockwise at 1.0 rad/s
        self.cmd_vel_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = TurtleController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()