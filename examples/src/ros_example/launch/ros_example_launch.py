import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    config = os.path.join(
        get_package_share_directory("ros_example"), "config", "config.yaml"
    )
    return LaunchDescription(
        [
            Node(
                package="ros_example",
                executable="ros_example_node",
                name="ros_example_node",
                parameters=[config],
            ),
        ]
    )
