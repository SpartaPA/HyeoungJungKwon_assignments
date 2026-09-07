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

`service_client`는 `/turtle1/teleport_absolute`, `/turtle1/set_pen`, `/spawn`, `/clear`를 `call_async`와 `spin_until_future_complete`로 순서 호출한다. `square_driver`에는 `SetBool` 기반 enable/disable 서버와 `Trigger` 기반 home 저장 서버를 추가했다. `rotate_client --cancel`은 goal 취소 요청도 보낸다. 구독 콜백에서 동기 서비스 응답을 기다리면 SingleThreadedExecutor가 현재 콜백에 묶여 응답 콜백을 실행하지 못하므로 교착된다. 비동기 요청과 별도 spin이 정답이다.

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

`qos_demo.py`는 Best-Effort publisher와 Reliable subscriber를 동시에 실행해 비호환 경고를 재현하고, Transient Local waypoint publisher도 함께 실행한다. 진단은 `ros2 topic info /turtle_dist --verbose`에서 Reliability/Durability를 비교하고 양쪽을 같은 정책으로 맞추는 순서다.

| 토픽 | Reliability | Durability | 근거 |
|---|---|---|---|
| `/turtle1/pose` | Best Effort | Volatile | 최신 센서 스트림 |
| `/turtle1/cmd_vel` | Reliable | Volatile | 제어 명령 손실 방지 |
| `/waypoints` | Reliable | Transient Local | late-joiner도 경유점 필요 |
| `/turtle_dist` | Reliable (기본 노드) / Best Effort (qos_demo) | Volatile | 계산된 주기 스트림 및 비호환 실험 |
| `/diagnostics` | Reliable | Volatile | 진단 이벤트 보존 |

## 문제 8 — colcon 워크스페이스

`ros2_ws/src`에는 `turtle_interfaces`, `turtle_py`, `turtle_cpp`가 있다. `colcon`은 package.xml 의존성 DAG를 분석하므로 interface 패키지가 먼저 빌드된다. `source install/setup.bash` 전에는 overlay 패키지를 찾지 못하고, 후에는 `AMENT_PREFIX_PATH`와 Python 경로가 등록되어 `ros2 run`이 동작한다.

## 문제 9 — launch와 파라미터

`launch/turtle_system.launch.py`는 turtlesim, publisher, monitor, polygon action server를 함께 기동한다. `publish_rate`와 `warn_distance`는 `config/params.yaml`을 기본으로 읽고 launch argument로 덮어쓸 수 있다.

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

Ubuntu 22.04 + ROS 2 Humble 환경에서 colcon build, turtlesim 실행, 노드 통신, GUI 캡처와 rosbag 기록을 확인했다. 추가 실행 결과와 캡처 목록은 본 보고서와 `screenshots/`에 정리했다.

각 문제의 Linux 실행 명령은 해당 문제 절의 코드 블록에 기록했다. 제출물에는 실행에 필요한 소스와 실제 검증 증거만 포함한다.

## 선택 문제 실행 보강 기록 (문제 5~10)

### 문제 5

내장 서비스 4종을 순서대로 호출해 모두 응답을 받았다. 추가로 `square_driver`의 `/square_driver/set_enabled` (`SetBool`)에 `false`를 보내 `enabled=False` 응답을 확인했고, `/square_driver/save_home` (`Trigger`)는 `home_saved phase=4 tick=2`를 반환했다. `rotate_client --cancel`은 `remaining=-3.142`, `cancel_requested=True`를 출력했다.

### 문제 6

`Waypoint`, `WaypointList`, `SetGain`, `DrawPolygon` 인터페이스를 `ros2 interface show`로 확인했다. 다각형 action은 삼각형·사각형·육각형에서 각각 `SUCCEEDED`, 총 이동 거리 `3.0`, `4.0`, `6.0`을 반환했으며, 사각형 실행에서 `completed_sides=1..4`, `progress=0.25..1.0` 피드백을 확인했다. 캡처는 `screenshots/11-triangle.png`, `12-square.png`, `13-hexagon.png`이다.

### 문제 7

`qos_demo`에서 Best-Effort publisher와 Reliable subscriber의 `incompatible QoS ... RELIABILITY` 경고를 재현했다. `/waypoints`는 Transient Local publisher를 먼저 실행한 뒤 늦게 참여한 `ros2 topic echo`가 3개의 waypoint를 수신했다. depth 1 subscriber는 느린 콜백으로 `depth1 received=1` 로그를 남겼다.

### 문제 8~9

`colcon build --symlink-install` 결과 `turtle_cpp`, `turtle_interfaces`, `turtle_py` 3개 패키지가 성공했다. launch는 turtlesim, publisher, monitor, action server 4개를 기동했고 `publish_rate=5.0`, `warn_distance=1.0`을 `ros2 param get`으로 확인했다. namespace 실행 결과 `/turtle2/turtle_dist`가 생성됐다.

### 문제 10

