# 모듈 ② — turtlesim 기반 C++·Python ROS2 패키지 개발

환경: Ubuntu 22.04, ROS 2 Humble, Python 3.10, C++17

## 공통 제출 규격

- 거리 토픽: /turtle_dist
- 메시지: std_msgs/msg/Float64
- 주기: 5 Hz
- 일반 publisher/subscriber QoS depth: 13
- 제출 bag: bags/turtle_run_final/
- 제출 빌드 산출물: 제외

## 문제 1 — C++ 빌드 체계

수동 빌드:

    g++ -Wall -std=c++17 -c motor.cpp
    g++ -Wall -std=c++17 -c main.cpp
    g++ main.o motor.o -o motor_demo
    ./motor_demo

실행 결과:

    drive_motor started

motor.o를 제외한 링크에서는 컴파일은 완료되지만 구현 함수의 주소를 연결할 수 없어 다음 오류가 발생한다.

    undefined reference to Motor::Motor(...)
    undefined reference to Motor::start() const
    collect2: error: ld returned 1 exit status

CMake 검증:

    cmake -S cpp_basics -B /tmp/cpp-basics-build-linux
    cmake --build /tmp/cpp-basics-build-linux --verbose

    [100%] Built target motor_demo

증분 빌드는 소스와 헤더의 수정 시각 및 의존성 정보를 비교한다. motor.cpp만 변경하면 motor.cpp의 object만 다시 만들고, 마지막에 실행 파일을 다시 링크한다.

## 문제 2 — 현대 C++ 센서 계층

Sensor를 순수 가상 기반으로 만들고 Lidar와 Imu를 상속시켰다. 센서는 vector<unique_ptr<Sensor>>에 담아 다형성으로 순회했다.

실행 결과:

    lidar read=1.2
    imu read=0.03
    near_goal_count=1
    clamp_speed=1 clamp_pixel=255
    Lidar destroyed
    Sensor destroyed
    leak_safe_owner=1

자식 클래스 소멸자가 먼저 호출되고 부모 소멸자가 뒤따르는 것을 확인했다. unique_ptr은 소유권을 보관하므로 스코프 종료 시 자동으로 자원을 해제한다.

Valgrind 결과:

    11 allocs, 11 frees
    All heap blocks were freed -- no leaks are possible
    ERROR SUMMARY: 0 errors from 0 contexts

가상 소멸자를 제거하면 부모 포인터를 통한 삭제에서 자식 소멸자가 호출되지 않을 수 있으므로, 다형성 부모에는 가상 소멸자를 둔다.

## 문제 3 — rclpy 상태 발행·감시·주행

/turtle1/pose의 x, y, theta, linear_velocity, angular_velocity를 구독한다. 콜백에서는 최신 Pose를 저장하고, 타이머 콜백에서 원점까지의 hypot 거리를 /turtle_dist에 발행한다.

실행 규격:

    std_msgs/msg/Float64
    /turtle_dist
    약 5 Hz
    QoS depth 13

경고 로그:

    [distance_monitor]: distance 7.870 exceeds 1.000
    [distance_monitor_b]: distance 7.870 exceeds 1.000

동일 publisher를 두 monitor가 동시에 구독해 두 노드에서 같은 거리값을 수신했다. square_driver는 전진과 제자리 회전을 번갈아 발행하고 종료 시 zero Twist를 발행한다.

관련 캡처:

- screenshots/01-turtlesim.png
- screenshots/02-square-driver.png
- screenshots/03-services-spawn.png
- screenshots/27-pentagon.png
- screenshots/28-octagon.png

## 문제 4 — rclcpp 교차 언어 통신

Python publisher와 C++ monitor를 동시에 실행했다.

    [distance_publisher]: distance node up
    [distance_monitor_cpp]: monitor C++ node up
    [distance_monitor_cpp]: distance=7.870

Python과 C++가 같은 ROS 2 토픽 타입을 사용하면 언어가 달라도 통신할 수 있다.

| 항목 | rclpy | rclcpp |
|---|---|---|
| 노드 생성 | Node | Node 상속 |
| 타이머 | create_timer | create_wall_timer |
| 콜백 | Python 함수 | lambda/std::function |
| 종료 | destroy_node, shutdown | destroy_node, shutdown |

## 문제 5 — Service와 Action

내장 서비스는 다음 순서로 비동기 호출했다.

- /turtle1/teleport_absolute
- /turtle1/set_pen
- /spawn
- /clear

자체 서비스 결과:

    SetBool: success=True, message='enabled=False'
    Trigger: success=True, message='home_saved phase=4 tick=2'

RotateAbsolute 취소 결과:

    [rotate_client]: remaining=3.045
    [rotate_client]: cancel_requested=True
    [rotate_client]: cancel_result_status=5 (expected 5)

