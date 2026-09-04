# 모듈 ② — turtlesim 기반 C++·Python ROS2 패키지 개발

이 제출물은 문제 1~10을 하나의 ROS 2 Humble 워크스페이스로 구성한다. 구현 규격은 개정 채점 규격인 `/turtle_dist`, `std_msgs/msg/Float64`, 5 Hz, QoS depth 13을 우선한다.

## 문제 1 — C++ 빌드 체계

### 수동 2단계 빌드

```bash
g++ -Wall -std=c++17 -c motor.cpp
g++ -Wall -std=c++17 -c main.cpp
g++ main.o motor.o -o motor_demo
./motor_demo
# drive_motor started
```

`g++ -c`는 헤더의 선언과 현재 번역 단위를 검사해 `.o`를 만들고, 링크 단계는 여러 `.o`의 실제 함수 주소를 연결한다. 따라서 `g++ main.o -o motor_demo`는 컴파일은 끝났지만 `Motor::Motor`와 `Motor::start`의 구현 주소를 찾지 못해 `undefined reference`를 낸다.

### CMake 및 증분 빌드

```bash
cmake -S . -B build
cmake --build build --verbose
```

`motor.cpp`만 변경하면 CMake의 의존성 그래프와 파일 수정 시각을 기준으로 `motor.cpp`만 재컴파일하고, 링크 단계에서 실행 파일을 다시 만든다.

## 문제 2~10

## 문제 2 — 현대 C++ 센서 계층

`cpp_basics/sensors/main.cpp`는 `Sensor`의 순수 가상 `read()`와 가상 소멸자를 사용하고, `std::vector<std::unique_ptr<Sensor>>`로 Lidar/Imu를 다형성 순회한다. 실행 시 `Lidar destroyed` 후 `Sensor destroyed`가 출력되어 자식부터 소멸함을 확인한다. 스택 객체는 블록 종료 시, `make_unique` 객체는 `unique_ptr` 소유자 종료 시 소멸한다. 가상 소멸자를 제거하면 부모 포인터 삭제 시 자식 소멸자가 호출되지 않아 자원 정리가 깨진다.

```bash
cmake -S cpp_basics/sensors -B cpp_basics/sensors/build
cmake --build cpp_basics/sensors/build
./cpp_basics/sensors/build/sensor_demo
# lidar read=1.2
# imu read=0.03
# near_goal_count=1
# clamp_speed=1 clamp_pixel=255
```

누수 재현은 `new Lidar`를 `delete`하지 않는 별도 실험으로 `-fsanitize=address` 또는 Valgrind에서 확인하고, 제출 구현은 `std::make_unique`로 수정한 상태다.

## 문제 3 — rclpy 상태 발행·감시·정사각형 주행

`turtle_py`는 `/turtle1/pose`의 `x,y,theta,linear_velocity,angular_velocity`를 받아 최신 Pose만 저장하고 타이머에서 5 Hz로 `std_msgs/msg/Float64` `/turtle_dist`를 발행한다. 기본 QoS depth는 13이며 `publish_rate`와 `warn_distance`는 런타임 파라미터다. `square_driver`는 전진/제자리 회전을 번갈아 보내고 종료 시 zero Twist를 발행한다.

```bash
ros2 run turtlesim turtlesim_node
ros2 run turtle_py distance_publisher
ros2 run turtle_py distance_monitor --ros-args -p warn_distance:=3.0
ros2 topic hz /turtle_dist
```

## 문제 4 — rclcpp 교차 언어 통신

`turtle_cpp`의 `distance_publisher_cpp`와 `distance_monitor_cpp`는 동일한 `/turtle_dist`·Float64·depth 13 규격을 사용한다. Python publisher와 C++ monitor를 섞어 실행해도 ROS 2 인터페이스 타입이 같으므로 통신한다.

| 항목 | rclpy | rclcpp |
|---|---|---|
| 노드 생성 | `Node(...)` | `class Node` 상속 |
| 타이머 | `create_timer` | `create_wall_timer` |
| 콜백 | Python 함수 | lambda/std::function |
| 종료 | destroy + shutdown | shutdown |

## 문제 5 — Service/Action

`service_client`는 `/turtle1/teleport_absolute`, `/turtle1/set_pen`, `/spawn`, `/clear`를 `call_async`와 `spin_until_future_complete`로 순서 호출한다. `rotate_client`는 `RotateAbsolute`의 remaining 피드백과 결과를 출력한다. 구독 콜백에서 동기 서비스 응답을 기다리면 SingleThreadedExecutor가 현재 콜백에 묶여 응답 콜백을 실행하지 못하므로 교착된다. 비동기 요청과 별도 spin이 정답이다.

`toggle_servers`는 `/enable_driving`(SetBool), `/save_home`(Trigger), `/go_home`(Trigger)를 제공한다. 주행 명령은 타이머에서만 발행하고, `enable_driving=false`이면 zero Twist를 보내 즉시 정지한다. `/go_home`은 서비스 콜백에서 응답을 블로킹하지 않고 `call_async`와 완료 콜백으로 처리한다.

