import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64

class DepthSensorNode(Node):
    def __init__(self):
        super().__init__("depth_sensor")
        self.depth_pub = self.create_publisher(Float64, "depth_reading", 10)
        self.timer = self.create_timer(1.0, self.publish_depth)
        self.current_depth = 0.0

    def publish_depth(self):
        msg = Float64()
        msg.data = self.current_depth
        self.depth_pub.publish(msg)
        self.get_logger().info(f"Publishing Depth: {msg.data}m")

def main(args=None):
    rclpy.init(args=args)
    node = DepthSensorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()