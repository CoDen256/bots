import dataclasses
import datetime
from dataclasses import dataclass, fields
from typing import Any


@dataclass
class DefaultVal:
    val: Any


@dataclass
class NoneRefersDefault:
    def __post_init__(self):
        for field in fields(self):

            # if a field of this data class defines a default value of type
            # `DefaultVal`, then use its value in case the field after
            # initialization has either not changed or is None.
            if isinstance(field.default, DefaultVal):
                field_val = getattr(self, field.name)
                if isinstance(field_val, DefaultVal) or field_val is None:
                    setattr(self, field.name, field.default.val)

@dataclass
class Wohnung(NoneRefersDefault):
    address: str
    zip: str
    name: str = DefaultVal("N/A")
    company: str = DefaultVal("N/A")
    url: str = DefaultVal("N/A")

    phone: str = DefaultVal("N/A")
    mobile: str = DefaultVal("N/A")
    space: str = DefaultVal("0.0")
    total_rent: str = DefaultVal("0.0")

    ome: str = DefaultVal("-1")
    htwk: str = DefaultVal("-1")

    kitchen: str = DefaultVal("No" )# No, Yes
    pets: str = DefaultVal("VB" )# No, Yes, VB

    move: str = DefaultVal("01.01.2023")
    extra: bool = DefaultVal(False)

    def copy(self):
        return dataclasses.replace(self)