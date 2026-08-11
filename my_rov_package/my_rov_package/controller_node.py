import rclpy
from rclpy.node import Node 
from std_msgs.msg import Float64
import pytest

class ControllerNode(Node):
    def __init__(self, kp: float = 2.0, ki: float = 2.0, kd: float = 2.0, output_min: float = -10.0, output_max = 10.0, setpoint: float = 5.0):
        super().__init__("controller_node")

        self.target_depth: float = setpoint

        self.declare_parameter("kp", kp)
        self.declare_parameter("ki", ki)
        self.declare_parameter("kd", kd)

        self._kp: float = self.get_parameter("kp").value
        self._ki: float = self.get_parameter("ki").value
        self._kd: float = self.get_parameter("kd").value

        self._output_min: float = output_min
        self._output_max: float = output_max

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

@pytest.fixture
def only_pid():
    return ControllerNode()

def test_proportional_output(only_pid):
    only_pid._ki = 0.0
    only_pid._kd = 0.0

    captured_msgs = []
    only_pid.thruster_pub.publish = lambda msg: captured_msgs.append(msg)

    msg = Float64()
    msg.data = 2.0

    only_pid.depth_callback(msg) # initalize self.previous_time
    only_pid.depth_callback(msg) # run the pid calcuation
 
    assert only_pid.previous_error == 3.0
    assert captured_msgs[0].data == 6.0

def test_integral_output(only_pid):
    only_pid._kp = 0.0
    only_pid._kd = 0.0

    only_pid.integral = 1.5

    captured_msgs = []
    only_pid.thruster_pub.publish = lambda msg: captured_msgs.append(msg)

    msg = Float64()
    msg.data = 2.0

    only_pid.depth_callback(msg)
    only_pid.depth_callback(msg)

    assert captured_msgs[0].data == pytest.approx(3.0, abs=0.01)

def derivative_output(only_pid):
    only_pid._kd = 0.0
    only_pid._ki = 0.0




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