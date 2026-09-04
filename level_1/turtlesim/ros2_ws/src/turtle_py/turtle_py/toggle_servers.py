import rclpy
from geometry_msgs.msg import Twist
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_srvs.srv import SetBool, Trigger
from turtlesim.msg import Pose
from turtlesim.srv import TeleportAbsolute


class ToggleServers(Node):
    def __init__(self):
        super().__init__('turtle_toggle_servers')
        self.declare_parameter('start_enabled', False)
        self.declare_parameter('linear_speed', 1.0)
        self.declare_parameter('angular_speed', 0.8)
        self.enabled = bool(self.get_parameter('start_enabled').value)
        self.latest_pose = None
        self.home = None
        self.pose_sub = self.create_subscription(Pose, '/turtle1/pose', self.on_pose, 10)
        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.publish_command)
        self.enable_srv = self.create_service(SetBool, '/enable_driving', self.enable_driving)
        self.save_srv = self.create_service(Trigger, '/save_home', self.save_home)
        self.go_home_srv = self.create_service(Trigger, '/go_home', self.go_home)
        self.teleport = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        self.get_logger().info('toggle services started')

    def on_pose(self, msg):
        self.latest_pose = msg

    def publish_command(self):
        if not self.enabled:
            return
        command = Twist()
        command.linear.x = float(self.get_parameter('linear_speed').value)
        command.angular.z = float(self.get_parameter('angular_speed').value)
        self.cmd_pub.publish(command)

    def enable_driving(self, request, response):
        self.enabled = bool(request.data)
        if not self.enabled:
            self.cmd_pub.publish(Twist())
        response.success = True
        response.message = 'driving enabled' if self.enabled else 'driving disabled'
        return response

    def save_home(self, request, response):
        if self.latest_pose is None:
            response.success = False
            response.message = 'pose has not arrived yet'
            return response
        self.home = (self.latest_pose.x, self.latest_pose.y, self.latest_pose.theta)
        response.success = True
        response.message = f'home saved: {self.home}'
        return response

    def go_home(self, request, response):
        if self.home is None:
            response.success = False
            response.message = 'save_home must be called first'
            return response
        if not self.teleport.service_is_ready():
            response.success = False
            response.message = 'teleport service is unavailable'
            return response
        teleport_request = TeleportAbsolute.Request()
        teleport_request.x, teleport_request.y, teleport_request.theta = self.home
        future = self.teleport.call_async(teleport_request)
        future.add_done_callback(self.teleport_done)
        response.success = True
        response.message = 'teleport request sent'
        return response

    def teleport_done(self, future):
        if future.exception() is None:
            self.get_logger().info('home teleport completed')
        else:
            self.get_logger().error(f'home teleport failed: {future.exception()}')


def main(args=None):
    rclpy.init(args=args)
    node = ToggleServers()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        node.get_logger().info('normal shutdown')
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
