import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Publisher(Node):
    def __init__(self):
        super().__init__("publisher")
        self.get_logger().info("Publisher Node Started!!")
        self.publisher = self.create_publisher(String,"/string",10)
        self.counter=0
        self.create_timer(1,self.timer_callback)
 
    def timer_callback(self):
        self.get_logger().info(f"Hello {self.counter}")
        self.publisher.publish(String(data=f"Hello {self.counter}"))
        self.counter+=1

def main():
    rclpy.init()
    node = Publisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()