import math
import sys
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from turtlesim.action import RotateAbsolute
from action_msgs.msg import GoalStatus

class RotateClient(Node):
    def __init__(self): super().__init__('rotate_client'); self.client=ActionClient(self,RotateAbsolute,'/turtle1/rotate_absolute')
    def send(self, theta):
        if not self.client.wait_for_server(timeout_sec=3.0): self.get_logger().warning('rotate action unavailable'); return
        goal=RotateAbsolute.Goal(); goal.theta=theta; future=self.client.send_goal_async(goal,feedback_callback=self.feedback); rclpy.spin_until_future_complete(self,future); handle=future.result()
        if handle is None or not handle.accepted: return
        if '--cancel' in sys.argv:
            rclpy.spin_once(self, timeout_sec=0.5)
            cancel = handle.cancel_goal_async(); rclpy.spin_until_future_complete(self, cancel)
            cancel_accepted = bool(cancel.result().goals_canceling)
            self.get_logger().info(f'cancel_requested={cancel_accepted}')
            result = handle.get_result_async(); rclpy.spin_until_future_complete(self, result)
            status = result.result().status
            self.get_logger().info(f'cancel_result_status={status} (expected {GoalStatus.STATUS_CANCELED})')
            return
        result=handle.get_result_async(); rclpy.spin_until_future_complete(self,result); self.get_logger().info(f'result={result.result().result}')
    def feedback(self, msg): self.get_logger().info(f'remaining={msg.feedback.remaining:.3f}')
def main(args=None):
    rclpy.init(args=args); node=RotateClient(); node.send(math.pi); node.destroy_node(); rclpy.shutdown() if rclpy.ok() else None
