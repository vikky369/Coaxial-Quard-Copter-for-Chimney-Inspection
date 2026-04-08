import rclpy

from px4_offboard_control.teleop_control import Px4TeleopControl


def main(args=None) -> None:
    rclpy.init(args=args)
    node = Px4TeleopControl()

    node.pending_offboard = True
    node.pending_arm = True
    node.target_z = -abs(float(node.takeoff_altitude))
    node.get_logger().info(
        f"offboard_takeoff started. Requesting takeoff to {abs(float(node.takeoff_altitude)):.1f} m"
    )

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
