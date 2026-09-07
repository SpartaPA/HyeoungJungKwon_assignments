#pragma once

#include <string>

class Motor {
 public:
  explicit Motor(std::string name);
  void start() const;

 private:
  std::string name_;
};
