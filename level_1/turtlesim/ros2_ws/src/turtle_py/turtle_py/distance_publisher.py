import math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from std_msgs.msg import Float32
from turtlesim.msg import Pose

class DistancePublisher(Node):
    def __init__(self):
        super().__init__('distance_publisher')
        self.declare_parameter('publish_rate', 10.0)
        self.declare_parameter('enabled', True)
        rate = float(self.get_parameter('publish_rate').value)
        if rate <= 0:
            self.get_logger().warning('publish_rate must be > 0; using 10.0')
            rate = 10.0
        qos = QoSProfile(depth=10)
        self.pose = None
        self.publisher = self.create_publisher(Float32, '/turtle_distance', qos)
        self.pose_sub = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, qos)
        self.timer = self.create_timer(1.0 / rate, self.publish_distance)
        self.get_logger().info('distance publisher started')

    def pose_callback(self, msg):
        self.pose = msg

    def publish_distance(self):
        if self.pose is None or not self.get_parameter('enabled').value:
            return
        msg = Float32()
        msg.data = math.hypot(self.pose.x, self.pose.y)
        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args); node = DistancePublisher()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    finally: node.destroy_node(); rclpy.shutdown()
