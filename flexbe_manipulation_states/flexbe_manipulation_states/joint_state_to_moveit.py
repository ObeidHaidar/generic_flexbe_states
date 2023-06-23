#!/usr/bin/env python3

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
State to send a joint state configuration to MoveIt to plan and move.

Created on 10.10.2016

@author: Alberto Romay
"""


from flexbe_core import EventState, Logger

from flexbe_core.proxy import ProxyActionClient

from moveit_msgs.action._move_group import MoveGroup, MoveGroup_Goal
from moveit_msgs.msg import Constraints, JointConstraint, MoveItErrorCodes


class JointStateToMoveit(EventState):
    """
    State to send a joint state configuration to MoveIt to plan and move.

    ># config_name        string        Name of the joint configuration of interest.

    ># move_group         string        Name of the move group to be used for planning.

    ># action_topic     string        Topic on which MoveIt is listening for action calls.

    ># robot_name         string        Optional name of the robot to be used.
                                If left empty, the first one found will be used
                                (only required if multiple robots are specified in the same file).

    ># joint_names        string[]        Names of the target joints.
                                    Same order as their corresponding names in joint_values.

    ># joint_values     float[]         Target configuration of the joints.
                                    Same order as their corresponding names in joint_names.

    <= reached                    Target joint configuration has been reached.
    <= planning_failed                Failed to find a plan to the given joint configuration.
    <= control_failed                 Failed to move the arm along the planned trajectory.

    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__(input_keys=['config_name', 'move_group', 'robot_name',
                                     'action_topic', 'joint_values', 'joint_names'],
                         outcomes=['reached', 'planning_failed', 'control_failed'],
                         output_keys=['config_name', 'move_group', 'robot_name',
                                      'action_topic', 'joint_values', 'joint_names'])

        self._control_failed = False
        self._planning_failed = False
        self._success = False
        self._client = None
        self._config_name = None
        self._robot_name = None
        self._move_group = None
        self._action_topic = None
        self._joint_config = None
        self._joint_names = None

    def execute(self, userdata):  # pylint: disable=R0911
        """
        Execute this state
        """
        if self._planning_failed:
            return 'planning_failed'

        if self._control_failed:
            return 'control_failed'

        if self._success:
            return 'reached'

        if self._client.has_result(self._action_topic):
            result = self._client.get_result(self._action_topic)

            if result.error_code.val == MoveItErrorCodes.CONTROL_FAILED:
                Logger.logwarn(f'Control failed for move action of group: {self._move_group}'
                               f' (error code: {str(result.error_code)})')
                self._control_failed = True
                return 'control_failed'

            if result.error_code.val != MoveItErrorCodes.SUCCESS:
                Logger.logwarn(f'Move action failed with result error code: {str(result.error_code)}')
                self._planning_failed = True
                return 'planning_failed'

            self._success = True
            return 'reached'

        return None

    def on_enter(self, userdata):
        self._planning_failed = False
        self._control_failed = False
        self._success = False
        self._config_name = userdata.config_name    # Currently not used
        self._robot_name = userdata.robot_name    # Currently not used
        self._move_group = userdata.move_group
        self._action_topic = userdata.action_topic
        self._joint_config = userdata.joint_values
        self._joint_names = userdata.joint_names

        self._client = ProxyActionClient({self._action_topic: MoveGroup})

        # Action Initialization
        action_goal = MoveGroup_Goal()
        action_goal.request.group_name = self._move_group
        action_goal.request.allowed_planning_time = 1.0
        goal_constraints = Constraints()
        for i, jnt_name in enumerate(self._joint_names):
            goal_constraints.joint_constraints.append(JointConstraint(
                                                          joint_name=jnt_name,
                                                          position=self._joint_config[i],
                                                          weight=1.0))
        action_goal.request.goal_constraints.append(goal_constraints)

        try:
            self._client.send_goal(self._action_topic, action_goal)
            userdata.action_topic = self._action_topic    # Save action topic to output key
        except Exception as exc:  # pylint: disable=W0703
            Logger.logwarn(f"Failed to send action goal for group: {self._move_group}\n  {str(exc)}")
            self._planning_failed = True

    def on_stop(self):
        try:
            if self._client.is_available(self._action_topic) and not self._client.has_result(self._action_topic):
                self._client.cancel(self._action_topic)
        except Exception:  # pylint: disable=W0703
            # client already closed
            pass

    def on_pause(self):
        self._client.cancel(self._action_topic)

    def on_resume(self, userdata):
        self.on_enter(userdata)