feedback을 받은 뒤 취소 요청을 보냈고 STATUS_CANCELED=5를 확인했다.

| 기능 | 통신 모델 | 이유 |
|---|---|---|
| 자세 스트리밍 | Topic | 지속적인 단방향 데이터 |
| 순간이동 | Service | 즉시 요청·응답 |
| 펜 설정 | Service | 즉시 설정 |
| 거북이 생성 | Service | 즉시 생성 결과 필요 |
| 목표 각도 회전 | Action | 장기 작업·feedback·취소 |

## 문제 6 — 커스텀 인터페이스

다음 인터페이스를 turtle_interfaces에서 생성했다.

- Waypoint.msg
- WaypointList.msg
- SetGain.srv
- DrawPolygon.action

확인 명령:

    ros2 interface show turtle_interfaces/msg/WaypointList
    ros2 interface show turtle_interfaces/srv/SetGain
    ros2 interface show turtle_interfaces/action/DrawPolygon

Waypoint echo 결과:

    P1=(2,2)
    P2=(6,2)
    P3=(6,6)
    P4=(2,6)

DrawPolygon 결과:

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

Best-Effort publisher와 Reliable subscriber의 비호환을 재현했다.

    New publisher discovered on topic '/turtle_dist', offering incompatible QoS.
    Last incompatible policy: RELIABILITY

depth 1 subscriber 결과:

    depth1 received=1 value=1.0
    depth1 received=2 value=6.0
    depth1 received=3 value=11.0
    depth1 received=4 value=16.0
    depth1 received=5 value=21.0

발행 주기는 0.1초, 콜백 지연은 0.5초이므로 depth 1 큐에서 중간 메시지가 누락됐다. /waypoints는 Reliable, Transient Local로 late-joiner가 이전 메시지를 받을 수 있도록 설정했다.

관련 캡처:

- screenshots/15-qos-late-joiner.png

## 문제 8 — colcon workspace

빌드 결과:

    Starting >>> turtle_interfaces
    Starting >>> turtle_cpp
    Finished <<< turtle_interfaces
    Finished <<< turtle_cpp
    Starting >>> turtle_py
    Finished <<< turtle_py
    Summary: 3 packages finished

turtle_interfaces가 먼저 빌드되는 이유는 package.xml 의존성 DAG에서 메시지 생성 패키지가 노드 패키지보다 선행하기 때문이다.

source 전후 결과:

    source 전: Package 'turtle_py' not found
    source 후: /home/pa27/Git/HyeoungJungKwon_assginments/level_1/turtlesim/ros2_ws/install/turtle_py

## 문제 9 — launch와 파라미터

launch에서 다음 네 노드를 함께 기동했다.

- turtlesim
- distance_publisher
- distance_monitor
- draw_polygon_server

YAML 변경 결과:

    warn_distance: 3.0 → 1.0
    Double value is: 1.0

재빌드 없이 params.yaml을 변경하고 다시 실행해 파라미터 값이 바뀌는 것을 확인했다. namespace 실행 결과에는 /turtle2/turtle_dist가 생성됐다.

관련 캡처:

- screenshots/16-launch-namespace.png
- screenshots/24-rqt-graph-final.png

## 문제 10 — TF·RViz2·rosbag·pytest

TF broadcaster는 world에서 turtle1로 변환을 발행하고, waypoint marker는 frame_id=world로 발행한다.

RViz2 최종 설정:

    Fixed Frame: world
    TF display: enabled
    Marker topic: /waypoint_markers
    Global Status: Ok

최종 bag 정보:

    기록 시간: 45.360500823 s
    /turtle1/pose: 2836 messages
    /turtle_dist: 227 messages
    총 메시지: 3063

bag 재생 후 구독자 수신:

    [ros2 topic echo /turtle_dist --once]
    data: 2.7924806058350633

정상 pytest:

    7 passed in 0.01s

의도적 실패 실험:

    distance()에 임시로 +1.0을 추가
    2 failed, 5 passed in 0.04s

원복 후:

    7 passed in 0.01s

진단 순서는 다음과 같다.

    ros2 node list
    ros2 topic list
    ros2 topic info /turtle_dist --verbose
    ros2 topic hz /turtle_dist
    publisher 로그 확인

관련 캡처:

- screenshots/10-rqt-graph.png
- screenshots/24-rqt-graph-final.png
- screenshots/26-rviz2-world-tf-marker.png
- screenshots/18-test-failure-detection.png

## 제출 파일 점검

제출 폴더에는 다음만 포함한다.

    report.md
    cpp_basics/
    ros2_ws/src/
    screenshots/
    bags/

다음은 포함하지 않는다.

    build/
    install/
    log/
    __pycache__/
    .venv/
    ros2_ws/bags/

모든 결과는 Ubuntu 22.04와 ROS 2 Humble에서 실제 실행한 기록을 기준으로 작성했다.

