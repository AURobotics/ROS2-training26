import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class ServiceService(Node):
    def __init__(self):
        super().__init__("service_server")
        self.get_logger().info("Service Server Node Started!!")
        self.srv = self.create_service(AddTwoInts, "add_two_ints", self.add_two_ints_callback)

    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f"Incoming request: a={request.a}, b={request.b}. Sending back response: {response.sum}")
        return response

def main():
    rclpy.init()
    node = ServiceService()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()