from setuptools import find_packages, setup
from glob import glob

package_name = 'workshop2'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='abdelaziz',
    maintainer_email='abdelaziz.islam.galal@gmail.com',
    description=(
        'Workshop 2: GoToPose action server/client, parameterized square '
        'trajectory client, launch integration, and a SetBool serial service.'
    ),
    license='Apache-2.0',
    extras_require={
            'test': [
                'pytest',
            ],
        },
    entry_points={
        'console_scripts': [
            'go_to_pose_action_server = workshop2.go_to_pose_action_server:main',
            'go_to_pose_action_client = workshop2.go_to_pose_action_client:main',
            'go_to_goal = workshop2.go_to_goal:main',
            'go_to_goal_client = workshop2.go_to_goal_client:main',
            'go_to_goal_bonus = workshop2.go_to_goal_bonus:main',
            'go_to_goal_client_bonus = workshop2.go_to_goal_client_bonus:main',
            'square_client = workshop2.square_client:main',
            'serial_read = workshop2.serial_read:main',
            'mock_sensor_source = workshop2.mock_sensor_source:main',
        ],
    },
)
