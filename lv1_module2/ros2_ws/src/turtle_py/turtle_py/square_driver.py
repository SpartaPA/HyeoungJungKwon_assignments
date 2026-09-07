import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_srvs.srv import SetBool, Trigger
from turtlesim.msg import Pose

class SquareDriver(Node):
    def __init__(self):
        super().__init__('square_driver'); self.pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.phase = 0; self.tick = 0; self.enabled = True; self.home = None
        self.pose_sub = self.create_subscription(Pose, '/turtle1/pose', self.update_pose, 10)
        self.timer = self.create_timer(0.1, self.step)
        self.enable_service = self.create_service(SetBool, '/square_driver/set_enabled', self.set_enabled)
        self.home_service = self.create_service(Trigger, '/square_driver/save_home', self.save_home)
        self.get_logger().info('square driver up')
    def set_enabled(self, request, response):
        self.enabled = request.data
        if not self.enabled: self.pub.publish(Twist())
        response.success = True; response.message = f'enabled={self.enabled}'; return response
    def update_pose(self, pose):
        self.home_candidate = (pose.x, pose.y, pose.theta)
    def save_home(self, request, response):
        if not hasattr(self, 'home_candidate'):
            response.success = False
            response.message = 'pose unavailable; home not saved'
            return response
        self.home = self.home_candidate
        response.success = True
        response.message = (
            f'home_saved x={self.home[0]:.3f} y={self.home[1]:.3f} '
            f'theta={self.home[2]:.3f}'
        )
        return response
    def step(self):
        if not self.enabled:
            self.pub.publish(Twist()); return
        msg = Twist(); msg.linear.x = 1.5 if self.phase % 2 == 0 else 0.0; msg.angular.z = 0.0 if self.phase % 2 == 0 else 1.5708
        self.pub.publish(msg); self.tick += 1
        if self.tick >= (30 if self.phase % 2 == 0 else 10): self.tick = 0; self.phase = (self.phase + 1) % 8

def main(args=None):
    rclpy.init(args=args); node = SquareDriver()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    finally:
        if rclpy.ok(): node.pub.publish(Twist())
        node.destroy_node(); rclpy.shutdown() if rclpy.ok() else None
