# schedulelist.py

from draftsman.classes.schedule import Schedule

from typing import MutableSequence


class ScheduleList(MutableSequence):
    def __init__(self, initlist=None):
        self.data = initlist or []

    def insert(self, index, schedule):
        if not isinstance(schedule, Schedule):
            raise TypeError("'schedule' must be an instance of <Schedule>")

        self.data.insert(index, schedule)

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, item):
        self.data[index] = item

    def __delitem__(self, index):
        del self.data[index]

    def __len__(self):
        return len(self.data)

    # def __deepcopy__(self, memo):
    #     pass
