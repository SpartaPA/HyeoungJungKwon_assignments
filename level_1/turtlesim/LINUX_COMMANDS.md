# Linux 실행 명령

Ubuntu 22.04 + ROS2 Humble에서 아래 명령을 순서대로 실행한다.

## 0. 설치

```bash
sudo apt update
sudo apt install -y ros-humble-turtlesim ros-humble-rviz2 ros-humble-rqt-graph ros-humble-tf-transformations python3-colcon-common-extensions python3-pytest
source /opt/ros/humble/setup.bash
```

## 1. 빌드

```bash
cd ~/HyeoungJungKwon_assginments/level_1/turtlesim/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install --event-handlers console_direct+
source install/setup.bash
```

## 2. 실행 — 터미널 1~4

각 터미널에서 먼저 실행한다.

```bash
cd ~/HyeoungJungKwon_assginments/level_1/turtlesim/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
```

터미널 1:

```bash
ros2 run turtlesim turtlesim_node
```

터미널 2:

```bash
ros2 run turtle_py distance_publisher
```

터미널 3:

```bash
ros2 run turtle_py distance_monitor --ros-args -p warn_distance:=3.0
```

터미널 4:

```bash
ros2 run turtle_py square_driver
```

## 3. 상태 확인 및 캡처

```bash
ros2 topic echo /turtle1/pose --once
ros2 topic hz /turtle_dist
ros2 topic info /turtle_dist --verbose
ros2 node list
ros2 topic list
```

화면 캡처:

```bash
mkdir -p ../screenshots
gnome-screenshot -w -f ../screenshots/01-turtlesim-square.png
```

## 4. launch 실행

기존 실행 노드를 `Ctrl+C`로 종료한 뒤 실행한다.

```bash
ros2 launch turtle_py turtle_system.launch.py publish_rate:=5.0 warn_distance:=1.0
```

다른 터미널에서:

```bash
ros2 node list
ros2 param get /distance_publisher publish_rate
ros2 param get /distance_monitor warn_distance
```

## 5. Service와 Action

```bash
ros2 service list
ros2 service type /turtle1/teleport_absolute
ros2 service type /turtle1/set_pen
ros2 service type /spawn
ros2 service type /clear
ros2 run turtle_py service_client
ros2 run turtle_py rotate_client
```

## 6. 커스텀 인터페이스와 다각형

```bash
ros2 interface show turtle_interfaces/msg/Waypoint
ros2 interface show turtle_interfaces/msg/WaypointList
ros2 interface show turtle_interfaces/srv/SetGain
ros2 interface show turtle_interfaces/action/DrawPolygon
ros2 run turtle_py waypoint_publisher
ros2 topic echo /waypoints
ros2 run turtle_py draw_polygon_server
```

다른 터미널에서 삼각형·사각형·육각형을 각각 실행한다.

```bash
ros2 action send_goal /draw_polygon turtle_interfaces/action/DrawPolygon "{sides: 3, side_length: 1.0}"
ros2 action send_goal /draw_polygon turtle_interfaces/action/DrawPolygon "{sides: 4, side_length: 1.0}"
ros2 action send_goal /draw_polygon turtle_interfaces/action/DrawPolygon "{sides: 6, side_length: 1.0}"
```

## 7. rqt_graph와 TF/RViz2 캡처

```bash
ros2 run turtle_py tf_marker_broadcaster
ros2 run rqt_graph rqt_graph
```

새 터미널에서:

```bash
rviz2
```

RViz2에서 `Fixed Frame`을 `world`로 설정하고 `TF`, `Marker`를 추가한 뒤 캡처한다.

```bash
gnome-screenshot -w -f ../screenshots/02-rqt-graph.png
gnome-screenshot -w -f ../screenshots/03-rviz2-tf-marker.png
```

## 8. rosbag 기록과 재생

기록:

```bash
mkdir -p ../bags
ros2 bag record -o ../bags/turtle_run /turtle1/pose /turtle_dist
```

몇 초 후 `Ctrl+C`로 기록을 종료하고, turtlesim 및 publisher를 종료한 뒤 재생한다.

```bash
ros2 bag info ../bags/turtle_run
ros2 run turtle_py distance_monitor
ros2 bag play ../bags/turtle_run
```

## 9. pytest

```bash
cd ~/HyeoungJungKwon_assginments/level_1/turtlesim/ros2_ws
source /opt/ros/humble/setup.bash
PYTHONPATH=src/turtle_py pytest -q src/turtle_py/test
```
