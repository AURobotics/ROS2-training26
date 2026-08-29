import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Find the path to the installed YAML file
    pkg_share = get_package_share_directory('session2')
    param_file = os.path.join(pkg_share, 'config', 'params.yaml')

    # Define the node execution
    demo_node = Node(
        package='session2',
        executable='general_node',
        name='general_node',
        output='screen',
        parameters=[param_file]
    )

    return LaunchDescription([
        demo_node
    ])