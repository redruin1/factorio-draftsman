# rail.py

"""
Imports a bunch of helper classes for placing rails and train stations, as well
as trains and their schedules.
"""

# from draftsman.classes.rail_planner import RailPlanner
from draftsman.classes.schedule import (
    Schedule,
    WaitCondition,
    WaitConditions,
    WaitConditionType,
)  # TODO: probably makes sense to move this to it's own file, so we can reuse it for space platform schedules/interrupts
from draftsman.classes.schedule_list import ScheduleList
from draftsman.classes.train_configuration import TrainConfiguration

__all__ = [
    "Schedule",
    "WaitCondition",
    "WaitConditions",
    "WaitConditionType",
    "ScheduleList",
    "TrainConfiguration",
]
