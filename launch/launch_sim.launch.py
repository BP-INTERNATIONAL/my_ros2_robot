import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node


def generate_launch_description():
    package_name = 'my_ros2_robot'

    package_share = get_package_share_directory(package_name)

    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(package_share, 'launch', 'rsp.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items()
    )

    xacro_file = os.path.join(
        package_share,
        'description',
        'robot.urdf.xacro'
    )
    robot_description = Command(['xacro ', xacro_file])

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-string', robot_description,
            '-name', 'my_ros2_robot',
            '-z', '0.15'
        ],
        output='screen'
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry'
        ],
        output='screen'
    )

    return LaunchDescription([
        rsp,
        gazebo,
        spawn_entity,
        bridge
    ])