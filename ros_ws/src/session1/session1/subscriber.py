import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Subscriber(Node):
    def __init__(self):
        super().__init__("subscriber")
        self.subscriber = self.create_subscription(String,"/string",self.subscriber_callback,10)

    def subscriber_callback(self,msg):
        self.get_logger().info(f"Received: {msg.data}")

def main():
    rclpy.init()
    node = Subscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()