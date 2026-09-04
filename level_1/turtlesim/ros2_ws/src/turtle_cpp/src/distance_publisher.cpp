#include <cmath>
#include <chrono>
#include <memory>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float32.hpp"
#include "turtlesim/msg/pose.hpp"
class DistancePublisher : public rclcpp::Node {
 public: DistancePublisher() : Node("distance_publisher_cpp"), x_(0), y_(0) {
  pub_ = create_publisher<std_msgs::msg::Float32>("/turtle_distance", 10);
  sub_ = create_subscription<turtlesim::msg::Pose>("/turtle1/pose", 10, [this](const auto m){x_=m->x; y_=m->y;});
  timer_ = create_wall_timer(std::chrono::milliseconds(100), [this]{ std_msgs::msg::Float32 m; m.data=std::hypot(x_,y_); pub_->publish(m); });
  RCLCPP_INFO(get_logger(), "distance C++ publisher started"); }
 private: double x_, y_; rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr pub_; rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr sub_; rclcpp::TimerBase::SharedPtr timer_;
};
int main(int argc,char** argv){rclcpp::init(argc,argv);rclcpp::spin(std::make_shared<DistancePublisher>());rclcpp::shutdown();}
