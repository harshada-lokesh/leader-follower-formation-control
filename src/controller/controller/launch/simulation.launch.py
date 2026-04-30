import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Get the Gazebo ROS package directory
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    
    # 2. Define the path to your custom models
    # This automatically finds your home directory regardless of the computer username
    home_dir = os.path.expanduser('~')
    
    # Pointing to the workspace where you have your marker0 and modified burger
    custom_model_path = os.path.join(home_dir, 'turtlebot3_ws', 'src')
    
    # 3. Set the GAZEBO_MODEL_PATH so Gazebo can find marker0 and the burger model
    # This acts like your manual 'export GAZEBO_MODEL_PATH' command
    set_gazebo_model_path = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=[os.environ.get('GAZEBO_MODEL_PATH', ''), ':', custom_model_path]
    )

    # 4. Include the standard Gazebo launch file
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        )
    )

    # 5. Spawn Leader (The modified Burger robot with the ArUco marker)
    # This uses the SDF file you moved to your turtlebot3_ws/src/ folder
    spawn_leader = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-file', os.path.join(custom_model_path, 'turtlebot3_burger', 'model.sdf'),
            '-entity', 'leader',
            '-robot_namespace', 'leader',
            '-x', '0.0', '-y', '0.0', '-z', '0.1'
        ],
        output='screen'
    )

    # 6. Spawn Follower (Waffle Pi - using the standard system path)
    spawn_follower = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-file', '/opt/ros/humble/share/turtlebot3_gazebo/models/turtlebot3_waffle_pi/model.sdf',
            '-entity', 'follower',
            '-robot_namespace', 'follower',
            '-x', '-1.5', '-y', '0.0', '-z', '0.1'
        ],
        output='screen'
    )

    return LaunchDescription([
        set_gazebo_model_path,
        gazebo,
        spawn_leader,
        spawn_follower
    ])
