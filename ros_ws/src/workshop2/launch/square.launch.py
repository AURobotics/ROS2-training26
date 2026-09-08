"""
CANCELLED TASK
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    square_params = os.path.join(
        get_package_share_directory('workshop2'),
        'config',
        'square_params.yaml',
    )

    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim_node',
            output='screen',
        ),
        Node(
            package='workshop2',
            executable='go_to_pose_action_server',
            name='go_to_pose_action_server',
            output='screen',
        ),
        Node(
            package='workshop2',
            executable='square_client',
            name='square_client',
            output='screen',
            parameters=[square_params],
        ),
    ])
