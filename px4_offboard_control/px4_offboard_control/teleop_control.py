import math
from typing import Dict, List

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSDurabilityPolicy, QoSProfile, QoSReliabilityPolicy
from sensor_msgs.msg import Joy

from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand, VehicleStatus


class Px4TeleopControl(Node):
    def __init__(self) -> None:
        super().__init__("teleop_control")

        self.declare_parameter("frame_id", "map")
        self.declare_parameter("timer_hz", 20.0)
        self.declare_parameter("deadzone", 0.1)
        self.declare_parameter("vehicle_status_topic", "/fmu/out/vehicle_status_v3")
        self.declare_parameter("max_horizontal_speed", 1.5)
        self.declare_parameter("max_vertical_speed", 1.0)
        self.declare_parameter("max_yaw_rate", 0.8)
        self.declare_parameter("takeoff_altitude", 2.0)

        self.declare_parameter("arm_button", 0)
        self.declare_parameter("disarm_button", 1)
        self.declare_parameter("offboard_button", 2)
        self.declare_parameter("takeoff_button", 3)
        self.declare_parameter("land_button", 4)
        self.declare_parameter("kill_button", 5)

        self.declare_parameter("forward_axis", 1)
        self.declare_parameter("right_axis", 0)
        self.declare_parameter("up_axis", 4)
        self.declare_parameter("yaw_axis", 3)

        self.offboard_pub = self.create_publisher(OffboardControlMode, "/fmu/in/offboard_control_mode", 10)
        self.setpoint_pub = self.create_publisher(TrajectorySetpoint, "/fmu/in/trajectory_setpoint", 10)
        self.cmd_pub = self.create_publisher(VehicleCommand, "/fmu/in/vehicle_command", 10)

        self.create_subscription(Joy, "/joy", self.joy_callback, 10)
        status_qos = QoSProfile(
            depth=10,
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE,
        )

        self.create_subscription(
            VehicleStatus,
            str(self.get_parameter("vehicle_status_topic").value),
            self.status_callback,
            status_qos,
        )

        self.timer_hz = float(self.get_parameter("timer_hz").value)
        self.deadzone = float(self.get_parameter("deadzone").value)
        self.max_horizontal_speed = float(self.get_parameter("max_horizontal_speed").value)
        self.max_vertical_speed = float(self.get_parameter("max_vertical_speed").value)
        self.max_yaw_rate = float(self.get_parameter("max_yaw_rate").value)
        self.takeoff_altitude = float(self.get_parameter("takeoff_altitude").value)

        self.button_map: Dict[str, int] = {
            "arm": int(self.get_parameter("arm_button").value),
            "disarm": int(self.get_parameter("disarm_button").value),
            "offboard": int(self.get_parameter("offboard_button").value),
            "takeoff": int(self.get_parameter("takeoff_button").value),
            "land": int(self.get_parameter("land_button").value),
            "kill": int(self.get_parameter("kill_button").value),
        }

        self.axis_map: Dict[str, int] = {
            "forward": int(self.get_parameter("forward_axis").value),
            "right": int(self.get_parameter("right_axis").value),
            "up": int(self.get_parameter("up_axis").value),
            "yaw": int(self.get_parameter("yaw_axis").value),
        }

        self.buttons_prev: List[int] = []
        self.last_joy: Joy | None = None

        self.target_x = 0.0
        self.target_y = 0.0
        self.target_z = -0.5
        self.target_yaw = 0.0

        self.pending_arm = False
        self.pending_disarm = False
        self.pending_offboard = False
        self.pending_land = False
        self.pending_kill = False

        self.armed = False
        self.offboard_enabled = False
        self.last_timer_time = self.get_clock().now()

        period = 1.0 / self.timer_hz if self.timer_hz > 0.0 else 0.05
        self.create_timer(period, self.timer_callback)

        self.get_logger().info("PX4 teleop control ready. Press OFFBOARD, ARM, then TAKEOFF.")

    def status_callback(self, msg: VehicleStatus) -> None:
        self.armed = msg.arming_state == VehicleStatus.ARMING_STATE_ARMED
        self.offboard_enabled = msg.nav_state == VehicleStatus.NAVIGATION_STATE_OFFBOARD

    def apply_deadzone(self, value: float) -> float:
        return 0.0 if abs(value) < self.deadzone else value

    def axis(self, joy: Joy, key: str) -> float:
        idx = self.axis_map[key]
        if idx < 0 or idx >= len(joy.axes):
            return 0.0
        return self.apply_deadzone(float(joy.axes[idx]))

    def button_pressed(self, buttons: List[int], key: str) -> bool:
        idx = self.button_map[key]
        if idx < 0 or idx >= len(buttons):
            return False

        current = buttons[idx] == 1
        previous = False
        if idx < len(self.buttons_prev):
            previous = self.buttons_prev[idx] == 1
        return current and not previous

    def joy_callback(self, msg: Joy) -> None:
        self.last_joy = msg
        now = self.get_clock().now()
        dt = (now - self.last_timer_time).nanoseconds / 1e9
        dt = max(0.0, min(dt, 0.2))

        forward = self.axis(msg, "forward")
        right = self.axis(msg, "right")
        up = self.axis(msg, "up")
        yaw_rate = self.axis(msg, "yaw")

        if dt > 0.0:
            self.target_x += forward * self.max_horizontal_speed * dt
            self.target_y += right * self.max_horizontal_speed * dt
            self.target_z -= up * self.max_vertical_speed * dt
            self.target_yaw += yaw_rate * self.max_yaw_rate * dt
            self.target_yaw = math.atan2(math.sin(self.target_yaw), math.cos(self.target_yaw))

        buttons = msg.buttons
        if self.button_pressed(buttons, "offboard"):
            self.pending_offboard = True
            self.get_logger().info("Requested OFFBOARD mode")

        if self.button_pressed(buttons, "arm"):
            self.pending_arm = True
            self.get_logger().info("Requested ARM")

        if self.button_pressed(buttons, "disarm"):
            self.pending_disarm = True
            self.get_logger().info("Requested DISARM")

        if self.button_pressed(buttons, "takeoff"):
            self.target_z = -abs(self.takeoff_altitude)
            self.pending_offboard = True
            self.pending_arm = True
            self.get_logger().info(f"Requested TAKEOFF to {abs(self.takeoff_altitude):.1f} m")

        if self.button_pressed(buttons, "land"):
            self.pending_land = True
            self.get_logger().info("Requested LAND")

        if self.button_pressed(buttons, "kill"):
            self.pending_kill = True
            self.get_logger().warn("Requested KILL")

        self.buttons_prev = list(buttons)

    def _timestamp_us(self) -> int:
        return int(self.get_clock().now().nanoseconds / 1000)

    def publish_offboard_heartbeat(self) -> None:
        msg = OffboardControlMode()
        msg.position = True
        msg.velocity = False
        msg.acceleration = False
        msg.attitude = False
        msg.body_rate = False
        msg.timestamp = self._timestamp_us()
        self.offboard_pub.publish(msg)

    def publish_position_setpoint(self) -> None:
        msg = TrajectorySetpoint()
        msg.position = [float(self.target_x), float(self.target_y), float(self.target_z)]
        msg.yaw = float(self.target_yaw)
        msg.yawspeed = 0.0
        msg.timestamp = self._timestamp_us()
        self.setpoint_pub.publish(msg)

    def send_vehicle_command(self, command: int, param1: float = 0.0, param2: float = 0.0) -> None:
        msg = VehicleCommand()
        msg.param1 = float(param1)
        msg.param2 = float(param2)
        msg.command = int(command)
        msg.target_system = 1
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1
        msg.from_external = True
        msg.timestamp = self._timestamp_us()
        self.cmd_pub.publish(msg)

    def timer_callback(self) -> None:
        self.last_timer_time = self.get_clock().now()
        self.publish_offboard_heartbeat()
        self.publish_position_setpoint()

        if self.pending_offboard:
            self.send_vehicle_command(VehicleCommand.VEHICLE_CMD_DO_SET_MODE, 1.0, 6.0)
            self.pending_offboard = False

        if self.pending_arm:
            self.send_vehicle_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, 1.0)
            self.pending_arm = False

        if self.pending_disarm:
            self.send_vehicle_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, 0.0)
            self.pending_disarm = False

        if self.pending_land:
            self.send_vehicle_command(VehicleCommand.VEHICLE_CMD_NAV_LAND)
            self.pending_land = False

        if self.pending_kill:
            self.send_vehicle_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, 0.0, 21196.0)
            self.pending_kill = False


def main(args=None) -> None:
    rclpy.init(args=args)
    node = Px4TeleopControl()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
