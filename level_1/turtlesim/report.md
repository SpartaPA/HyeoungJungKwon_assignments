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

실행 명령과 확인 결과는 각 패키지의 소스 주석 및 아래 절에 기록한다. ROS 2가 설치된 Ubuntu에서 다음을 먼저 실행한다.

```bash
cd ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```
