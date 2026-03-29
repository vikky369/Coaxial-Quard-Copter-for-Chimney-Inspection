import rclpy
from rclpy.node import Node
from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand


class OffboardTakeoff(Node):
    def __init__(self):
        super().__init__('offboard_takeoff')

        self.offboard_pub = self.create_publisher(
            OffboardControlMode, '/fmu/in/offboard_control_mode', 10)
        self.traj_pub = self.create_publisher(
            TrajectorySetpoint, '/fmu/in/trajectory_setpoint', 10)
        self.cmd_pub = self.create_publisher(
            VehicleCommand, '/fmu/in/vehicle_command', 10)

        self.counter = 0
        self.timer = self.create_timer(0.1, self.timer_callback)  # 10Hz

    def publish_vehicle_command(self, command, param1=0.0, param2=0.0):
        msg = VehicleCommand()
        msg.command = command
        msg.param1 = param1
        msg.param2 = param2
        msg.target_system = 1
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1
        msg.from_external = True
        self.cmd_pub.publish(msg)

    def timer_callback(self):
        # 1. Offboard heartbeat
        offboard_msg = OffboardControlMode()
        offboard_msg.velocity = True
        self.offboard_pub.publish(offboard_msg)

        # 2. Takeoff command (go UP)
        traj_msg = TrajectorySetpoint()
        traj_msg.position = [float('nan'), float('nan'), float('nan')]
        traj_msg.velocity = [0.0, 0.0, -1.0]  # UP in NED
        traj_msg.yaw = 0.0
        self.traj_pub.publish(traj_msg)

        # 3. After few cycles → switch mode + arm
        if self.counter == 20:
            # Switch to OFFBOARD
            self.publish_vehicle_command(176, 1.0, 6.0)
            # Arm
            self.publish_vehicle_command(400, 1.0)

        self.counter += 1


def main():
    rclpy.init()
    node = OffboardTakeoff()
    rclpy.spin(node)


if __name__ == '__main__':
    main()