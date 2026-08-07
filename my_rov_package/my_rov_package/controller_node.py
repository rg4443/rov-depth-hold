import rclpy
from rclpy.node import Node 
from std_msgs.msg import Float64

class ControllerNode(Node):
    def __init__(self):
        super().__init__("controller_node")

        self.target_depth: float = 3.0

        self.declare_parameter("kp", 2.0)
        self.declare_parameter("ki", 0.0)
        self.declare_parameter("kd", 0.1)

        self._kp: float = self.get_parameter("kp").value
        self._kd: float = self.get_parameter("ki").value
        self._ki: float = self.get_parameter("kd").value

        self._output_min: float = -1.0
        self._output_max: float = 1.0

        self.integral: float = 0.0
        self.previous_error = None
        self.previous_time = None

        self.depth_sub = self.create_subscription(Float64, "depth_reading", self.depth_callback, 10)

        self.thruster_pub = self.create_publisher(Float64, "thruster_command", 10)
        self.get_logger().info("Controller Node Initialized")

    def depth_callback(self, msg):
        if self.previous_time is None: 
            self.previous_time = self.get_clock().now()
            return

        current_depth = msg.data

        error = self.target_depth - current_depth

        p_term = Float64()
        p_term.data = error * self._kp

        current_time = self.get_clock().now()
        time_difference = current_time - self.previous_time
        dt = time_difference.nanoseconds / 1e9 

        if dt <= 0: return

        integral_delta: float = error * dt 
        self.integral += integral_delta
        i_term = Float64()
        i_term.data = self._ki * self.integral

        d_term = Float64()

        if self.previous_error is None:
            d_term.data = 0.0
        else:
            d_term.data = self._kd * (error - self.previous_error) / dt

        output = p_term.data + i_term.data +  d_term.data
        clamped_output = Float64()
        clamped_output.data = min(self._output_max, max(self._output_min, output))

        is_saturated = output == clamped_output.data
        is_same_direction = (output > self._output_max and error > 0) or (output < self._output_min and error < 0)

        if is_saturated and is_same_direction:
            i_term.data -= integral_delta

            i_term.data = self._ki * self.integral
            output = p_term.data + i_term.data + d_term.data
            clamped_output.data = min(self._output_max, max(self._output_min, output))

        self.previous_error = error
        self.previous_time = current_time

        self.thruster_pub.publish(clamped_output)

        self.get_logger().info(f"Current Depth: {current_depth}m | Error: {error}m | Output Thrust: {clamped_output.data:.2f}")

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