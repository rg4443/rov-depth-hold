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
        parameters=[{'kp': 2.0, 'ki': 0.0, 'kd': 0.0}]
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