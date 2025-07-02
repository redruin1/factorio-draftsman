# schedule.py

from draftsman.classes.association import Association
from draftsman.classes.exportable import (
    Exportable,
)
from draftsman.constants import (
    Ticks,
    WaitConditionType,
)
from draftsman.prototypes.locomotive import Locomotive
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    Condition,
    uint32,
)
from draftsman.validators import instance_of, one_of, try_convert

from draftsman.data import mods

import attrs
import copy
from typing import Literal, Optional, Union


# TODO: Right now, everything is just lumped into one WaitCondition class, which means
# that it's possible to (incorrectly) specify conditions into train schedules/
# space platform schedules that do not belong there
# Perhaps ideally, it would be better to have two separate categories, one for
# train and one for space platform schedules as what conditions can be inserted
# into each are similar but distinct


@attrs.define
class WaitCondition(Exportable):
    """
    An object that represents a particular criteria to wait for when a train is
    stopped at a station. Multiple :py:class:`WaitCondition` objects can (and
    typically are) combined into a :py:class:`WaitConditions` object, which is
    a list of conditions conjoined by a set of boolean ``AND`` or ``OR``
    operations.

    To make specifying :py:class:`WaitConditions` objects easier, they can be
    created with a set of :py:class:`WaitCondition` objects combined with the
    bitwise and (``&``) and or (``|``) operators:

    .. example: python

        from draftsman.classes.schedule import WaitCondition
        from draftsman.constants import Ticks, WaitConditionType

        cargo_full = WaitCondition(WaitConditionType.CARGO_FULL)
        inactivity = WaitCondition(WaitConditionType.INACTIVITY, ticks=1 * Ticks.MINUTE)
        run_signal = WaitCondition(WaitConditionType.CIRCUIT_SIGNAL, condition=("signal-R", "=", 1))

        # (If the cargo is full and inactive for 1 minute) or signal sent
        conditions = cargo_full & inactivity | run_signal
        assert isinstance(conditions, WaitConditions)
    """

    type: WaitConditionType = attrs.field(
        converter=try_convert(WaitConditionType),
        validator=instance_of(WaitConditionType),
    )
    """
    Type of this particular wait condition. All wait condition types consider
    :py:attr:`.compare_type` during evaluation, but certain other types may opt-
    in to the other attributes defined on this class.
    """

    # =========================================================================

    compare_type: Literal["or", "and"] = attrs.field(validator=one_of("or", "and"))
    """
    Manner in which to compare this wait condition with the condition directly
    preceding it.
    """

    @compare_type.default
    def _(self):
        # In Factorio 1.0, the default compare type was "or"; in 2.0 it's "and"
        if mods.versions["base"] < (2, 0):  # pragma: no coverage
            return "or"
        else:
            return "and"

    # =========================================================================

    station: Optional[str] = attrs.field(
        default="", validator=instance_of(Optional[str])
    )
    """
    A particular station name that this condition should consider. Used with:

    * :py:data:`WaitConditionType.AT_STATION`
    * :py:data:`WaitConditionType.NOT_AT_STATION`
    * :py:data:`WaitConditionType.SPECIFIC_DESTINATION_FULL`
    * :py:data:`WaitConditionType.SPECIFIC_DESTINATION_NOT_FULL`

    If :py:attr:`.type` is not one of the above, then setting this attribute has
    no effect.
    """

    # =========================================================================

    ticks: Optional[uint32] = attrs.field(validator=instance_of(Optional[uint32]))
    """
    An amount of time, specified in a count of game ticks. Used with:

    * :py:data:`WaitConditionType.INACTIVITY`
    * :py:data:`WaitConditionType.TIME_PASSED`

    If :py:attr:`.type` is not one of the above, then setting this attribute has
    no effect.
    """

    @ticks.default
    def _(self):
        if self.type is WaitConditionType.TIME_PASSED:
            return 30 * Ticks.SECOND
        elif self.type is WaitConditionType.INACTIVITY:
            return 5 * Ticks.SECOND
        else:
            return None

    # =========================================================================

    condition: Optional[Condition] = attrs.field(
        converter=Condition.converter,
        validator=instance_of(Optional[Condition]),
    )
    """
    Circuit condition to use. Used by:

    * :py:data:`WaitConditionType.CIRCUIT_CONDITION`
    * :py:data:`WaitConditionType.FUEL_COUNT_ALL`
    * :py:data:`WaitConditionType.FUEL_COUNT_ANY`
    * :py:data:`WaitConditionType.FLUID_COUNT`
    * :py:data:`WaitConditionType.ITEM_COUNT`
    * :py:data:`WaitConditionType.REQUEST_SATISFIED`
    * :py:data:`WaitConditionType.REQUEST_NOT_SATISFIED`

    If :py:attr:`.type` is not one of the above, then setting this attribute has
    no effect.
    """

    @condition.default
    def _(self):
        if self.type in {
            WaitConditionType.CIRCUIT_CONDITION,
            WaitConditionType.FUEL_COUNT_ALL,
            WaitConditionType.FUEL_COUNT_ANY,
            WaitConditionType.FLUID_COUNT,
            WaitConditionType.ITEM_COUNT,
            WaitConditionType.REQUEST_SATISFIED,
            WaitConditionType.REQUEST_NOT_SATISFIED,
        }:
            return Condition()
        else:
            return None

    # =========================================================================

    def __and__(
        self, other: Union["WaitCondition", "WaitConditions"]
    ) -> "WaitConditions":
        self_copy = copy.deepcopy(self)
        other_copy = copy.deepcopy(other)
        if isinstance(other, WaitCondition):
            other_copy.compare_type = "and"
            return WaitConditions([self_copy, other_copy])
        elif isinstance(other, WaitConditions):
            other_copy._conditions[0].compare_type = "and"
            return WaitConditions([self_copy] + other_copy._conditions)
        else:
            return NotImplemented

    def __rand__(
        self, other: Union["WaitCondition", "WaitConditions"]
    ) -> "WaitConditions":
        self_copy = copy.deepcopy(self)
        other_copy = copy.deepcopy(other)
        if isinstance(other, WaitConditions):
            self_copy.compare_type = "and"
            return WaitConditions(other_copy._conditions + [self_copy])
        else:
            return NotImplemented

    def __or__(
        self, other: Union["WaitCondition", "WaitConditions"]
    ) -> "WaitConditions":
        self_copy = copy.deepcopy(self)
        other_copy = copy.deepcopy(other)
        if isinstance(other, WaitCondition):
            other_copy.compare_type = "or"
            return WaitConditions([self_copy, other_copy])
        elif isinstance(other, WaitConditions):
            other_copy._conditions[0].compare_type = "or"
            return WaitConditions([self_copy] + other_copy._conditions)
        else:
            return NotImplemented

    def __ror__(
        self, other: Union["WaitCondition", "WaitConditions"]
    ) -> "WaitConditions":
        self_copy = copy.deepcopy(self)
        other_copy = copy.deepcopy(other)
        if isinstance(other, WaitConditions):
            self_copy.compare_type = "or"
            return WaitConditions(other_copy._conditions + [self_copy])
        else:
            return NotImplemented


