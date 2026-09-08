cmake_minimum_required(VERSION 3.12...3.40)
project(turtle_interfaces)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(turtlesim REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "action/GoToPose.action"
  "srv/SetTarget.srv"
  DEPENDENCIES turtlesim
)

ament_export_dependencies(rosidl_default_runtime turtlesim)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()