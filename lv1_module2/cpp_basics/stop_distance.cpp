#include <cmath>
#include <iostream>

int main() {
  double speed = 0.0;
  double friction = 0.0;
  std::cout << "speed friction: ";
  if (!(std::cin >> speed >> friction) || speed < 0.0 || friction <= 0.0) {
    std::cerr << "speed must be >= 0 and friction must be > 0\n";
    return 1;
  }
  std::cout << "stop_distance=" << (speed * speed) / (2.0 * friction) << '\n';
}
