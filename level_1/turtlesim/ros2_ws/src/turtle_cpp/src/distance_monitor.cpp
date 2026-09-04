#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float64.hpp"
class DistanceMonitor : public rclcpp::Node { public: DistanceMonitor():Node("distance_monitor_cpp"){ sub_=create_subscription<std_msgs::msg::Float64>("/turtle_dist",13,[this](const std_msgs::msg::Float64::SharedPtr m){RCLCPP_INFO(get_logger(),"distance=%.3f",m->data);}); RCLCPP_INFO(get_logger(),"monitor C++ node up"); } private:rclcpp::Subscription<std_msgs::msg::Float64>::SharedPtr sub_;};
int main(int argc,char** argv){rclcpp::init(argc,argv);rclcpp::spin(std::make_shared<DistanceMonitor>());rclcpp::shutdown();}
