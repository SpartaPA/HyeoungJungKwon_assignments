import asyncio
import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtle_interfaces.action import DrawPolygon

class DrawPolygonServer(Node):
    def __init__(self):
        super().__init__('draw_polygon_server'); self.pub=self.create_publisher(Twist,'/turtle1/cmd_vel',13); self.server=ActionServer(self,DrawPolygon,'/draw_polygon',execute_callback=self.execute,goal_callback=self.goal,cancel_callback=self.cancel); self.get_logger().info('polygon action server up (rev A3)')
    def goal(self, goal): return GoalResponse.ACCEPT if goal.sides >= 3 and goal.side_length > 0 else GoalResponse.REJECT
    def cancel(self, goal): return CancelResponse.ACCEPT
    async def execute(self, goal_handle):
        goal=goal_handle.request; result=DrawPolygon.Result(); feedback=DrawPolygon.Feedback(); total=0.0
        for side in range(goal.sides):
            for _ in range(10):
                if goal_handle.is_cancel_requested: self.pub.publish(Twist()); goal_handle.canceled(); return result
                msg=Twist(); msg.linear.x=goal.side_length; self.pub.publish(msg); await asyncio.sleep(0.1)
            self.pub.publish(Twist()); total += goal.side_length; feedback.completed_sides=side+1; feedback.progress=(side+1)/goal.sides; goal_handle.publish_feedback(feedback)
        result.total_distance=total; goal_handle.succeed(); return result
def main(args=None):
    rclpy.init(args=args); node=DrawPolygonServer()
    try:rclpy.spin(node)
    except KeyboardInterrupt:pass
    finally:node.destroy_node();rclpy.shutdown()
