# schedule.py

from draftsman.classes.association import Association
from draftsman.classes.exportable import (
    Exportable,
    ValidationResult,
    attempt_and_reissue,
)
from draftsman.constants import (
    Ticks,
    ValidationMode,
    WaitConditionType,
    WaitConditionCompareType,
)
from draftsman.error import DataFormatError
from draftsman.prototypes.locomotive import Locomotive
from draftsman.signatures import Condition, DraftsmanBaseModel, uint32

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


# TODO: make dataclass?
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

        # (If the cargo is full and been inactive for 1 minute) or signal sent
        conditions = cargo_full & inactivity | run_signal
        assert isinstance(conditions, WaitConditions)
    """

    class Format(DraftsmanBaseModel):
        type: WaitConditionType = Field(
            ..., description="""The type of wait condition."""
        )
        compare_type: WaitConditionCompareType = Field(
            "or",
            description="""
            The boolean operation to perform in relation to the next condition
            in the list of wait conditions. Contrary to what you might expect,
            the 'compare_type' of a wait condition indicates it's relation to 
            the *previous* wait condition, not the following. This means that if
            you want to 'and' two wait conditions together, you need to set the
            'compare_type' of the second condition to 'and'; the 'compare_type' 
            of the first condition is effectively ignored.
            """,
        )
        ticks: Optional[uint32] = Field(
            None,
            description="""
            The amount of game ticks to wait, if the 'type' of the wait 
            condition is set to either 'time' or 'inactivity'. Defaults to 30 
            seconds if type is 'time', 5 seconds if type is  'inactivity', and 
            null for everything else.
            """,
        )
        condition: Optional[Condition] = Field(
            Condition(),
            description="""
            A condition that must be satisfied in order for the schedule to 
            progress; only used if 'type' is set to 'item_count', 'fluid_count',
            or 'circuit'.
            """,
        )

        @model_validator(mode="wrap")
        @classmethod
        def handle_class_instance(cls, value: Any, handler):
            if isinstance(value, WaitCondition):
                return value
            else:
                return handler(value)

        model_config = ConfigDict(title="WaitCondition")

    def __init__(
        self,
        type: Literal[
            "time",
            "inactivity",
            "full",
            "empty",
            "item_count",
            "fluid_count",
            "circuit",
            "passenger_present",
            "passenger_not_present",
        ],
        compare_type: Literal["and", "or"] = "or",
        ticks: uint32 = None,
        condition: Condition = None,
        validate: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
    ):
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
        self._root: __class__.Format

        super().__init__()

        self._root = self.Format.model_construct()

        self.type = type
        self.compare_type = compare_type
        if type == WaitConditionType.TIME_PASSED and ticks is None:
            self.ticks = 30 * Ticks.SECOND
        elif type == WaitConditionType.INACTIVITY and ticks is None:
            self.ticks = 5 * Ticks.SECOND
        else:
            self.ticks = ticks
        if type in {
            WaitConditionType.ITEM_COUNT,
            WaitConditionType.FLUID_COUNT,
            WaitConditionType.CIRCUIT_CONDITION,
        }:
            self.condition = Condition() if condition is None else condition
        else:
            self.condition = condition

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    # def to_dict(self) -> dict:
    #     result = {"type": self.type, "compare_type": self.compare_type}
    #     if self.ticks:
    #         result["ticks"] = self.ticks
    #     if self.condition:
    #         result["condition"] = {
    #             "first_signal": self.condition[0],
    #             "comparator": self.condition[1],
    #         }
    #         b = self.condition[2]
    #         if isinstance(b, int):
    #             result["condition"]["constant"] = b
    #         else:
    #             result["condition"]["second_signal"] = b

    #     return result

    # =========================================================================

    @property
    def type(self) -> WaitConditionType:
        return self._root.type

    @type.setter
    def type(self, value: WaitConditionType):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, __class__.Format, self._root, "type", value
            )
            self._root.type = result
        else:
            self._root.type = value

    # =========================================================================

    @property
    def compare_type(self):
        return self._root.compare_type

    @compare_type.setter
    def compare_type(self, value: WaitConditionCompareType):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, __class__.Format, self._root, "compare_type", value
            )
            self._root.compare_type = result
        else:
            self._root.compare_type = value

    # =========================================================================

    @property
    def ticks(self) -> Optional[uint32]:
        """
        TODO
        """
        return self._root.ticks

    @ticks.setter
    def ticks(self, value: Optional[uint32]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, __class__.Format, self._root, "ticks", value
            )
            self._root.ticks = result
        else:
            self._root.ticks = value

    # =========================================================================

    @property
    def condition(self) -> Optional[Condition]:
        """
        TODO
        """
        return self._root.condition

    @condition.setter
    def condition(self, value: Optional[Condition]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, __class__.Format, self._root, "condition", value
            )
            self._root.condition = result
        else:
            self._root.condition = value

    # =========================================================================

    def validate(
        self, mode: ValidationMode = ValidationMode.STRICT, force: bool = False
    ) -> ValidationResult:
        mode = ValidationMode(mode)

        output = ValidationResult([], [])

        if mode is ValidationMode.NONE or (self.is_valid and not force):
            return output

        context = {
            "mode": mode,
            "object": self,
            "warning_list": [],
            "assignment": False,
        }

        try:
            result = self.Format.model_validate(
                self._root, strict=False, context=context
            )
            # print("result:", result)
            # Reassign private attributes
            # TODO
            # Acquire the newly converted data
            self._root = result
        except ValidationError as e:
            output.error_list.append(DataFormatError(e))

        output.warning_list += context["warning_list"]

        return output

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

    def __eq__(self, other: "WaitCondition") -> bool:
        return (
            isinstance(other, WaitCondition)
            and self.type == other.type
            and self.compare_type == other.compare_type
            and self.ticks == other.ticks
            and self.condition == other.condition
        )

    def __repr__(self) -> str:
        return "<WaitCondition>{{{}}}".format(str(self._root))


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

    def to_dict(self) -> list:
        return [condition.to_dict() for condition in self._conditions]

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

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls, handler(list[WaitCondition.Format])
        )


class Schedule(Exportable):
    """
    An object representing a particular train schedule. Schedules contain
    :py:class:`Association`s to the Locomotives that inherit them, as well as
    the order of stops and their conditions.
    """

    class Format(DraftsmanBaseModel):
        class Stop(DraftsmanBaseModel):
            station: str = Field(
                ..., description="""The name of the station for this particular stop."""
            )
            wait_conditions: WaitConditions = Field(
                [],
                description="""
                A list of wait conditions that a train with this schedule must satisfy 
                in order proceed from the associated 'station' name.""",
            )

            @field_validator("wait_conditions", mode="before")
            @classmethod
            def instantiate_wait_conditions_list(cls, value: Any):
                if isinstance(value, list):
                    return WaitConditions(value)
                else:
                    return value

            # @field_validator("wait_conditions", mode="after")
            # @classmethod
            # def test(cls, value: Any):
            #     print("test")
            #     print(value)
            #     print(type(value))
            #     return value

            @field_serializer("wait_conditions")
            def serialize_wait_conditions(self, value: WaitConditions, _):
                return value.to_dict()

        # _locomotives: list[Association.Format] = PrivateAttr()

        locomotives: list[Association.Format] = Field(
            [],
            description="""
            A list of the 'entity_number' of each locomotive in a blueprint that
            has this schedule.
            """,
        )
        schedule: list[Stop] = Field(
            [],
            description="""
            The list of all train stops and their conditions associated with 
            this schedule.
            """,
        )

    def __init__(
        self,
        locomotives: list[Association] = [],
        schedule: list[Format.Stop] = [],
        validate: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
    ):
        """
        TODO
        """
        self._root: __class__.Format

        super().__init__()

        # Construct root
        self._root = __class__.Format.model_validate(
            {"locomotives": locomotives, "schedule": schedule},
            context={"construction": True, "mode": ValidationMode.NONE},
        )
        # self._root._locomotives = locomotives

        # TODO: do I have to convert ints to associations here?
        # self.locomotives: list[Association] = []
        # for locomotive in locomotives:
        #     self.locomotives.append(locomotive)

        # self._stops: list[dict] = []
        # for stop in self.stops:
        #     if not isinstance(stop["wait_conditions"], WaitConditions):
        #         # self.stops.append(
        #         #     {
        #         #         "station": stop["station"],
        #         #         "wait_conditions": WaitConditions(stop["wait_conditions"]),
        #         #     }
        #         # )
        #         stop["wait_conditions"] = WaitConditions(stop["wait_conditions"])

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    # =========================================================================

    @property
    def locomotives(self) -> list[Association]:
        """
        The list of :py:class:`Association`s to each :py:class:`Locomotive` that
        uses this particular ``Schedule``. Read only; use
        :py:meth:`add_locomotive` or :py:meth:`remove_locomotive` to change this
        list.
        """
        return self._root.locomotives

    @property
    def stops(self) -> list[Format.Stop]:
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
        return self._root.schedule

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
            index, self.Format.Stop(station=name, wait_conditions=wait_conditions)
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
                if stop["station"] == name:
                    self.stops.pop(i)
                    return
            raise ValueError("No station with name '{}' found in schedule".format(name))
        else:
            for i, stop in enumerate(self.stops):
                if (
                    stop["station"] == name
                    and stop["wait_conditions"] == wait_conditions
                ):
                    self.stops.pop(i)
                    return
            raise ValueError(
                "No station with name '{}' and conditions '{}' found in schedule".format(
                    name, wait_conditions
                )
            )

    def validate(
        self, mode: ValidationMode = ValidationMode.STRICT, force: bool = False
    ) -> ValidationResult:  # TODO: defer to parent
        mode = ValidationMode(mode)

        output = ValidationResult([], [])

        if mode is ValidationMode.NONE or (self.is_valid and not force):
            return output

        context = {
            "mode": mode,
            "object": self,
            "warning_list": [],
            "assignment": False,
        }

        try:
            result = self.Format.model_validate(
                self._root, strict=False, context=context
            )
            # print("result:", result)
            # Reassign private attributes
            # TODO
            # Acquire the newly converted data
            self._root = result
        except ValidationError as e:
            output.error_list.append(DataFormatError(e))

        output.warning_list += context["warning_list"]

        return output

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

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, Schedule)
            and self.locomotives == other.locomotives
            and self.stops == other.stops
        )

    def __repr__(self) -> str:
        return "<Schedule>{}".format(self.to_dict())
