from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    params = os.path.join(get_package_share_directory('turtle_py'), 'config', 'params.yaml')
    return LaunchDescription([
        DeclareLaunchArgument('publish_rate', default_value='5.0'),
        DeclareLaunchArgument('warn_distance', default_value='3.0'),
        Node(package='turtlesim', executable='turtlesim_node', name='turtlesim_node'),
        Node(package='turtle_py', executable='distance_publisher', name='distance_publisher', parameters=[params, {'publish_rate': LaunchConfiguration('publish_rate')}]),
        Node(package='turtle_py', executable='distance_monitor', name='distance_monitor', parameters=[params, {'warn_distance': LaunchConfiguration('warn_distance')}]),
        Node(package='turtle_py', executable='draw_polygon_server', name='draw_polygon_server'),
    ])
