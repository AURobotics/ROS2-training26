import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

PACKAGE_NAME = 'workshop2'


def generate_launch_description():
    # Path to the YAML parameter file installed alongside this package.
    # Assumes go_to_goal_params.yaml is installed under:
    #   <install>/share/<PACKAGE_NAME>/config/go_to_goal_params.yaml
    # (i.e. it's listed in setup.py's data_files under a 'config' folder).
    params_file = os.path.join(
        get_package_share_directory(PACKAGE_NAME),
        'config',
        'go_to_goal_params.yaml',
    )

    turtlesim_node = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='turtlesim_node',
        output='screen',
    )

    go_to_goal_node = Node(
        package=PACKAGE_NAME,
        executable='go_to_goal',
        name='go_to_goal',
        output='screen',
        parameters=[params_file],
    )

    go_to_goal_client_node = Node(
        package=PACKAGE_NAME,
        executable='go_to_goal_client',
        name='go_to_goal_client',
        output='screen',
        parameters=[{'delay_sec': 5.0}] # optional
    )

    return LaunchDescription([
        turtlesim_node,
        go_to_goal_node,
        go_to_goal_client_node,
    ])