from setuptools import find_packages, setup

package_name = 'yolo_vision'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/yolo_vision']),
        ('share/yolo_vision', ['package.xml']),
        ('share/yolo_vision/launch', ['launch/yolo.launch.py']),
        ('share/yolo_vision/config', ['config/yolo.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Palanisamy',
    maintainer_email='palanisamyindhrani@gmail.com',
    description='YOLO vision package for ROS 2',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'yolo_node = yolo_vision.yolo_node:main',
        ],
    },
)
    