# 모듈 ② — turtlesim 기반 C++·Python ROS2 패키지 개발

검증 환경: Ubuntu 22.04, ROS 2 Humble, Python 3.10, C++17

## 제출 규격

거리 상태는 공개 과제 본문 기준으로 다음을 사용했다.

    토픽: /turtle_distance
    타입: std_msgs/msg/Float32
    주기: 10 Hz
    일반 publisher/subscriber QoS depth: 10

제출 폴더에는 report.md, cpp_basics/, ros2_ws/src/, screenshots/, bags/만 포함한다. build/, install/, log/, .venv/, ros2_ws/bags/는 제외했다.

## 문제 1 — C++ 빌드 체계

수동 2단계 빌드:

    g++ -Wall -std=c++17 -c motor.cpp
    g++ -Wall -std=c++17 -c main.cpp
    g++ main.o motor.o -o motor_demo
    ./motor_demo

실행:

    drive_motor started

motor.o를 제외한 링크는 컴파일은 끝났지만 구현 함수의 주소를 연결하지 못했다.

    undefined reference to Motor::Motor(...)
    undefined reference to Motor::start() const
    collect2: error: ld returned 1 exit status

CMake:

    cmake -S cpp_basics -B /tmp/cpp-basics-build-linux
    cmake --build /tmp/cpp-basics-build-linux --verbose
    [100%] Built target motor_demo

## 문제 2 — 현대 C++ 센서 계층

Sensor를 순수 가상 클래스로 만들고 Lidar와 Imu를 상속시켰다. unique_ptr vector로 다형성 순회를 수행했다.

    lidar read=1.2
    imu read=0.03
    near_goal_count=1
    clamp_speed=1 clamp_pixel=255
    Lidar destroyed
    Sensor destroyed
    leak_safe_owner=1

Valgrind:

    11 allocs, 11 frees
    All heap blocks were freed -- no leaks are possible
    ERROR SUMMARY: 0 errors from 0 contexts

가상 소멸자가 없으면 부모 포인터를 통한 삭제에서 자식 소멸자가 호출되지 않을 수 있으므로 다형성 부모에는 가상 소멸자를 선언한다.

## 문제 3 — rclpy 상태 발행·감시·주행

/turtle1/pose의 x, y, theta, linear_velocity, angular_velocity를 구독하고, 콜백에서는 최신 자세만 저장한다. 타이머에서 원점 거리를 계산해 /turtle_distance에 발행한다.

실제 topic hz:

    average rate: 9.998
    average rate: 10.004
    average rate: 10.001
    average rate: 9.990

두 monitor 동시 수신:

    [distance_monitor]: distance 7.841 exceeds 2.500
    [distance_monitor_b]: distance 7.841 exceeds 2.500

square_driver는 전진과 제자리 회전을 번갈아 발행하고 종료 시 zero Twist를 발행한다.

## 문제 4 — rclcpp 교차 언어 통신

C++ subscriber가 Python publisher의 Float32 /turtle_distance 메시지를 반복 수신했다.

    [distance_monitor_cpp]: monitor C++ node up
    [distance_monitor_cpp]: distance=7.841

| 항목 | rclpy | rclcpp |
|---|---|---|
| 노드 생성 | Node | Node 상속 |
| 타이머 | create_timer | create_wall_timer |
| 콜백 | Python 함수 | lambda/std::function |
| 종료 | destroy_node, shutdown | destroy_node, shutdown |

## 문제 5 — Service와 Action

내장 서비스는 teleport_absolute, set_pen, spawn, clear 순서로 비동기 호출했다. 자체 서비스 결과:

    SetBool: success=True, message=enabled=False
    Trigger: success=True, home 저장

RotateAbsolute 취소:

    remaining=3.045
    cancel_requested=True
    cancel_result_status=5

STATUS_CANCELED가 5로 확인되어 실행 중 취소가 처리되었다.

## 문제 6 — 커스텀 인터페이스

