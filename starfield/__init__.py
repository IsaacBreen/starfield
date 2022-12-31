from typing import *
from attrs import *


def starfield(cls: type, fields: List[Attribute]) -> list[Attribute]:
    # Get fields with init="*" and raise an error if there isn't exactly one.
    star_fields = [field for field in fields if field.init == "*"]
    if len(star_fields) != 1:
        raise ValueError(f"Expected exactly one field with init='*', got {len(star_fields)}: {star_fields}")
    star_field = fields[0]
    # Make all other fields kw-only.
    fields = [field if field == star_field else field.evolve(kw_only=True) for field in fields]
    # Construct __init__.
    def __init__(self, *args, **kwargs):
        if not hasattr(self, "__attrs_init__"):
            raise TypeError(f"Class {cls.__name__} has no __attrs_init__ method.")
        # The star field can be passed as a variadic positional argument or as a keyword argument.
        # Ensure it is not passed as both.
        if len(args) > 0 and star_field.name in kwargs:
            raise ValueError(f"Cannot pass star field {star_field.name} as a keyword argument when there are variadic positional arguments")
        # If variadic positional arguments are passed, add them to the keyword arguments.
        if len(args) > 0:
            kwargs[star_field.name] = args
        # Call __attrs_init__.
        self.__attrs_init__(**kwargs)

    if hasattr(cls, "__attrs_attrs__"):
        if not hasattr(cls, "__attrs_init__"):
            cls.__attrs_init__ = cls.__init__
        cls.__init__ = __init__
    else:
        cls.__init__ = __init__
    return fields