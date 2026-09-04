import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from turtlesim.msg import Pose
from visualization_msgs.msg import Marker
from tf2_ros import TransformBroadcaster
from turtle_interfaces.msg import WaypointList
from tf_transformations import quaternion_from_euler

class TfMarkerBroadcaster(Node):
    def __init__(self):
        super().__init__('tf_marker_broadcaster'); self.tf=TransformBroadcaster(self); self.markers=self.create_publisher(Marker,'/waypoint_markers',13)
        self.pose_sub=self.create_subscription(Pose,'/turtle1/pose',self.pose,13); self.wp_sub=self.create_subscription(WaypointList,'/waypoints',self.waypoints,13); self.points=[]; self.get_logger().info('TF marker broadcaster started')
    def pose(self,msg):
        t=TransformStamped(); t.header.stamp=self.get_clock().now().to_msg(); t.header.frame_id='world';t.child_frame_id='turtle1';t.transform.translation.x=msg.x;t.transform.translation.y=msg.y; q=quaternion_from_euler(0,0,msg.theta);t.transform.rotation.x,qy,qz,qw=q;t.transform.rotation.y=qy;t.transform.rotation.z=qz;t.transform.rotation.w=qw;self.tf.sendTransform(t)
    def waypoints(self,msg):
        self.points=msg.waypoints
        for i,p in enumerate(self.points):
            m=Marker();m.header.frame_id='world';m.header.stamp=self.get_clock().now().to_msg();m.ns='waypoints';m.id=i;m.type=Marker.SPHERE;m.action=Marker.ADD;m.pose.position.x=p.x;m.pose.position.y=p.y;m.pose.position.z=0.05;m.scale.x=m.scale.y=m.scale.z=0.2;m.color.a=1.0;m.color.r=0.9;m.color.g=0.36;m.color.b=0.02;self.markers.publish(m)
def main(args=None):
    rclpy.init(args=args);node=TfMarkerBroadcaster()
    try:rclpy.spin(node)
    except KeyboardInterrupt:pass
    finally:node.destroy_node();rclpy.shutdown()
