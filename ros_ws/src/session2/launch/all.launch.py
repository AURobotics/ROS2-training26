import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    # Path to parameter file
    pkg_share = get_package_share_directory('session2')

    # 1. general_node launch file
    general_node_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'general_node.launch.py')
        )
    )

    # 2. Service Server Node
    service_server_node = Node(
        package='session2',
        executable='service_server',
        name='service_server',
        output='screen'
    )

    # 3. Service Client Node
    service_client_node = Node(
        package='session2',
        executable='service_client',
        name='service_client',
        output='screen'
    )

    # 4. Action Server Node
    action_server_node = Node(
        package='session2',
        executable='action_server',
        name='action_server',
        output='screen'
    )

    # 5. Action Client Node
    action_client_node = Node(
        package='session2',
        executable='action_client',
        name='action_client',
        output='screen'
    )

    return LaunchDescription([
        general_node_launch,
        service_server_node,
        service_client_node,
        action_server_node,
        action_client_node
    ])