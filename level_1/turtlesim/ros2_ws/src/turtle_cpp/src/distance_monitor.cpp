#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float32.hpp"
class DistanceMonitor : public rclcpp::Node { public: DistanceMonitor():Node("distance_monitor_cpp"){ sub_=create_subscription<std_msgs::msg::Float32>("/turtle_distance",10,[this](const auto m){RCLCPP_INFO(get_logger(),"distance=%.3f",m->data);}); RCLCPP_INFO(get_logger(),"distance C++ monitor started"); } private:rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr sub_;};
int main(int argc,char** argv){rclcpp::init(argc,argv);rclcpp::spin(std::make_shared<DistanceMonitor>());rclcpp::shutdown();}
