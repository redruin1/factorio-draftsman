# schedule.py

from draftsman.classes.association import Association
from draftsman.prototypes.locomotive import Locomotive
from draftsman.constants import Ticks, WaitConditionType, WaitConditionCompareType
from draftsman.signatures import SIGNAL_ID_OR_NONE, COMPARATOR, SIGNAL_ID_OR_CONSTANT

import json
from typing import Union

# TODO: make dataclass?
class WaitCondition(object):
    """
    An object that represents a particular criteria to wait for when a train is
    stopped at a station. Multiple :py:class:`WaitCondition` objects can (and
    typically are) combined into a :py:class:`WaitConditions` object, which is
    a list of conditions conjoined by a set of boolean ``AND`` or ``OR`` 
    operations.

    To make specifying :py:class:`WaitConditions` objects easier, they can be
    created as a set of :py:class:`WaitCondition` objects combined with the 
    bitwise and (``&``) and or (``|``) operators:

    .. example: python

        from draftsman.classes.schedule import WaitCondition
        from draftsman.constants import Ticks, WaitConditionType
    
        cargo_full = WaitCondition(WaitConditionType.CARGO_FULL)
        inactivity = WaitCondition(WaitConditionType.INACTIVITY, ticks=1 * Ticks.MINUTE)
        run_signal = WaitCondition(WaitConditionType.CIRCUIT_SIGNAL, condition=("signal-R", "=", 1))

        # (If the cargo is full and been inactive for 1 minute) or signal sent
        conditions = cargo_full & inactivity | run_signal
        assert isinstance(conditions, WaitConditions)
    """
    def __init__(self, type, compare_type=WaitConditionCompareType.OR, ticks=None, condition=None):
        # type: (WaitConditionType, WaitConditionCompareType, int, list) -> None
        """
        Constructs a new :py:class:`WaitCondition` object.

        :param type: A ``str`` value equivalent to one of the members of 
            :py:class:`WaitConditionType`.
        :param compare_type: A ``str`` value equivalent to one of the members of
            :py:class:`WaitConditionCompareType`.
        :param ticks: The number of in-game ticks to wait for on conditions of 
            type ``TIME_PASSED`` and ``INACTIVITY``.
        :param condition: The condition to use for conditions of type 
            ``ITEM_COUNT``, ``FLUID_COUNT``, and ``CIRCUIT_CONDITION``. 
            Specified as a sequence of the format 
            ``(first_signal, comparator, second_signal_or_constant)``.
        """
        self.type = type
        self.compare_type = compare_type
        if type == WaitConditionType.TIME_PASSED and ticks is None:
            self.ticks = 30 * Ticks.SECOND
        elif type == WaitConditionType.INACTIVITY and ticks is None:
            self.ticks = 5 * Ticks.SECOND
        else:
            self.ticks = ticks
        self.condition = condition

    def to_dict(self) -> dict:
        result = {"type": self.type, "compare_type": self.compare_type}
        if self.ticks: result["ticks"] = self.ticks
        if self.condition: 
            result["condition"] = {
                "first_signal": SIGNAL_ID_OR_NONE.validate(self.condition[0]),
                "comparator": COMPARATOR.validate(self.condition[1])
            }
            b = SIGNAL_ID_OR_CONSTANT.validate(self.condition[2])
            if isinstance(b, int):
                result["condition"]["constant"] = b
            else:
                result["condition"]["second_signal"] = b
            
        return result
    
    # =========================================================================

    def __and__(self, other):
        # type: (Union[WaitCondition, WaitConditions]) -> WaitConditions
        if isinstance(other, WaitCondition):
            other.compare_type = "and"
            return WaitConditions([self, other])
        elif isinstance(other, WaitConditions):
            other._conditions[0].compare_type = "and"
            return WaitConditions([self] + other._conditions)
        else:
            raise ValueError("Can only perform this operation on 'WaitCondition' or 'WaitConditions' objects")
    
    def __rand__(self, other):
        # type: (Union[WaitCondition, WaitConditions]) -> WaitConditions
        if isinstance(other, WaitCondition):
            self.compare_type = "and"
            return WaitConditions([other, self])
        elif isinstance(other, WaitConditions):
            self.compare_type = "and"
            return WaitConditions(other._conditions + [self])
        else:
            raise ValueError("Can only perform this operation on 'WaitCondition' or 'WaitConditions' objects")

    def __or__(self, other):
        # type: (Union[WaitCondition, WaitConditions]) -> WaitConditions
        if isinstance(other, WaitCondition):
            other.compare_type = "or"
            return WaitConditions([self, other])
        elif isinstance(other, WaitConditions):
            other._conditions[0].compare_type = "or"
            return WaitConditions([self] + other._conditions)
        else:
            raise ValueError("Can only perform this operation on 'WaitCondition' or 'WaitConditions' objects")
    
    def __ror__(self, other):
        # type: (Union[WaitCondition, WaitConditions]) -> WaitConditions
        if isinstance(other, WaitCondition):
            self.compare_type = "or"
            return WaitConditions([other, self])
        elif isinstance(other, WaitConditions):
            self.compare_type = "or"
            return WaitConditions(other._conditions + [self])
        else:
            raise ValueError("Can only perform this operation on 'WaitCondition' or 'WaitConditions' objects")

    def __repr__(self) -> str:
        if self.type == WaitConditionType.TIME_PASSED:
            optional = ", ticks='{}'".format(self.ticks)
        elif self.type in {WaitConditionType.ITEM_COUNT, WaitConditionType.FLUID_COUNT, WaitConditionType.CIRCUIT_CONDITION}:
            optional = ", condition={}".format(self.condition)
        else:
            optional = ""
        return "<WaitCondition>(type='{}', compare_type='{}'{})".format(self.type, self.compare_type, optional)