모든 publisher를 종료한 뒤 `ros2 bag play bags/turtle_run`을 실행하고 `distance_monitor`가 기록된 `/turtle_dist`를 다시 수신하는 것을 확인했다. 기존 bag에는 5.567초 동안 `/turtle1/pose` 349개, `/turtle_dist` 28개가 있다. 2026-09-04 Linux 재검증에서는 35.85초 동안 `/turtle1/pose` 2,241개, `/turtle_dist` 180개(총 2,421개)를 새로 기록하고 재생했다. pytest는 정상 상태에서 8개 통과했다. 기존 TF·RViz2·rqt_graph 캡처는 `screenshots/08~10`이며 최신 Linux 캡처는 아래 재검증 절에 링크했다.

## 2026-09-04 재검증

- `colcon build --symlink-install`: `turtle_interfaces`, `turtle_cpp`, `turtle_py` 3개 패키지 성공
- `/usr/bin/python3 -m pytest -q src/turtle_py/test`: `8 passed in 0.01s`
- C++ 수동 빌드, CMake 빌드, `motor.o` 제외 링크 실패(`undefined reference`) 재현 성공
- Valgrind: 11 allocations/11 frees, `All heap blocks were freed`, 오류 0
- launch에서 turtlesim, distance publisher/monitor, polygon action server 4개 노드 기동 및 clean shutdown 확인
- `/turtle_dist` topic hz: 평균 4.988~5.000 Hz, `std_msgs/msg/Float64`, publisher 1개 확인
- Service: `/spawn` 호출 후 `name='turtle2'` 응답 확인
- Action: 삼각형 goal의 1~3면 피드백과 `total_distance=3.0`, `SUCCEEDED` 확인
- 신규 rosbag: 35.850초, `/turtle1/pose` 2,241개, `/turtle_dist` 180개(총 2,421개); `ros2 bag play` 완료
- 신규 실제 Linux 캡처:
  - [turtlesim 실행 화면](screenshots/19-turtlesim-linux.png)
  - [rqt_graph 노드 연결](screenshots/20-rqt-graph-linux.png)
  - [RViz2 기동 화면](screenshots/21-rviz2-linux.png)

## 2026-09-04 실제 Ubuntu 22.04 최종 확인

아래 결과는 이 실행에서 일반 사용자 `pa27`로 실제 명령을 다시 실행해 얻은 출력이다. `sudo`는 GUI 캡처 도구 설치 시도에만 사용했으며, 비밀번호 입력이 필요한 환경이라 설치는 완료되지 않았다. 대신 설치되어 있던 ImageMagick `import`으로 실제 창을 캡처했다.

- 환경: `ROS_DISTRO=humble`, `/opt/ros/humble/bin/ros2`, `ros2 doctor` 1 check passed
- 빌드: `colcon build --symlink-install` 성공. `turtle_interfaces`, `turtle_cpp`, `turtle_py`가 설치됨
- Python: `python3 -m pytest -p no:anyio -q src/turtle_py/test` → `7 passed in 0.01s`
- launch: `/turtlesim_node`, `/distance_publisher`, `/distance_monitor`, `/draw_polygon_server` 4개 노드 기동
- `/turtle_dist`: `std_msgs/msg/Float64`, 평균 `5.001~5.006 Hz`, publisher 1개
- 파라미터: `/distance_publisher publish_rate = 5.0`, `/distance_monitor warn_distance = 3.0`
- 서비스: `/turtle1/teleport_absolute`, `/turtle1/set_pen`, `/spawn`, `/clear` 응답 성공; `/spawn`은 `turtle2` 반환
- 회전 action: `result=...delta=3.1359999` 확인
- 다각형 action: sides `3/4/6` 모두 `SUCCEEDED`, total distance `3.0/4.0/6.0`
- Waypoint: `P1=(2,2)`, `P2=(6,2)`, `P3=(6,6)` 수신. `/waypoints`는 `WaypointList`, `RELIABLE`, `TRANSIENT_LOCAL`
- QoS: Best-Effort publisher와 Reliable subscriber의 `incompatible QoS ... RELIABILITY` 경고를 실제 재현
- TF/Marker: `world -> turtle1` 조회 성공(translation `[1.864, 2.080, 0.000]`), `/waypoint_markers`의 `frame_id=world` 확인
- C++: `stop_distance` 입력 `4 0.5` → `stop_distance=16`; motor 실행 → `drive_motor started`; sensor CMake/ASAN 실행 완료, 누수 오류 출력 없음
- rosbag: `bags/turtle_run_final`에 실제 기록. `45.360500823 s`, `/turtle1/pose` (`turtlesim/msg/Pose`) `2836개`, `/turtle_dist` (`std_msgs/msg/Float64`) `227개`, 총 `3063개`; Ctrl+C 종료 후 `ros2 bag info` 확인
- 실제 신규 캡처: [turtlesim](screenshots/22-turtlesim-final.png), [turtlesim 보조 화면](screenshots/23-topic-rate-final.png), [rqt_graph](screenshots/24-rqt-graph-final.png), [RViz2 world/TF/Marker 설정](screenshots/26-rviz2-world-tf-marker.png)

