import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand


class JoyToPX4(Node):

    def __init__(self):
        super().__init__('joy_to_px4')

        # Publishers
        self.offboard_pub = self.create_publisher(
            OffboardControlMode,
            '/fmu/in/offboard_control_mode',
            10
        )

        self.traj_pub = self.create_publisher(
            TrajectorySetpoint,
            '/fmu/in/trajectory_setpoint',
            10
        )

        self.vehicle_command_pub = self.create_publisher(
            VehicleCommand,
            '/fmu/in/vehicle_command',
            10
        )

        # Subscriber
        self.sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_callback,
            10
        )

        # State variables
        self.last_cmd = Twist()
        self.offboard_setpoint_counter = 0

        # Drone position state (VERY IMPORTANT)
        self.x = 0.0
        self.y = 0.0
        self.z = -2.0   # hover height (NED frame)

        # Timer
        self.dt = 0.05  # 20 Hz
        self.timer = self.create_timer(self.dt, self.publish_setpoint)

    # Keyboard input
    def cmd_callback(self, msg):
        self.last_cmd = msg

    # Send PX4 command
    def send_vehicle_command(self, command, param1=0.0, param2=0.0):
        msg = VehicleCommand()
        msg.command = command
        msg.param1 = param1
        msg.param2 = param2
        msg.target_system = 1
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1
        msg.from_external = True
        msg.timestamp = self.get_clock().now().nanoseconds // 1000
        self.vehicle_command_pub.publish(msg)

    # Main control loop
    def publish_setpoint(self):

        # Switch to OFFBOARD + ARM
        if self.offboard_setpoint_counter == 10:
            self.get_logger().info("Switching to OFFBOARD mode")
            self.send_vehicle_command(176, 1.0, 6.0)

            self.get_logger().info("Arming drone")
            self.send_vehicle_command(400, 1.0)

        self.offboard_setpoint_counter += 1

        # Control mode
        offboard = OffboardControlMode()
        offboard.position = True
        offboard.velocity = True
        offboard.timestamp = self.get_clock().now().nanoseconds // 1000


        SCALE = 3.0


        self.x += SCALE * self.last_cmd.linear.x * self.dt
        self.y += SCALE * self.last_cmd.linear.y * self.dt

        # Maintain altitude (no falling)
        self.z = -2.0

        # Set trajectory
        traj = TrajectorySetpoint()
        traj.position = [self.x, self.y, self.z]
        traj.yaw = self.last_cmd.angular.z
        traj.timestamp = offboard.timestamp

        # Publish
        self.offboard_pub.publish(offboard)
        self.traj_pub.publish(traj)


def main():
    rclpy.init()
    node = JoyToPX4()
    rclpy.spin(node)
    rclpy.shutdown()


# source 
# make px4_sitl gz
# MicroXRCEAgent udp4 -p 8888
# ros2 run teleop_twist_keyboard teleop_twist_keyboard
# ros2 run px4_offboard_control joy_to_px4