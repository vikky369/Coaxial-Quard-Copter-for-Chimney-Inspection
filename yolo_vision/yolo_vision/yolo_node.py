#!/home/sabaris/yolo_env/bin/python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

from .detector import YoloDetector

class YoloNode(Node):

    def __init__(self):
        super().__init__('yolo_node')

        # Parameters
        self.declare_parameter("model_path", "yolov8n.pt")
        self.declare_parameter("image_topic", "/camera")
        self.declare_parameter("view_image", True)

        model_path = self.get_parameter("model_path").value
        image_topic = self.get_parameter("image_topic").value
        self.view_image = self.get_parameter("view_image").value

        # YOLO Detector
        self.detector = YoloDetector(model_path)

        # ROS tools
        self.bridge = CvBridge()

        # Subscriber
        self.subscription = self.create_subscription(
            Image,
            image_topic,
            self.image_callback,
            10
        )

        self.get_logger().info(f"YOLO Node started. Subscribed to {image_topic}")

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        annotated, center, label = self.detector.detect(frame)

        if center is not None:
            cx, cy = center
            self.get_logger().info(f"{label} at: ({cx}, {cy})")
        else:
            self.get_logger().info("No object detected")

        if self.view_image:
            cv2.imshow("YOLO Detection", annotated)
            cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = YoloNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
