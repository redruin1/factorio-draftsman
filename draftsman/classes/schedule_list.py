# schedulelist.py

from draftsman.classes.schedule import Schedule
from draftsman.error import DataFormatError

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from typing import Any, MutableSequence


class ScheduleList(MutableSequence):
    """
    TODO
    """

    def __init__(self, initlist=None):
        """
        TODO
        """
        self.data = []
        if initlist is not None:
            if not isinstance(initlist, list):
                raise TypeError("'initlist' must be either a list or None")
            for elem in initlist:
                if isinstance(elem, Schedule):
                    self.append(elem)
                elif isinstance(elem, dict):
                    self.append(Schedule(**elem))
                else:
                    raise DataFormatError(
                        "ScheduleList only accepts Schedule or dict entries"
                    )

    def insert(self, index, schedule):
        """
        TODO
        """
        if not isinstance(schedule, Schedule):
            raise TypeError("Entry in <ScheduleList> must be an instance of <Schedule>")

        self.data.insert(index, schedule)

    def __getitem__(self, index: int) -> Schedule:
        return self.data[index]

    def __setitem__(self, index: int, item: Schedule):
        if isinstance(item, MutableSequence):
            for i in range(len(item)):
                if not isinstance(item[i], Schedule):
                    raise TypeError(
                        "Entry in <ScheduleList> must be an instance of <Schedule>"
                    )
        else:
            if not isinstance(item, Schedule):
                raise TypeError(
                    "Entry in <ScheduleList> must be an instance of <Schedule>"
                )

        self.data[index] = item

    def __delitem__(self, index: int):
        del self.data[index]

    def __len__(self) -> int:
        return len(self.data)

    def __eq__(self, other: "ScheduleList") -> bool:
        if not isinstance(other, ScheduleList):
            return False
        if len(self.data) != len(other.data):
            return False
        for i in range(len(self.data)):
            if self.data[i] != other.data[i]:
                return False
        return True

    def __repr__(self) -> str:
        return "<ScheduleList>{}".format(repr(self.data))

    # def __deepcopy__(self, memo):
    #     pass # TODO, I think

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls, handler(list[Schedule.Format])
        )  # pragma: no coverage
