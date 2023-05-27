# test_schedule_list.py

from draftsman.classes.association import Association
from draftsman.classes.schedule import Schedule
from draftsman.classes.schedule_list import ScheduleList
from draftsman.prototypes.locomotive import Locomotive

import pytest


class TestScheduleList:
    def test_insert(self):
        sl = ScheduleList()
        with pytest.raises(
            TypeError, match="Entry in <ScheduleList> must be an instance of <Schedule>"
        ):
            sl.insert(0, TypeError)

    def test_getitem(self):
        pass  # TODO

    def test_setitem(self):
        sl = ScheduleList()
        sl.append(Schedule())
        assert len(sl) == 1

        sl[0] = Schedule()
        assert len(sl) == 1

        with pytest.raises(
            TypeError, match="Entry in <ScheduleList> must be an instance of <Schedule>"
        ):
            sl[0] = TypeError

    def test_delitem(self):
        sl = ScheduleList()
        sl.append(Schedule())
        assert len(sl) == 1

        del sl[0]
        assert len(sl) == 0
        assert sl.data == []

    def test_equals(self):
        # Not equivalent type
        a = ScheduleList()
        assert a != TypeError

        # Not equivalent length
        b = ScheduleList([Schedule()])
        assert a != b

        some_train = Locomotive()

        # Component difference
        a = ScheduleList([Schedule(locomotives=[Association(some_train)])])
        assert a != b

        # True equality
        b = ScheduleList([Schedule(locomotives=[Association(some_train)])])
        assert a == b

    def test_repr(self):
        sl = ScheduleList()
        assert repr(sl) == "<ScheduleList>[]"
