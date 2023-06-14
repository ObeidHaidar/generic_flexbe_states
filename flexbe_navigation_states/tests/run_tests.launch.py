from os.path import join

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch_ros.parameter_descriptions import ParameterValue
def generate_launch_description():

    flexbe_testing_dir = get_package_share_directory('flexbe_testing')
    flex_nav_states_test_dir = get_package_share_directory('flexbe_navigation_states')

    path = join(flex_nav_states_test_dir, "tests")

    testcases = ""
    testcases += join(path, "move_base_state_import.test") + "\n"

    return LaunchDescription([
        DeclareLaunchArgument("pkg", default_value="flexbe_navigation_states"), #flexbe_testing"),
        DeclareLaunchArgument("testcases", default_value=testcases),
        DeclareLaunchArgument("compact_format", default_value='true'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(join(flexbe_testing_dir, "launch", "flexbe_testing.launch.py")),
            launch_arguments={
                'package': LaunchConfiguration("pkg"),
                'compact_format': LaunchConfiguration("compact_format"),
                'testcases': LaunchConfiguration("testcases"),
            }.items()
        )
    ])
