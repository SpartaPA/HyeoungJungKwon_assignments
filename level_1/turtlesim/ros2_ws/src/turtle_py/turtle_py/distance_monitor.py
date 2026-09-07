import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from std_msgs.msg import Float32

class DistanceMonitor(Node):
    def __init__(self):
        super().__init__('distance_monitor')
        self.declare_parameter('warn_distance', 2.5)
        self.subscription = self.create_subscription(Float32, 'turtle_distance', self.callback, QoSProfile(depth=10))
        self.get_logger().info('monitor node up')
    def callback(self, msg):
        limit = float(self.get_parameter('warn_distance').value)
        if msg.data > limit:
            self.get_logger().warning(f'distance {msg.data:.3f} exceeds {limit:.3f}')

def main(args=None):
    rclpy.init(args=args); node = DistanceMonitor()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    finally: node.destroy_node(); rclpy.shutdown() if rclpy.ok() else None
