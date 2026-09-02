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

실행 명령과 확인 결과는 각 패키지의 소스 주석 및 아래 절에 기록한다. ROS 2가 설치된 Ubuntu에서 다음을 먼저 실행한다.

```bash
cd ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```
