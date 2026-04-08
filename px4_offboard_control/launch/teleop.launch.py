from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            Node(
                package="joy",
                executable="joy_node",
                name="joy_node",
                output="screen",
            ),
            Node(
                package="px4_offboard_control",
                executable="teleop_control",
                name="teleop_control",
                output="screen",
            ),
        ]
    )
