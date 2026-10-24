# road_detector_launch.py
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='video_streaming',
            executable='viewer_node',
            name='viewer1',
            parameters=[{
                'topic': '/camera1/image_raw',
            }],
            output='screen'
        ),
        Node(
                    package='video_streaming',
                    executable='viewer_node',
                    name='viewer2',
                    parameters=[{
                        'topic': '/camera2/image_raw',
                    }],
                    output='screen'
                ),
                Node(
                            package='video_streaming',
                            executable='viewer_node',
                            name='viewer3',
                            parameters=[{
                                'topic': '/camera3/image_raw',
                            }],
                            output='screen'
                        ),
    ])