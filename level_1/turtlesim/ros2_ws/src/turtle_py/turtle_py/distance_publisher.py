import math

import rclpy
from rcl_interfaces.msg import SetParametersResult
from rclpy.node import Node
from rclpy.qos import QoSProfile
from std_msgs.msg import Float64
from turtlesim.msg import Pose

class DistancePublisher(Node):
    def __init__(self):
        super().__init__('distance_publisher')
        self.declare_parameter('publish_rate', 5.0)
        self.declare_parameter('enabled', True)
        rate = float(self.get_parameter('publish_rate').value)
        if rate <= 0:
            self.get_logger().warning('publish_rate must be > 0; using 5.0')
            rate = 5.0
        qos = QoSProfile(depth=13)
        self.pose = None
        self.publisher = self.create_publisher(Float64, 'turtle_dist', qos)
        self.pose_sub = self.create_subscription(Pose, 'turtle1/pose', self.pose_callback, qos)
        self.timer = self.create_timer(1.0 / rate, self.publish_distance)
        self.add_on_set_parameters_callback(self.parameters_changed)
        self.get_logger().info('distance node up (rev A3)')

    def pose_callback(self, msg):
        self.pose = msg

    def publish_distance(self):
        if self.pose is None or not self.get_parameter('enabled').value:
            return
        msg = Float64()
        msg.data = math.hypot(self.pose.x, self.pose.y)
        self.publisher.publish(msg)

    def parameters_changed(self, parameters):
        for parameter in parameters:
            if parameter.name != 'publish_rate':
                continue
            rate = float(parameter.value)
            if rate <= 0.0:
                self.get_logger().warning('publish_rate must be > 0; keeping current rate')
                return SetParametersResult(successful=False, reason='publish_rate must be > 0')
            self.destroy_timer(self.timer)
            self.timer = self.create_timer(1.0 / rate, self.publish_distance)
            self.get_logger().info(f'publish_rate updated to {rate:.3f} Hz')
        return SetParametersResult(successful=True)

def main(args=None):
    rclpy.init(args=args)
    node = DistancePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
