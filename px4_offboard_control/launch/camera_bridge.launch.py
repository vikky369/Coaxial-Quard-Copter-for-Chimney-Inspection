from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description() -> LaunchDescription:
    config_path = os.path.join(
        get_package_share_directory("px4_offboard_control"),
        "config",
        "ros_gz_bridge.yaml",
    )

    return LaunchDescription(
        [
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                name="camera_bridge",
                output="screen",
                parameters=[{"config_file": config_path}],
            ),
        ]
    )