turtle_interfaces에 Waypoint, WaypointList, SetGain, DrawPolygon을 정의했다.

Waypoint echo:

    P1=(2,2)
    P2=(6,2)
    P3=(6,6)
    P4=(2,6)

다각형 결과:

    오각형: completed_sides=1..5, progress=0.2..1.0, total_distance=5.0, SUCCEEDED
    팔각형: completed_sides=1..8, progress=0.125..1.0, total_distance=8.0, SUCCEEDED

관련 캡처:

- screenshots/04-action-waypoints.png
- screenshots/06-interface-action.png
- screenshots/11-triangle.png
- screenshots/12-square.png
- screenshots/13-hexagon.png
- screenshots/27-pentagon.png
- screenshots/28-octagon.png

## 문제 7 — QoS 진단

Best-Effort publisher와 Reliable subscriber의 연결 단절:

    New publisher discovered on topic '/turtle_distance', offering incompatible QoS.
    Last incompatible policy: RELIABILITY

depth 1 실험:

    depth1 received=1 value=1.0
    depth1 received=2 value=6.0
    depth1 received=3 value=11.0
    depth1 received=4 value=16.0
    depth1 received=5 value=21.0

발행 주기는 0.1초이고 콜백 지연은 0.5초이므로 중간 값이 누락됐다. Waypoint publisher는 Reliable, Transient Local로 late-joiner 수신을 지원한다.

## 문제 8 — colcon workspace

빌드 순서:

    Starting >>> turtle_interfaces
    Starting >>> turtle_cpp
    Finished <<< turtle_interfaces
    Finished <<< turtle_cpp
    Starting >>> turtle_py
    Finished <<< turtle_py
    Summary: 3 packages finished

source 전후:

    source 전: Package 'turtle_py' not found
    source 후: /home/pa27/Git/HyeoungJungKwon_assginments/level_1/turtlesim/ros2_ws/install/turtle_py

인터페이스 패키지는 노드 패키지가 의존하므로 먼저 빌드된다.

## 문제 9 — launch와 파라미터

launch에서 turtlesim, distance publisher, distance monitor, DrawPolygon server를 함께 실행했다.

    publish_rate = 10.0
    warn_distance = 2.5

YAML의 warn_distance를 2.5에서 1.0으로 변경하고 재빌드 없이 실행해 다음을 확인했다.

    Double value is: 1.0

namespace 실행에서는 /turtle2/turtle_distance가 생성됐다.

## 문제 10 — TF·RViz2·rosbag·pytest

TF broadcaster는 world에서 turtle1로 변환을 발행하고, Marker는 frame_id=world로 발행한다. RViz2의 Fixed Frame은 world로 설정했다.

제출 bag 정보:

    경로: bags/turtle_run_final
    기록 시간: 31.840045651 s
    /turtle1/pose: 1991 messages
    /turtle_distance: 318 messages
    총 메시지: 2309

bag 재생 중 구독자 수신:

    data: 2.7924806058350633

pytest:

    7 passed in 0.01s

의도적 실패 실험:

    distance()에 임시 오류를 넣음
    2 failed, 5 passed in 0.04s
    원복 후 7 passed in 0.01s

진단 순서:

    ros2 node list
    ros2 topic list
    ros2 topic info /turtle_distance --verbose
    ros2 topic hz /turtle_distance
    publisher 로그 확인

캡처:

- screenshots/01-turtlesim.png
- screenshots/02-square-driver.png
- screenshots/03-services-spawn.png
- screenshots/31-rqt-graph-public.png
- screenshots/29-rviz2-world.png
- screenshots/30-turtlesim-public.png
- screenshots/27-pentagon.png
- screenshots/28-octagon.png

## 최종 점검

    report.md
    cpp_basics/
    ros2_ws/src/
    screenshots/
    bags/turtle_run_final/

제출에서 제외:

    build/
    install/
    log/
    .venv/
    __pycache__/
    ros2_ws/bags/
