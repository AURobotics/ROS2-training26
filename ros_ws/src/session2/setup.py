from setuptools import find_packages, setup
from glob import glob

package_name = 'session2'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='abdelaziz',
    maintainer_email='abdelaziz.islam.galal@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'service_server = session2.service_server:main',
            'service_client = session2.service_client:main',
            'action_server = session2.action_server:main',
            'action_client = session2.action_client:main',
            'general_node = session2.general_node:main',
        ],
    },
)
