import math
import time
import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtle_interfaces.action import DrawPolygon

class DrawPolygonServer(Node):
    def __init__(self):
        super().__init__('draw_polygon_server')
        self.pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.server = ActionServer(
            self,
            DrawPolygon,
            '/draw_polygon',
            execute_callback=self.execute,
            goal_callback=self.goal,
            cancel_callback=self.cancel,
            callback_group=ReentrantCallbackGroup(),
        )
        self.get_logger().info('polygon action server up')
    def goal(self, goal): return GoalResponse.ACCEPT if goal.sides >= 3 and goal.side_length > 0 else GoalResponse.REJECT
    def cancel(self, goal): return CancelResponse.ACCEPT
    def execute(self, goal_handle):
        goal=goal_handle.request; result=DrawPolygon.Result(); feedback=DrawPolygon.Feedback(); total=0.0
        for side in range(goal.sides):
            for _ in range(10):
                if goal_handle.is_cancel_requested:
                    self.stop_and_cancel(goal_handle)
                    return result
                msg=Twist(); msg.linear.x=goal.side_length; self.pub.publish(msg); time.sleep(0.1)
            for _ in range(10):
                if goal_handle.is_cancel_requested:
                    self.stop_and_cancel(goal_handle)
                    return result
                msg=Twist(); msg.angular.z=2.0*math.pi/goal.sides; self.pub.publish(msg); time.sleep(0.1)
            self.pub.publish(Twist()); total += goal.side_length; feedback.completed_sides=side+1; feedback.progress=(side+1)/goal.sides; goal_handle.publish_feedback(feedback)
        result.total_distance=total; goal_handle.succeed(); return result
    def stop_and_cancel(self, goal_handle):
        self.pub.publish(Twist())
        goal_handle.canceled()
        self.get_logger().info('polygon goal canceled; turtle stopped')
def main(args=None):
    rclpy.init(args=args)
    node = DrawPolygonServer()
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.server.destroy()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
