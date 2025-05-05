# schedule.py

from draftsman.classes.association import Association
from draftsman.classes.exportable import (
    Exportable,
)
from draftsman.constants import (
    Ticks,
    ValidationMode,
    WaitConditionType,
    WaitConditionCompareType,
)
from draftsman.error import DataFormatError
from draftsman.prototypes.locomotive import Locomotive
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    AttrsSimpleCondition,
    DraftsmanBaseModel,
    uint32,
)
from draftsman.validators import instance_of, one_of, try_convert

import attrs
import copy
from pydantic import (
    ConfigDict,
    Field,
    GetCoreSchemaHandler,
    ValidationError,
    field_serializer,
    field_validator,
    model_validator,
)
from pydantic_core import CoreSchema, core_schema
from typing import Any, Literal, Mapping, Optional, Union


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

    # @property
    # def type(self) -> WaitConditionType:
    #     return self._root.type

    # @type.setter
    # def type(self, value: WaitConditionType):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, __class__.Format, self._root, "type", value
    #         )
    #         self._root.type = result
    #     else:
    #         self._root.type = value

    # =========================================================================

    compare_type: Literal["or", "and"] = attrs.field(
        default="or", validator=one_of("or", "and")
    )

    # @property
    # def compare_type(self):
    #     return self._root.compare_type

    # @compare_type.setter
    # def compare_type(self, value: WaitConditionCompareType):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, __class__.Format, self._root, "compare_type", value
    #         )
    #         self._root.compare_type = result
    #     else:
    #         self._root.compare_type = value

    # =========================================================================

    ticks: Optional[uint32] = attrs.field(validator=instance_of(Optional[uint32]))
    """
    TODO
    """

    @ticks.default
    def _(self):
        if self.type is WaitConditionType.TIME_PASSED:
            return 30 * Ticks.SECOND
        elif self.type is WaitConditionType.INACTIVITY:
            return 5 * Ticks.SECOND
        else:
            return None

    # @property
    # def ticks(self) -> Optional[uint32]:
    #     """
    #     TODO
    #     """
    #     return self._root.ticks

    # @ticks.setter
    # def ticks(self, value: Optional[uint32]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, __class__.Format, self._root, "ticks", value
    #         )
    #         self._root.ticks = result
    #     else:
    #         self._root.ticks = value

    # =========================================================================

    condition: Optional[AttrsSimpleCondition] = attrs.field(
        converter=AttrsSimpleCondition.converter,
        validator=instance_of(Optional[AttrsSimpleCondition]),
    )
    """
    TODO
    """

    @condition.default
    def _(self):
        if self.type in {
            WaitConditionType.ITEM_COUNT,
            WaitConditionType.FLUID_COUNT,
            WaitConditionType.CIRCUIT_CONDITION,
        }:
            return AttrsSimpleCondition()
        else:
            return None

    # @property
    # def condition(self) -> Optional[Condition]:
    #     """
    #     TODO
    #     """
    #     return self._root.condition

    # @condition.setter
    # def condition(self, value: Optional[Condition]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, __class__.Format, self._root, "condition", value
    #         )
    #         self._root.condition = result
    #     else:
    #         self._root.condition = value

    # =========================================================================

    # def validate(
    #     self, mode: ValidationMode = ValidationMode.STRICT, force: bool = False
    # ) -> ValidationResult:
    #     mode = ValidationMode(mode)

    #     output = ValidationResult([], [])

    #     if mode is ValidationMode.NONE and not force:  # (self.is_valid and not force):
    #         return output

    #     context = {
    #         "mode": mode,
    #         "object": self,
    #         "warning_list": [],
    #         "assignment": False,
    #     }

    #     try:
    #         self.Format.model_validate(self._root, strict=False, context=context)
    #         # print("result:", result)
    #         # Reassign private attributes
    #         # TODO
    #         # Acquire the newly converted data
    #         # self._root = result
    #     except ValidationError as e:
    #         output.error_list.append(DataFormatError(e))

    #     output.warning_list += context["warning_list"]

    #     return output

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

    # def __eq__(self, other: "WaitCondition") -> bool:
    #     return (
    #         isinstance(other, WaitCondition)
    #         and self.type == other.type
    #         and self.compare_type == other.compare_type
    #         and self.ticks == other.ticks
    #         and self.condition == other.condition
    #     )


draftsman_converters.add_schema(
    {"$id": "factorio:wait_condition"},
    WaitCondition,
    lambda fields: {
        "type": fields.type.name,
        "compare_type": fields.compare_type.name,
        "ticks": fields.ticks.name,
        "condition": fields.condition.name,
    },
)


