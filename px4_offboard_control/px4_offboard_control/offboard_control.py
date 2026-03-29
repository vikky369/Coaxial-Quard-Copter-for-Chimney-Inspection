import rclpy
from rclpy.node import Node
from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand


class Mission(Node):
    def __init__(self):
        super().__init__('mission_node')

        self.offboard_pub = self.create_publisher(
            OffboardControlMode, '/fmu/in/offboard_control_mode', 10)
        self.traj_pub = self.create_publisher(
            TrajectorySetpoint, '/fmu/in/trajectory_setpoint', 10)
        self.cmd_pub = self.create_publisher(
            VehicleCommand, '/fmu/in/vehicle_command', 10)

        self.counter = 0
        self.timer = self.create_timer(0.1, self.run)  # 10Hz

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

    def run(self):
        # 1. Offboard heartbeat
        offboard = OffboardControlMode()
        offboard.position = True
        self.offboard_pub.publish(offboard)

        traj = TrajectorySetpoint()
        traj.velocity = [float('nan')] * 3
        traj.yaw = 0.0

        # Mission timeline
        if self.counter < 100:
            # Send dummy setpoints before OFFBOARD
            traj.position = [0.0, 0.0, -1.0]

        elif self.counter == 100:
            # Switch to OFFBOARD + ARM
            self.publish_vehicle_command(176, 1.0, 6.0)  # OFFBOARD
            self.publish_vehicle_command(400, 1.0)       # ARM

        elif self.counter < 300:
            # TAKEOFF → go to 3m
            traj.position = [0.0, 0.0, -3.0]

        elif self.counter < 500:
            # HOLD position
            traj.position = [0.0, 0.0, -3.0]

        elif self.counter < 700:
            # MOVE to new waypoint
            traj.position = [2.0, 0.0, -3.0]

        elif self.counter < 900:
            # HOLD at waypoint
            traj.position = [2.0, 0.0, -3.0]

        elif self.counter == 900:
            # LAND command
            self.publish_vehicle_command(21.0)  # LAND

        else:
            # After landing, do nothing
            return

        self.traj_pub.publish(traj)
        self.counter += 1


def main():
    rclpy.init()
    node = Mission()
    rclpy.spin(node)


if __name__ == '__main__':
    main()