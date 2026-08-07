from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package="my_rov_package",
            executable="controller_node",
            name="controller_node",
        ),
        Node(
            package="my_rov_package",
            executable="depth_sensor",
            name="depth_node",
        )
    ])