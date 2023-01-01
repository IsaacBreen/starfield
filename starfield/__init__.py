from typing import List

from attrs import Attribute


def starfield(target_class: type, attributes: List[Attribute]) -> List[Attribute]:
    """
    Modify a class to accept a "star field" argument. A star field is a special type of argument
    that is passed as a tuple of variadic positional arguments (i.e., "*args").

    :param target_class: The class to modify.
    :param attributes: A list of Attribute objects for the class.
    :return: A list of modified Attribute objects, with the star field included as is and the other
        attributes having their `kw_only` attribute set to `True`.
    """
    # Find the attribute with `init` set to "*"
    variadic_attributes = [attribute for attribute in attributes if attribute.init == "*"]
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
    target_class.__attrs_init__ = getattr(target_class, "__attrs_init__", target_class.__init__)
    target_class.__init__ = __init__

    # Return a list of modified Attribute objects
    return [attribute.evolve(kw_only=True) if attribute != variadic_attribute else attribute for attribute in
        attributes]
