import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from std_msgs.msg import Float32
from turtle_interfaces.msg import WaypointList

class BestEffortDistancePublisher(Node):
    def __init__(self):
        super().__init__('qos_best_effort_publisher')
        qos=QoSProfile(depth=10); qos.reliability=ReliabilityPolicy.BEST_EFFORT
        self.pub=self.create_publisher(Float32,'/turtle_distance',qos); self.n=0.0; self.timer=self.create_timer(0.1,self.publish)
    def publish(self): self.n+=1; self.pub.publish(Float32(data=self.n))

class ReliableDistanceSubscriber(Node):
    def __init__(self):
        super().__init__('qos_reliable_subscriber')
        qos=QoSProfile(depth=10); qos.reliability=ReliabilityPolicy.RELIABLE
        self.sub=self.create_subscription(Float32,'/turtle_distance',lambda m:self.get_logger().info(str(m.data)),qos)

class LatchedWaypointPublisher(Node):
    def __init__(self):
        super().__init__('latched_waypoint_publisher')
        qos=QoSProfile(depth=10); qos.durability=DurabilityPolicy.TRANSIENT_LOCAL
        self.pub=self.create_publisher(WaypointList,'/waypoints',qos); self.timer=self.create_timer(0.5,self.publish); self.sent=False
    def publish(self):
        if self.sent:return
        self.pub.publish(WaypointList()); self.sent=True

def main(args=None):
    rclpy.init(args=args)
    node = BestEffortDistancePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node(); rclpy.shutdown()
