import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts
from functools import partial

class Service_client(Node):
    def __init__(self):
        super().__init__("service_client")
        self.get_logger().info("Service Client Node Started!!")


        self.send_request()



    def send_request(self):
        self.client = self.create_client(AddTwoInts, "add_two_ints")

        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Service not available, waiting again...")

        self.request = AddTwoInts.Request()
        self.request.a = 5
        self.request.b = 7

        future = self.client.call_async(self.request)
        future.add_done_callback(partial(self.service_callback, a=self.request.a, b=self.request.b))

    def service_callback(self, future, a, b):
        try:
            response = future.result()
            self.get_logger().info(f"Service response: {a} + {b} = {response.sum}")
        except Exception as e:
            self.get_logger().error(f"Service call failed: {e}")

def main():
    rclpy.init()
    node = Service_client()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()