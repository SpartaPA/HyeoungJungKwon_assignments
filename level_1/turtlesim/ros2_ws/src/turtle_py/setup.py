from setuptools import setup

package_name = 'turtle_py'
setup(name=package_name, version='0.1.0', packages=[package_name],
      data_files=[('share/ament_index/resource_index/packages', ['resource/' + package_name]),
                  ('share/' + package_name, ['package.xml']),
                  ('share/' + package_name + '/launch', ['launch/turtle_system.launch.py']),
                  ('share/' + package_name + '/config', ['config/params.yaml'])],
      install_requires=['setuptools'], zip_safe=True,
      entry_points={'console_scripts': [
          'distance_publisher = turtle_py.distance_publisher:main',
          'distance_monitor = turtle_py.distance_monitor:main',
          'square_driver = turtle_py.square_driver:main',
          'service_client = turtle_py.service_client:main',
          'toggle_servers = turtle_py.toggle_servers:main',
          'rotate_client = turtle_py.rotate_client:main',
          'draw_polygon_server = turtle_py.draw_polygon_server:main',
          'waypoint_publisher = turtle_py.waypoint_publisher:main',
          'tf_marker_broadcaster = turtle_py.tf_marker_broadcaster:main',
          'qos_demo = turtle_py.qos_demo:main',
          'qos_reliable_subscriber = turtle_py.qos_demo:reliable_subscriber_main',
          'qos_latched_waypoint_publisher = turtle_py.qos_demo:latched_waypoint_main',
      ]})
