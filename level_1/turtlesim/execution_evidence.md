# ROS 2 실행 검증 기록

검증 환경: Ubuntu 22.04 / ROS 2 Humble / `ROS_DOMAIN_ID=2`

## 캡처

- [turtlesim 기본 실행](screenshots/01-turtlesim.png)
- [square_driver 주행](screenshots/02-square-driver.png)
- [서비스 호출 및 turtle2 생성](screenshots/03-services-spawn.png)
- [커스텀 action/waypoint 실행 후 화면](screenshots/04-action-waypoints.png)
- [노드·토픽·거리 메시지 검증](screenshots/05-topic-status.png)
- [커스텀 인터페이스·action 검증](screenshots/06-interface-action.png)
- [rosbag 기록 검증](screenshots/07-rosbag-info.png)
- [TF 연결 및 turtlesim](screenshots/08-tf-turtlesim.png)
- [RViz2 실행 화면](screenshots/09-rviz-tf-marker.png)
- [rqt_graph 노드 그래프](screenshots/10-rqt-graph.png)
- [자체 서비스 서버](screenshots/14-services-server.png)
- [QoS 비호환·late joiner](screenshots/15-qos-late-joiner.png)
- [launch 파라미터·namespace](screenshots/16-launch-namespace.png)
- [rosbag 재생 수신](screenshots/17-bag-playback.png)
- [의도적 테스트 실패 검출](screenshots/18-test-failure-detection.png)
- [삼각형 action](screenshots/11-triangle.png)
- [사각형 action](screenshots/12-square.png)
- [육각형 action](screenshots/13-hexagon.png)

## 실행 결과

- `/distance_publisher` → `/turtle_dist` → `/distance_monitor` 통신 성공
- `/turtle1/teleport_absolute`, `/turtle1/set_pen`, `/spawn`, `/clear` 호출 성공
- `/draw_polygon` action server 실행 및 삼각형 goal 수락·완료 성공 (`total_distance=3.0`)
- rosbag: 5.567초, 377 messages (`/turtle1/pose` 349 / `/turtle_dist` 28)
- Python 계산 테스트: 6 passed
- C++ ROS 2 노드 직접 CMake 검증: 두 executable 빌드 성공
- `tf_marker_broadcaster` 실행 성공, `world -> turtle1` 변환 확인
- RViz2 OpenGL 초기화 성공, rqt_graph에서 TF/waypoint 연결 확인
- `colcon build --symlink-install`: 3 packages finished
- QoS demo에서 Best-Effort/Reliable 비호환 경고 재현, Ctrl+C 종료 시 추가 shutdown 예외 없음
- 자체 `SetBool`/`Trigger` 서비스 응답 성공
- `/draw_polygon` 삼각형·사각형·육각형 goal 성공 및 피드백 확인
- publisher 종료 후 `ros2 bag play`로 monitor 재수신 확인
- 의도적으로 틀린 거리 기대값에서 `1 failed, 5 passed` 검출 후 테스트 원복

## 참고

5~10번 선택 항목 중 일부는 실행 결과와 캡처를 함께 보강했다. 전체 워크스페이스는 `colcon build --symlink-install`로 3개 패키지 모두 빌드되는 것을 확인했다.
