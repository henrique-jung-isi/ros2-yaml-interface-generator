#include <rclcpp/rclcpp.hpp>
#include <ros_example/ros_example_node.hpp>
#include <string>
class RosExampleNode : public rclcpp::Node {
public:
  RosExampleNode(const std::string &name)
      : rclcpp::Node(
            name, rclcpp::NodeOptions()
                      .automatically_declare_parameters_from_overrides(true)),
        _frontConfig{this} {
    auto parameters_list =
        this->list_parameters({}, 10); // 10 is config deep level

    // update parameter map
    std::stringstream ss;
    for (const auto &name : parameters_list.names) {
      auto param = this->get_parameter(name);
      ss << "[" << name << "] = " << param << std::endl;
    }
    RCLCPP_INFO(this->get_logger(), "From get_parameter: \n%s",
                ss.str().c_str());
    RCLCPP_INFO(this->get_logger(), "From generator: \n%s",
                _frontConfig.toString().c_str());
  }

private:
  ros_example_node::front _frontConfig;
};

int main(int argc, char *argv[]) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<RosExampleNode>("ros_example_node"));
  rclcpp::shutdown();
  return 0;
}