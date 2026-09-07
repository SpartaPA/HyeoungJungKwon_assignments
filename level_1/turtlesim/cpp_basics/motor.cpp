#include "motor.hpp"

#include <iostream>
#include <utility>

Motor::Motor(std::string name) : name_(std::move(name)) {}

void Motor::start() const { std::cout << name_ << " started\n"; }