class WaitConditions(object):
    """
    A list of :py:class:`WaitCondition` objects.
    """
    def __init__(self, conditions: list[WaitCondition]) -> None:
        self._conditions: list[WaitCondition] = conditions

    def to_dict(self) -> list:
        return [condition.to_dict() for condition in self._conditions]

    def __repr__(self) -> str:
        return "<WaitConditions>{}".format(repr(self._conditions))


class Schedule(object):
    """
    An object representing a particular train schedule. Schedules contain 
    :py:class:`Association`s to the Locomotives that inherit them, as well as 
    the order of stops and their conditions.
    """

    def __init__(self):
        self._locomotives: list[Association] = []
        self._stops: list[dict] = []

    # =========================================================================

    @property
    def locomotives(self):
        # type: () -> list[Association]
        """
        The list of :py:class:`Association`s to each :py:class:`Locomotive` that
        uses this particular ``Schedule``. Read only; use 
        :py:meth:`add_locomotive` or :py:meth:`remove_locomotive` to change this
        list.
        """
        return self._locomotives

    @property
    def stops(self):
        # type: () -> list[dict]
        """
        A list of dictionaries of the format:

        .. code-block: python

            [
                {
                    "station": str, # The name of the station
                    "wait_conditions": WaitConditions, # A WaitConditions object
                },
                ...
            ]

        Read only; use :py:meth:`append_stop`, :py:meth:`insert_stop`, or 
        :py:meth:`remove_stop` to modify this value.

        :returns: A ``list`` of ``dict``s in the format specified above.
        """
        return self._stops
    
    # =========================================================================

    def add_locomotive(self, locomotive):
        # type: (Locomotive) -> None
        """
        Adds a locomotive to the set of locomotives associated with this 
        schedule.

        :param locomotive: The locomotive in a particular Blueprint or Group to
            assign this schedule to.

        :raises TypeError: If ``locomotive`` is not an instance of 
            :py:class:`Locomotive`.
        """
        if not isinstance(locomotive, Locomotive):
            raise TypeError("'locomotive' must be an instance of <Locomotive>")

        if locomotive not in self._locomotives:
            self._locomotives.append(Association(locomotive))

    def remove_locomotive(self, locomotive):
        # type: (Locomotive) -> None
        """
        Removes a locomotive from the set of locomotives assicated with this 
        schedule.

        :param locomotive: The locomotive in a particular Blueprint or Group to
            remove this schedule from.

        :raises ValueError: If the specified locomotive doesn't currently exist
            in this schedule's locomotives.
        """
        self._locomotives.remove(Association(locomotive))

    def append_stop(self, name, wait_conditions=None):
        # type: (str, list[dict]) -> None
        """
        Adds a stop to the end of the list of stations.

        :param name: The name of the station to add.
        :param wait_conditions: Either a :py:class:`WaitCondition` or a 
            :py:class:`WaitConditions` object of the station to add.
        """
        self.insert_stop(len(self.stops), name, wait_conditions)

    def insert_stop(self, index, name, wait_conditions=None):
        # type: (int, str, list[dict]) -> None
        """
        Inserts a stop at ``index`` into the list of stations.
        
        :param index: The index at which to insert the stop in the list.
        :param name: The name of the station to add.
        :param wait_conditions: Either a :py:class:`WaitCondition` or a 
            :py:class:`WaitConditions` object of the station to add.
        
        :raises IndexError: If ``index`` is outside the valid range of this 
            schedule's stops.
        """
        if wait_conditions is None:
            wait_conditions = WaitConditions([])
        if isinstance(wait_conditions, list):
            wait_conditions = WaitConditions(wait_conditions)
        if isinstance(wait_conditions, WaitCondition):
            wait_conditions = WaitConditions([wait_conditions])
        
        self._stops.insert(index, {"station": name, "wait_conditions": wait_conditions})

    def remove_stop(self, name, wait_conditions=None):
        """
        Removes a stop with a particular ``name`` and ``wait_conditions``. If 
        ``wait_conditions`` is not specified, the first stop with a matching
        name is removed. Otherwise, both ``name`` and ``wait_conditions`` have
        to strictly match in order for the stop to be removed.

        :param name: The name of station to remove reference to. Case-sensitive.
        :param wait_conditions: Either a :py:class:`WaitCondition` or a 
            :py:class:`WaitConditions` object of the station to remove.

        :raises ValueError: If unable to find any stop matching the specified 
            criteria in this :py:class:`Schedule`.
        """
        if wait_conditions is None:
            for i, stop in enumerate(self._stops):
                if stop["name"] == name:
                    self._stops.pop(i)
                    return
            raise ValueError("No station with name '{}' found in schedule".format(name))
        else:
            self._stops.remove({"station": name, "wait_conditions": wait_conditions})

    def to_dict(self):
        # type: () -> dict
        """
        Converts this Schedule into it's JSON dict form.

        .. NOTE:

            Not directly JSON serializable; returns :py:class:`Association`s 
            which are usually converted in a parent method.

        :returns: A ``dict`` representation of this schedule.
        """
        stop_list = []
        for stop in self._stops:
            stop_list.append(
                {
                    "station": stop["station"], 
                    "wait_conditions": stop["wait_conditions"].to_dict()
                }
            )
        return {
            "locomotives": list(self._locomotives), 
            "schedule": stop_list
        }
    
    # def __repr__(self) -> str:
    #     pass # TODO