class WaitConditions:
    """
    A list of :py:class:`WaitCondition` objects.

    TODO
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
    WaitConditions, lambda l, _: WaitConditions([WaitCondition(**elem) for elem in l])
)


def wait_conditions_unstructure_factory(cls: type, converter):
    def unstructure_hook(inst):
        return [converter.unstructure(w) for w in inst._conditions]

    return unstructure_hook


draftsman_converters.register_unstructure_hook_factory(
    lambda cls: issubclass(cls, WaitConditions), wait_conditions_unstructure_factory
)


# @custom_define(field_order=["locomotives", "schedule", "extra_keys"])
@attrs.define
class Schedule(Exportable):
    """
    An object representing a particular train schedule. Schedules contain
    :py:class:`Association`s to the Locomotives that inherit them, as well as
    the order of stops and their conditions.
    """

    @attrs.define
    class Specification(Exportable):
        @attrs.define
        class Stop(Exportable):
            station: str = attrs.field(validator=instance_of(str))
            wait_conditions: WaitConditions = attrs.field(
                factory=WaitConditions, validator=instance_of(WaitConditions)
            )

            @classmethod
            def converter(cls, value):
                if isinstance(value, dict):
                    return cls(**value)
                return value

        def _records_converter(value):
            if isinstance(value, list):
                res = [None] * len(value)
                for i, elem in enumerate(value):
                    res[i] = Schedule.Specification.Stop.converter(elem)
                return res
            else:
                return value

        records: list[Stop] = attrs.field(
            factory=list,
            converter=_records_converter,
            validator=instance_of(list),  # TODO: validators
        )
        # TODO: interrupts

        @classmethod
        def converter(cls, value):
            if isinstance(value, dict):
                return cls(**value)
            return value

    # class Format(DraftsmanBaseModel):
    #     class ScheduleSpecification(DraftsmanBaseModel):
    #         class Stop(DraftsmanBaseModel):
    #             station: str = Field(
    #                 ...,
    #                 description="""The name of the station for this particular stop.""",
    #             )
    #             wait_conditions: WaitConditions = Field(
    #                 [],
    #                 description="""
    #                 A list of wait conditions that a train with this schedule must satisfy
    #                 in order proceed from the associated 'station' name.""",
    #             )

    #             @field_validator("wait_conditions", mode="before")
    #             @classmethod
    #             def instantiate_wait_conditions_list(cls, value: Any):
    #                 if isinstance(value, list):
    #                     return WaitConditions(value)
    #                 else:
    #                     return value

    #             # @field_validator("wait_conditions", mode="after")
    #             # @classmethod
    #             # def test(cls, value: Any):
    #             #     print("test")
    #             #     print(value)
    #             #     print(type(value))
    #             #     return value

    #             @field_serializer("wait_conditions")
    #             def serialize_wait_conditions(self, value: WaitConditions, _):
    #                 return value.to_dict()

    #         records: list[Stop] = Field([], description="""List of regular stops.""")

    #         # TODO: interrupts

    #     # _locomotives: list[Association.Format] = PrivateAttr()

    #     locomotives: list[Association.Format] = Field(
    #         [],
    #         description="""
    #         A list of the 'entity_number' of each locomotive in a blueprint that
    #         has this schedule.
    #         """,
    #     )
    #     schedule: ScheduleSpecification = Field(
    #         ScheduleSpecification(),
    #         description="""
    #         The list of all train stops and their conditions associated with
    #         this schedule.
    #         """,
    #     )

    # def __init__(
    #     self,
    #     locomotives: list[Association] = [],
    #     schedule: Format.ScheduleSpecification = {},
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    # ):
    #     """
    #     TODO
    #     """
    #     self._root: __class__.Format

    #     super().__init__()

    #     # Construct root
    #     self._root = __class__.Format.model_validate(
    #         {"locomotives": locomotives, "schedule": schedule},
    #         context={"construction": True, "mode": ValidationMode.NONE},
    #     )
    #     # self._root._locomotives = locomotives

    #     # TODO: do I have to convert ints to associations here?
    #     # self.locomotives: list[Association] = []
    #     # for locomotive in locomotives:
    #     #     self.locomotives.append(locomotive)

    #     # self._stops: list[dict] = []
    #     # for stop in self.stops:
    #     #     if not isinstance(stop["wait_conditions"], WaitConditions):
    #     #         # self.stops.append(
    #     #         #     {
    #     #         #         "station": stop["station"],
    #     #         #         "wait_conditions": WaitConditions(stop["wait_conditions"]),
    #     #         #     }
    #     #         # )
    #     #         stop["wait_conditions"] = WaitConditions(stop["wait_conditions"])

    #     self.validate_assignment = validate_assignment

    # =========================================================================

    locomotives: list[Association] = attrs.field(
        factory=list, validator=instance_of(list)  # TODO: validators
    )
    """
    The list of :py:class:`Association`s to each :py:class:`Locomotive` that
    uses this particular ``Schedule``.
    """

    # @property
    # def locomotives(self) -> list[Association]:
    #     """
    #     The list of :py:class:`Association`s to each :py:class:`Locomotive` that
    #     uses this particular ``Schedule``. Read only; use
    #     :py:meth:`add_locomotive` or :py:meth:`remove_locomotive` to change this
    #     list.
    #     """
    #     return self._root.locomotives

    schedule: Specification = attrs.field(
        factory=Specification,
        converter=Specification.converter,
        validator=instance_of(Specification),
    )

    @property
    def stops(self) -> list[Specification.Stop]:
        """
        TODO: update
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
        return self.schedule.records
    
    @stops.setter
    def stops(self, value: list[Specification.Stop]):
        self.schedule.records = value

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
    ):
        """
        Inserts a stop at ``index`` into the list of stations.

        :param index: The index at which to insert the stop in the list.
        :param name: The name of the station to add.
        :param wait_conditions: Either a :py:class:`WaitCondition` or a
            :py:class:`WaitConditions` object of the station to add.
        """
        if wait_conditions is None:
            wait_conditions = WaitConditions([])
        elif isinstance(wait_conditions, WaitCondition):
            wait_conditions = WaitConditions([wait_conditions])

        self.stops.insert(
            index,
            Schedule.Specification.Stop(station=name, wait_conditions=wait_conditions),
        )

    def remove_stop(
        self, name: str, wait_conditions: Union[WaitCondition, WaitConditions] = None
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
            raise ValueError("No station with name '{}' found in schedule".format(name))
        else:
            for i, stop in enumerate(self.stops):
                if stop.station == name and stop.wait_conditions == wait_conditions:
                    self.stops.pop(i)
                    return
            raise ValueError(
                "No station with name '{}' and conditions '{}' found in schedule".format(
                    name, wait_conditions
                )
            )

    # def validate(
    #     self, mode: ValidationMode = ValidationMode.STRICT, force: bool = False
    # ) -> ValidationResult:  # TODO: defer to parent
    #     mode = ValidationMode(mode)

    #     output = ValidationResult([], [])

    #     if (
    #         mode is ValidationMode.NONE and not force
    #     ):  # or (self.is_valid and not force):
    #         return output

    #     context = {
    #         "mode": mode,
    #         "object": self,
    #         "warning_list": [],
    #         "assignment": False,
    #     }

    #     try:
    #         result = self.Format.model_validate(
    #             self._root, strict=False, context=context
    #         )
    #         # print("result:", result)
    #         # Reassign private attributes
    #         # TODO
    #         # Acquire the newly converted data
    #         self._root = result
    #     except ValidationError as e:
    #         output.error_list.append(DataFormatError(e))

    #     output.warning_list += context["warning_list"]

    #     return output

    # def to_dict(self) -> dict:  # TODO: defer to parent
    #     """
    #     Converts this Schedule into it's JSON dict form.

    #     .. NOTE:

    #         Not directly JSON serializable; returns :py:class:`Association`s
    #         which are usually converted in a parent method.

    #     :returns: A ``dict`` representation of this schedule.
    #     """
    #     # stop_list = []
    #     # for stop in self.stops:
    #     #     stop_list.append(
    #     #         {
    #     #             "station": stop["station"],
    #     #             "wait_conditions": stop["wait_conditions"] # .to_dict(),
    #     #         }
    #     #     )
    #     # return {"locomotives": list(self.locomotives), "schedule": stop_list}
    #     return self._root.model_dump(
    #         by_alias=True,
    #         exclude_none=True,
    #         exclude=exclude_defaults=True
    #     )

    # =========================================================================

    # def __eq__(self, other) -> bool:
    #     return (
    #         isinstance(other, Schedule)
    #         and self.locomotives == other.locomotives
    #         and self.stops == other.stops
    #     )

    def __repr__(self) -> str:
        return "<Schedule>{}".format(self.to_dict())


draftsman_converters.add_schema(
    {"$id": "factorio:schedule:specification:stop"},
    Schedule.Specification.Stop,
    lambda fields: {
        "station": fields.station.name,
        "wait_conditions": fields.wait_conditions.name,
    },
)

draftsman_converters.add_schema(
    {"$id": "factorio:schedule:specification"},
    Schedule.Specification,
    lambda fields: {
        "records": fields.records.name,
    },
)

draftsman_converters.add_schema(
    {"$id": "factorio:schedule"},
    Schedule,
    lambda fields: {
        "locomotives": fields.locomotives.name,
        "schedule": fields.schedule.name,
    },
)
