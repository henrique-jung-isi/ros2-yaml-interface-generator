#include <rclcpp/rclcpp.hpp>
#include <string>

class RosExampleNode : public rclcpp::Node {
public:
  RosExampleNode(const std::string &name)
      : rclcpp::Node(
            name, rclcpp::NodeOptions()
                      .automatically_declare_parameters_from_overrides(true)) {
    auto parameters_list =
        this->list_parameters({}, 10); // 10 is config deep level

    // update parameter map
    for (const auto &name : parameters_list.names) {
      auto param = this->get_parameter(name);
      RCLCPP_INFO(this->get_logger(), "[%s] = %s", name.c_str(),
                  param.value_to_string().c_str());
    }
  }

private:
};

int main(int argc, char *argv[]) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<RosExampleNode>("ros_example_node"));
  rclcpp::shutdown();
  return 0;
}