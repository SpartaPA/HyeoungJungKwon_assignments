# 제출 파일 안내

이 문서는 `lv1_module2_hyeoungjungkwon.zip` 안의 각 파일이 담당하는 채점 항목을 설명한다.

## 문서

- `report.md` — 문제 1~10의 구현 설명, 실행 명령, 검증 결과와 선택 문제 보강 기록을 담은 메인 보고서다.
- `execution_evidence.md` — 실행 결과와 캡처 파일을 항목별로 연결한 검증 요약이다.

## 문제 1~2: C++ 기초

- `cpp_basics/CMakeLists.txt` — `stop_distance`와 `motor_demo`를 C++17로 빌드하는 CMake 설정이다.
- `cpp_basics/stop_distance.cpp` — 속도와 마찰계수로 제동거리를 계산하고 잘못된 입력을 검사한다.
- `cpp_basics/motor.hpp` — `Motor` 클래스의 이름과 `start()` 인터페이스를 선언한다.
- `cpp_basics/motor.cpp` — `Motor` 생성자와 `start()` 구현을 정의한다.
- `cpp_basics/main.cpp` — `Motor` 객체를 생성하고 다중 파일 링크 결과를 확인하는 실행 파일이다.
- `cpp_basics/sensors/CMakeLists.txt` — 센서 예제를 C++17과 경고 옵션으로 빌드한다.
- `cpp_basics/sensors/main.cpp` — 추상 `Sensor`, `Lidar`, `Imu`, 다형성, `unique_ptr`, `unordered_map`, `vector`, `count_if`, `clamp`와 소멸 순서를 시연한다.

## 문제 3~5: ROS 2 노드

- `ros2_ws/src/turtle_py/package.xml` — Python 패키지와 ROS 2 의존성을 선언한다.
- `ros2_ws/src/turtle_py/setup.py` — Python 패키지 설치 정보와 모든 `ros2 run` entry point를 등록한다.
- `ros2_ws/src/turtle_py/setup.cfg` — ament Python 설치 경로 설정이다.
- `ros2_ws/src/turtle_py/resource/turtle_py` — ament index가 패키지를 찾도록 하는 marker 파일이다.
- `ros2_ws/src/turtle_py/turtle_py/__init__.py` — `turtle_py` Python 패키지 초기화 파일이다.
- `ros2_ws/src/turtle_py/turtle_py/calculations.py` — 거리, 목표 각도 관련 계산과 도달 판정 순수 함수다.
- `ros2_ws/src/turtle_py/turtle_py/distance_publisher.py` — turtle pose를 구독해 `/turtle_dist`에 거리를 발행한다.
- `ros2_ws/src/turtle_py/turtle_py/distance_monitor.py` — 거리 토픽을 구독하고 `warn_distance` 초과 시 경고한다.
- `ros2_ws/src/turtle_py/turtle_py/square_driver.py` — `/turtle1/cmd_vel`로 정사각형 주행을 수행하며 SetBool/Trigger 서버도 제공한다.
- `ros2_ws/src/turtle_py/turtle_py/service_client.py` — teleport, set_pen, spawn, clear 내장 서비스를 비동기로 순서 호출한다.
- `ros2_ws/src/turtle_py/turtle_py/rotate_client.py` — `RotateAbsolute` action을 호출하고 feedback과 취소 요청을 처리한다.

## 문제 6: 커스텀 인터페이스와 action

- `ros2_ws/src/turtle_interfaces/package.xml` — 인터페이스 전용 패키지와 생성 의존성을 선언한다.
- `ros2_ws/src/turtle_interfaces/CMakeLists.txt` — msg, srv, action 파일을 ROS 2 타입으로 생성한다.
- `ros2_ws/src/turtle_interfaces/msg/Waypoint.msg` — x, y, tolerance, label을 갖는 단일 waypoint 메시지다.
- `ros2_ws/src/turtle_interfaces/msg/WaypointList.msg` — Header와 Waypoint 배열을 갖는 목록 메시지다.
- `ros2_ws/src/turtle_interfaces/srv/SetGain.srv` — 회전 게인 설정용 서비스 인터페이스다.
- `ros2_ws/src/turtle_interfaces/action/DrawPolygon.action` — 변 수·길이 goal, 진행률 feedback, 총 이동 거리 result를 정의한다.
- `ros2_ws/src/turtle_py/turtle_py/waypoint_publisher.py` — 3개 waypoint를 `/waypoints`에 Transient Local로 발행한다.
- `ros2_ws/src/turtle_py/turtle_py/draw_polygon_server.py` — `DrawPolygon` goal을 받아 cmd_vel로 다각형을 그리고 취소 시 정지한다.

