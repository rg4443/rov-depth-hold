import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64

class PhysicsSimulatorNode(Node):
    def __init__(self):
        super().__init__("physics_simulator_node")

        self.mass = 10.0           # kg
        self.drag_coeff = 5.0      # N*s/m
        self.buoyancy_force = -2.0

        self.depth = 0.0           # meters
        self.velocity = 0.0        # m/s
        self.applied_thrust = 0.0  # N

        self.thrust_sub = self.create_subscription(Float64, "thruster_command", self.thrust_callback, 10)
        self.depth_pub = self.create_publisher(Float64, "depth_reading", 10)

        self.timer = self.create_timer(0.1, self.physics_update)

        self.get_logger().info("PhysicsSimulatorNode Initialized")

    def thrust_callback(self, msg):
        self.applied_thrust = msg.data

    def physics_update(self):
        net_force = self.applied_thrust + self.buoyancy_force - (self.drag_coeff * self.velocity)
        acceleration = net_force / self.mass 
        self.velocity = self.velocity + acceleration * 0.1
        self.depth = self.depth + self.velocity * 0.1

        msg = Float64()
        msg.data = self.depth
        self.depth_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = PhysicsSimulatorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()