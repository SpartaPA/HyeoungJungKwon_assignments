import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class SquareDriver(Node):
    def __init__(self):
        super().__init__('square_driver'); self.pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.phase = 0; self.tick = 0; self.timer = self.create_timer(0.1, self.step)
        self.get_logger().info('square driver started')
    def step(self):
        msg = Twist(); msg.linear.x = 1.5 if self.phase % 2 == 0 else 0.0; msg.angular.z = 0.0 if self.phase % 2 == 0 else 1.5708
        self.pub.publish(msg); self.tick += 1
        if self.tick >= (30 if self.phase % 2 == 0 else 10): self.tick = 0; self.phase = (self.phase + 1) % 8

def main(args=None):
    rclpy.init(args=args); node = SquareDriver()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    finally:
        node.pub.publish(Twist()); node.destroy_node(); rclpy.shutdown()