## 문제 7: QoS

- `ros2_ws/src/turtle_py/turtle_py/qos_demo.py` — Best-Effort/Reliable 비호환, Transient Local late-joiner, depth 1 지연 subscriber를 실행한다.

## 문제 8~9: workspace와 launch

- `ros2_ws/src/turtle_cpp/package.xml` — C++ ROS 2 패키지 의존성 선언이다.
- `ros2_ws/src/turtle_cpp/CMakeLists.txt` — rclcpp 노드 두 개를 빌드·설치하는 ament CMake 설정이다.
- `ros2_ws/src/turtle_cpp/src/distance_publisher.cpp` — C++로 pose를 구독하고 거리 토픽을 발행한다.
- `ros2_ws/src/turtle_cpp/src/distance_monitor.cpp` — C++로 거리 토픽을 구독해 로그를 출력한다.
- `ros2_ws/src/turtle_py/config/params.yaml` — publisher 주기와 monitor 경고 거리를 기본 파라미터로 정의한다.
- `ros2_ws/src/turtle_py/launch/turtle_system.launch.py` — turtlesim, publisher, monitor, action server를 한 번에 기동하고 YAML/launch 인자를 주입한다.

## 문제 10: 테스트·시각화·기록

- `ros2_ws/src/turtle_py/test/test_calculations.py` — 거리, 각도 정규화, 허용 오차와 예외를 검증하는 pytest다.
- `ros2_ws/bags/turtle_run/metadata.yaml` — rosbag의 저장 형식, 토픽, 메시지 수, 녹화 시간을 기록한다.
- `ros2_ws/bags/turtle_run/turtle_run_0.db3` — `/turtle1/pose`와 `/turtle_dist` 실제 메시지가 저장된 SQLite rosbag 데이터다.
- `screenshots/01-turtlesim.png` — turtlesim 기본 실행 화면이다.
- `screenshots/02-square-driver.png` — square driver 주행 화면이다.
- `screenshots/03-services-spawn.png` — 서비스 호출과 turtle2 생성 후 화면이다.
- `screenshots/04-action-waypoints.png` — action/waypoint 실행 화면이다.
- `screenshots/05-topic-status.png` — 노드 목록, 토픽 목록과 거리 메시지 검증 결과다.
- `screenshots/06-interface-action.png` — 커스텀 interface와 action 결과다.
- `screenshots/07-rosbag-info.png` — rosbag 녹화 정보다.
- `screenshots/08-tf-turtlesim.png` — TF broadcaster 실행 중 turtlesim 화면이다.
- `screenshots/09-rviz-tf-marker.png` — RViz2 실행 화면이다.
- `screenshots/10-rqt-graph.png` — rqt_graph 노드·토픽 연결 화면이다.
- `screenshots/11-triangle.png` — 삼각형 action 성공 후 turtlesim 캡처다.
- `screenshots/12-square.png` — 사각형 action 성공 후 turtlesim 캡처다.
- `screenshots/13-hexagon.png` — 육각형 action 성공 후 turtlesim 캡처다.
- `screenshots/14-services-server.png` — 자체 SetBool/Trigger 서비스 응답 캡처다.
- `screenshots/15-qos-late-joiner.png` — QoS 정보와 late-joiner waypoint 수신 결과다.
- `screenshots/16-launch-namespace.png` — launch 파라미터와 `/turtle2/turtle_dist` 확인 결과다.
- `screenshots/17-bag-playback.png` — publisher 종료 후 rosbag playback 실행 결과다.
- `screenshots/18-test-failure-detection.png` — 일부러 틀린 기대값을 넣었을 때 pytest가 실패를 검출한 결과다.

제출 압축에는 재빌드 가능한 소스와 증거만 포함하고 `build/`, `install/`, `log/`는 포함하지 않는다.
