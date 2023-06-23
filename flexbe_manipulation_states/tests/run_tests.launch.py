# Copyright 2023 Philipp Schillinger,  Christopher Newport University
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#    * Neither the name of the Philipp Schillinger,  Christopher Newport University nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


"""
flexbe_manipulation_states test launch
"""
from os.path import join

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    """
    Generate launch description for tests
    """
    flexbe_testing_dir = get_package_share_directory('flexbe_testing')
    flexbe_states_test_dir = get_package_share_directory('flexbe_manipulation_states')

    path = join(flexbe_states_test_dir, "tests")

    testcases = ""
    testcases += join(path, "get_joints_from_srdf_group_import.test\n")
    testcases += join(path, "get_joint_values_import.test\n")
    testcases += join(path, "moveit_to_joints_import.test\n")
    testcases += join(path, "srdf_state_to_moveit_import.test\n")
    testcases += join(path, "get_joints_from_srdf_import.test\n")
    testcases += join(path, "joint_state_to_moveit_import.test\n")
    testcases += join(path, "get_joint_values_dyn_import.test\n")
    testcases += join(path, "moveit_to_joints_dyn_import.test\n")
    testcases += join(path, "srdf_state_to_moveit_execute_trajectory_import.test\n")

    return LaunchDescription([
        DeclareLaunchArgument("pkg", default_value="flexbe_manipulation_states"),
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
