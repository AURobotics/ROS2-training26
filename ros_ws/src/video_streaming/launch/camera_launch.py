# road_detector_launch.py
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='video_streaming',
            executable='external_camera_node',
            name='camera1',
            parameters=[{
                'device_index': 2,
                'publish_rate': 15.0,
                'topic': '/camera1/image_raw',
                'frame_id': 'camera',
            }],
            output='screen'
        ),
        Node(
                    package='video_streaming',
                    executable='external_camera_node',
                    name='camera2',
                    parameters=[{
                        'device_index': 4,
                        'publish_rate': 15.0,
                        'topic': '/camera2/image_raw',
                        'frame_id': 'camera',
                    }],
                    output='screen'
                ),
                Node(
                            package='video_streaming',
                            executable='external_camera_node',
                            name='camera3',
                            parameters=[{
                                'device_index': 6,
                                'publish_rate': 15.0,
                                'topic': '/camera3/image_raw',
                                'frame_id': 'camera',
                            }],
                            output='screen'
                        ),
    ])