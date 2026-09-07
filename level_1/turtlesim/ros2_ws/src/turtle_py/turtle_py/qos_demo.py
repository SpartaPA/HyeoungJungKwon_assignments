import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
import time
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from std_msgs.msg import Float32
from turtle_interfaces.msg import Waypoint, WaypointList

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
        msg=WaypointList()
        for i,(x,y) in enumerate([(2.0,2.0),(6.0,2.0),(6.0,6.0),(2.0,6.0)]):
            msg.waypoints.append(Waypoint(x=x,y=y,tolerance=0.2,label=f'P{i+1}'))
        self.pub.publish(msg); self.sent=True

class SlowDepthOneSubscriber(Node):
    def __init__(self):
        super().__init__('qos_slow_depth_one_subscriber')
        self.count = 0
        qos=QoSProfile(depth=1); qos.reliability=ReliabilityPolicy.BEST_EFFORT
        self.sub=self.create_subscription(Float32,'/qos_depth_one',self.callback,qos)
    def callback(self, msg):
        self.count += 1; self.get_logger().info(f'depth1 received={self.count} value={msg.data}'); time.sleep(0.5)

class DepthOnePublisher(Node):
    def __init__(self):
        super().__init__('qos_depth_one_publisher')
        qos=QoSProfile(depth=1); qos.reliability=ReliabilityPolicy.BEST_EFFORT
        self.pub=self.create_publisher(Float32,'/qos_depth_one',qos); self.n=0
        self.timer=self.create_timer(0.1,self.publish)
    def publish(self):
        self.n += 1; self.pub.publish(Float32(data=float(self.n)))

def main(args=None):
    rclpy.init(args=args)
    nodes = [BestEffortDistancePublisher(), ReliableDistanceSubscriber(), LatchedWaypointPublisher(), DepthOnePublisher(), SlowDepthOneSubscriber()]
    executor = MultiThreadedExecutor()
    for node in nodes: executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        for node in nodes: node.destroy_node()
        rclpy.shutdown() if rclpy.ok() else None
