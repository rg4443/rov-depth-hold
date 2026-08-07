import rclpy
from rclpy.node import Node 
from std_msgs.msg import Float64

class ControllerNode(Node):
    def __init__(self):
        super().__init__("controller_node")

        self.target_depth: float = 3.0
        self.kp: float = 2.0

        self.depth_sub = self.create_subscription(Float64, "depth_reading", self.depth_callback, 10)

        self.thruster_pub = self.create_publisher(Float64, "thruster_command", 10)
        self.get_logger().info("Controller Node Initialized")

    def depth_callback(self, msg):
        current_depth = msg.data

        error = self.target_depth - current_depth

        thrust_cmd = Float64()
        thrust_cmd.data = error * self.kp

        self.thruster_pub.publish(thrust_cmd)

        self.get_logger().info(f"Current Depth: {current_depth}m | Error: {error}m | Output Thrust: {thrust_cmd.data:.2f}")

        self.thruster_pub = self.create_publisher(Float64, "thrust_cmd", 10)

def main(args=None):
    rclpy.init(args=args)
    node = ControllerNode()

    try: 
        rclpy.spin(node)
    except KeyboardInterrupt: 
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()