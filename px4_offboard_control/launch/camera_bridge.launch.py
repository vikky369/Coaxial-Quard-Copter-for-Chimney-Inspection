import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('px4_offboard_control')
    config_file = os.path.join(pkg_share, 'config', 'ros_gz_bridge.yaml')
    
    return LaunchDescription([
        TimerAction(
            period=5.0,
            actions=[
                Node(
                    package='ros_gz_bridge',
                    executable='parameter_bridge',
                    parameters=[{'config_file': config_file}],
                    output='screen'
                )
            ]
        )
    ])