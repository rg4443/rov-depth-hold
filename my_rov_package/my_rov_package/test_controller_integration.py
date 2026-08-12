import unittest
import launch
import launch_ros.actions
import launch_testing.actions
import pytest
import rclpy
from std_msgs.msg import Float64

@pytest.mark.launch_test
def generate_test_description():
    controller_node = launch_ros.actions.Node(
        package='my_rov_package',
        executable='controller_node',
        name='controller_node',
        parameters=[{'kp': 2.0, 'ki': 0.0, 'kd': 0.0, 'target_depth': 5.0}]
    )

    return launch.LaunchDescription([
        controller_node,
        launch_testing.actions.ReadyToTest()
    ])

class TestControllerIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.test_node = rclpy.create_node('test_controller_helper')

    def tearDown(self):
        self.test_node.destroy_node()

    def test_depth_command_response(self):
        depth_pub = self.test_node.create_publisher(Float64, "/depth", 10)

        captured_msgs = []
        self.test_node.create_subscription(Float64, "/thruster_cmd", lambda msg: captured_msgs.append(msg), 10)

        while depth_pub.get_subscription_count() == 0: 
            rclpy.spin_once(self.test_node, timeout_sec=0.1)
            current_time = self.test_node.get_clock().now().nanoseconds / 1e9
            
            if current_time - start_time: self.fail("Timed out waiting for controller_node to connect to /depth")

        msg = Float64()
        msg.data = 2.0
        depth_pub.publish(msg)

        timeout_sec = 2.0
        start_time = self.test_node.get_clock().now().nanoseconds / 1e9

        while len(captured_msgs) == 0:
            rclpy.spin_once(self.test_node, timeout_sec=0.1)

            current_time = self.test_node.get_clock().now().nanoseconds / 1e9

            if (current_time - start_time) > timeout_sec: self.fail("Timed out waiting for message on /thruster_cmd!")

        assert captured_msgs[0].data == pytest.approx(6.0)
