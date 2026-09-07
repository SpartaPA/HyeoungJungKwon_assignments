#include <algorithm>
#include <cmath>
#include <iostream>
#include <memory>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

class Sensor {
 public:
  virtual ~Sensor() { std::cout << "Sensor destroyed\n"; }
  virtual double read() const = 0;
  virtual std::string name() const = 0;
};

class Lidar final : public Sensor {
 public:
  ~Lidar() override { std::cout << "Lidar destroyed\n"; }
  double read() const override { return 1.2; }
  std::string name() const override { return "lidar"; }
};

class Imu final : public Sensor {
 public:
  ~Imu() override { std::cout << "Imu destroyed\n"; }
  double read() const override { return 0.03; }
  std::string name() const override { return "imu"; }
};

template <typename T>
T clamp(T value, T low, T high) {
  return std::clamp(value, low, high);
}

struct Measurement {
  std::string sensor;
  double x;
  double y;
};

int main() {
  std::vector<std::unique_ptr<Sensor>> sensors;
  sensors.emplace_back(std::make_unique<Lidar>());
  sensors.emplace_back(std::make_unique<Imu>());
  std::unordered_map<std::string, double> latest;
  for (const auto& sensor : sensors) {
    latest[sensor->name()] = sensor->read();
    std::cout << sensor->name() << " read=" << sensor->read() << '\n';
  }

  std::vector<Measurement> log{{"lidar", 1.0, 1.0}, {"imu", 0.2, 0.2},
                               {"lidar", 2.0, 2.0}};
  const auto near_goal = std::count_if(log.begin(), log.end(), [](const auto& m) {
    return std::hypot(m.x, m.y) <= 0.5;
  });
  std::cout << "near_goal_count=" << near_goal << '\n';
  std::cout << "clamp_speed=" << clamp(4.2, 0.0, 1.0)
            << " clamp_pixel=" << clamp(300, 0, 255) << '\n';

  { Lidar stack_sensor; }
  auto heap_sensor = std::make_unique<Imu>();
  std::cout << "leak_safe_owner=" << (heap_sensor != nullptr) << '\n';
}
