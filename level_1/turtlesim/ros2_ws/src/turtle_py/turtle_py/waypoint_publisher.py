import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from turtle_interfaces.msg import Waypoint, WaypointList
class WaypointPublisher(Node):
    def __init__(self):
        super().__init__('waypoint_publisher'); qos=QoSProfile(depth=10); qos.durability=DurabilityPolicy.TRANSIENT_LOCAL; self.pub=self.create_publisher(WaypointList,'/waypoints',qos); self.timer=self.create_timer(1.0,self.publish); self.get_logger().info('waypoint publisher started')
    def publish(self):
        msg=WaypointList(); msg.header.stamp=self.get_clock().now().to_msg()
        for i,(x,y) in enumerate([(2.0,2.0),(6.0,2.0),(6.0,6.0)]):
            p=Waypoint(); p.x=x;p.y=y;p.tolerance=0.2;p.label=f'P{i+1}';msg.waypoints.append(p)
        self.pub.publish(msg)
def main(args=None):
    rclpy.init(args=args);node=WaypointPublisher()
    try:rclpy.spin(node)
    except KeyboardInterrupt:pass
    finally:node.destroy_node();rclpy.shutdown()