| 기능 | 모델 | 근거 |
|---|---|---|
| 자세 스트리밍 | Topic | 연속 단방향 데이터 |
| 순간이동/펜/생성 | Service | 즉시 요청-응답 |
| 목표 각도 회전 | Action | 장기 작업·피드백·취소 |
| 궤적 삭제 | Service | 즉시 명령 |
| 반복 다각형 주행 | Action | 진행률·취소 필요 |

## 문제 6 — 커스텀 인터페이스

`turtle_interfaces`를 노드와 분리해 메시지 생성 의존성과 노드 구현 의존성을 분리했다. `Waypoint`, `WaypointList`, `SetGain`, `DrawPolygon` 정의와 waypoint publisher, polygon action server를 포함한다.

```bash
ros2 interface show turtle_interfaces/msg/WaypointList
ros2 topic echo /waypoints
ros2 action send_goal /draw_polygon turtle_interfaces/action/DrawPolygon "{sides: 4, side_length: 1.0}"
```

## 문제 7 — QoS 진단

`qos_demo.py`는 Best-Effort publisher와 Reliable subscriber 조합을 제공해 비호환을 재현하고, 별도 waypoint publisher는 `TRANSIENT_LOCAL`로 늦게 연결한 구독자에게 마지막 메시지를 전달한다. 진단은 `ros2 topic info /turtle_dist --verbose`에서 Reliability/Durability를 비교하고 양쪽을 Best-Effort로 맞추는 순서다. depth 1과 느린 콜백을 조합하면 큐가 덮어써져 메시지 누락이 발생한다.

| 토픽 | Reliability | Durability | 근거 |
|---|---|---|---|
| `/turtle1/pose` | Best Effort | Volatile | 최신 센서 스트림 |
| `/turtle1/cmd_vel` | Reliable | Volatile | 제어 명령 손실 방지 |
| `/waypoints` | Reliable | Transient Local | late-joiner도 경유점 필요 |
| `/turtle_dist` | Best Effort | Volatile | 계산된 주기 스트림 |
| `/diagnostics` | Reliable | Volatile | 진단 이벤트 보존 |

## 문제 8 — colcon 워크스페이스

`ros2_ws/src`에는 `turtle_interfaces`, `turtle_py`, `turtle_cpp`가 있다. `colcon`은 package.xml 의존성 DAG를 분석하므로 interface 패키지가 먼저 빌드된다. `source install/setup.bash` 전에는 overlay 패키지를 찾지 못하고, 후에는 `AMENT_PREFIX_PATH`와 Python 경로가 등록되어 `ros2 run`이 동작한다.

## 문제 9 — launch와 파라미터

`launch/turtle_system.launch.py`는 turtlesim, publisher, monitor, polygon action server를 함께 기동한다. `publish_rate`와 `warn_distance`는 launch argument 및 `config/params.yaml`로 주입한다.

```bash
ros2 launch turtle_py turtle_system.launch.py publish_rate:=5.0 warn_distance:=1.0
ros2 node list
ros2 param get /distance_publisher publish_rate
```

네임스페이스 실행은 `ros2 run turtle_py distance_publisher --ros-args -r __ns:=/turtle2`처럼 수행하며 해당 노드의 상대 토픽을 namespace 아래로 격리한다.

## 문제 10 — TF·기록·테스트

`tf_marker_broadcaster`는 `world -> turtle1` TF와 `/waypoint_markers` Marker를 발행한다. RViz2 Fixed Frame은 `world`로 설정한다. 기록/재생은 다음으로 확인한다.

```bash
ros2 bag record -o bags/turtle_run /turtle1/pose /turtle_dist
ros2 bag play bags/turtle_run
pytest -q ros2_ws/src/turtle_py/test
```

계산 함수 테스트는 거리, `[-pi,pi]` 각도 정규화, 허용 오차 경계 및 음수 tolerance 예외를 다룬다. 데이터 미수신 시 `ros2 node list` → `ros2 topic list` → `ros2 topic info --verbose`(타입/QoS) → `ros2 topic hz` → publisher 로그 순서로 진단한다. 빈 waypoint 목록과 잘못된 publish rate는 경고 후 안전한 기본값/무동작으로 처리한다.

실행 명령과 확인 결과는 각 패키지의 소스 주석 및 아래 절에 기록한다. ROS 2가 설치된 Ubuntu에서 다음을 먼저 실행한다.

```bash
cd ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

### 제출 체크리스트

- `cpp_basics/`: 문제 1·2 소스와 CMake
- `ros2_ws/src/`: 문제 3~10 패키지 전체
- `screenshots/`: turtlesim/rqt_graph/RViz2 캡처 위치
- `bags/`: rosbag 기록 결과 위치
- 압축 시 `build/`, `install/`, `log/`는 제외

현재 개발 호스트에는 ROS2 Humble, colcon, pytest, RViz2가 설치되어 있지 않아 GUI·bag 실측 로그는 생성하지 못했다. Ubuntu 22.04 + Humble에서 위 명령을 실행해 캡처와 bag를 채우면 제출본이 완성된다.

Linux에서 복사 실행할 명령은 [`LINUX_COMMANDS.md`](LINUX_COMMANDS.md)에 모아 두었다. 빌드와 순수 함수 테스트만 자동 실행하려면 `bash run_linux.sh`를 사용한다.
