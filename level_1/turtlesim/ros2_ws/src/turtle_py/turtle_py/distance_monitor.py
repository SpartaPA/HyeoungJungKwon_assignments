import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from std_msgs.msg import Float64

class DistanceMonitor(Node):
    def __init__(self):
        super().__init__('distance_monitor')
        self.declare_parameter('warn_distance', 3.0)
        self.subscription = self.create_subscription(Float64, '/turtle_dist', self.callback, QoSProfile(depth=13))
        self.get_logger().info('distance monitor started')
    def callback(self, msg):
        limit = float(self.get_parameter('warn_distance').value)
        if msg.data > limit:
            self.get_logger().warning(f'distance {msg.data:.3f} exceeds {limit:.3f}')

def main(args=None):
    rclpy.init(args=args); node = DistanceMonitor()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    finally: node.destroy_node(); rclpy.shutdown()
