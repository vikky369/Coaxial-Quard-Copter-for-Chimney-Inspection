from setuptools import find_packages, setup

package_name = 'px4_offboard_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # ('share/' + package_name + '/launch', [
        #     'launch/offboard_control.launch.py',
        #     'launch/camera_bridge.launch.py',
        #     'launch/teleop.launch.py',
        #     'launch/teleop_with_bridge.launch.py',
        # ]),
        # ('share/' + package_name + '/config', ['config/ros_gz_bridge.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='palanisamy',
    maintainer_email='kit.23.19bme053@gmail.com',
    description='PX4 offboard control with teleop support for drone operations',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'offboard_control = px4_offboard_control.velocity_control:main',
            'offboard_takeoff = px4_offboard_control.velocity_control:main',
            'teleop_control = px4_offboard_control.control:main',
            'joy_to_px4 = px4_offboard_control.joy_to_px4:main',
        ],
    },
)
