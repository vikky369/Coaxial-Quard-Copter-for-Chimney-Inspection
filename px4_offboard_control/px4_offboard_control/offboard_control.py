import rclpy

from px4_offboard_control.teleop_control import Px4TeleopControl


def main(args=None) -> None:
    rclpy.init(args=args)
    node = Px4TeleopControl()
    node.get_logger().info("offboard_control alias started (teleop mode)")
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
