from launch import LaunchDescription
from launch_ros.actions import Node
import os

def generate_launch_description():

    config = os.path.join(
        os.getcwd(),
        'src/yolo_vision/config/yolo.yaml'
    )

    return LaunchDescription([

        # 🔹 Bridge camera from Gazebo → ROS
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/camera@sensor_msgs/msg/Image@gz.msgs.Image'
            ],
            output='screen'
        ),

        # # 🔹 YOLO node
        # Node(
        #     package='yolo_vision',
        #     executable='yolo_node',
        #     name='yolo_node',
        #     parameters=[config],
        #     output='screen'
        # ),
        Node(
            package='yolo_vision',
            executable='/home/sabaris/yolo_env/bin/python',
            arguments=['-m', 'yolo_vision.yolo_node'],
            name='yolo_node',
            output='screen',
            parameters=['/home/sabaris/drone_ws/src/yolo_vision/config/yolo.yaml']
        )
    ])