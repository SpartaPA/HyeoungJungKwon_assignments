import rclpy
from rclpy.node import Node
from turtlesim.srv import TeleportAbsolute, SetPen, Spawn, Clear

class ServiceClient(Node):
    def __init__(self):
        super().__init__('service_client'); self.get_logger().info('service client started')
    def call(self, name, srv_type, request):
        client = self.create_client(srv_type, name)
        if not client.wait_for_service(timeout_sec=3.0):
            self.get_logger().warning(f'service unavailable: {name}'); return None
        future = client.call_async(request); rclpy.spin_until_future_complete(self, future)
        if future.result() is not None: self.get_logger().info(f'{name}: {future.result()}')
        return future.result()

def main(args=None):
    rclpy.init(args=args); node=ServiceClient()
    requests=[('/turtle1/teleport_absolute',TeleportAbsolute,TeleportAbsolute.Request(x=2.0,y=2.0,theta=0.0)),('/turtle1/set_pen',SetPen,SetPen.Request(r=255,g=80,b=20,width=3,off=0)),('/spawn',Spawn,Spawn.Request(x=8.0,y=8.0,theta=0.0,name='turtle2')),('/clear',Clear,Clear.Request())]
    for item in requests: node.call(*item)
    node.destroy_node(); rclpy.shutdown()
