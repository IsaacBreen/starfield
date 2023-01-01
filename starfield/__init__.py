from typing import List, TypeVar, Type

from attrs import Attribute, fields
from delegatefn import delegate

T = TypeVar("T")

STARFIELD_KEY = type("STARFIELD_KEY", (), {})()


def starfield(target_class: Type[T]) -> Type[T]:
    """
    Modify a class to accept a "star field" argument. A star field is a special type of argument
    that is passed as a tuple of variadic positional arguments (i.e., "*args").

    :param target_class: The class to modify.
    :return: The modified class.
    """
    if not hasattr(target_class, "__attrs_attrs__"):
        raise TypeError(f"Expected attrs class, but did not find __attrs_attrs__ attribute on {target_class}")
    # Get the list of attributes defined on the class
    attributes: List[Attribute] = fields(target_class)
    # Find the attribute with metadata[STARFIELD_KEY]["is_starfield"] == True
    variadic_attributes = [attribute for attribute in attributes if attribute.metadata.get(STARFIELD_KEY, {}).get("is_starfield")]
    # Raise an error if there is not exactly one such attribute
    if len(variadic_attributes) != 1:
        raise ValueError(
            f"Expected exactly one attribute with init='*', got {len(variadic_attributes)}: {variadic_attributes}"
        )
    variadic_attribute = attributes[0]

    def __init__(self, *args, **kwargs):
        """
        Modify the original `__init__` method of the class to accept a "star field" argument.
        """
        # Raise an error if the star field is passed as a keyword argument and there are also variadic positional arguments
        if variadic_attribute.name in kwargs and len(args) > 0:
            raise ValueError(
                f"Cannot pass star field {variadic_attribute.name} as a keyword argument when there are variadic positional arguments"
            )
        # Store the tuple of variadic positional arguments as the value for the star field in the `kwargs` dictionary
        kwargs[variadic_attribute.name] = args
        # Call the original `__attrs_init__` method of the class, passing it the modified `kwargs` dictionary
        self.__attrs_init__(**kwargs)

    # Modify the class to use the new `__init__` method
    target_class.__init__ = __init__ # type: ignore[misc]

    # Return a list of modified Attribute objects
    return [attribute.evolve(kw_only=True) if attribute != variadic_attribute else attribute for attribute in
        attributes]