제한 사항: `gnome-screenshot` 패키지는 sudo 비밀번호 프롬프트로 설치하지 못해 ImageMagick 대체 캡처를 사용했다. RViz2는 `Fixed Frame=world`, TF/Marker 디스플레이를 임시 설정 파일로 기동했고 Global Status가 정상임을 확인했다. 신규 bag은 `ros2 bag play ../bags/turtle_run_final --rate 10`으로 재생했으며, 별도 `ros2 topic echo /turtle_dist --once`에서 `data: 2.7924806058350633` 수신을 확인했다.

## 2026-09-07 추가 보강

- Waypoint publisher를 4개 경유점(P1~P4)으로 수정하고 `ros2 topic echo /waypoints --once`에서 P1=(2,2), P2=(6,2), P3=(6,6), P4=(2,6)을 확인했다.
- `DrawPolygon` 오각형 goal: feedback `completed_sides=1..5`, `progress=0.2..1.0`, `total_distance=5.0`, `SUCCEEDED`.
- `DrawPolygon` 팔각형 goal: feedback `completed_sides=1..8`, `progress=0.125..1.0`, `total_distance=8.0`, `SUCCEEDED`.
- 추가 캡처: [오각형](screenshots/27-pentagon.png), [팔각형](screenshots/28-octagon.png).

### 의도적 pytest 실패 검증

`calculations.py`의 `distance()`에 임시로 `+ 1.0` 오차를 넣고 실행한 뒤 즉시 원복했다.

```text
python3 -m pytest -p no:anyio -q src/turtle_py/test
2 failed, 5 passed in 0.04s
실패: test_distance_normal_and_zero, test_reached_boundary_and_invalid_tolerance
```

원복 후 재실행 결과:

```text
python3 -m pytest -p no:anyio -q src/turtle_py/test
7 passed in 0.01s

## 2026-09-07 추가 터미널 검증

### 문제 1 C++ 빌드 출력

```text
printf "4 0.5" | ./stop_distance
speed friction: stop_distance=16
./motor_linux
drive_motor started

motor.o를 제외한 링크:
undefined reference to `Motor::Motor(...)`
undefined reference to `Motor::start() const`
collect2: error: ld returned 1 exit status

CMake: [100%] Built target motor_demo
```

### 문제 2 센서·Valgrind 출력

```text
lidar read=1.2
imu read=0.03
near_goal_count=1
clamp_speed=1 clamp_pixel=255
Lidar destroyed
Sensor destroyed
leak_safe_owner=1

Valgrind: 11 allocs, 11 frees
All heap blocks were freed -- no leaks are possible
ERROR SUMMARY: 0 errors from 0 contexts
```

### 문제 4 Python publisher → C++ subscriber 교차 통신

```text
[distance_publisher]: distance node up
[distance_monitor_cpp]: monitor C++ node up
[distance_monitor_cpp]: distance=7.870
```

Python publisher가 발행한 `/turtle_dist`를 C++ subscriber가 반복 수신하는 것을 확인했다.

### 문제 5 RotateAbsolute 취소 보강

```text
[rotate_client]: remaining=3.045
[rotate_client]: cancel_requested=True
[rotate_client]: cancel_result_status=5 (expected 5)
```

goal 실행 중 feedback을 받은 뒤 취소 요청을 보냈고, ROS 2 `STATUS_CANCELED=5` 결과를 확인했다.

### 문제 7 QoS·depth 1 추가 출력

```text
New publisher discovered on topic '/turtle_dist', offering incompatible QoS.
Last incompatible policy: RELIABILITY
depth1 received=1 value=1.0
depth1 received=2 value=6.0
depth1 received=3 value=11.0
depth1 received=4 value=16.0
depth1 received=5 value=21.0
```

Best-Effort publisher와 Reliable subscriber의 연결 단절을 확인했고, 0.1초 발행·0.5초 처리의 depth 1 구독자에서 메시지 값이 건너뛰는 현상을 확인했다.

### 문제 8~9 source·YAML 추가 출력

```text
source 전: Package 'turtle_py' not found
source 후: /home/pa27/Git/HyeoungJungKwon_assginments/level_1/turtlesim/ros2_ws/install/turtle_py
YAML 변경 후 warn_distance:
Double value is: 1.0
```

`params.yaml`의 `warn_distance`를 3.0에서 1.0으로 바꾸고 재빌드 없이 파라미터 파일을 다시 읽어 동작값이 1.0으로 바뀌는 것을 확인했다.

### 문제 3 두 subscriber 동시 수신

동일한 publisher를 두 monitor가 동시에 구독했다.

```text
[distance_monitor]: distance 7.870 exceeds 1.000
[distance_monitor_b]: distance 7.870 exceeds 1.000
```

두 노드가 같은 `/turtle_dist` 메시지를 동시에 수신하는 것을 확인했다.
```
