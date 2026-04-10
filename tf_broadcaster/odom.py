import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from px4_msgs.msg import VehicleOdometry
from tf2_ros import TransformBroadcaster

class OdomTF(Node):
    def __init__(self):
        super().__init__('odom_tf')

        self.br = TransformBroadcaster(self)

        self.sub = self.create_subscription(
            VehicleOdometry,
            '/fmu/out/vehicle_odometry',
            self.callback,
            10)

    def callback(self, msg):
        t = TransformStamped()

        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'

        t.transform.translation.x = msg.position[0]
        t.transform.translation.y = msg.position[1]
        t.transform.translation.z = msg.position[2]

        t.transform.rotation.x = msg.q[0]
        t.transform.rotation.y = msg.q[1]
        t.transform.rotation.z = msg.q[2]
        t.transform.rotation.w = msg.q[3]

        self.br.sendTransform(t)

def main():
    rclpy.init()
    node = OdomTF()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()