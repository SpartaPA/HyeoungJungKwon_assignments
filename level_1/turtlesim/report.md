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

실행 명령과 확인 결과는 각 패키지의 소스 주석 및 아래 절에 기록한다. ROS 2가 설치된 Ubuntu에서 다음을 먼저 실행한다.

```bash
cd ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```