draftsman_converters.get_version((1, 0)).add_hook_fns(
    WaitCondition,
    lambda fields: {
        "type": fields.type.name,
        "compare_type": fields.compare_type.name,
        "ticks": fields.ticks.name,
        "condition": fields.condition.name,
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    WaitCondition,
    lambda fields: {
        "type": fields.type.name,
        "compare_type": fields.compare_type.name,
        "station": fields.station.name,
        "ticks": fields.ticks.name,
        "condition": fields.condition.name,
    },
)


class WaitConditions:
    """
    A list of :py:class:`WaitCondition` objects. Specifies custom operators for
    joining wait condition lists together with singular :py:class:`WaitCondition`
    objects, or other completed :py:class:`WaitConditions` lists.
    """

    def __init__(self, conditions: list[WaitCondition] = []) -> None:
        """
        TODO
        """
        for i, condition in enumerate(conditions):
            if not isinstance(condition, WaitCondition):
                conditions[i] = WaitCondition(**condition)

        self._conditions: list[WaitCondition] = conditions

    def __len__(self) -> int:
        return len(self._conditions)

    def __eq__(self, other) -> bool:
        if not isinstance(other, WaitConditions):
            return False
        if len(self._conditions) != len(other._conditions):
            return False
        for i in range(len(self._conditions)):
            if self._conditions[i] != other._conditions[i]:
                return False
        return True

    def __getitem__(self, index) -> WaitCondition:
        return self._conditions[index]

    def __repr__(self) -> str:
        return "<WaitConditions>{}".format(repr(self._conditions))


draftsman_converters.register_structure_hook(
    WaitConditions,
    lambda input_list, _: WaitConditions(
        [WaitCondition(**elem) for elem in input_list]
    ),
)


def wait_conditions_unstructure_factory(cls: type, converter):
    def unstructure_hook(inst):
        return [converter.unstructure(w) for w in inst._conditions]

    return unstructure_hook


draftsman_converters.register_unstructure_hook_factory(
    lambda cls: issubclass(cls, WaitConditions), wait_conditions_unstructure_factory
)


@attrs.define
class Schedule(Exportable):
    """
    An object representing a particular schedule, for both trains and space
    platforms. Schedules contain :py:class:`Association`s to the Locomotives/
    SpacePlatformHubs that inherit them, as well as a set of stops and
    interrupts.
    """

    @attrs.define
    class Stop(Exportable):
        station: str = attrs.field(validator=instance_of(str))
        """
        The name of the station or planet that this train or space platform
        should stop at.
        """
        wait_conditions: WaitConditions = attrs.field(
            factory=WaitConditions,
            converter=WaitConditions,
            validator=instance_of(WaitConditions),
        )
        """
        A list of :py:class:`.WaitCondition` objects to evaluate at this
        particular stop.
        """
        allows_unloading: Optional[bool] = attrs.field(
            default=True, validator=instance_of(Optional[bool])
        )
        """
        Whether or not this stop permits this space platform to fulfill any
        requests at the planet it's stopped above. Only applies to space
        platform schedules.
        """

    @attrs.define
    class Interrupt(Exportable):
        name: str = attrs.field(validator=instance_of(str))
        """
        The name of this particular interrupt.
        """
        conditions: WaitConditions = attrs.field(
            factory=WaitConditions,
            converter=WaitConditions,
            validator=instance_of(WaitConditions),
        )
        """
        The set of conditions that need to pass in order for this interrupt
        to be triggered.
        """
        targets: list["Schedule.Stop"] = attrs.field(
            factory=list,
            # TODO: converter
            validator=instance_of(list["Schedule.Stop"]),
        )
        """
        The target schedule that the interrupt should execute if it's 
        triggered.
        """
        inside_interrupt: bool = attrs.field(
            default=False,
        )
        """
        Whether or not this interrupt can be triggered midway through an 
        already executing interrupt.
        """

    # =========================================================================

    locomotives: list[Association] = attrs.field(
        factory=list,
        # TODO: convert given list of ints/entity instances to associations
        validator=instance_of(list),  # TODO: list[Association]
    )
    """
    The list of :py:class:`Association`s to each :py:class:`Locomotive` that
    uses this particular ``Schedule``.

    To avoid handling the associations yourself, you can instead use 
    :py:meth:`.add_locomotive` and :py:meth:`.remove_locomotive`.
    """

    # =========================================================================

    stops: list[Stop] = attrs.field(
        factory=list,
        validator=instance_of(list[Stop]),
    )
    """
    The list of all stops that this schedule uses.

    You can manually edit this value yourself, or you can use the helper methods
    :py:meth:`.append_stop`, :py:meth:`.insert_stop`, and :py:meth:`.insert_stop`.
    """

    # =========================================================================

    interrupts: list[Interrupt] = attrs.field(
        factory=list,
        validator=instance_of(list[Interrupt]),
    )
    """
    The list of all interrupts that apply to this schedule.

    You can manually edit this value yourself, or you can use the helper methods
    :py:meth:`.add_interrupt` and :py:meth:`.remove_interrupt`.
    """

    # =========================================================================

    def add_locomotive(self, locomotive: Locomotive):
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

        loco_association = Association(locomotive)
        if loco_association not in self.locomotives:
            self.locomotives.append(loco_association)

    def remove_locomotive(self, locomotive: Locomotive):
        """
        Removes a locomotive from the set of locomotives assicated with this
        schedule.

        :param locomotive: The locomotive in a particular Blueprint or Group to
            remove this schedule from.

        :raises ValueError: If the specified locomotive doesn't currently exist
            in this schedule's locomotives.
        """
        self.locomotives.remove(Association(locomotive))

    def append_stop(
        self, name: str, wait_conditions: Union[WaitCondition, WaitConditions] = None
    ):
        """
        Adds a stop to the end of the list of stations.

        :param name: The name of the station to add.
        :param wait_conditions: Either a :py:class:`WaitCondition` or a
            :py:class:`WaitConditions` object of the station to add.
        """
        self.insert_stop(len(self.stops), name, wait_conditions)

    def insert_stop(
        self,
        index: int,
        name: str,
        wait_conditions: Union[WaitCondition, WaitConditions] = None,
        allows_unloading: bool = True,
    ):
        """
        Inserts a stop at ``index`` into the list of stations.

        :param index: The index at which to insert the stop in the list.
        :param name: The name of the station to add.
        :param wait_conditions: Either a :py:class:`WaitCondition` or a
            :py:class:`WaitConditions` object of the station to add.
        :parma allows_unloading: Whether or not this space platform should
            satisfy logistic requests at this particular planet. Has no effect
            on train schedules.
        """
        if wait_conditions is None:
            wait_conditions = WaitConditions([])
        elif isinstance(wait_conditions, WaitCondition):
            wait_conditions = WaitConditions([wait_conditions])

        self.stops.insert(
            index,
            Schedule.Stop(
                station=name,
                wait_conditions=wait_conditions,
                allows_unloading=allows_unloading,
            ),
        )

    def remove_stop(
        self,
        name: str,
        wait_conditions: Union[WaitCondition, WaitConditions] = None,
    ):
        """
        Removes a stop with a particular ``name`` and ``wait_conditions``. If
        ``wait_conditions`` is not specified, the first stop from the beginning
        with a matching name is removed. Otherwise, both ``name`` and
        ``wait_conditions`` have to strictly match in order for the stop to be
        removed.

        :param name: The name of station to remove reference to. Case-sensitive.
        :param wait_conditions: Either a :py:class:`WaitCondition` or a
            :py:class:`WaitConditions` object of the station to remove.

        :raises ValueError: If unable to find any stop matching the specified
            criteria in this :py:class:`Schedule`.
        """
        if isinstance(wait_conditions, WaitCondition):
            wait_conditions = WaitConditions([wait_conditions])

        if wait_conditions is None:
            for i, stop in enumerate(self.stops):
                if stop.station == name:
                    self.stops.pop(i)
                    return
            msg = "No station with name '{}' found in schedule".format(name)
            raise ValueError(msg)
        else:
            for i, stop in enumerate(self.stops):
                if stop.station == name and stop.wait_conditions == wait_conditions:
                    self.stops.pop(i)
                    return
            msg = "No station with name '{}' and conditions '{}' found in schedule".format(
                name, wait_conditions
            )
            raise ValueError(msg)

    def add_interrupt(
        self,
        name: str,
        conditions: Union[WaitCondition, WaitConditions],
        targets: list[Stop],
        inside_interrupt: bool = False,
    ):
        """
        Adds a new interrupt to the end of the current list of interrupts on
        this schedule.

        :param name: The name of the interrupt to create.
        :param conditions: The conditions which trigger the interrupt. Not all
            wait condition types are permitted as interrupt conditions.
        :param targets: The "target" schedule to perform if this interrupt is
            triggered.
        :param inside_interrupt: Whether or not this interrupt can be triggered
            from the inside of an already executing interrupt.
        """
        if isinstance(conditions, WaitCondition):
            conditions = WaitConditions([conditions])

        self.interrupts.append(
            Schedule.Interrupt(
                name=name,
                conditions=conditions,
                targets=targets,
                inside_interrupt=inside_interrupt,
            )
        )

    def remove_interrupt(self, name):
        """
        Removes the first interrupt with name ``name``.

        :param name: The name of the interrupt to remove.
        :raises ValueError: If no interrupt with the name ``name`` currently
            exists in the schedule.
        """
        for i, interrupt in enumerate(self.interrupts):
            if interrupt.name == name:
                self.interrupts.pop(i)
                return
        msg = "No interrupt with name '{}' found in schedule".format(name)
        raise ValueError(msg)

    def __repr__(self) -> str:
        return "<Schedule>{}".format(self.to_dict())


draftsman_converters.get_version((1, 0)).add_hook_fns(
    Schedule.Stop,
    lambda fields: {
        "station": fields.station.name,
        "wait_conditions": fields.wait_conditions.name,
        None: fields.allows_unloading.name,
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    Schedule.Stop,
    lambda fields: {
        "station": fields.station.name,
        "wait_conditions": fields.wait_conditions.name,
        "allows_unloading": fields.allows_unloading.name,
    },
)

draftsman_converters.add_hook_fns(
    Schedule.Interrupt,
    lambda fields: {
        "name": fields.name.name,
        "conditions": fields.conditions.name,
        "targets": fields.targets.name,
        "inside_interrupt": fields.inside_interrupt.name,
    },
)

draftsman_converters.get_version((1, 0)).add_hook_fns(
    Schedule,
    lambda fields: {
        "locomotives": fields.locomotives.name,
        "schedule": fields.stops.name,
        None: fields.interrupts.name,
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    Schedule,
    lambda fields: {
        "locomotives": fields.locomotives.name,
        ("schedule", "records"): fields.stops.name,
        ("schedule", "interrupts"): fields.interrupts.name,
    },
)
