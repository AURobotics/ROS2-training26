import rclpy
from rclpy.node import Node

class Basic_node(Node):
    def __init__(self):
        super().__init__("basic_node")
        self.get_logger().info("Basic Node Started!!")
        self.counter=0
        self.create_timer(1,self.timer_callback)
 
    def timer_callback(self):
        self.get_logger().info(f"Hello {self.counter}")
        self.counter+=1

def main():
    rclpy.init()
    node = Basic_node()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()